#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_yunfeng_by_year.py — 把运丰照片复制/去重/按年份分类到 E:\待整理照片\运丰
流程(幂等, 原图不动):
  1. 从 face_index.db 取 运丰 person_id 对应的去重照片源路径 + 年份(photo_index.db.date)
  2. 复制 502 张 master 到 E:\待整理照片\运丰 (平铺)
     - 源已存在同内容 -> 跳过
     - 异内容同名 -> 加 __<hash8> 后缀
  3. 哈希去重: 目标内所有平铺文件(含原有28张种子)按内容去重, 每组留1, 其余移 _duplicates
  4. 按年份分类: 每文件移入 <base>/<year>/ ; 无年份 EXIF 兜底, 仍无则 _undated
用法:
  python export_yunfeng_by_year.py            # dry-run 预览
  python export_yunfeng_by_year.py --run      # 执行
"""
import os
import sys
import sqlite3
import shutil
import hashlib
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
FACE_DB = os.path.join(HERE, "face_index.db")
PHOTO_DB = os.path.join(HERE, "..", "database", "photo_index.db")
DEFAULT_TARGET = r"E:\待整理照片\运丰"
DEFAULT_PERSON = "运丰"


def file_hash(path, blk=1 << 20):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(blk), b""):
            h.update(c)
    return h.hexdigest()


def get_year_db(con, path):
    """photo_index.db 按 path 查 date"""
    r = con.execute("SELECT date FROM photos WHERE path=?", (path,)).fetchone()
    if r and r[0] and len(r[0]) >= 4:
        return r[0][:4]
    return None


def get_year_exif(path):
    """EXIF DateTimeOriginal / DateTime 兜底; 再退文件名中的年份"""
    # 文件名年份兜底 (如 IMG_20140802_xxx.jpg)
    import re
    m = re.search(r"(?:19|20)\d{2}", os.path.basename(path))
    fn_year = m.group(0) if m else None
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        im = Image.open(path)
        ex = im.getexif()
        for tid in (36867, 306):  # DateTimeOriginal, DateTime
            val = ex.get(tid)
            if val:
                return str(val)[:4]
        # IFD 递归
        for ifd in ex.get_ifds(im):
            d = ex.get_ifd(ifd)
            for k, v in d.items():
                if TAGS.get(k) in ("DateTimeOriginal", "DateTime") and v:
                    return str(v)[:4]
    except Exception:
        pass
    return fn_year


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--person", default=DEFAULT_PERSON, help="人物名(persons.name)")
    ap.add_argument("--target", default=None, help="目标目录(默认 E:\\待整理照片\\<person>)")
    ap.add_argument("--run", action="store_true", help="执行(不加则 dry-run)")
    args, _ = ap.parse_known_args()
    do_run = args.run
    PERSON = args.person
    TARGET = args.target or os.path.join(r"E:\待整理照片", PERSON)
    fc = sqlite3.connect(FACE_DB)
    pc = sqlite3.connect(PHOTO_DB)
    pid = fc.execute("SELECT id FROM persons WHERE name=?", (PERSON,)).fetchone()
    if not pid:
        print("ERROR: 找不到人物", PERSON); return
    pid = pid[0]
    rows = fc.execute(
        "SELECT DISTINCT f.path FROM faces f WHERE f.person_id=?", (pid,)).fetchall()
    sources = [r[0] for r in rows]

    # 取年份(来自 photo_index.db.date)
    year_map = {}      # src_path -> year
    nodate = []
    for p in sources:
        y = get_year_db(pc, p)
        if y:
            year_map[p] = y
        else:
            nodate.append(p)
    fc.close(); pc.close()

    print(f"== {'[DRY-RUN 预览]' if not do_run else '[执行]'}  人物={PERSON}")
    print(f"{PERSON}去重照片: {len(sources)} 张")
    print(f"  有日期: {len(year_map)}  无日期(需EXIF兜底): {len(nodate)}")
    yc = Counter(year_map.values())
    print(f"  年份分布: {dict(sorted(yc.items()))}")
    print(f"目标目录: {TARGET}")
    print(f"  当前已存在条目: {len(os.listdir(TARGET)) if os.path.isdir(TARGET) else '不存在(将建)'}")

    if not do_run:
        print("\n(预览完毕, 加 --run 执行真实复制/去重/分类)")
        return

    os.makedirs(TARGET, exist_ok=True)
    dup_dir = os.path.join(TARGET, "_duplicates")
    undated_dir = os.path.join(TARGET, "_undated")
    os.makedirs(dup_dir, exist_ok=True)

    # ---- 1. 复制 ----
    copied = 0
    skipped_same = 0
    renamed = 0
    missing = 0
    flat_files = []          # 平铺写入的目标文件绝对路径
    flat_year = {}           # 目标文件名 -> year (来自 year_map 或 EXIF/undated)
    for src in sources:
        if not os.path.exists(src):
            missing += 1
            continue
        y = year_map.get(src)
        base = os.path.basename(src)
        dst = os.path.join(TARGET, base)
        if os.path.exists(dst):
            if file_hash(src) == file_hash(dst):
                skipped_same += 1
                flat_files.append(dst)
                if y:
                    flat_year[base] = y
                continue
            else:
                stem, ext = os.path.splitext(base)
                dst = os.path.join(TARGET, f"{stem}__{file_hash(src)[:8]}{ext}")
                renamed += 1
        shutil.copy2(src, dst)
        copied += 1
        flat_files.append(dst)
        if y:
            flat_year[os.path.basename(dst)] = y

    # 原有28张种子(不在 sources 内) -> 补进 flat 列表, 年份稍后解析
    for fn in os.listdir(TARGET):
        fp = os.path.join(TARGET, fn)
        if os.path.isfile(fp) and fp not in flat_files:
            flat_files.append(fp)

    print(f"\n[复制] 复制 {copied}  同内容跳过 {skipped_same}  改名 {renamed}  源缺失 {missing}")
    print(f"  平铺文件总数(含原有种子): {len(flat_files)}")

    # ---- 2. 哈希去重 ----
    by_hash = defaultdict(list)
    for fp in flat_files:
        if os.path.isfile(fp):
            by_hash[file_hash(fp)].append(fp)
    moved_dup = 0
    removed_basenames = set()
    for h, group in by_hash.items():
        if len(group) > 1:
            keep = sorted(group)[0]
            for fp in group[1:]:
                shutil.move(fp, os.path.join(dup_dir, os.path.basename(fp)))
                moved_dup += 1
                removed_basenames.add(os.path.basename(fp))
    # 更新 flat 列表(去掉被移走的)
    flat_files = [fp for fp in flat_files
                  if os.path.isfile(fp) and os.path.dirname(fp) == TARGET]
    print(f"[去重] 移入 _duplicates: {moved_dup} 张 (剩余平铺 {len(flat_files)})")

    # ---- 3. 按年份分类 ----
    # 种子照存储路径≠master, year_map 查不到; 用 basename 反查 photo_index.db 兜底
    pc2 = sqlite3.connect(PHOTO_DB)
    per_year = Counter()
    undated = 0
    for fp in flat_files:
        bn = os.path.basename(fp)
        y = flat_year.get(bn)
        if not y:
            y = get_year_exif(fp)          # EXIF + 文件名年份
        if not y:
            r = pc2.execute("SELECT date FROM photos WHERE path LIKE ?",
                            (f"%{bn}",)).fetchone()
            if r and r[0] and len(r[0]) >= 4:
                y = r[0][:4]
        if y and y.isdigit():
            dest = os.path.join(TARGET, y)
            os.makedirs(dest, exist_ok=True)
            shutil.move(fp, os.path.join(dest, bn))
            per_year[y] += 1
        else:
            os.makedirs(undated_dir, exist_ok=True)
            shutil.move(fp, os.path.join(undated_dir, bn))
            undated += 1

    print("[分类] 年份分布:")
    for y, n in sorted(per_year.items()):
        print(f"  {y}: {n}")
    pc2.close()
    print(f"  无日期(_undated): {undated}")
    print(f"\n完成。目标目录: {TARGET}")
    print(f"  _duplicates(可删复核): {len(os.listdir(dup_dir))}")


if __name__ == "__main__":
    main()
