#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
PAIOS Capture Pipeline — Stage 3 (Promotion / Routing)

扫描 00_CAPTURE/inbox 中已捕获的内容，依据 YAML 元数据 type/project
将"已治理"内容晋升到对应生命周期层：

    30_SYSTEM   <- governance / adr / decision / packet
    20_KNOWLEDGE<- architecture / research / tech / lessons
    10_WORK     <- project / doc
    90_ARCHIVE  <- 显式标记 archive 或超龄
    15_INBOX_PROCESSING/needs_review <- 无法判定 / 需人工确认
    15_INBOX_PROCESSING/failed       <- 无元数据 / 解析失败

重要：本脚本是 PAIOS 内唯一被允许向 20_KNOWLEDGE / 30_SYSTEM /
40_AUTOMATION 写入的通道。日常 AI 产出禁止直写这些层，必须先经
00_CAPTURE/inbox 捕获，再由本脚本晋升。

用法：
    classify_capture.py                 # 试运行，打印路由不移动
    classify_capture.py --apply         # 实际晋升
    classify_capture.py --source workbuddy   # 仅处理某来源
    classify_capture.py --root D:\PAIOS-PORTABLE\Core
"""

import os
import re
import argparse
from pathlib import Path
from datetime import datetime

# type -> (目标层根, 子目录)
ROUTE = {
    "governance":  ("30_SYSTEM", "governance"),
    "adr":         ("30_SYSTEM", "ADR"),
    "decision":    ("30_SYSTEM", "governance/decisions"),
    "packet":      ("30_SYSTEM", "packets"),
    "architecture":("20_KNOWLEDGE", "architecture"),
    "research":    ("20_KNOWLEDGE", "research"),
    "tech":        ("20_KNOWLEDGE", "tech"),
    "lessons":     ("20_KNOWLEDGE", "lessons"),
    "project":     ("10_WORK", ""),
    "doc":         ("10_WORK", ""),
    "image":       (None, None),   # 附件已在 attachments，跳过
    "other":       ("15_INBOX_PROCESSING", "needs_review"),
}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_metadata(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    block = m.group(1)
    meta = {}
    for line in block.splitlines():
        mm = re.match(r"^\s*(\w+):\s*(.*)$", line)
        if mm:
            k, v = mm.group(1), mm.group(2).strip()
            if v.startswith("[") and v.endswith("]"):
                v = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
            meta[k] = v
    return meta


def set_promoted(text: str, target_rel: str) -> str:
    # 更新 frontmatter: promoted: true, promoted_to: <rel>
    new_block = FRONTMATTER_RE.sub("", text)  # 去掉旧头
    lines = ["---", "metadata:"]
    # 重新构建：保留原 metadata 字段并覆写 promoted
    meta = parse_metadata(text) if not True else {}
    # 简单策略：重新生成 status/promoted 行，其余原样拼接
    m = FRONTMATTER_RE.match(text)
    body = text[m.end():] if m else text
    # 在 metadata 块内更新 promoted 字段
    block = m.group(1) if m else ""
    block_lines = block.splitlines()
    updated = []
    seen_promoted = False
    for ln in block_lines:
        if re.match(r"^\s*promoted:", ln):
            updated.append("  promoted: true")
            seen_promoted = True
        elif re.match(r"^\s*promoted_to:", ln):
            continue
        else:
            updated.append(ln)
    if not seen_promoted:
        updated.append("  promoted: true")
    updated.append(f"  promoted_to: {target_rel}")
    new_head = "---\n" + "\n".join(updated) + "\n---\n"
    return new_head + body


def detect_root() -> Path:
    env = os.environ.get("PAIOS_CORE")
    if env:
        p = Path(env)
        if (p / "00_CAPTURE").exists():
            return p
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "00_CAPTURE").exists():
            return parent
    return Path.cwd()


def classify(inbox: Path, root: Path, apply: bool, only_source=None):
    files = sorted(inbox.glob("*.md"))
    if not files:
        print("[完成] inbox 为空，无需晋升。")
        return

    log_lines = []
    stats = {"promoted": 0, "needs_review": 0, "failed": 0, "skipped": 0}

    for f in files:
        text = f.read_text(encoding="utf-8")
        meta = parse_metadata(text)
        if not meta:
            dest = root / "15_INBOX_PROCESSING" / "failed" / f.name
            if apply:
                dest.parent.mkdir(parents=True, exist_ok=True)
                f.rename(dest)
            print(f"  [failed] 无元数据: {f.name}")
            stats["failed"] += 1
            continue

        src = meta.get("source", "")
        if only_source and src != only_source:
            stats["skipped"] += 1
            continue

        typ = meta.get("type", "other")
        if meta.get("promoted") is True or str(meta.get("promoted", "")).lower() == "true":
            stats["skipped"] += 1
            continue

        if typ == "image":
            stats["skipped"] += 1
            continue

        layer, sub = ROUTE.get(typ, (None, None))
        if layer == "15_INBOX_PROCESSING":
            dest = root / "15_INBOX_PROCESSING" / "needs_review" / f.name
            if apply:
                dest.parent.mkdir(parents=True, exist_ok=True)
                f.rename(dest)
            print(f"  [needs_review] type={typ}: {f.name}")
            stats["needs_review"] += 1
            continue

        if layer is None:
            stats["skipped"] += 1
            continue

        dest_dir = root / layer
        if sub:
            dest_dir = dest_dir / sub
        dest_dir.mkdir(parents=True, exist_ok=True)
        target_rel = f"{layer}/{sub}/{f.name}" if sub else f"{layer}/{f.name}"
        dest = dest_dir / f.name

        if apply:
            new_text = set_promoted(text, target_rel)
            dest.write_text(new_text, encoding="utf-8")
            f.unlink()
            log_lines.append(f"- {datetime.now().strftime('%H:%M:%S')} {f.name} -> {target_rel}")
        print(f"  [promote] {typ} -> {target_rel}")

    if apply and log_lines:
        log_path = root / "15_INBOX_PROCESSING" / "classified" / "PROMOTE_LOG.md"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        header = f"\n## {datetime.now().strftime('%Y-%m-%d')}\n"
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(header + "\n".join(log_lines) + "\n")

    print()
    print("=" * 50)
    print(f"  [+] 晋升: {stats['promoted'] if apply else stats['promoted']}  "
          f"(promoted={stats['promoted']}, needs_review={stats['needs_review']}, "
          f"failed={stats['failed']}, skipped={stats['skipped']})")
    if not apply:
        print("  [试运行] 未实际移动。加 --apply 执行晋升。")


def main():
    ap = argparse.ArgumentParser(description="PAIOS Capture Pipeline - Stage 3 Promotion")
    ap.add_argument("--apply", action="store_true", help="实际晋升（默认试运行）")
    ap.add_argument("--source", default="")
    ap.add_argument("--root", default="")
    args = ap.parse_args()

    root = Path(args.root) if args.root else detect_root()
    inbox = root / "00_CAPTURE" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)

    print("==============")
    print("  [PAIOS Capture 晋升分类器]")
    print(f"  [inbox] {inbox}")
    print("==============\n")
    classify(inbox, root, args.apply, only_source=args.source or None)


if __name__ == "__main__":
    main()
