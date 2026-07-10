#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""预热审查报告缩略图缓存 — 后台跑，生成全部 1075 张的 /thumb 缓存。"""
import sqlite3
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from serve_review import make_thumb  # 复用服务脚本的缩略图逻辑

DB_PATH = r"E:\PAIOS\10_WORK\photos_organizer\database\photo_index.db"


def get_paths():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    p1 = conn.execute(
        "SELECT path FROM photos WHERE source = '07_ToReview'").fetchall()
    p2 = conn.execute(
        "SELECT path FROM photos WHERE primary_category = '其他' "
        "AND source != '07_ToReview' ORDER BY confidence ASC LIMIT 200").fetchall()
    p3 = conn.execute(
        "SELECT path FROM photos WHERE confidence < 0.4 AND classifier = 'local_clip' "
        "AND source != '07_ToReview' AND primary_category != '其他' "
        "ORDER BY confidence ASC LIMIT 200").fetchall()
    conn.close()
    paths = [r['path'] for r in p1] + [r['path'] for r in p2] + [r['path'] for r in p3]
    return paths


def worker(path):
    try:
        make_thumb(path)
        return True
    except Exception as e:
        print(f"预热失败 {path}: {e}")
        return False


def main():
    paths = get_paths()
    total = len(paths)
    print(f"开始预热 {total} 张缩略图...")
    t0 = time.time()
    done = 0
    ok = 0
    with ThreadPoolExecutor(max_workers=3) as ex:
        for res in ex.map(worker, paths):
            done += 1
            if res:
                ok += 1
            if done % 100 == 0:
                print(f"  进度 {done}/{total}  用时 {time.time()-t0:.0f}s")
    print(f"预热完成: {ok}/{total} 成功, 失败 {total-ok}, 总用时 {time.time()-t0:.0f}s")


if __name__ == '__main__':
    main()
