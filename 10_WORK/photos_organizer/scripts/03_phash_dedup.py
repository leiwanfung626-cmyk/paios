# 03_phash_dedup.py — 感知去重（pHash/dHash 汉明距离）
# 不自动删除，仅标记 duplicate_group 供人工确认
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import hamming_similarity
from PIL import Image
import imagehash


def compute_phash(path):
    try:
        with Image.open(path) as img:
            return str(imagehash.phash(img))
    except Exception:
        return None


def compute_dhash(path):
    try:
        with Image.open(path) as img:
            return str(imagehash.dhash(img))
    except Exception:
        return None


def find_perceptual_duplicate(conn, phash_val, media_type, threshold):
    """在 DB 中查找感知相似文件。
    用 phash 前 6 字符分桶加速（汉明距离≥threshold 必在同一桶）。
    返回 (duplicate_id, similarity%) 或 (None, 0.0)"""
    if not phash_val:
        return None, 0.0
    prefix = phash_val[:6]
    rows = conn.execute(
        "SELECT id, phash FROM photos WHERE media_type=? AND phash LIKE ? AND phash IS NOT NULL",
        (media_type, prefix + "%"),
    ).fetchall()
    best_id, best_sim = None, 0.0
    for r in rows:
        sim = hamming_similarity(phash_val, r["phash"])
        if sim >= threshold and sim > best_sim:
            best_sim, best_id = sim, r["id"]
    return best_id, best_sim


if __name__ == "__main__":
    import argparse
    from utils import load_config

    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    args = ap.parse_args()
    cfg = load_config()
    conn = get_db(cfg["paths"]["db"])
    ph = compute_phash(args.path)
    dh = compute_dhash(args.path)
    print(f"pHash: {ph}\ndHash: {dh}")
    dup_id, sim = find_perceptual_duplicate(
        conn, ph, "photo", cfg["dedup"]["phash_threshold"]
    )
    print(f"Perceptual duplicate id: {dup_id}, similarity: {sim}%")
    conn.close()
