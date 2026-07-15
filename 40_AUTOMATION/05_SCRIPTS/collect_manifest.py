#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
collect_manifest.py — PAIOS Federated Instance Manifest (FIM) MVP

设计原则（ADR-0013）：
  - Observe, Don't Own：只读现有结构，零行为改变
  - 输出 manifest.yaml（仅状态，无正文）
  - 内容永不出本机；aggregator 主动拉取

用法：
  python collect_manifest.py            # 生成 PAIOS-Usage/manifest.yaml 并输出到 stdout
  python collect_manifest.py --print    # 仅输出到 stdout，不写文件
  python collect_manifest.py --add-evidence "OBJECT" "note"  # 增加自定义证据行

依赖：仅 Python 标准库（无 pyyaml / git 外部调用通过 subprocess）
"""

import os
import re
import sys
import json
import uuid
import subprocess
from datetime import datetime, timedelta

# ---------- 定位 PAIOS 根目录 ----------
# 脚本位于 <root>/40_AUTOMATION/05_SCRIPTS/collect_manifest.py
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAIOS_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if not os.path.isdir(os.path.join(PAIOS_ROOT, "20_KNOWLEDGE")):
    # 允许通过环境变量覆盖
    PAIOS_ROOT = os.environ.get("PAIOS_ROOT", PAIOS_ROOT)

USAGE_DIR = os.path.join(PAIOS_ROOT, "30_SYSTEM", "PAIOS-Usage")
ID_FILE = os.path.join(USAGE_DIR, "instance-id.txt")
PROFILE_FILE = os.path.join(USAGE_DIR, "profile.yaml")
MANIFEST_FILE = os.path.join(USAGE_DIR, "manifest.yaml")


def run_git(args):
    """运行 git 命令，失败返回空字符串。"""
    try:
        out = subprocess.run(
            ["git", "-C", PAIOS_ROOT] + args,
            capture_output=True, text=True, timeout=30
        )
        return out.stdout.strip()
    except Exception:
        return ""


def load_profile():
    """解析 PAIOS-Usage/profile.yaml（嵌套 + 列表感知）。

    返回结构：
        {"schema": "1",
         "instance": {"id": "case-01"},
         "profile": {"primary": "work", "secondary": ["office", ...]},
         "owner": {"alias": "user-a"},
         "privacy": {"manifest": "share"}}
    文件不存在或损坏时返回 None。
    """
    if not os.path.isfile(PROFILE_FILE):
        return None
    data = {"schema": None, "instance": {}, "profile": {},
            "owner": {}, "privacy": {}}
    section = None
    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.rstrip("\n")
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                indent = len(line) - len(line.lstrip(" "))
                if indent == 0:
                    if ":" in s:
                        k, v = s.split(":", 1)
                        k, v = k.strip(), v.strip()
                        if v == "":
                            section = k
                        else:
                            data[k] = v
                            section = None
                else:
                    if section in data and isinstance(data[section], dict):
                        if s.startswith("- "):
                            item = s[2:].strip()
                            target = data[section].get("secondary")
                            if isinstance(target, list):
                                target.append(item)
                        elif ":" in s:
                            k, v = s.split(":", 1)
                            k, v = k.strip(), v.strip()
                            if k == "secondary" and v == "":
                                data[section]["secondary"] = []
                            else:
                                data[section][k] = v
    except Exception:
        return None
    return data


def get_instance_id(profile):
    """instance.id 优先取自 profile.yaml（语义 ID，如 case-01）；
    否则生成并持久化 UUID 作为回退。"""
    if profile and profile.get("instance", {}).get("id"):
        return profile["instance"]["id"]
    os.makedirs(USAGE_DIR, exist_ok=True)
    if os.path.isfile(ID_FILE):
        with open(ID_FILE, "r", encoding="utf-8") as f:
            val = f.read().strip()
            if val:
                return val
    new_id = str(uuid.uuid4())
    with open(ID_FILE, "w", encoding="utf-8") as f:
        f.write(new_id)
    return new_id


def get_profile(profile):
    """从 profile 数据提取 {primary, secondary[]}；缺省回退。"""
    default = {"primary": "work", "secondary": ["knowledge"]}
    if not profile or not profile.get("profile"):
        return default
    p = profile["profile"]
    primary = p.get("primary", "work")
    secondary = p.get("secondary", ["knowledge"])
    if not isinstance(secondary, list):
        secondary = [secondary] if secondary else []
    return {"primary": primary, "secondary": secondary}


def get_version():
    """读 SYSTEM_VERSION.md 首行或 MANIFEST.json。"""
    sv = os.path.join(PAIOS_ROOT, "SYSTEM_VERSION.md")
    if os.path.isfile(sv):
        with open(sv, "r", encoding="utf-8") as f:
            first = f.readline().strip()
            m = re.search(r"v?[\d]+\.[\d]+\.[\d]+", first)
            if m:
                return "v" + m.group(0).lstrip("v")
    mj = os.path.join(PAIOS_ROOT, "MANIFEST.json")
    if os.path.isfile(mj):
        try:
            with open(mj, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "version" in data:
                return "v" + str(data["version"]).lstrip("v")
        except Exception:
            pass
    return "unknown"


def count_md(dir_path):
    """统计目录下 .md 文件数，排除 index / _template。"""
    if not os.path.isdir(dir_path):
        return 0
    n = 0
    for fn in os.listdir(dir_path):
        if fn.endswith(".md") and not fn.startswith("_") and "index" not in fn.lower():
            n += 1
    return n


def get_assets():
    """统计 20_KNOWLEDGE 各子类文档数。

    注意：Phase B 将平台知识迁入 20_KNOWLEDGE/Platform/（按类型子目录
    Concepts/Methods/SOP/Decisions/Models/References 组织），个人知识迁入
    20_KNOWLEDGE/Personal/。故资产统计基准为 Platform/。
    """
    kbase = os.path.join(PAIOS_ROOT, "20_KNOWLEDGE", "Platform")
    mapping = {
        "references": "References",
        "concepts": "Concepts",
        "decisions": "Decisions",
        "models": "Models",
        "methods": "Methods",
        "sops": "SOP",
    }
    assets = {}
    for key, sub in mapping.items():
        assets[key] = count_md(os.path.join(kbase, sub))
    # 项目数
    active = os.path.join(PAIOS_ROOT, "10_WORK", "Active")
    projects_n = 0
    if os.path.isdir(active):
        projects_n = len([d for d in os.listdir(active)
                          if os.path.isdir(os.path.join(active, d))])
    assets["projects"] = projects_n
    return assets


def get_features():
    """检测功能采用（capability），只读目录/标记，不读内容。"""
    def has_dir(name):
        return os.path.isdir(os.path.join(PAIOS_ROOT, name))

    feats = {
        "capture": has_dir("00_CAPTURE"),
        "knowledge": has_dir("20_KNOWLEDGE"),
        "automation": os.path.isdir(os.path.join(PAIOS_ROOT, "40_AUTOMATION", "05_SCRIPTS"))
                       and any(f.endswith(".py") for f in os.listdir(
                           os.path.join(PAIOS_ROOT, "40_AUTOMATION", "05_SCRIPTS"))),
        "git": os.path.isdir(os.path.join(PAIOS_ROOT, ".git")),
        "photo": os.path.isdir(os.path.join(PAIOS_ROOT, "Photo-OS"))
                 or os.path.isfile(os.path.join(PAIOS_ROOT, "PAIOS-Usage", "feature-photo")),
        "growth": os.path.isfile(os.path.join(
            PAIOS_ROOT, "20_KNOWLEDGE", "Platform", "Concepts", "Growth-OS-Life-Companion.md")),
        "review": os.path.isdir(os.path.join(PAIOS_ROOT, "40_AUDIT"))
                  and any(f.endswith(".md") for f in os.listdir(os.path.join(PAIOS_ROOT, "40_AUDIT"))),
    }
    return feats


def get_projects():
    """读 10_WORK/Active 下项目，生成 id（目录名转 slug）+ 状态。"""
    active = os.path.join(PAIOS_ROOT, "10_WORK", "Active")
    projects = []
    if not os.path.isdir(active):
        return projects
    for d in sorted(os.listdir(active)):
        full = os.path.join(active, d)
        if not os.path.isdir(full):
            continue
        pid = re.sub(r"[^A-Za-z0-9]", "-", d).upper()[:16]
        # 状态：存在 当前状态.md 且含"进行中/active"则 active，否则 archived
        status = "active"
        cs = os.path.join(full, "当前状态.md")
        if os.path.isfile(cs):
            try:
                with open(cs, "r", encoding="utf-8") as f:
                    txt = f.read().lower()
                if "归档" in txt or "archived" in txt or "完成" in txt:
                    status = "archived"
            except Exception:
                pass
        projects.append({"id": pid, "name": d, "status": status})
    return projects


def get_evidence():
    """解析 ADR-INDEX.md，evidence 绑定到具体对象（非计数）。"""
    idx = os.path.join(PAIOS_ROOT, "30_SYSTEM", "ADR", "ADR-INDEX.md")
    evidence = []
    if not os.path.isfile(idx):
        return evidence
    pat = re.compile(r"^\|\s*(ADR-[\d]+)\s*\|\s*([A-Za-z]+)\s*\|")
    with open(idx, "r", encoding="utf-8") as f:
        for line in f:
            m = pat.match(line)
            if m:
                adr, status = m.group(1), m.group(2)
                if adr == "ADR-9999":
                    continue
                level = "Accepted" if status in ("Accepted", "Active") else status
                evidence.append({"object": adr, "level": level})
    return evidence


def get_usage():
    """git 活跃度：总 commits、最近提交日、近 30 天活跃天数。"""
    commits = run_git(["rev-list", "--count", "HEAD"])
    total = int(commits) if commits.isdigit() else 0
    last = run_git(["log", "-1", "--format=%ad", "--date=short"])
    since = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    days_out = run_git(["log", "--since=" + since, "--format=%ad", "--date=short"])
    active_days = len(set(days_out.split("\n")) - {""}) if days_out else 0
    return {
        "last_active": last or "unknown",
        "active_days_30d": active_days,
        "git_commits_total": total,
    }


def build_manifest(extra_evidence=None):
    """组装 manifest 字典（可选 extra_evidence：{object, level, note}）。"""
    profile = load_profile()
    inst_id = get_instance_id(profile)
    prof = get_profile(profile)
    owner = profile.get("owner", {}).get("alias") if profile else None
    privacy = profile.get("privacy", {}).get("manifest") if profile else None
    m = {
        "manifest_version": 1,
        "instance": {
            "id": inst_id,
            "version": get_version(),
            "profile": prof,
            "owner": owner,
            "privacy": privacy,
        },
        "usage": get_usage(),
        "features": get_features(),
        "assets": get_assets(),
        "projects": get_projects(),
        "evidence": get_evidence(),
        "feedback": {"pain_points": []},
    }
    if extra_evidence:
        m["evidence"].append(extra_evidence)
    return m


def to_yaml(m):
    """极简 YAML 序列化（固定 schema，避免外部依赖）。"""
    lines = []
    lines.append("manifest_version: %d" % m["manifest_version"])
    lines.append("")
    lines.append("instance:")
    lines.append('  id: "%s"' % m["instance"]["id"])
    lines.append('  version: "%s"' % m["instance"]["version"])
    lines.append("  profile:")
    lines.append("    primary: %s" % m["instance"]["profile"].get("primary", "work"))
    sec = m["instance"]["profile"].get("secondary", [])
    if isinstance(sec, list) and sec:
        lines.append("    secondary:")
        for s in sec:
            lines.append("      - %s" % s)
    elif isinstance(sec, str):
        lines.append("    secondary: %s" % sec)
    else:
        lines.append("    secondary: []")
    if m["instance"].get("owner"):
        lines.append('  owner: "%s"' % m["instance"]["owner"])
    if m["instance"].get("privacy"):
        lines.append("  privacy: %s" % m["instance"]["privacy"])
    lines.append("")
    lines.append("usage:")
    for k, v in m["usage"].items():
        lines.append("  %s: %s" % (k, v))
    lines.append("")
    lines.append("features:")
    for k, v in m["features"].items():
        lines.append("  %s: %s" % (k, "true" if v else "false"))
    lines.append("")
    lines.append("assets:")
    for k, v in m["assets"].items():
        lines.append("  %s: %s" % (k, v))
    lines.append("")
    lines.append("projects:")
    if m["projects"]:
        for p in m["projects"]:
            lines.append("  - id: %s" % p["id"])
            lines.append("    name: %s" % p["name"])
            lines.append("    status: %s" % p["status"])
    else:
        lines.append("  []")
    lines.append("")
    lines.append("evidence:")
    if m["evidence"]:
        for e in m["evidence"]:
            lines.append("  - object: %s" % e["object"])
            lines.append("    level: %s" % e["level"])
            if e.get("note"):
                lines.append('    note: "%s"' % e["note"])
    else:
        lines.append("  []")
    lines.append("")
    lines.append("feedback:")
    lines.append("  pain_points: []")
    lines.append("")
    return "\n".join(lines)


def main():
    extra = None
    for i, a in enumerate(sys.argv):
        if a == "--add-evidence" and i + 2 < len(sys.argv):
            extra = {"object": sys.argv[i + 1], "level": "Validated",
                     "note": sys.argv[i + 2]}
    m = build_manifest(extra_evidence=extra)
    yaml_text = to_yaml(m)
    if "--print" not in sys.argv:
        os.makedirs(USAGE_DIR, exist_ok=True)
        with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
            f.write(yaml_text)
        print("# manifest written to: %s" % MANIFEST_FILE)
        print("# instance id: %s" % m["instance"]["id"])
        print("-" * 40)
    print(yaml_text)


if __name__ == "__main__":
    main()
