#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
PAIOS ASSETS 入库助手
=====================
把下载的原始素材（视频/音频/图片/转写稿）移动 + 改名 + 分类归档到
ASSETS/{种类}/{门类}/{年份}/，并登记到 ASSETS/_index.md。

设计原则（来自 Evan 2026-07-17 要求）：
- 原素材只进 ASSETS，绝不进知识库（20_KNOWLEDGE）
- 分类：种类(video/audio/image/text) - 门类(tech/reading/...) - 年份
- 命名：{YYYYMMDD}-{门类}-{来源}-{slug}.{ext}
- 索引是唯一权威，负责溯源 / 去重 / 防知识库膨胀

用法：
    # 登记一个下载的视频
    python asset_store.py --file 70_TMP/douyin_raw.mp4 \
        --category video --genre tech --source douyin \
        --slug xiaodai-personal-kb --url "https://v.douyin.com/xxx"

    # 登记对应转写稿，并回填视频行的「转写稿」列
    python asset_store.py --file 70_TMP/douyin_transcript.txt \
        --category text --genre tech --source douyin \
        --slug xiaodai-personal-kb --transcript-of AST-2026-0001

    # 标注加工状态（promoted 后回填对应知识模块）
    python asset_store.py --mark-promoted AST-2026-0001 \
        --module "20_KNOWLEDGE/Platform/Methods/xxx.md"
"""

import os
import re
import argparse
import shutil
from pathlib import Path
from datetime import datetime

CATEGORIES = {"video", "audio", "image", "text"}
GENRES = {"tech", "reading", "life", "health", "study", "drug", "growth", "work", "other"}
SOURCES = {"douyin", "bilibili", "youtube", "other"}

# _index.md 表格列（1-based）
COL = {
    "id": 1, "category": 2, "genre": 3, "year": 4, "source": 5,
    "url": 6, "path": 7, "transcript": 8, "status": 9, "module": 10,
}

ID_RE = re.compile(r"AST-(\d{4})-(\d{4})")


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


def next_asset_id(index: Path, year: str) -> str:
    if not index.exists():
        return f"AST-{year}-0001"
    max_n = 0
    for line in index.read_text(encoding="utf-8").splitlines():
        m = ID_RE.search(line)
        if m and m.group(1) == year:
            max_n = max(max_n, int(m.group(2)))
    return f"AST-{year}-{max_n + 1:04d}"


def index_has_path(index: Path, rel_path: str) -> bool:
    if not index.exists():
        return False
    return rel_path in index.read_text(encoding="utf-8")


def read_rows(index: Path) -> list:
    if not index.exists():
        return []
    return [ln for ln in index.read_text(encoding="utf-8").splitlines()
            if ln.strip().startswith("|") and "资产ID" not in ln and "---" not in ln]


def write_index_header(index: Path):
    header = (
        "# ASSETS 资产索引\n\n"
        "> 原素材绝不进入知识库。本索引是唯一权威（溯源/去重/防膨胀）。\n\n"
        "## 索引表\n\n"
        "| 资产ID | 种类 | 门类 | 年份 | 来源 | 原链接 | 资产路径 | 转写稿 | 处理状态 | 对应知识模块 |\n"
        "|--------|------|------|------|------|--------|----------|--------|----------|--------------|\n"
    )
    index.write_text(header, encoding="utf-8")


def append_row(index: Path, row: dict):
    if not index.exists():
        write_index_header(index)
    cells = [
        row["id"], row["category"], row["genre"], row["year"], row["source"],
        row.get("url", ""), row["path"], row.get("transcript", ""),
        row.get("status", "raw"), row.get("module", ""),
    ]
    line = "| " + " | ".join(cells) + " |"
    with index.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def update_cell(index: Path, asset_id: str, col: str, value: str):
    """在索引表中找到 asset_id 所在行，改写某列（幂等）。"""
    if not index.exists():
        return False
    lines = index.read_text(encoding="utf-8").splitlines()
    idx = COL[col]
    changed = False
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|") and asset_id in ln:
            parts = [p.strip() for p in ln.strip().strip("|").split("|")]
            while len(parts) < 10:
                parts.append("")
            parts[idx - 1] = value
            lines[i] = "| " + " | ".join(parts) + " |"
            changed = True
            break
    if changed:
        index.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changed


def register(args):
    root = detect_root()
    assets = root / "ASSETS"
    index = assets / "_index.md"

    category = args.category.lower()
    genre = args.genre.lower()
    source = args.source.lower()
    if category not in CATEGORIES:
        raise SystemExit(f"[错误] 未知种类: {category}，可选 {sorted(CATEGORIES)}")
    if genre not in GENRES:
        raise SystemExit(f"[错误] 未知门类: {genre}，可选 {sorted(GENRES)}")
    if source not in SOURCES:
        raise SystemExit(f"[错误] 未知来源: {source}，可选 {sorted(SOURCES)}")

    src = Path(args.file)
    if not src.exists():
        raise SystemExit(f"[错误] 文件不存在: {src}")

    year = args.year or str(datetime.now().year)
    date = datetime.now().strftime("%Y%m%d")
    ext = src.suffix
    new_name = f"{date}-{genre}-{source}-{args.slug}{ext}"

    dest_dir = assets / category / genre / year
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / new_name
    if dest.exists():
        raise SystemExit(f"[跳过] 目标已存在: {dest}")

    rel_path = f"{category}/{genre}/{year}/{new_name}"
    if index_has_path(index, rel_path):
        raise SystemExit(f"[跳过] 索引已登记: {rel_path}")

    shutil.move(str(src), str(dest))
    asset_id = next_asset_id(index, year)

    row = {
        "id": asset_id, "category": category, "genre": genre,
        "year": year, "source": source, "url": args.url or "",
        "path": rel_path, "status": "raw",
    }
    append_row(index, row)
    print(f"[登记] {asset_id} -> {rel_path}")

    # 若这是转写稿且指定了所属视频，回填视频行的「转写稿」列
    if args.transcript_of:
        ok = update_cell(index, args.transcript_of, "transcript", rel_path)
        print(f"[{'OK' if ok else 'X'}] 回填 {args.transcript_of} 的转写稿列 -> {rel_path}")


def mark_promoted(args):
    root = detect_root()
    index = root / "ASSETS" / "_index.md"
    ok1 = update_cell(index, args.mark_promoted, "status", "promoted")
    ok2 = True
    if args.module:
        ok2 = update_cell(index, args.mark_promoted, "module", args.module)
    print(f"[标记] {args.mark_promoted} status=promoted module={args.module or '(未填)'} "
          f"({'OK' if ok1 and ok2 else 'X'})")


def main():
    ap = argparse.ArgumentParser(description="PAIOS ASSETS 入库助手")
    sub = ap.add_subparsers(dest="cmd")

    p_reg = sub.add_parser("add", help="登记一个素材")
    p_reg.add_argument("--file", required=True)
    p_reg.add_argument("--category", required=True)
    p_reg.add_argument("--genre", required=True)
    p_reg.add_argument("--source", required=True)
    p_reg.add_argument("--slug", required=True)
    p_reg.add_argument("--url", default="")
    p_reg.add_argument("--year", default="")
    p_reg.add_argument("--transcript-of", default="", help="关联的 video 资产ID")

    p_mk = sub.add_parser("promote", help="标记已加工并回填知识模块")
    p_mk.add_argument("--mark-promoted", required=True, help="资产ID")
    p_mk.add_argument("--module", default="", help="对应知识模块相对路径")

    args = ap.parse_args()
    if args.cmd == "add":
        register(args)
    elif args.cmd == "promote":
        mark_promoted(args)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
