#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
paios_mcp_server.py — PAIOS MCP Server v0.1

把 PAIOS 知识库暴露为 MCP（Model Context Protocol）服务，
供其他 AI 实例（Claude Code、Cursor、WorkBuddy 等）查询。

用法：
  python paios_mcp_server.py
    → 启动 stdio 传输的 MCP Server（供 AI 工具调用）

  python paios_mcp_server.py --list-tools
    → 列出所有可用工具（不启动服务器）

依赖: pip install mcp
"""

import sys
import os
import json
import re

# ---------- 路径 ----------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAIOS_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
GRAPH_FILE = os.path.join(PAIOS_ROOT, "30_SYSTEM", "Registry", "relationship-graph.json")
KNOWLEDGE_DIR = os.path.join(PAIOS_ROOT, "20_KNOWLEDGE")
ADR_DIR = os.path.join(PAIOS_ROOT, "30_SYSTEM", "ADR")

# ---------- 复用 relationship_engine ----------
import relationship_engine as _re


# ============================================================
#  数据加载
# ============================================================

def _load_graph():
    """加载关系图 JSON（复用 relationship_engine）。"""
    return _re.load_graph(GRAPH_FILE)


def _read_md_file(rel_path):
    """读取知识模块内容。"""
    full = os.path.normpath(os.path.join(PAIOS_ROOT, rel_path))
    if not os.path.isfile(full):
        return None
    with open(full, "r", encoding="utf-8") as f:
        return f.read()


# ============================================================
#  MCP Server
# ============================================================

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool, TextContent,
        ListToolsResult, CallToolResult,
    )
    HAS_MCP = True
except ImportError:
    HAS_MCP = False


def _build_tool_list():
    """定义 MCP 工具清单。"""
    return [
        Tool(
            name="paios_search_knowledge",
            description="搜索 PAIOS 知识库。BM25 + Tag 联合检索，返回相关知识模块列表。",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词（中文/英文）",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回结果数（默认 10，最大 20）",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="paios_get_module",
            description="获取单个知识模块的完整内容（含 frontmatter）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "node_id": {
                        "type": "string",
                        "description": "知识模块 ID（如 REF-0010, KB-xxx, ADR-0017）",
                    },
                },
                "required": ["node_id"],
            },
        ),
        Tool(
            name="paios_get_relationships",
            description="查询知识模块的关系网络（谁引用了我 + 我引用了谁）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "node_id": {
                        "type": "string",
                        "description": "知识模块 ID",
                    },
                },
                "required": ["node_id"],
            },
        ),
        Tool(
            name="paios_list_modules",
            description="列出 PAIOS 知识库中所有模块，按类型分类。支持按类型过滤。",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_type": {
                        "type": "string",
                        "description": "可选过滤：adr / reference / concept / method / decision / sop / knowledge / all",
                        "default": "all",
                    },
                },
            },
        ),
        Tool(
            name="paios_get_stats",
            description="获取 PAIOS 知识库统计概览（节点数、关系数、分类统计）。",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


# ---------- 工具处理逻辑 ----------

def handle_search(graph, query, top_k=10):
    """paios_search_knowledge 处理。"""
    top_k = min(max(top_k, 1), 20)
    if not graph:
        return "错误：关系图未构建，请先运行 relationship_engine.py build"

    # 直接调用 relationship_engine 中的 BM25 搜索
    # 为避免 import 循环，内联搜索逻辑
    query_lower = query.lower().strip()
    if not query_lower:
        return "错误：查询不能为空"

    tokens = re.findall(r'[a-zA-Z0-9\u4e00-\u9fff]+', query_lower)
    if not tokens:
        return "错误：查询中没有可检索的内容"

    # 计算 BM25 评分
    import math
    from collections import Counter

    nodes = graph.get("nodes", [])
    N = len(nodes)
    if N == 0:
        return "知识库为空"

    # 构建倒排索引
    doc_lengths = []
    term_node_map = {}
    for node in nodes:
        text_parts = [
            node.get("title", ""),
            node.get("summary", ""),
            " ".join(node.get("tags", [])),
            " ".join(node.get("keywords", [])),
        ]
        text = " ".join(p for p in text_parts if p)
        node_tokens = re.findall(r'[a-zA-Z0-9\u4e00-\u9fff]+', text.lower())
        doc_lengths.append(len(node_tokens))
        tf_counter = Counter(node_tokens)
        for term, tf in tf_counter.items():
            term_node_map.setdefault(term, []).append((node["id"], tf))

    avgdl = sum(doc_lengths) / N if N > 0 else 0.0
    k1, b = 1.5, 0.75
    idf_map = {term: math.log((N - len(p) + 0.5) / (len(p) + 0.5) + 1.0)
               for term, p in term_node_map.items()}

    results = []
    for node in nodes:
        nid = node["id"]
        title = node.get("title", "")
        title_lower = title.lower()

        # BM25
        node_tf = {}
        for term, postings in term_node_map.items():
            for nid_i, tf in postings:
                if nid_i == nid:
                    node_tf[term] = tf
                    break
        doc_len = sum(node_tf.values())
        bm25 = sum(
            idf_map.get(t, 0) * (node_tf.get(t, 0) * (k1 + 1)) /
            (node_tf.get(t, 0) + k1 * (1 - b + b * doc_len / max(avgdl, 1)))
            for t in tokens
        )
        bm25_score = bm25

        # Tag 加分
        tag_score = 0.0
        tags = node.get("tags", [])
        if isinstance(tags, list):
            for t in tags:
                if isinstance(t, str) and query_lower in t.lower():
                    tag_score = max(tag_score, 0.3)

        # Title 匹配
        title_score = 0.2 if query_lower in title_lower else 0.0
        if title_lower.startswith(query_lower):
            title_score = 0.4

        total = bm25_score * 0.4 + tag_score + title_score
        if total > 0:
            results.append({
                "id": nid,
                "title": title,
                "type": node.get("type", ""),
                "score": round(total, 3),
                "path": node.get("path", ""),
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def handle_get_module(graph, node_id):
    """paios_get_module 处理。"""
    if not graph:
        return "错误：关系图未构建"
    node_id = node_id.strip()
    for node in graph.get("nodes", []):
        if node["id"] == node_id:
            path = node.get("path", "")
            content = _read_md_file(path)
            if content is None:
                return f"错误：文件不存在 ({path})"
            # 用 relationship_engine 的成熟 frontmatter 解析
            fm_dict = _re.extract_frontmatter(content)
            body = content
            if fm_dict:
                # 精确截取 body（frontmatter 之后的内容）
                fm_end = content.find('\n---', 3)
                if fm_end > 0:
                    body = content[fm_end + 4:].strip()
            return {
                "id": node_id,
                "title": node.get("title", ""),
                "type": node.get("type", ""),
                "path": path,
                "tags": node.get("tags", []),
                "summary": node.get("summary", ""),
                "body": body.strip()[:2000],  # 限制 body 长度
            }
    return f"错误：未找到模块 '{node_id}'"


def handle_relationships(graph, node_id):
    """paios_get_relationships 处理。"""
    if not graph:
        return "错误：关系图未构建"
    node_id = node_id.strip()
    node_ids = {n["id"] for n in graph.get("nodes", [])}
    if node_id not in node_ids:
        return f"错误：未找到节点 '{node_id}'"

    outbound = []
    inbound = []

    for e in graph.get("edges_declared", []):
        if e["source"] == node_id:
            outbound.append({
                "target": e["target"] if e["resolved"] else e["raw"],
                "type": "declared",
                "resolved": e["resolved"],
                "source_file": e.get("source_file", ""),
                "created_time": e.get("created_time", ""),
            })
        if e["target"] == node_id and e["resolved"]:
            inbound.append({
                "source": e["source"],
                "type": "backlink",
                "resolved": True,
                "source_file": e.get("source_file", ""),
            })

    for e in graph.get("edges_backlinks", []):
        if e["source"] == node_id:
            outbound.append({
                "target": e["target"],
                "type": "backlink",
                "resolved": True,
            })
        if e["target"] == node_id:
            inbound.append({
                "source": e["source"],
                "type": "declared",
                "resolved": True,
            })

    for e in graph.get("edges_supersedes", []):
        if e["source"] == node_id:
            outbound.append({
                "target": e["target"],
                "type": "supersedes",
                "resolved": True,
            })
        if e["target"] == node_id:
            inbound.append({
                "source": e["source"],
                "type": "superseded_by",
                "resolved": True,
            })

    return {
        "node_id": node_id,
        "outbound": outbound,
        "inbound": inbound,
    }


def handle_list_modules(graph, filter_type="all"):
    """paios_list_modules 处理。"""
    if not graph:
        return "错误：关系图未构建"
    nodes = graph.get("nodes", [])
    if filter_type != "all":
        nodes = [n for n in nodes if n.get("type") == filter_type]

    groups = {}
    for n in nodes:
        ntype = n.get("type", "unknown")
        groups.setdefault(ntype, []).append({
            "id": n["id"],
            "title": n.get("title", ""),
            "path": n.get("path", ""),
        })

    result = []
    for ntype in sorted(groups.keys()):
        items = groups[ntype]
        result.append({
            "type": ntype,
            "count": len(items),
            "modules": items,
        })

    return result


def handle_stats(graph):
    """paios_get_stats 处理。"""
    if not graph:
        return "错误：关系图未构建"
    stats = graph.get("stats", {})
    # 补充按类型统计
    type_counts = {}
    for n in graph.get("nodes", []):
        ntype = n.get("type", "unknown")
        type_counts[ntype] = type_counts.get(ntype, 0) + 1

    return {
        "total_nodes": stats.get("nodes", 0),
        "declared_edges": stats.get("declared_edges", 0),
        "backlinks": stats.get("backlinks", 0),
        "supersedes": stats.get("supersedes", 0),
        "unresolved_refs": stats.get("unresolved", 0),
        "orphan_nodes": stats.get("orphans", 0),
        "by_type": type_counts,
        "generated_at": stats.get("generated_at", ""),
    }


# ---------- Server 入口 ----------

async def serve():
    graph = _load_graph()

    server = Server("paios-mcp-server")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return _build_tool_list()

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        graph = _load_graph()  # 每次调用重新加载，支持热更新
        if name == "paios_search_knowledge":
            result = handle_search(graph, arguments["query"], arguments.get("top_k", 10))
        elif name == "paios_get_module":
            result = handle_get_module(graph, arguments["node_id"])
        elif name == "paios_get_relationships":
            result = handle_relationships(graph, arguments["node_id"])
        elif name == "paios_list_modules":
            result = handle_list_modules(graph, arguments.get("filter_type", "all"))
        elif name == "paios_get_stats":
            result = handle_stats(graph)
        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]

    async with stdio_server() as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())


# ============================================================
#  CLI 入口
# ============================================================

_USAGE = """PAIOS MCP Server — 知识库查询服务

用法（MCP 模式 - 供 WorkBuddy/Claude/Cursor 连接）:
  python paios_mcp_server.py
    → 启动 stdio MCP Server（等待 MCP 客户端连接）

用法（CLI 模式 - 供 Reasonix/Shell 直接调用）:
  python paios_mcp_server.py search <query> [--top-k N]
    → 搜索知识库（BM25 + Tag 联合检索）

  python paios_mcp_server.py get-module <node_id>
    → 获取知识模块内容

  python paios_mcp_server.py relationships <node_id>
    → 查询模块关系网络

  python paios_mcp_server.py list [<filter_type>]
    → 按类型列出模块

  python paios_mcp_server.py stats
    → 知识库统计概览

  python paios_mcp_server.py --list-tools
    → 列出 MCP 工具清单

示例:
  python paios_mcp_server.py search "OpenWRT 路由器"
  python paios_mcp_server.py get-module REF-0010
  python paios_mcp_server.py relationships REF-0008
  python paios_mcp_server.py list adr
"""


def _cli_search():
    """CLI: paios_mcp_server.py search <query> [--top-k N]"""
    graph = _load_graph()
    if not graph:
        print("错误：关系图未构建。请先运行 relationship_engine.py build", file=sys.stderr)
        return 1

    # 查找查询参数（跳过 search 子命令和可选标志）
    args = sys.argv[2:]
    query = None
    top_k = 10
    i = 0
    while i < len(args):
        if args[i] == "--top-k" and i + 1 < len(args):
            try:
                top_k = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        elif not args[i].startswith("--"):
            query = args[i]
            i += 1
        else:
            i += 1

    if not query:
        print("用法：python paios_mcp_server.py search <query> [--top-k N]", file=sys.stderr)
        return 1

    result = handle_search(graph, query, top_k)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _cli_get_module():
    """CLI: paios_mcp_server.py get-module <node_id>"""
    graph = _load_graph()
    if not graph:
        print("错误：关系图未构建", file=sys.stderr)
        return 1
    if len(sys.argv) < 3:
        print("用法：python paios_mcp_server.py get-module <node_id>", file=sys.stderr)
        return 1
    node_id = sys.argv[2]
    result = handle_get_module(graph, node_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _cli_relationships():
    """CLI: paios_mcp_server.py relationships <node_id>"""
    graph = _load_graph()
    if not graph:
        print("错误：关系图未构建", file=sys.stderr)
        return 1
    if len(sys.argv) < 3:
        print("用法：python paios_mcp_server.py relationships <node_id>", file=sys.stderr)
        return 1
    node_id = sys.argv[2]
    result = handle_relationships(graph, node_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _cli_list():
    """CLI: paios_mcp_server.py list [filter_type]"""
    graph = _load_graph()
    if not graph:
        print("错误：关系图未构建", file=sys.stderr)
        return 1
    filter_type = "all"
    if len(sys.argv) >= 3:
        filter_type = sys.argv[2]
    result = handle_list_modules(graph, filter_type)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _cli_stats():
    """CLI: paios_mcp_server.py stats"""
    graph = _load_graph()
    if not graph:
        print("错误：关系图未构建", file=sys.stderr)
        return 1
    result = handle_stats(graph)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main():
    # CLI 模式：强制 UTF-8 输出，避免 GBK 控制台 emoji 报错
    if len(sys.argv) >= 2 and sys.argv[1] not in ("",):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    if "--list-tools" in sys.argv:
        tools = _build_tool_list()
        for t in tools:
            print(f"\n{t.name}")
            print(f"  描述: {t.description}")
            print(f"  Schema: {json.dumps(t.inputSchema, ensure_ascii=False)}")
        return 0

    if len(sys.argv) >= 2:
        cmd = sys.argv[1]
        if cmd == "search":
            return _cli_search()
        elif cmd == "get-module":
            return _cli_get_module()
        elif cmd == "relationships":
            return _cli_relationships()
        elif cmd == "list":
            return _cli_list()
        elif cmd == "stats":
            return _cli_stats()
        elif cmd in ("-h", "--help"):
            print(_USAGE)
            return 0

    # 无参数 → MCP Server 模式
    if not HAS_MCP:
        print("错误：需要安装 mcp 包", file=sys.stderr)
        print(_USAGE, file=sys.stderr)
        return 1

    import asyncio
    asyncio.run(serve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
