#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_cooccurrence.py - 人物元数据扩展 + 共现网络 (PAIOS face_index)
Phase: 数据运营层 #1(人物命名系统) + #4(共现关系网络)
原则: 不修改任何原图, 仅改 face_index.db 元数据。
幂等: 重复运行安全 (ALTER 检查列存在 / photo_persons 全量重建)。

产出:
  - persons 表扩展: display_name / aliases / relationship / birth_year / confidence / cover_face_id
  - photo_persons 物化表 (photo_id, person_id, face_id) 每照片每人物去重到 1 行
  - person_pairs 视图 (任意两人同框次数)
  - export/cooccurrence_matrix.csv  (人物对共现)
  - export/cooccurrence_by_year.csv (逐年共现, 联 photo_index.db.photos.date)
"""
import sqlite3, os, csv

FACE_DB = "E:/PAIOS/10_WORK/photos_organizer/face_index/face_index.db"
PHOTO_DB = "E:/PAIOS/10_WORK/photos_organizer/database/photo_index.db"
EXPORT = "E:/PAIOS/10_WORK/photos_organizer/face_index/export"


def cols(c, table):
    return {r[1] for r in c.execute(f"PRAGMA table_info({table})").fetchall()}


def migrate_persons(c):
    need = {
        "display_name": "TEXT",
        "aliases": "TEXT",
        "relationship": "TEXT",
        "birth_year": "INTEGER",
        "confidence": "REAL",
        "cover_face_id": "INTEGER",
    }
    existing = cols(c, "persons")
    for name, typ in need.items():
        if name not in existing:
            c.execute(f"ALTER TABLE persons ADD COLUMN {name} {typ}")
            print(f"  + persons.{name} ({typ})")
    # 回填 display_name = name（已有记录）
    c.execute("UPDATE persons SET display_name = name WHERE display_name IS NULL OR display_name = ''")
    # cover_face = 该人 det_score 最高的脸
    c.execute("""
        UPDATE persons SET cover_face_id = (
            SELECT id FROM faces f WHERE f.person_id = persons.id
            ORDER BY f.det_score DESC LIMIT 1
        ) WHERE cover_face_id IS NULL
    """)
    # confidence = person_judgments 中 accept 占比
    tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    if "person_judgments" in tables:
        for (pid,) in c.execute("SELECT id FROM persons").fetchall():
            row = c.execute(
                "SELECT SUM(CASE WHEN judgment='accept' THEN 1 ELSE 0 END)*1.0 / COUNT(*) "
                "FROM person_judgments WHERE person_id=?", (pid,)
            ).fetchone()
            if row and row[0] is not None:
                c.execute("UPDATE persons SET confidence=? WHERE id=?", (round(row[0], 3), pid))


def rebuild_photo_persons(c):
    c.execute("DROP TABLE IF EXISTS photo_persons")
    c.execute("""
        CREATE TABLE photo_persons (
            photo_id  INTEGER,
            person_id INTEGER,
            face_id   INTEGER,
            PRIMARY KEY (photo_id, person_id)
        )
    """)
    n = c.execute("""
        INSERT INTO photo_persons (photo_id, person_id, face_id)
        SELECT photo_id, person_id, id FROM faces
        WHERE person_id > 0 AND photo_id IS NOT NULL
    """).rowcount
    print(f"  photo_persons 重建: {n} 行 (每照片每人物去重到 1 行)")


def create_views(c):
    c.execute("DROP VIEW IF EXISTS person_pairs")
    c.execute("""
        CREATE VIEW person_pairs AS
        SELECT a.person_id pA, b.person_id pB, COUNT(*) cooc
        FROM photo_persons a
        JOIN photo_persons b
          ON a.photo_id = b.photo_id AND a.person_id < b.person_id
        GROUP BY a.person_id, b.person_id
    """)
    print("  person_pairs 视图已建")


def report(c):
    name = dict(c.execute("SELECT id, display_name FROM persons").fetchall())
    print("\n=== 共现对 (person_pairs) ===")
    rows = c.execute("SELECT pA, pB, cooc FROM person_pairs ORDER BY cooc DESC").fetchall()
    if not rows:
        print("  (暂无跨人物同框对 —— 需先命名更多人)")
    for a, b, co in rows:
        print(f"  {name.get(a, a)} <-> {name.get(b, b)} : {co} 次同框")

    os.makedirs(EXPORT, exist_ok=True)
    with open(os.path.join(EXPORT, "cooccurrence_matrix.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["personA", "personB", "cooc"])
        for a, b, co in rows:
            w.writerow([name.get(a, a), name.get(b, b), co])

    if os.path.exists(PHOTO_DB):
        c.execute(f"ATTACH DATABASE '{PHOTO_DB}' AS pidx")
        total_pp = c.execute("SELECT COUNT(*) FROM photo_persons").fetchone()[0]
        cov = c.execute("SELECT COUNT(*) FROM photo_persons pp JOIN pidx.photos ph ON ph.id = pp.photo_id").fetchone()[0]
        print(f"\n  photo_persons 能联回 photos.date 的比例: {cov}/{total_pp}")
        print("=== 逐年共现（已命名人物）===")
        yr = c.execute("""
            SELECT strftime('%Y', ph.date) y, a.person_id pA, b.person_id pB, COUNT(*) cooc
            FROM photo_persons a
            JOIN photo_persons b ON a.photo_id = b.photo_id AND a.person_id < b.person_id
            JOIN pidx.photos ph ON ph.id = a.photo_id
            WHERE ph.date IS NOT NULL
            GROUP BY y, a.person_id, b.person_id ORDER BY y, cooc DESC
        """).fetchall()
        with open(os.path.join(EXPORT, "cooccurrence_by_year.csv"), "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f); w.writerow(["year", "personA", "personB", "cooc"])
            for y, a, b, co in yr:
                w.writerow([y, name.get(a, a), name.get(b, b), co])
                print(f"  {y}: {name.get(a, a)} <-> {name.get(b, b)} = {co}")
        c.execute("DETACH DATABASE pidx")
        print(f"\n  已写 {EXPORT}/cooccurrence_matrix.csv 与 cooccurrence_by_year.csv")


def main():
    c = sqlite3.connect(FACE_DB)
    print(">> migrate persons schema")
    migrate_persons(c)
    print(">> rebuild photo_persons")
    rebuild_photo_persons(c)
    print(">> create views")
    create_views(c)
    c.commit()
    report(c)
    c.commit(); c.close()
    print("\n完成。仅改元数据, 原图未动。")


if __name__ == "__main__":
    main()
