# 02_md5_dedup.py — 精确去重（MD5 完全匹配）
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import get_db


def check_md5_dup(conn, md5):
    """返回 (is_dup, original_path)。
    md5 为空返回 (False, None)。
    用于增量：MD5 已存在于 DB 即视为重复（之前批次已处理）。"""
    if not md5:
        return False, None
    row = conn.execute(
        "SELECT path FROM photos WHERE md5=? LIMIT 1", (md5,)
    ).fetchone()
    if row:
        return True, row["path"]
    return False, None


def find_batch_duplicate(md5_map, md5):
    """在当前批次内存中查找 MD5 重复（批次内去重）。
    md5_map: {md5: first_path}；返回 (is_dup, original_path)"""
    if not md5:
        return False, None
    if md5 in md5_map:
        return True, md5_map[md5]
    return False, None


if __name__ == "__main__":
    # 快速测试：给定路径算 md5 并查库
    import argparse
    from utils import compute_md5, load_config

    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    args = ap.parse_args()
    cfg = load_config()
    conn = get_db(cfg["paths"]["db"])
    m = compute_md5(args.path)
    dup, orig = check_md5_dup(conn, m)
    print(f"MD5: {m}")
    print(f"Duplicate: {dup}, Original: {orig}")
    conn.close()
