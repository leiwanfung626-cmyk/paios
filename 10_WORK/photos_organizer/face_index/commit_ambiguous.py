#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
commit_ambiguous.py — 把重叠脸的双人指认回写进人物库
读 review_ambiguous.py 导出的 ambiguous_judgments.json：
  {"kind":"ambiguous_2way","persons":["皓祥","运丰"],
   "items":[{"face_id":12,"assign":"皓祥"}, ...]}
  assign: "皓祥"→person_id(皓祥)  "运丰"→person_id(运丰)  "neither"→person_id=-1
全部落 person_judgments 审计（judgment 记为 assign:<人名> 或 reject）。

用法：python commit_ambiguous.py
      （默认读 retrieval/ambiguous_judgments.json）
"""
import os
import sqlite3
import json
import datetime
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
FACE_DB = os.path.join(HERE, "face_index.db")
DEFAULT_JSON = os.path.join(HERE, "retrieval", "ambiguous_judgments.json")


def ensure_person(con, name):
    row = con.execute("SELECT id FROM persons WHERE name=?", (name,)).fetchone()
    if row:
        return row[0]
    cur = con.execute("INSERT INTO persons (name, created_at) VALUES (?, datetime('now'))",
                      (name,))
    return cur.lastrowid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="ambiguous_judgments.json 路径（默认 retrieval/ambiguous_judgments.json）")
    args = ap.parse_args()
    path = args.file or DEFAULT_JSON
    if not os.path.exists(path):
        print(f"ERROR: 找不到 {path}。请先在 review_ambiguous.html 审查并导出。")
        return
    d = json.load(open(path, encoding="utf-8"))
    con = sqlite3.connect(FACE_DB)
    con.execute("""CREATE TABLE IF NOT EXISTS person_judgments (
        id INTEGER PRIMARY KEY, face_id INTEGER, person_id INTEGER,
        judgment TEXT, reviewer TEXT, ts TEXT)""")
    pid = {name: ensure_person(con, name) for name in d.get("persons", ["皓祥", "运丰"])}
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    cnt = {"皓祥": 0, "运丰": 0, "neither": 0}
    for it in d.get("items", []):
        fid = it["face_id"]
        a = it.get("assign")
        if a in pid:
            con.execute("UPDATE faces SET person_id=? WHERE id=?", (pid[a], fid))
            con.execute("INSERT INTO person_judgments (face_id, person_id, judgment, reviewer, ts) "
                        "VALUES (?,?,?,?,?)", (fid, pid[a], f"assign:{a}", "Evan", ts))
            cnt[a] += 1
        elif a == "neither":
            con.execute("UPDATE faces SET person_id=-1 WHERE id=?", (fid,))
            con.execute("INSERT INTO person_judgments (face_id, person_id, judgment, reviewer, ts) "
                        "VALUES (?,?,?,?,?)", (fid, pid.get("皓祥"), "reject", "Evan", ts))
            cnt["neither"] += 1
    con.commit()
    for name, p in pid.items():
        n = con.execute("SELECT COUNT(*), COUNT(DISTINCT photo_id) FROM faces WHERE person_id=?",
                        (p,)).fetchone()
        print(f"  {name}: {n[0]} 人脸 / {n[1]} 照片")
    con.close()
    print(f"重叠脸回写完成：皓祥 +{cnt['皓祥']} ｜ 运丰 +{cnt['运丰']} ｜ 都不是 {cnt['neither']}")


if __name__ == "__main__":
    main()
