#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
relationship_engine.py — PAIOS 知识关系反向发现引擎 v0.1

把 20_KNOWLEDGE + 30_SYSTEM/ADR 中已有的 related 字段激活为可查询的双向关系图。

核心原则：
  - 只读源文件，不修改任何 20_KNOWLEDGE / 30_SYSTEM/ADR 文件
  - 输出 = 派生 sidecar JSON（可删除重建，不进数据库，不污染治理）
  - 容错优先：现有 related 字段有 4 种格式、4 种引用目标，引擎全容错
  - 纯 Python 标准库 + 可选 PyYAML

用法：
  python relationship_engine.py build                          # 全量扫描 + 重建
  python relationship_engine.py backlinks <node_id>            # 谁引用了我
  python relationship_engine.py forward <node_id>              # 我引用了谁
  python relationship_engine.py orphans                        # 孤岛节点
  python relationship_engine.py unresolved                     # 断链清单
  python relationship_engine.py graph --format dot             # 导出 Graphviz DOT
  python relationship_engine.py stats                          # 图统计
  python relationship_engine.py stats --json                   # JSON 格式统计

退出码：0 = 成功（含警告）；1 = 错误（冲突/崩溃）
"""

import copy
import os
import re
import sys
import json
import glob as glob_module
from datetime import datetime, timezone, timedelta

# ---------- Try PyYAML, fallback to custom parser ----------
try:
    import yaml as _yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# ---------- 定位 PAIOS 根目录 ----------
# 脚本位于 <root>/40_AUTOMATION/05_SCRIPTS/relationship_engine.py
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAIOS_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if not os.path.isdir(os.path.join(PAIOS_ROOT, "20_KNOWLEDGE")):
    PAIOS_ROOT = os.environ.get("PAIOS_ROOT", PAIOS_ROOT)

SCOPE_DIRS = [
    ("20_KNOWLEDGE", os.path.join(PAIOS_ROOT, "20_KNOWLEDGE")),
    ("30_SYSTEM/ADR", os.path.join(PAIOS_ROOT, "30_SYSTEM", "ADR")),
]
OUTPUT_RELATIVE = "30_SYSTEM/Registry/relationship-graph.json"
OUTPUT_FILE = os.path.join(PAIOS_ROOT, OUTPUT_RELATIVE)

# ---------- 正则模式 ----------
ADR_FILENAME_RE = re.compile(r'^(ADR-\d+)')  # 从文件名提取 ADR-00xx
ADR_LOOKUP_RE = re.compile(r'^(ADR-\d+)')     # 从引用串提取 ADR-00xx
SUPERSEDES_RE = re.compile(
    r'(?:\*\*Supersedes\*\*|Supersedes|supersedes|取代)\s*:\s*(ADR-\d+)',
    re.IGNORECASE
)
# 前页标记：仅匹配文件最开头的 ---...--- 块
FRONTMATTER_RE = re.compile(r'\A---\s*$(.*?)\n---\s*$', re.MULTILINE | re.DOTALL)

# ==== 自定义 Frontmatter YAML 解析（fallback） ====

CUSTOM_BOOLS = {"true": True, "false": False, "yes": True, "no": False}


def _parse_fm_value(v):
    """解析一个标量值（无嵌套结构）。"""
    v = v.strip()
    if v == "":
        return None
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    if v in CUSTOM_BOOLS:
        return CUSTOM_BOOLS[v]
    if re.fullmatch(r'-?\d+(?:\.\d+)?', v):
        return float(v) if "." in v else int(v)
    return v


def _parse_fm_line(line):
    """解析单行 key: value 或 key:（list 开始）。"""
    if ":" not in line:
        return None, None
    k, _, v = line.partition(":")
    k = k.strip()
    v = v.strip()
    return k, v


def _has_frontmatter(text):
    """检查文本是否以 YAML frontmatter 开头。"""
    return text.startswith('---')


def extract_frontmatter_block(text):
    """提取 frontmatter 块的原始文本。返回 (raw_text | None)。"""
    if not _has_frontmatter(text):
        return None
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    raw = m.group(1)
    if not raw.strip():
        return None
    return raw


def parse_frontmatter_yaml(text):
    """简易 frontmatter YAML 解析（处理嵌套缩进和 inline 数组）。

    覆盖字段：scalar / list (inline `[a,b]` 或 block `- xxx`) / nested dict。
    仅在 PyYAML 不可用或失败时作为 fallback。
    """
    raw = extract_frontmatter_block(text)
    if raw is None:
        return {}
    return _parse_yaml_lines(raw.splitlines())


def _parse_yaml_lines(lines):
    """将 YAML 行解析为嵌套 dict。

    支持：
      - scalar: key: value
      - inline list: key: [a, b, c] 或 key: ["a", "b"]
      - block list:
          key:
            - item1
            - item2
      - nested dict:
          key:
            subkey: value
    """
    result = {}
    stack = [(0, result)]  # (indent, dict)
    block_list_key = None
    block_list_target = None

    for raw_line in lines:
        line = raw_line.rstrip("\n\r")
        stripped = line.strip()
        if stripped == "" or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))

        if stripped.startswith("- "):
            # block list item
            item_val = _parse_fm_value(stripped[2:])
            if block_list_target is not None:
                block_list_target.append(item_val)
            else:
                # block list 刚在空键下开始：将空 {} 占位符转为 []
                if len(stack) >= 2:
                    parent = stack[-2][1]
                    empty_ref = stack[-1][1]
                    for pk, pv in parent.items():
                        if pv is empty_ref:
                            parent[pk] = []
                            block_list_target = parent[pk]
                            block_list_target.append(item_val)
                            break
            continue
        else:
            block_list_key = None
            block_list_target = None

        if ":" not in stripped:
            continue

        k, _, v = stripped.partition(":")
        k = k.strip()
        v = v.strip()

        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()

        current = stack[-1][1]

        if v == "" or v is None:
            new_dict = {}
            current[k] = new_dict
            stack.append((indent, new_dict))
        elif v == "[]":
            current[k] = []
        elif v == "{}":
            current[k] = {}
        elif v.startswith("["):
            current[k] = _parse_inline_list(v)
        else:
            current[k] = _parse_fm_value(v)

    return result


def _parse_inline_list(text):
    """Parse [a, b, c] or ["a", "b"] into a Python list."""
    text = text.strip()
    if not (text.startswith("[") and text.endswith("]")):
        return [_parse_fm_value(text)]
    inner = text[1:-1].strip()
    if not inner:
        return []
    items = []
    for item in re.split(r',\s*(?=(?:[^"]*"[^"]*")*[^"]*$)', inner):
        item = item.strip()
        if not item:
            continue
        items.append(_parse_fm_value(item))
    return items


def parse_frontmatter_yaml_pyyaml(text):
    """使用 PyYAML 解析 frontmatter。"""
    raw = extract_frontmatter_block(text)
    if raw is None:
        return {}
    try:
        result = _yaml.safe_load(raw)
        if isinstance(result, dict):
            return result
        return {}
    except Exception:
        return {}


def extract_frontmatter(text):
    """提取 frontmatter dict。

    优先使用 PyYAML（更可靠），回退到自定义解析器。
    返回 dict（无 frontmatter 时返回空 dict）。
    """
    if not _has_frontmatter(text):
        return {}
    if HAS_YAML:
        try:
            result = parse_frontmatter_yaml_pyyaml(text)
            if isinstance(result, dict) and result:
                return result
        except Exception:
            pass
    result = parse_frontmatter_yaml(text)
    if isinstance(result, dict):
        return result
    return {}


def extract_title(text, filename_stem):
    """从 frontmatter 或正文 h1 提取标题。"""
    fm = extract_frontmatter(text)
    if fm.get("title"):
        return fm["title"]
    m = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return filename_stem


# ==== 扫描 ====

class Scanner:
    """扫描 PAIOS 目录，收集所有 .md 文件的基本信息。"""

    def __init__(self):
        self.files = []

    def scan(self):
        """执行扫描，返回文件列表。

        每个条目：{
            "path": "相对路径",
            "abspath": "绝对路径",
            "scope": "20_KNOWLEDGE" | "30_SYSTEM/ADR",
            "raw_text": 文件全文,
            "filename_stem": "文件名（去 .md）",
            "path_stem": "含目录上下文的路径风格 ID",
        }
        """
        self.files = []
        for scope_name, scope_dir in SCOPE_DIRS:
            if scope_name == "20_KNOWLEDGE":
                pattern = os.path.join(scope_dir, "**", "*.md")
            else:
                pattern = os.path.join(scope_dir, "*.md")

            matched = glob_module.glob(pattern, recursive=(scope_name == "20_KNOWLEDGE"))
            for abspath in sorted(matched):
                relpath = os.path.relpath(abspath, PAIOS_ROOT)
                filename_stem = os.path.splitext(os.path.basename(abspath))[0]
                try:
                    with open(abspath, "r", encoding="utf-8") as f:
                        raw_text = f.read()
                except (OSError, UnicodeDecodeError):
                    continue
                # 路径风格 ID（去掉 scope 前缀和 .md 扩展名）
                path_stem = relpath.replace("\\", "/")
                if path_stem.endswith(".md"):
                    path_stem = path_stem[:-3]
                if path_stem.startswith("20_KNOWLEDGE/"):
                    path_stem = path_stem[13:]
                elif path_stem.startswith("30_SYSTEM/"):
                    path_stem = path_stem[10:]
                path_stem = path_stem.replace("/", "-")

                self.files.append({
                    "path": relpath.replace("\\", "/"),
                    "abspath": abspath,
                    "scope": scope_name,
                    "raw_text": raw_text,
                    "filename_stem": filename_stem,
                    "path_stem": path_stem,
                })
        return self.files


# ==== 节点解析 ====

class NodeResolver:
    """将扫描得到的文件解析为 node（含 node_id 三层 fallback）。"""

    def __init__(self):
        self.nodes = []
        self.id_to_node = {}
        self.stem_to_nodes = {}
        self.refid_to_node = {}
        self.conflicts = []

    def resolve_all(self, scanned_files):
        """对扫描结果批量解析 node。"""
        self.nodes = []
        self.id_to_node = {}
        self.stem_to_nodes = {}
        self.refid_to_node = {}
        self.conflicts = []

        for sf in scanned_files:
            node = self._resolve_one(sf)
            self.nodes.append(node)

        # 检查冲突并去重
        seen_ids = {}
        for node in self.nodes:
            nid = node["id"]
            if nid in seen_ids:
                path_part = node["path"].replace("\\", "/")
                # 用父目录名 + 文件名做去重后缀
                parts = path_part.split("/")
                parent_dir = parts[-2] if len(parts) >= 2 else "root"
                fname = parts[-1].replace(".md", "")
                path_slug = f"{parent_dir}-{fname}"
                if len(path_slug) > 80:
                    path_slug = path_slug[-80:]
                disambiguated = f"{nid}__{path_slug}"
                self.conflicts.append({
                    "node_id": nid,
                    "files": [seen_ids[nid]["path"], node["path"]],
                    "resolved_as": disambiguated,
                })
                node["_conflict"] = True
                node["_conflict_with"] = seen_ids[nid]["path"]
                node["id"] = disambiguated
                node["_original_id"] = nid
                node["_resolved_from"] = f"{node.get('_resolved_from', '?')} (disambiguated)"
                seen_ids[disambiguated] = node
                self.id_to_node[disambiguated] = node
            else:
                seen_ids[nid] = node
                self.id_to_node[nid] = node

            stem = node.get("_filename_stem", "")
            self.stem_to_nodes.setdefault(stem, []).append(node)

            ref_id = node.get("_resolved_ref_id")
            if ref_id:
                self.refid_to_node[ref_id] = node

        return self.nodes

    def _resolve_one(self, sf):
        """解析单个文件为 node。"""
        raw_text = sf["raw_text"]
        fm = extract_frontmatter(raw_text)
        filename_stem = sf["filename_stem"]
        is_adr = sf["scope"] == "30_SYSTEM/ADR"

        node_id = None
        resolved_from = None

        # P1: frontmatter.id
        fm_id = fm.get("id")
        if fm_id and isinstance(fm_id, str) and fm_id.strip():
            node_id = fm_id.strip()
            resolved_from = "frontmatter.id"

        # P2: frontmatter.ref_id
        if not node_id:
            fm_ref_id = fm.get("ref_id")
            if fm_ref_id and isinstance(fm_ref_id, str) and fm_ref_id.strip():
                node_id = fm_ref_id.strip()
                resolved_from = "frontmatter.ref_id"

        # ADR 特例：adr 字段 -> ADR-{adr}
        if not node_id and is_adr:
            fm_adr = fm.get("adr")
            if fm_adr is not None:
                adr_str = str(fm_adr).strip().strip('"').strip("'")
                if adr_str:
                    node_id = f"ADR-{adr_str}"
                    resolved_from = "frontmatter.adr"

        # ADR 特例：文件名前缀 ADR-XXXX
        if not node_id and is_adr:
            m = ADR_FILENAME_RE.match(filename_stem)
            if m:
                node_id = m.group(1)
                resolved_from = "filename-adr-prefix"

        # P3: 路径风格 stem（含目录上下文）
        if not node_id:
            node_id = sf["path_stem"]
            resolved_from = "path-stem"

        # 提取 title
        title = fm.get("title")
        if not title:
            m = re.search(r'^#\s+(.+)$', raw_text, re.MULTILINE)
            if m:
                title = m.group(1).strip()
            else:
                title = filename_stem

        tags = fm.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        if not isinstance(tags, list):
            tags = []

        node_type = "knowledge"
        if is_adr:
            node_type = "adr"
        else:
            fm_type = fm.get("type")
            if fm_type and isinstance(fm_type, str):
                node_type = fm_type

        node = {
            "id": node_id,
            "path": sf["path"],
            "title": title,
            "type": node_type,
            "has_frontmatter": bool(fm),
            "tags": tags,
            "_filename_stem": filename_stem,
            "_resolved_from": resolved_from,
            "_raw_text": raw_text,
            "_fm": fm,
        }
        if fm.get("ref_id"):
            node["_resolved_ref_id"] = str(fm["ref_id"]).strip()
        if fm.get("adr"):
            node["_raw_adr"] = str(fm["adr"])
        if "related" in fm:
            node["_raw_related"] = fm["related"]

        return node


# ==== Related 字段解析 ====

class RelatedParser:
    """解析 frontmatter 中的 related 字段（4 种格式容错）。"""

    @staticmethod
    def parse(raw_related):
        """接收 frontmatter.related 的原始值，返回解析后的字符串列表。

        兼容 4 种输入格式：
        A. ["a", "b"] - YAML inline list
        B. [] - 空 list（返回 []）
        C. - "a" / - a（YAML block list）
        D. "a, b, c" - 裸逗号字符串

        返回值：(items: list[str], warnings: list[str])
        """
        warnings = []
        if raw_related is None:
            return [], warnings

        if isinstance(raw_related, list):
            items = []
            for item in raw_related:
                if isinstance(item, str):
                    s = item.strip()
                    if s:
                        items.append(s)
                elif isinstance(item, (int, float)):
                    s = str(item).strip()
                    if s:
                        items.append(s)
            return items, warnings

        if isinstance(raw_related, str):
            s = raw_related.strip()
            if not s or s == "[]" or s == "{}":
                return [], warnings
            if s.startswith("[") and s.endswith("]"):
                inner = s[1:-1].strip()
                if not inner:
                    return [], warnings
                items = []
                for part in re.split(r',\s*(?=(?:[^"]*"[^"]*")*[^"]*$)', inner):
                    part = part.strip().strip('"').strip("'").strip()
                    if part:
                        items.append(part)
                return items, warnings
            items = [x.strip() for x in s.split(",") if x.strip()]
            return items, warnings

        return [str(raw_related).strip()], warnings


# ==== 引用目标解析 ====

class TargetResolver:
    """把 raw target 字符串解析为目标 node_id。"""

    def __init__(self, node_resolver):
        self.nr = node_resolver
        self.unresolved = []

    def resolve(self, source_node_id, raw_target):
        """解析单个 raw_target，返回 (node_id|None, reason|None)。"""
        target = raw_target.strip().strip('"').strip("'").strip()
        if not target:
            return None, None

        # Step 1: 直接匹配已扫描节点的 id
        if target in self.nr.id_to_node:
            return target, None

        # Step 2: 匹配已扫描节点的 ref_id
        if target in self.nr.refid_to_node:
            return self.nr.refid_to_node[target]["id"], None

        # Step 3: 匹配 ADR-XXXX 前缀
        m = ADR_LOOKUP_RE.match(target)
        if m:
            adr_prefix = m.group(1)
            if adr_prefix in self.nr.id_to_node:
                return adr_prefix, None
            for nid, node in self.nr.id_to_node.items():
                if node["path"].startswith("30_SYSTEM/ADR/") and target in node["path"]:
                    return nid, None

        # Step 4: 匹配文件名 stem
        target_stem = os.path.basename(target)
        if target_stem.endswith(".md"):
            target_stem = target_stem[:-3]
        if target_stem in self.nr.stem_to_nodes:
            candidates = self.nr.stem_to_nodes[target_stem]
            if len(candidates) == 1:
                return candidates[0]["id"], None
            else:
                return candidates[0]["id"], None

        # Step 4b: 尝试相对路径解析
        for base_dir in [PAIOS_ROOT, os.path.join(PAIOS_ROOT, "20_KNOWLEDGE"),
                         os.path.join(PAIOS_ROOT, "30_SYSTEM")]:
            candidate = os.path.normpath(os.path.join(base_dir, target))
            if os.path.isfile(candidate):
                cstem = os.path.splitext(os.path.basename(candidate))[0]
                if cstem in self.nr.stem_to_nodes:
                    candidates = self.nr.stem_to_nodes[cstem]
                    if len(candidates) == 1:
                        return candidates[0]["id"], None
                    for c in candidates:
                        if os.path.normpath(os.path.join(PAIOS_ROOT, c["path"])) == candidate:
                            return c["id"], None

        # Step 5: 匹配各节点的原始文件名 stem（bare stem 引用）
        bare_stem = os.path.splitext(os.path.basename(target))[0]
        for nid, node in self.nr.id_to_node.items():
            node_bare_stem = node.get("_filename_stem", "")
            full_path = node.get("path", "")
            path_dotless = full_path.replace(".md", "").replace("\\", "/")
            if bare_stem == node_bare_stem or path_dotless.endswith(bare_stem):
                return nid, None

        # Unresolved
        reason = self._unresolved_reason(target)
        self.unresolved.append({
            "from": source_node_id,
            "raw_target": raw_target,
            "reason": reason,
        })
        return None, reason

    def _unresolved_reason(self, target):
        if "*" in target:
            return "glob-pattern"
        if "/" in target and not target.startswith("ADR-"):
            return "path-unresolved"
        for scope_name, scope_dir in SCOPE_DIRS:
            candidate = os.path.join(scope_dir, target)
            if os.path.isfile(candidate):
                return "file-outside-scope"
        if target.upper().startswith("README"):
            return "ambiguous-readme"
        return "no-matching-node"

    def resolve_all(self, nodes):
        """批量解析所有节点的 related 字段。"""
        self.unresolved = []
        declared_edges = []

        for node in nodes:
            raw_related = node.get("_raw_related")
            if raw_related is None:
                continue
            items, _warnings = RelatedParser.parse(raw_related)
            for raw_target in items:
                source_id = node["id"]
                target_id, reason = self.resolve(source_id, raw_target)
                if target_id and target_id == source_id:
                    continue
                edge = {
                    "source": source_id,
                    "target": target_id if target_id else f"__UNRESOLVED__{raw_target}",
                    "raw": raw_target,
                    "resolved": target_id is not None,
                }
                declared_edges.append(edge)

        # 去重
        seen = set()
        unique = []
        for e in declared_edges:
            key = (e["source"], e["target"])
            if key not in seen:
                seen.add(key)
                unique.append(e)
        return unique


# ==== Graph Builder ====

class GraphBuilder:
    """构建完整的关系图。"""

    def __init__(self, scanner, node_resolver, target_resolver):
        self.scanner = scanner
        self.nr = node_resolver
        self.tr = target_resolver

    def build(self):
        """执行全量构建。"""
        scanned = self.scanner.scan()
        nodes = self.nr.resolve_all(scanned)

        if self.nr.conflicts:
            for c in self.nr.conflicts:
                disambiguated = c.get("resolved_as", "?")
                print(f"[WARN] Node ID conflict: '{c['node_id']}' -> '{disambiguated}' for {c['files'][1]}", file=sys.stderr)

        cst = timezone(timedelta(hours=8))
        self._build_ts = datetime.now(cst).strftime("%Y-%m-%dT%H:%M:%S%z")

        declared_edges = self.tr.resolve_all(nodes)
        backlinks = self._generate_backlinks(declared_edges, nodes)
        supersedes = self._parse_supersedes(nodes)

        clean_nodes = []
        for n in nodes:
            clean_nodes.append({
                "id": n["id"],
                "path": n["path"],
                "title": n["title"],
                "type": n["type"],
                "has_frontmatter": n["has_frontmatter"],
            })

        all_edge_ids = set()
        for e_list in [declared_edges, backlinks, supersedes]:
            for e in e_list:
                all_edge_ids.add(e["source"])
                all_edge_ids.add(e["target"])
        orphans = [n["id"] for n in clean_nodes if n["id"] not in all_edge_ids]

        stats = {
            "nodes": len(clean_nodes),
            "declared_edges": len(declared_edges),
            "backlinks": len(backlinks),
            "supersedes": len(supersedes),
            "unresolved": len(self.tr.unresolved),
            "orphans": len(orphans),
        }

        graph = {
            "generated_at": self._build_ts,
            "generator": "relationship_engine v0.1",
            "stats": stats,
            "nodes": clean_nodes,
            "edges_declared": [
                {
                    **{k: v for k, v in e.items() if k != "_index"},
                    "confidence": 1.0,
                    "source_type": "human_frontmatter",
                    "created_by": "human",
                    "created_time": self._build_ts,
                }
                for e in declared_edges
            ],
            "edges_backlinks": backlinks,
            "edges_supersedes": supersedes,
            "unresolved": self.tr.unresolved,
            "orphans": sorted(orphans),
            "warnings": [],
        }
        return graph

    def _generate_backlinks(self, declared_edges, nodes):
        backlinks = []
        for e in declared_edges:
            if not e["resolved"]:
                continue
            bl = {
                "source": e["target"],
                "target": e["source"],
                "type": "backlink",
                "via": f"backlink-of:{e['source']}->{e['target']}",
                "confidence": 1.0,
                "source_type": "engine_derived",
                "created_by": "relationship_engine",
                "created_time": self._build_ts,
            }
            backlinks.append(bl)
        return backlinks

    def _parse_supersedes(self, nodes):
        supersedes = []
        for node in nodes:
            if node["type"] != "adr":
                continue
            raw_text = node.get("_raw_text", "")
            for m in SUPERSEDES_RE.finditer(raw_text):
                target = m.group(1)
                if target in self.nr.id_to_node:
                    supersedes.append({
                        "source": node["id"],
                        "target": target,
                        "type": "supersedes",
                        "via": "adr-text-scan",
                        "confidence": 1.0,
                        "source_type": "adr_text_scan",
                        "created_by": "relationship_engine",
                        "created_time": self._build_ts,
                    })
                else:
                    self.tr.unresolved.append({
                        "from": node["id"],
                        "raw_target": target,
                        "reason": "supersedes-target-not-found",
                    })
        return supersedes


# ==== 图序列化 ====

def write_graph(graph, output_path=None):
    if output_path is None:
        output_path = OUTPUT_FILE
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)
    return output_path


def load_graph(path=None):
    if path is None:
        path = OUTPUT_FILE
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ==== A-2 resolve_node — 自然语言 → 候选 node_id 精确匹配 ====

def resolve_node(graph, query):
    """AI 消费 graph 的入口函数（A-2 合同 v0.1）。

    纯精确匹配（v0.1，不做 embedding/RAG）：
      1. 文件名 stem 精确匹配
      2. title 子串匹配
      3. tag 精确匹配

    返回：[(node_id, title, match_reason), ...]（最多 10 条候选）
    """
    candidates = []
    query_lower = query.lower().strip()
    if not query_lower:
        return candidates

    for node in graph.get("nodes", []):
        nid = node["id"]
        title = node.get("title", "")
        path = node.get("path", "")

        # 文件名 stem 匹配（精确 + 前缀）
        stem = os.path.splitext(os.path.basename(path))[0].lower()
        if query_lower == stem or stem.startswith(query_lower + "-"):
            candidates.append((nid, title, "stem_exact"))
            continue

        # title 子串匹配（不区分大小写）
        if query_lower in title.lower():
            candidates.append((nid, title, "title_substring"))
            continue

        # tag 精确匹配
        tags = node.get("tags", [])
        if isinstance(tags, list):
            for t in tags:
                if isinstance(t, str) and t.lower() == query_lower:
                    candidates.append((nid, title, f"tag_exact:{t}"))
                    break

    # 按匹配质量排序：stem_exact > tag_exact > title_substring
    priority = {"stem_exact": 0, "tag_exact": 1, "title_substring": 2}
    candidates.sort(key=lambda x: priority.get(x[2], 99))

    return candidates[:10]


# ==== DOT 导出 ====

def export_dot(graph):
    lines = ['digraph PAIOS_Relationship_Graph {']
    lines.append('  rankdir=LR;')
    lines.append('  node [shape=box, style=rounded];')
    lines.append('')
    for n in graph["nodes"]:
        label = n["id"]
        color = "lightyellow" if n["type"] == "adr" else "lightblue"
        lines.append(f'  "{n["id"]}" [label="{label}", fillcolor="{color}", style="rounded,filled"];')
    lines.append('')
    for e in graph["edges_declared"]:
        if "__UNRESOLVED__" in e["target"]:
            continue
        lines.append(f'  "{e["source"]}" -> "{e["target"]}" [style=solid, color=blue];')
    for e in graph["edges_backlinks"]:
        lines.append(f'  "{e["source"]}" -> "{e["target"]}" [style=dashed, color=green, label="backlink"];')
    for e in graph["edges_supersedes"]:
        lines.append(f'  "{e["source"]}" -> "{e["target"]}" [style=bold, color=red, label="supersedes"];')
    lines.append('}')
    return "\n".join(lines)


# ==== CLI 查询 ====

def format_node_id(nid, graph):
    for n in graph["nodes"]:
        if n["id"] == nid:
            return f"{nid} ({n['title']})"
    return nid


def cmd_build(args):
    scanner = Scanner()
    nr = NodeResolver()
    tr = TargetResolver(nr)
    builder = GraphBuilder(scanner, nr, tr)
    graph = builder.build()
    out_path = write_graph(graph)
    stats = graph["stats"]
    print(f"[OK] Relationship graph built successfully")
    print(f"     Output: {out_path}")
    print(f"     Nodes: {stats['nodes']} | Declared edges: {stats['declared_edges']} | "
          f"Backlinks: {stats['backlinks']} | Supersedes: {stats['supersedes']}")
    print(f"     Unresolved: {stats['unresolved']} | Orphans: {stats['orphans']}")
    return 0


def cmd_backlinks(args):
    graph = load_graph()
    if graph is None:
        print("No graph found. Run 'build' first.", file=sys.stderr)
        return 1
    node_id = args.get("node_id", args.get("positional", [None])[0])
    if not node_id:
        print("Usage: relationship_engine.py backlinks <node_id>", file=sys.stderr)
        return 1
    node_ids = {n["id"] for n in graph["nodes"]}
    if node_id not in node_ids:
        print(f"Node '{node_id}' not found in graph.", file=sys.stderr)
        return 1
    backlinks = [e for e in graph["edges_backlinks"] if e["target"] == node_id]
    forward_to = [e for e in graph["edges_declared"] if e["target"] == node_id and e["resolved"]]
    if not backlinks and not forward_to:
        print(f"No backlinks found for {format_node_id(node_id, graph)}")
        return 0
    print(f"[IN] Backlinks to {format_node_id(node_id, graph)}:")
    for bl in backlinks:
        print(f"  <- {format_node_id(bl['source'], graph)}  (backlink)")
    if forward_to:
        print(f"[OUT] Nodes that reference {format_node_id(node_id, graph)}:")
        for e in forward_to:
            print(f"  <- {format_node_id(e['source'], graph)}  (via declared: {e['raw']})")
    return 0


def cmd_forward(args):
    graph = load_graph()
    if graph is None:
        print("No graph found. Run 'build' first.", file=sys.stderr)
        return 1
    node_id = args.get("node_id", args.get("positional", [None])[0])
    if not node_id:
        print("Usage: relationship_engine.py forward <node_id>", file=sys.stderr)
        return 1
    node_ids = {n["id"] for n in graph["nodes"]}
    if node_id not in node_ids:
        print(f"Node '{node_id}' not found in graph.", file=sys.stderr)
        return 1
    declared = [e for e in graph["edges_declared"] if e["source"] == node_id]
    backlinks = [e for e in graph["edges_backlinks"] if e["source"] == node_id]
    supersedes_edges = [e for e in graph["edges_supersedes"] if e["source"] == node_id]
    if not declared and not supersedes_edges:
        print(f"No forward references from {format_node_id(node_id, graph)}")
        return 0
    print(f"[OUT] Forward references from {format_node_id(node_id, graph)}:")
    for e in declared:
        status = "OK" if e["resolved"] else "XX"
        target_name = format_node_id(e["target"], graph) if e["resolved"] else e["raw"]
        print(f"  -> {target_name}  (declared, {status})")
    for e in supersedes_edges:
        print(f"  -> {format_node_id(e['target'], graph)}  (supersedes)")
    for e in backlinks:
        print(f"  -> {format_node_id(e['target'], graph)}  (backlink)")
    return 0


def cmd_orphans(args):
    graph = load_graph()
    if graph is None:
        print("No graph found. Run 'build' first.", file=sys.stderr)
        return 1
    orphans = graph.get("orphans", [])
    if not orphans:
        print("[OK] No orphan nodes found -- all nodes have at least one edge.")
        return 0
    print(f"[ISLAND] Orphan nodes ({len(orphans)}):")
    for oid in orphans:
        print(f"  {format_node_id(oid, graph)}")
    return 0


def cmd_unresolved(args):
    graph = load_graph()
    if graph is None:
        print("No graph found. Run 'build' first.", file=sys.stderr)
        return 1
    unresolved = graph.get("unresolved", [])
    if not unresolved:
        print("[OK] No unresolved references.")
        return 0
    print(f"[WARN] Unresolved references ({len(unresolved)}):")
    for u in unresolved:
        print(f"  [{u['from']}] -> {u['raw_target']}  ({u['reason']})")
    return 0


def cmd_graph(args):
    graph = load_graph()
    if graph is None:
        print("No graph found. Run 'build' first.", file=sys.stderr)
        return 1
    fmt = args.get("format", "dot")
    if fmt == "dot":
        print(export_dot(graph))
    else:
        print(f"Unknown format: {fmt}. Supported: dot", file=sys.stderr)
        return 1
    return 0


def cmd_stats(args):
    graph = load_graph()
    if graph is None:
        print("No graph found. Run 'build' first.", file=sys.stderr)
        return 1
    stats = graph["stats"]
    use_json = args.get("json", False)
    if use_json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    else:
        print(f"[STATS] PAIOS Relationship Graph Stats")
        print(f"   {'Nodes':.<30} {stats['nodes']}")
        print(f"   {'Declared edges':.<30} {stats['declared_edges']}")
        print(f"   {'Backlinks':.<30} {stats['backlinks']}")
        print(f"   {'Supersedes':.<30} {stats['supersedes']}")
        print(f"   {'Unresolved':.<30} {stats['unresolved']}")
        print(f"   {'Orphans':.<30} {stats['orphans']}")
    return 0


# ==== 参数解析（轻量级） ====

def parse_args(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        return None
    cmd = argv[0]
    rest = argv[1:]
    args = {"command": cmd, "positional": [], "format": "dot", "json": False}
    i = 0
    while i < len(rest):
        arg = rest[i]
        if arg == "--format" and i + 1 < len(rest):
            args["format"] = rest[i + 1]
            i += 2
        elif arg == "--json":
            args["json"] = True
            i += 1
        elif arg.startswith("--"):
            i += 1
        else:
            args["positional"].append(arg)
            i += 1
    if cmd == "backlinks" and args["positional"]:
        args["node_id"] = args["positional"][0]
    elif cmd == "forward" and args["positional"]:
        args["node_id"] = args["positional"][0]
    return args


def print_usage():
    print(__doc__)


def main():
    args = parse_args()
    if args is None:
        print_usage()
        return 0
    cmd = args["command"]
    commands = {
        "build": cmd_build,
        "backlinks": cmd_backlinks,
        "forward": cmd_forward,
        "orphans": cmd_orphans,
        "unresolved": cmd_unresolved,
        "graph": cmd_graph,
        "stats": cmd_stats,
    }
    if cmd not in commands:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print_usage()
        return 1
    return commands[cmd](args)


if __name__ == "__main__":
    sys.exit(main())
