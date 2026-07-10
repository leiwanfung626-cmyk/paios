#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_retrieval.py — 全量提取完成后的串联脚本 (Phase 2 一键出报告)
流程：cluster.py(建索引+聚类) -> retrieve.py --seeds 皓祥 -> retrieve.py --seeds 运丰
前置：face_extract.py 全量跑完，face_index.db 完整。
用法：python run_retrieval.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable  # 当前 venv 解释器

SEEDS = {
    "皓祥": r"E:\待整理照片\皓祥",
    "运丰": r"E:\待整理照片\运丰",
}


def run(cmd):
    print("\n>>> " + " ".join(cmd))
    rc = subprocess.run(cmd, cwd=HERE)
    if rc.returncode != 0:
        print(f"!!! 失败 (rc={rc.returncode}): {' '.join(cmd)}")
        sys.exit(rc.returncode)


def main():
    # 1) 建索引 + 聚类
    run([PY, "cluster.py", "--sim-thr", "0.38"])

    # 2) 对每个目标人物出检索报告
    for tag, folder in SEEDS.items():
        if not os.path.isdir(folder):
            print(f"!!! 种子文件夹不存在，跳过 {tag}: {folder}")
            continue
        run([PY, "retrieve.py", "--seeds", folder, "--tag", tag,
             "--topk", "400", "--sim-thr", "0.30"])

    print("\n=== 全部完成 ===")
    for tag in SEEDS:
        rep = os.path.join(HERE, "retrieval", tag, "report.html")
        print(f"  {tag}: file:///{rep}")


if __name__ == "__main__":
    main()
