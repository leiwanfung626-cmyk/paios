#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cluster.py — 人脸聚类 + 建 FAISS 检索索引 (Phase 1 收尾 + Phase 3 索引)
读取 face_index.db 中全部人脸 embedding，做：
  1) 归一化 -> 建 faiss IndexFlatIP (余弦)
  2) 连通分量聚类 (余弦阈值 thr)：相近人脸连边 -> 同簇
     —— 注：20 年年龄跨度会导致同一人分裂成多个簇，属预期；聚类仅作候选分组辅助
  3) 持久化：faiss_index.bin / face_ids.npy / norm_emb.npy + clusters 表
cluster_id 写回 faces 表，供检索与人工命名。

用法：
  python cluster.py                 # 默认 sim_thr=0.38
  python cluster.py --sim-thr 0.40  # 调紧/调松
"""
import argparse
import os
import sqlite3
import numpy as np
import faiss

HERE = os.path.dirname(os.path.abspath(__file__))
FACE_DB = os.path.join(HERE, "face_index.db")
EMB_DIM = 512


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim-thr", type=float, default=0.38, help="余弦相似度聚类阈值")
    ap.add_argument("--topk", type=int, default=20, help="每个脸检索的近邻数(建图用)")
    args = ap.parse_args()

    con = sqlite3.connect(FACE_DB)
    rows = con.execute("SELECT id, embedding FROM faces WHERE embedding IS NOT NULL").fetchall()
    if not rows:
        print("ERROR: faces 表无人脸。请先跑 face_extract.py。")
        return
    ids = [r[0] for r in rows]
    embs = np.stack([np.frombuffer(r[1], dtype=np.float32) for r in rows]).astype("float32")
    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    nembs = embs / norms
    N = len(ids)
    print(f"人脸总数={N}  聚类阈值={args.sim_thr}")

    index = faiss.IndexFlatIP(EMB_DIM)
    index.add(nembs)
    k = min(args.topk + 1, N)
    D, I = index.search(nembs, k)

    # 并查集
    parent = list(range(N))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i in range(N):
        for j in range(1, k):  # j=0 是自
            if D[i][j] >= args.sim_thr:
                union(i, I[i][j])

    buckets = {}
    for i in range(N):
        buckets.setdefault(find(i), []).append(i)
    clusters = sorted(buckets.values(), key=len, reverse=True)

    face_to_cluster = {}
    for cid, members in enumerate(clusters, start=1):
        for m in members:
            face_to_cluster[ids[m]] = cid

    con.execute("UPDATE faces SET cluster_id=NULL")
    con.executemany("UPDATE faces SET cluster_id=? WHERE id=?",
                    [(cid, fid) for fid, cid in face_to_cluster.items()])
    con.commit()

    sizes = [len(c) for c in clusters]
    print(f"簇数量={len(clusters)}  最大簇={sizes[0] if sizes else 0}  "
          f"Top10 大小={sizes[:10]}")

    # 持久化
    faiss.write_index(index, os.path.join(HERE, "faiss_index.bin"))
    np.save(os.path.join(HERE, "face_ids.npy"), np.array(ids, dtype=np.int64))
    np.save(os.path.join(HERE, "norm_emb.npy"), nembs)
    print("已保存 faiss_index.bin / face_ids.npy / norm_emb.npy")

    # clusters 摘要表
    con.execute("DROP TABLE IF EXISTS clusters")
    con.execute("CREATE TABLE clusters (id INTEGER PRIMARY KEY, size INTEGER, rep_face_id INTEGER)")
    for cid, members in enumerate(clusters, start=1):
        rep = max(members, key=lambda m: con.execute(
            "SELECT det_score FROM faces WHERE id=?", (ids[m],)).fetchone()[0])
        con.execute("INSERT INTO clusters (id, size, rep_face_id) VALUES (?,?,?)",
                    (cid, len(members), ids[rep]))
    con.commit()
    print("clusters 表已更新。")


if __name__ == "__main__":
    main()
