#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
PAIOS Capture Pipeline — Stage 1 (Capture) + Stage 2 (Metadata Extraction)

唯一入口助手：任何 AI 或人工产生的新内容，经由本脚本落入
    D:\PAIOS-PORTABLE\Core\00_CAPTURE\inbox
并自动生成 YAML 元数据头，供 Stage-3 晋升分类器消费。

命名规范：
    YYYYMMDD-HHMMSS-source-type-title.md
    例：20260716-163100-workbuddy-governance-capture-pipeline.md

用法：
    # 从文件捕获
    capture.py --title "Capture管道设计" --source workbuddy --type governance \
        --project paios-core --keywords 捕获,管道,治理 --body-file design.md

    # 从 stdin 捕获
    echo "正文..." | capture.py --title "xxx" --source chatgpt --type research --stdin

    # 仅附件（图片/文档），无正文
    capture.py --title "征兵照片" --source workbuddy --type image \
        --attach "D:/x/a.jpg" --attach "D:/x/b.jpg"

    # 捕获后直接进入待处理（跳过 needs_review）
    capture.py ... --auto

参数：
    --title        必填，简短标题（英文/拼音或中文均可，用于文件名）
    --source       来源：workbuddy|chatgpt|doubao|qianwen|yuanbao|human
    --type         类型：governance|adr|architecture|tech|research|doc|project|decision|packet|image|other
    --project      关联项目（可选）
    --keywords     逗号分隔关键词（可选）
    --related      关联文件/ID（可选，逗号分隔）
    --body-file    正文 markdown 文件路径（可选）
    --stdin        从标准输入读取正文（可选）
    --attach       附件路径，可多次（可选）
    --auto         捕获后直接置 status=processing（否则默认 captured，留待人工/定时晋升）
    --dry-run      只打印目标路径，不写文件
    --root         PAIOS Core 根目录（默认自动探测）
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

VALID_SOURCES = {"workbuddy", "chatgpt", "doubao", "qianwen", "yuanbao", "human", "other"}
VALID_TYPES = {"governance", "adr", "architecture", "tech", "research", "doc",
               "project", "decision", "packet", "image", "other"}


def detect_root() -> Path:
    # 优先环境变量，其次从本脚本位置向上找含 00_CAPTURE 的目录
    env = os.environ.get("PAIOS_CORE")
    if env:
        p = Path(env)
        if (p / "00_CAPTURE").exists():
            return p
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "00_CAPTURE").exists():
            return parent
    # fallback：当前工作目录
    return Path.cwd()


def slugify(text: str) -> str:
    # 文件名用：保留中文，替换空格和非法字符
    text = text.strip()
    for ch in ('\\', '/', ':', '*', '?', '"', '<', '>', '|'):
        text = text.replace(ch, '-')
    text = text.replace(' ', '-')
    return text[:60]


def build_metadata(args, now: datetime) -> str:
    def listify(s):
        if not s:
            return []
        return [x.strip() for x in s.split(',') if x.strip()]
    lines = ["---"]
    lines.append("metadata:")
    lines.append(f"  source: {args.source}")
    lines.append(f"  type: {args.type}")
    lines.append(f"  created: {now.strftime('%Y-%m-%dT%H:%M:%S')}")
    lines.append(f"  project: {args.project or ''}")
    lines.append(f"  keywords: {listify(args.keywords)}")
    lines.append(f"  related: {listify(args.related)}")
    lines.append(f"  status: {'processing' if args.auto else 'captured'}")
    lines.append(f"  promoted: false")
    lines.append("---")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="PAIOS Capture Pipeline - Stage 1+2")
    ap.add_argument("--title", required=True)
    ap.add_argument("--source", default="workbuddy")
    ap.add_argument("--type", default="other")
    ap.add_argument("--project", default="")
    ap.add_argument("--keywords", default="")
    ap.add_argument("--related", default="")
    ap.add_argument("--body-file", default="")
    ap.add_argument("--stdin", action="store_true")
    ap.add_argument("--attach", action="append", default=[])
    ap.add_argument("--auto", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--root", default="")
    args = ap.parse_args()

    if args.source not in VALID_SOURCES:
        print(f"[警告] source={args.source} 不在白名单，已归入 other")
        args.source = "other"
    if args.type not in VALID_TYPES:
        print(f"[警告] type={args.type} 不在白名单，已归入 other")
        args.type = "other"

    root = Path(args.root) if args.root else detect_root()
    inbox = root / "00_CAPTURE" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    stamp = now.strftime("%Y%m%d-%H%M%S")
    fname = f"{stamp}-{args.source}-{args.type}-{slugify(args.title)}.md"
    target = inbox / fname

    # 正文
    body = ""
    if args.body_file:
        bf = Path(args.body_file)
        if bf.exists():
            body = bf.read_text(encoding="utf-8")
    elif args.stdin:
        body = sys.stdin.read()

    # 附件：复制到 00_CAPTURE/attachments 并记录
    attached = []
    attach_dir = root / "00_CAPTURE" / "attachments"
    for att in args.attach:
        src = Path(att)
        if src.exists():
            attach_dir.mkdir(parents=True, exist_ok=True)
            dst = attach_dir / f"{stamp}-{src.name}"
            dst.write_bytes(src.read_bytes())
            attached.append(str(dst.relative_to(root)))
        else:
            print(f"[警告] 附件不存在: {att}")

    meta = build_metadata(args, now)
    content = meta + "\n\n"
    if args.title:
        content += f"# {args.title}\n\n"
    if attached:
        content += "## 附件\n\n"
        for a in attached:
            content += f"- {a}\n"
        content += "\n"
    if body:
        content += body + "\n"

    if args.dry_run:
        print(f"[dry-run] 目标: {target}")
        print("---- 预览 ----")
        print(content[:800])
        return

    target.write_text(content, encoding="utf-8")
    print(f"[已捕获] {target}")
    print(f"  source={args.source} type={args.type} status={'processing' if args.auto else 'captured'}")
    if attached:
        print(f"  附件: {len(attached)} 个 -> 00_CAPTURE/attachments/")


if __name__ == "__main__":
    main()
