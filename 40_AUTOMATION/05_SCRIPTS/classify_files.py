#!/usr/bin/env python3
r"""
QuarkSync 文件自动分类脚本

用法：
    python classify_files.py                          # 默认扫描 E:\QuarkSync\DATA
    python classify_files.py --dry-run                # 试运行，只显示不移动
    python classify_files.py --path D:\QuarkSync\DATA # 指定路径

规则（优先级从上到下，匹配多个规则时留根目录不动）：
  1. 媒体扩展名 -> 媒体素材/
  2. 含「个案」「案主」 -> 个案档案/
  3. 含「月报」「报告」「总结」「汇报」 -> 工作报告/
  4. 含「财务」「发票」「报销」「账单」 -> 财务资料/
  5. 以已知项目名开头 -> 项目档案/项目名/
  6. 超过 30 天未修改 -> 归档/
"""

import os
import re
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone


# -- 配置 -------------------------------------------------
DEFAULT_DATA_DIR = Path(os.environ.get("QUARK_DATA_DIR", "E:\\QuarkSync\\DATA"))
PROJECT_LIST_FILE = os.environ.get("QUARK_PROJECT_LIST", "") or (
    DEFAULT_DATA_DIR.parent / "PROJECT_LIST.md"
)

# -- 分类规则 -----------------------------------------------

MEDIA_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
    ".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv",
    ".mp3", ".wav", ".flac", ".wma",
}

KEYWORD_RULES = [
    (["个案", "案主"],             "个案档案"),
    (["月报", "报告", "总结", "汇报"], "工作报告"),
    (["财务", "发票", "报销", "账单"], "财务资料"),
]

ARCHIVE_DAYS = 30


def load_project_list(project_file: Path) -> dict:
    """从 PROJECT_LIST.md 加载项目名列表"""
    projects = {}
    if not project_file.exists():
        print(f"  [提示] 项目清单文件不存在: {project_file}")
        print(f"  [提示] 请创建该文件并填入项目名，或忽略项目分类。")
        return projects

    content = project_file.read_text(encoding="utf-8")
    for line in content.splitlines():
        line = line.strip()
        m = re.match(r"^-\s+(.+?)$", line)
        if m:
            name = m.group(1).strip()
            projects[name] = name
            continue
        m = re.match(r"^([^\s#:]+):", line)
        if m:
            name = m.group(1).strip()
            if name and not name.startswith("#"):
                projects[name] = name

    return projects


def get_classification(file_path: Path, projects: dict) -> tuple:
    """
    Returns (target_folder or None, reason or None)
    If multiple rules match, returns (None, "冲突: ...")
    """
    name = file_path.name
    ext = file_path.suffix.lower()
    matched = []  # [(folder, reason), ...]

    # 1. Media extension
    if ext in MEDIA_EXTENSIONS:
        matched.append(("媒体素材", f"扩展名 {ext}"))

    # 2-4. Keyword rules
    for keywords, folder in KEYWORD_RULES:
        for kw in keywords:
            if kw in name:
                matched.append((folder, f"含关键词 [{kw}]"))
                break

    # 5. Project name prefix
    for proj_name in projects:
        if name.startswith(proj_name):
            target = f"项目档案/{proj_name}"
            matched.append((target, f"以项目名 [{proj_name}] 开头"))
            break

    # 6. Older than 30 days
    if file_path.stat().st_mtime < time.time() - ARCHIVE_DAYS * 86400:
        matched.append(("归档", f"超过 {ARCHIVE_DAYS} 天未修改"))

    # -- Result --
    if len(matched) == 0:
        return (None, None)
    elif len(matched) == 1:
        return matched[0]
    else:
        reasons = "; ".join(r for _, r in matched)
        return (None, f"冲突: 同时匹配 {len(matched)} 条规则 ({reasons})")


def classify(data_dir: Path, project_list_path: Path = None, dry_run: bool = False):
    """Scan root directory files and classify"""
    if not data_dir.exists():
        print(f"[错误] 目录不存在: {data_dir}")
        return

    if project_list_path is None:
        project_list_path = PROJECT_LIST_FILE
    projects = load_project_list(project_list_path)
    print(f"[扫描目录] {data_dir}")
    print(f"[已加载项目] {len(projects)} 个")
    if projects:
        for p in projects:
            print(f"  - {p}")
    print()

    # Only process files in root (not recursive)
    files = [f for f in data_dir.iterdir() if f.is_file()]
    if not files:
        print("[完成] 根目录下没有需要分类的文件。")
        return

    stats = {"moved": 0, "conflict": 0, "skipped": 0}
    moves = {}  # folder_name -> [files]

    for f in sorted(files):
        folder, reason = get_classification(f, projects)
        if folder is None:
            if reason and "冲突" in reason:
                print(f"  [跳过-冲突] {f.name}")
                print(f"       {reason}")
                stats["conflict"] += 1
            else:
                print(f"  [跳过-无匹配] {f.name}")
                stats["skipped"] += 1
            continue

        target_dir = data_dir / folder
        target_path = target_dir / f.name
        moves.setdefault(folder, []).append(f)

        if not dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
            f.rename(target_path)

        stats["moved"] += 1

    # Summary
    print()
    print("=" * 50)
    print("[分类结果]:")
    for folder, folder_files in sorted(moves.items()):
        print(f"   [{folder}] ({len(folder_files)} 个)")
        for ff in folder_files:
            print(f"      | {ff.name}")
    print()
    print(f"   [+] 已移动: {stats['moved']} 个")
    print(f"   [!] 冲突: {stats['conflict']} 个")
    print(f"   [-] 无匹配: {stats['skipped']} 个")
    if dry_run:
        print("   [试运行] 未实际移动文件")


def main():
    parser = argparse.ArgumentParser(description="QuarkSync 文件自动分类")
    parser.add_argument(
        "--path",
        default=str(DEFAULT_DATA_DIR),
        help=f"DATA 目录路径 (默认: {DEFAULT_DATA_DIR})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="试运行模式，只显示不移动",
    )
    parser.add_argument(
        "--project-list",
        default=str(PROJECT_LIST_FILE),
        help=f"项目清单文件路径 (默认: {PROJECT_LIST_FILE})",
    )
    args = parser.parse_args()

    data_dir = Path(args.path)
    print("==============")
    print("  [QuarkSync 文件自动分类]")
    print("==============")
    if args.dry_run:
        print("  [试运行模式]")
        print()
    classify(data_dir, project_list_path=Path(args.project_list), dry_run=args.dry_run)


if __name__ == "__main__":
    main()
