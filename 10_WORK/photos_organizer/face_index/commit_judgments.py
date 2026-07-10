#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
commit_judgments.py — 把人工审查判断写回 PAIOS 人脸库 (Phase 2 回写)
人工在交互式 report.html 里点 ✓/✗/? 并导出 judgments.json，
本脚本将其持久化到 face_index.db：
  - 建/复用 persons 行（人物库）
  - 更新 faces.person_id（accept→人物id；reject→-1 排除；unsure→不动）
  - 写 person_judgments 审计表（谁/何时/判了谁）

输入：
  judgments.json 结构：
    {"person":"皓祥","source":"face_retrieval","exported_at":"...",
     "items":[{"face_id":12,"photo_id":99,"sim":0.82,"judgment":"accept"}, ...]}
  或 手动编辑的 results.csv（末列 judgment 填 accept/reject/unsure）

用法：
  python commit_judgments.py --tag 皓祥
        —— 读 retrieval/皓祥/judgments.json
  python commit_judgments.py --tag 皓祥 --file path/to/judgments.json
  python commit_judgments.py --tag 皓祥 --csv retrieval/皓祥/results.csv
"""
import argparse
import os
import sqlite3
import csv
import json
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
FACE_DB = os.path.join(HERE, "face_index.db")


def ensure_person(con, name):
    row = con.execute("SELECT id FROM persons WHERE name=?", (name,)).fetchone()
    if row:
        return row[0]
    cur = con.execute("INSERT INTO persons (name, created_at) VALUES (?, datetime('now'))",
                      (name,))
    return cur.lastrowid


def apply_one(con, pid, fid, judgment, reviewer):
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    if judgment == "accept":
        con.execute("UPDATE faces SET person_id=? WHERE id=?", (pid, fid))
        con.execute("INSERT INTO person_judgments (face_id, person_id, judgment, reviewer, ts) "
                    "VALUES (?,?,?,?,?)", (fid, pid, "accept", reviewer, ts))
        return "accept"
    elif judgment == "reject":
        con.execute("UPDATE faces SET person_id=-1 WHERE id=?", (fid,))
        con.execute("INSERT INTO person_judgments (face_id, person_id, judgment, reviewer, ts) "
                    "VALUES (?,?,?,?,?)", (fid, pid, "reject", reviewer, ts))
        return "reject"
    elif judgment == "unsure":
        con.execute("INSERT INTO person_judgments (face_id, person_id, judgment, reviewer, ts) "
                    "VALUES (?,?,?,?,?)", (fid, pid, "unsure", reviewer, ts))
        return "unsure"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True, help="人物名(对应 persons.name 与检索标签)")
    ap.add_argument("--file", help="judgments.json 路径(默认 retrieval/<tag>/judgments.json)")
    ap.add_argument("--csv", help="手动编辑的 results.csv(含 judgment 列)")
    ap.add_argument("--reviewer", default="Evan")
    args = ap.parse_args()

    con = sqlite3.connect(FACE_DB)
    con.execute("""CREATE TABLE IF NOT EXISTS person_judgments (
        id INTEGER PRIMARY KEY, face_id INTEGER, person_id INTEGER,
        judgment TEXT, reviewer TEXT, ts TEXT)""")
    pid = ensure_person(con, args.tag)

    acc = rej = uns = 0
    if args.csv:
        path = args.csv
        with open(path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                j = (r.get("judgment") or "").strip().lower()
                if not j:
                    continue
                res = apply_one(con, pid, int(r["face_id"]), j, args.reviewer)
                if res == "accept": acc += 1
                elif res == "reject": rej += 1
                elif res == "unsure": uns += 1
    else:
        path = args.file or os.path.join(HERE, "retrieval", args.tag, "judgments.json")
        if not os.path.exists(path):
            print(f"ERROR: 找不到 judgments.json: {path}")
            return
        d = json.load(open(path, encoding="utf-8"))
        for it in d.get("items", []):
            j = (it.get("judgment") or "").strip().lower()
            if not j:
                continue
            res = apply_one(con, pid, it["face_id"], j, args.reviewer)
            if res == "accept": acc += 1
            elif res == "reject": rej += 1
            elif res == "unsure": uns += 1

    con.commit()
    total = con.execute("SELECT COUNT(*) FROM faces WHERE person_id=?", (pid,)).fetchone()[0]
    con.close()
    print(f"人物 '{args.tag}' (id={pid}) 回写完成：接受 {acc} ｜ 排除 {rej} ｜ 存疑 {uns}")
    print(f"该人物目前在库人脸总数：{total}")


if __name__ == "__main__":
    main()
