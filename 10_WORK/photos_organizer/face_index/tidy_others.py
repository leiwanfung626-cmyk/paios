#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tidy_others.py — 把 <target>/others/ 中"年份可可靠解析"的照片移入对应年份文件夹。

仅采纳来源可靠的年份：exif / filename(显式日期) / wechat(微信时间戳)。
DB basename 兜底对短名易误匹配，不用于移动决策。
冲突安全：目标已存在同名文件则加 __n 后缀，内容相同则跳过。

用法：
  python tidy_others.py --target "E:\待整理照片\皓祥" [--dry]
"""
import argparse
import os
import shutil
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PHOTO_DB = os.path.join(ROOT, "database", "photo_index.db")

sys.path.insert(0, HERE)
from audit_person_folder import resolve_year


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--dry", action="store_true", help="仅预览不移动")
    args = ap.parse_args()
    TARGET = args.target
    OTHERS = os.path.join(TARGET, "others")
    if not os.path.isdir(OTHERS):
        print("无 others/ 目录，退出"); return
    pc = sqlite3.connect(PHOTO_DB)

    moved, skipped, stayed = [], [], []
    for bn in sorted(os.listdir(OTHERS)):
        fp = os.path.join(OTHERS, bn)
        if not os.path.isfile(fp):
            continue
        year, src = resolve_year(fp, pc)
        if year and src in ("exif", "filename", "wechat"):
            dest_dir = os.path.join(TARGET, year)
            os.makedirs(dest_dir, exist_ok=True)
            dest = os.path.join(dest_dir, bn)
            if os.path.exists(dest):
                if os.path.getsize(dest) == os.path.getsize(fp):
                    skipped.append((bn, year, "目标已存在(同内容)"))
                    continue
                base, ext = os.path.splitext(bn)
                c = 1
                while os.path.exists(dest):
                    c += 1
                    dest = os.path.join(dest_dir, f"{base}__{c}{ext}")
            if args.dry:
                moved.append((bn, year, "DRY"))
            else:
                shutil.move(fp, dest)
                moved.append((bn, year, "ok"))
        else:
            stayed.append((bn, year or "无", src or "无"))

    pc.close()
    print(f"== {'[DRY 预览]' if args.dry else '[执行]'} ==")
    print(f"移动 {len(moved)} 张：")
    for bn, yr, st in moved:
        print(f"  {bn:28} -> {yr}/  ({st})")
    print(f"跳过(同内容) {len(skipped)} 张：")
    for bn, yr, st in skipped:
        print(f"  {bn:28} -> {yr}/  ({st})")
    print(f"留 others/ {len(stayed)} 张(年份不可靠)：")
    for bn, yr, src in stayed:
        print(f"  {bn:28} 年份[{yr}] 来源[{src}]")
    # 清理空 others
    if not args.dry and not os.listdir(OTHERS):
        os.rmdir(OTHERS)
        print("others/ 已清空删除")


if __name__ == "__main__":
    main()
