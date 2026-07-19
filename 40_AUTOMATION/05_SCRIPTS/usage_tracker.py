#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
usage_tracker.py — PAIOS Memory Loop Usage Tracker v0.1

运行时知识使用行为记录管道。AI 使用知识后在此留下痕迹，形成
Runtime → Evidence → Improvement 的反馈闭环。

设计原则（PKT-EXE-20260719-002）：
  - 不自动 Hook AI Session（v0.1 仅手动 CLI 调用）
  - 不修改任何 20_KNOWLEDGE/30_SYSTEM 源文件
  - YAML 文件即存储（不建数据库）
  - trace 文件可删除重建（幂等）
  - 不依赖特定 AI 引擎（Tool Independence）

用法：
  python usage_tracker.py record \
    --session SESSION-001 \
    --task "考研规划" \
    --actor Buddy \
    --action retrieve \
    --assets "ADR-0017,adr" "定位共识v2.1,knowledge"

  python usage_tracker.py list [--date YYYY-MM-DD]

API：
  from usage_tracker import record_usage
  trace_id = record_usage(
      session_id="SESSION-001",
      task="考研规划",
      actor="Buddy",
      action="retrieve",
      assets=[("ADR-0017", "adr"), ("定位共识v2.1", "knowledge")],
  )
"""

import os
import re
import sys
import glob as glob_module
from datetime import datetime, timezone, timedelta

# ---------- 定位 PAIOS 根目录 ----------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAIOS_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if not os.path.isdir(os.path.join(PAIOS_ROOT, "20_KNOWLEDGE")):
    PAIOS_ROOT = os.environ.get("PAIOS_ROOT", PAIOS_ROOT)

USAGE_DIR = os.path.join(PAIOS_ROOT, "40_AUTOMATION", "10_TRACES", "usage")

VALID_ACTIONS = {"query", "retrieve", "reference", "generate", "validate"}

CST = timezone(timedelta(hours=8))


# ==== trace_id 生成 ====

def _generate_trace_id(date_str, date_dir):
    """生成 UT-YYYYMMDD-NNNN，跨 session 当日递增。"""
    existing = []
    if os.path.isdir(date_dir):
        for f in os.listdir(date_dir):
            m = re.match(r'^UT-(\d{8})-(\d{4})\.yaml$', f)
            if m and m.group(1) == date_str:
                existing.append(int(m.group(2)))
    next_seq = max(existing) + 1 if existing else 1
    return f"UT-{date_str}-{next_seq:04d}"


# ==== YAML 写入（纯字符串拼接，不依赖 PyYAML） ====

def _yaml_list(items):
    """生成 YAML 列表行。"""
    lines = []
    for item in items:
        lines.append(f"  - {item}")
    return "\n".join(lines)


def _write_trace(trace_id, record, date_dir):
    """写入单条 trace YAML 文件。"""
    os.makedirs(date_dir, exist_ok=True)
    path = os.path.join(date_dir, f"{trace_id}.yaml")

    lines = []
    lines.append(f"trace_id: {trace_id}")
    lines.append(f"created_time: {record['created_time']}")
    lines.append("")
    lines.append("session:")
    lines.append(f"  id: {record['session']['id']}")
    lines.append(f"  task: \"{record['session']['task']}\"")
    lines.append("")
    lines.append("actor:")
    lines.append(f"  type: {record['actor']['type']}")
    lines.append(f"  name: {record['actor']['name']}")
    lines.append("")
    lines.append("action:")
    lines.append(f"  type: {record['action']['type']}")
    lines.append("")

    lines.append("assets:")
    for a in record["assets"]:
        lines.append(f"  - id: {a['id']}")
        lines.append(f"    type: {a['type']}")

    if record.get("relationship"):
        lines.append("")
        lines.append("relationship:")
        rel = record["relationship"]
        if rel.get("query_type"):
            lines.append(f"  query_type: {rel['query_type']}")
        if rel.get("related_nodes"):
            lines.append("  related_nodes:")
            for node_id in rel["related_nodes"]:
                lines.append(f"    - {node_id}")

    lines.append("")
    lines.append("outcome:")
    outcome = record["outcome"]
    lines.append(f"  success: {_yaml_null(outcome['success'])}")

    content = "\n".join(lines) + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def _yaml_null(value):
    """YAML null 表示。"""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


# ==== record_usage API ====

def record_usage(
    session_id,
    task,
    actor,
    action,
    assets,
    outcome=None,
    relationship_query=None,
    related_nodes=None,
):
    """记录一次 AI 知识使用行为。

    参数：
        session_id (str): 父级 session ID（AI 会话标识），如 "SESSION-001"
        task (str): 用户任务描述，如 "考研复习规划"
        actor (str): AI 引擎名称，如 "Buddy" / "Reasonix" / "ChatGPT"
        action (str): 使用动作类型，query|retrieve|reference|generate|validate
        assets (list): [(asset_id, asset_type), ...]
                       asset_type ∈ {adr, knowledge, tool, system}
        outcome (bool|None): 本次使用的有效性，True=有效/False=问题/None=未知
        relationship_query (str|None): 关系查询类型（如 "backlinks"）
        related_nodes (list|None): 通过关系查询发现的相关节点 ID 列表

    返回：
        trace_id (str): 如 "UT-20260719-0001"

    不依赖外部模块，不 import relationship_engine。

    7 条红线：
        1. 不修改任何 Knowledge/System 源文件
        2. 不自动 Hook AI Session（仅手动调用）
        3. 不接入 Context Packet
        4. 不建数据库（YAML 文件即存储）
        5. 不写 < 1.0 的 confidence
        6. 不增加 failure_reason 或 reuse_value 字段
        7. 不依赖特定 AI 模型
    """
    # 输入校验
    if not session_id or not isinstance(session_id, str):
        raise ValueError("session_id is required (str)")
    if not task or not isinstance(task, str):
        raise ValueError("task is required (str)")
    if not actor or not isinstance(actor, str):
        raise ValueError("actor is required (str)")
    if action not in VALID_ACTIONS:
        raise ValueError(f"action must be one of {sorted(VALID_ACTIONS)}, got '{action}'")
    if not assets or not isinstance(assets, list):
        raise ValueError("assets is required (list of (id, type) tuples)")
    for a in assets:
        if not isinstance(a, (list, tuple)) or len(a) != 2:
            raise ValueError(f"each asset must be (id, type), got {a}")

    # 生成时间戳与 trace_id
    now = datetime.now(CST)
    date_str = now.strftime("%Y%m%d")
    created_time = now.strftime("%Y-%m-%dT%H:%M:%S%z")

    date_dir = os.path.join(USAGE_DIR, now.strftime("%Y-%m-%d"))
    trace_id = _generate_trace_id(date_str, date_dir)

    # 构建 record
    record = {
        "created_time": created_time,
        "session": {"id": session_id, "task": task},
        "actor": {"type": "agent", "name": actor},
        "action": {"type": action},
        "assets": [{"id": a[0], "type": a[1]} for a in assets],
        "outcome": {"success": outcome},
    }

    if relationship_query or related_nodes:
        rel = {}
        if relationship_query:
            rel["query_type"] = relationship_query
        if related_nodes:
            rel["related_nodes"] = related_nodes
        record["relationship"] = rel

    _write_trace(trace_id, record, date_dir)
    return trace_id


# ==== list_traces ====

def list_traces(date_str=None):
    """列出指定日期的 usage traces。

    参数：
        date_str (str|None): YYYY-MM-DD 格式，None=今天

    返回：
        [(trace_id, created_time, session_id, action_type), ...]
    """
    if date_str is None:
        date_str = datetime.now(CST).strftime("%Y-%m-%d")

    date_dir = os.path.join(USAGE_DIR, date_str)
    if not os.path.isdir(date_dir):
        return []

    results = []
    for f in sorted(os.listdir(date_dir)):
        if not f.endswith(".yaml"):
            continue
        path = os.path.join(date_dir, f)
        trace_id = f.replace(".yaml", "")
        # 简易解析 YAML 提取关键字段
        session_id = ""
        action_type = ""
        created_time = ""
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n\r")
                if line.startswith("created_time: "):
                    created_time = line.split(": ", 1)[1]
                elif line.strip() == "session:":
                    continue
                elif "id: " in line and not session_id:
                    # 粗略取第一个 id 字段（session 的 id）
                    m = re.search(r"^\s+id:\s+(.+)", line)
                    if m:
                        session_id = m.group(1)
                elif line.startswith("  type: ") and not action_type:
                    # action 的 type
                    m = re.search(r"^\s+type:\s+(.+)", line)
                    if m:
                        action_type = m.group(1)

        results.append((trace_id, created_time, session_id, action_type))
    return results


# ==== CLI ====

def cmd_record(args):
    """CLI: usage_tracker.py record ..."""
    session_id = args.get("session")
    task = args.get("task")
    actor = args.get("actor")
    action = args.get("action")
    raw_assets = args.get("assets", [])

    if not all([session_id, task, actor, action, raw_assets]):
        print("Usage: usage_tracker.py record --session <id> --task <task> --actor <name> "
              "--action <action> --assets \"id,type\" [...]")
        return 1

    # 解析 assets: ["id,type", ...]
    assets = []
    for raw in raw_assets:
        parts = raw.split(",")
        if len(parts) != 2:
            print(f"Error: asset must be 'id,type', got '{raw}'", file=sys.stderr)
            return 1
        assets.append((parts[0].strip(), parts[1].strip()))

    # 可选参数
    outcome_str = args.get("outcome")
    outcome = None
    if outcome_str is not None:
        if outcome_str.lower() in ("true", "1", "yes"):
            outcome = True
        elif outcome_str.lower() in ("false", "0", "no"):
            outcome = False

    rel_query = args.get("relationship_query")
    rel_nodes_str = args.get("related_nodes")
    related_nodes = None
    if rel_nodes_str:
        related_nodes = [n.strip() for n in rel_nodes_str.split(",") if n.strip()]

    try:
        trace_id = record_usage(
            session_id=session_id,
            task=task,
            actor=actor,
            action=action,
            assets=assets,
            outcome=outcome,
            relationship_query=rel_query,
            related_nodes=related_nodes,
        )
        print(f"[OK] Trace recorded: {trace_id}")
        print(f"     Path: {USAGE_DIR}/{datetime.now(CST).strftime('%Y-%m-%d')}/{trace_id}.yaml")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_list(args):
    """CLI: usage_tracker.py list [--date YYYY-MM-DD]"""
    date_str = args.get("date")
    traces = list_traces(date_str)

    target_date = date_str or datetime.now(CST).strftime("%Y-%m-%d")

    if not traces:
        print(f"No traces found for {target_date}.")
        return 0

    print(f"Traces for {target_date} ({len(traces)}):")
    for tid, ctime, sid, atype in traces:
        print(f"  {tid}  {ctime}  session={sid}  action={atype}")
    return 0


def parse_args(argv=None):
    """简易参数解析。"""
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        return None
    cmd = argv[0]
    rest = argv[1:]
    args = {"command": cmd, "assets": []}
    i = 0
    while i < len(rest):
        arg = rest[i]
        if arg.startswith("--"):
            key = arg[2:]
            if key == "assets":
                # 收集后续非 -- 开头的值直到下一个 --
                assets = []
                j = i + 1
                while j < len(rest) and not rest[j].startswith("--"):
                    assets.append(rest[j])
                    j += 1
                args["assets"] = assets
                i = j
            elif i + 1 < len(rest) and not rest[i + 1].startswith("--"):
                args[key] = rest[i + 1]
                i += 2
            else:
                # flag without value
                args[key] = True
                i += 1
        else:
            i += 1
    return args


def print_usage():
    print(__doc__)


def main():
    args = parse_args()
    if args is None:
        print_usage()
        return 0
    cmd = args["command"]
    if cmd == "record":
        return cmd_record(args)
    elif cmd == "list":
        return cmd_list(args)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print_usage()
        return 1


if __name__ == "__main__":
    sys.exit(main())
