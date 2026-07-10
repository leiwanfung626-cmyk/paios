# 06_correct.py — 人工纠偏工具
# 核心原则：Metadata Evolves, Assets Don't
# 纠偏 = 更新元数据（tags/photos/photo_versions），不动原图
#
# 用法:
#   # 单张纠偏
#   python 06_correct.py --photo-id 123 --correct-category "旅行" --correct-source "01_Personal"
#   python 06_correct.py --photo-id 123 --correct-category "旅行+人物" --correct-tags "scene:景区,people:家人,activity:旅行"
#
#   # 批量纠偏（从 corrections.json 文件）
#   python 06_correct.py --batch corrections.json
#
#   # 类别级批量纠偏
#   python 06_correct.py --from-category "其他" --to-category "美食" --where-tags-contain "食物,饮品"
#
#   # 显示某张照片的当前状态
#   python 06_correct.py --show 123
import argparse
import sqlite3
import os
import sys
import json
import datetime

DB_PATH = r"E:\PAIOS\10_WORK\photos_organizer\database\photo_index.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ══════════════════════════════════════════════════════════
# 一、corrections 表（字段级纠偏记录）
# ══════════════════════════════════════════════════════════
# 核心设计：不是一行记录一次纠偏，而是每个字段单独记录
# 这样能精确追踪"哪个字段被改了、为什么改"
# 纠偏数据才是真正的训练数据——不是改文件，而是记录偏差
CORRECTIONS_SCHEMA = """
CREATE TABLE IF NOT EXISTS corrections (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    photo_id        INTEGER NOT NULL,
    photo_path      TEXT,
    field           TEXT NOT NULL,       -- 被纠偏的字段: source/category/tags
    old_value       TEXT,                -- AI 原始输出
    new_value       TEXT,                -- 人工修正值
    reason          TEXT,                -- 纠偏原因（自然语言，这才是训练数据）
    pattern_id      TEXT,                -- 错误模式 ID（同一模式的纠偏归为一组）
    operator        TEXT DEFAULT 'user',
    created_at      TEXT,
    FOREIGN KEY (photo_id) REFERENCES photos(id)
);
"""


def ensure_corrections_table(conn):
    """确保 corrections 表存在。"""
    conn.execute(CORRECTIONS_SCHEMA)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_corr_photo ON corrections(photo_id);")
    conn.commit()


def snapshot_tags(conn, photo_id):
    """快照当前 tags 表的状态。"""
    rows = conn.execute(
        "SELECT tag_type, tag_value, source, confidence FROM tags WHERE photo_id = ?",
        (photo_id,)
    ).fetchall()
    return json.dumps([dict(r) for r in rows], ensure_ascii=False)


def apply_correction(conn, photo_id, correct_category=None, correct_source=None,
                     correct_tags=None, correction_type="all", reason=""):
    """应用一条纠偏，更新 photos/tags/photo_versions/corrections。"""
    now = datetime.datetime.now().isoformat()

    # 获取当前状态
    photo = conn.execute(
        "SELECT id, path, primary_category, source, confidence, classifier, classifier_version, caption FROM photos WHERE id = ?",
        (photo_id,)
    ).fetchone()
    if not photo:
        print(f"Photo ID {photo_id} 不存在")
        return False

    wrong_category = photo["primary_category"]
    wrong_source = photo["source"]
    wrong_tags = snapshot_tags(conn, photo_id)

    # 计算新值（只更新有改动的字段）
    new_category = correct_category or wrong_category
    new_source = correct_source or wrong_source
    new_confidence = 1.0  # 人工纠偏置信度 = 1.0（绝对可信）

    # 更新 photos 表
    conn.execute(
        "UPDATE photos SET primary_category=?, source=?, confidence=?, "
        "classifier='manual', classifier_version='human-correct-v1', updated_at=? "
        "WHERE id=?",
        (new_category, new_source, new_confidence, now, photo_id)
    )

    # 更新 tags 表：如果有新标签，先删旧再写新
    if correct_tags:
        conn.execute("DELETE FROM tags WHERE photo_id = ?", (photo_id,))
        for tt, tv in correct_tags:
            conn.execute(
                "INSERT INTO tags (photo_id, tag_type, tag_value, source, confidence, created_at) "
                "VALUES (?,?,?,?,?,?)",
                (photo_id, tt, tv, "manual", 1.0, now)
            )

    # 写入 photo_versions（新增版本）
    max_ver = conn.execute(
        "SELECT MAX(version) FROM photo_versions WHERE photo_id = ?",
        (photo_id,)
    ).fetchone()[0] or 0
    new_ver = max_ver + 1

    # 新标签快照
    new_tags_json = json.dumps(correct_tags if correct_tags else [], ensure_ascii=False)

    conn.execute(
        "INSERT INTO photo_versions "
        "(photo_id, version, classifier, classifier_version, primary_category, "
        "confidence, tags_json, caption, source, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (photo_id, new_ver, "manual", "human-correct-v1", new_category,
         new_confidence, new_tags_json, photo["caption"], new_source, now)
    )

    # 写入 corrections 表（字段级记录：每个被修改的字段单独一行）
    # 这才是真正的训练数据：AI 输了什么 → 应该是什么 → 为什么
    pattern_id = reason[:20] if reason else "manual"  # 同 reason 归为同一 pattern

    if correct_category and correct_category != wrong_category:
        conn.execute(
            "INSERT INTO corrections "
            "(photo_id, photo_path, field, old_value, new_value, reason, pattern_id, operator, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (photo_id, photo["path"], "category", wrong_category, new_category,
             reason or f"AI判{wrong_category}，实际是{new_category}", pattern_id, "user", now)
        )

    if correct_source and correct_source != wrong_source:
        conn.execute(
            "INSERT INTO corrections "
            "(photo_id, photo_path, field, old_value, new_value, reason, pattern_id, operator, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (photo_id, photo["path"], "source", wrong_source, new_source,
             reason or f"AI判{wrong_source}，实际是{new_source}", pattern_id, "user", now)
        )

    if correct_tags:
        conn.execute(
            "INSERT INTO corrections "
            "(photo_id, photo_path, field, old_value, new_value, reason, pattern_id, operator, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (photo_id, photo["path"], "tags", wrong_tags, new_tags_json,
             reason or "标签纠偏", pattern_id, "user", now)
        )

    conn.commit()
    print(f"纠偏已应用: photo_id={photo_id}")
    print(f"  {wrong_category} → {new_category}")
    print(f"  {wrong_source} → {new_source}")
    print(f"  version: {max_ver} → {new_ver}")
    return True


def show_photo(conn, photo_id):
    """显示照片当前状态。"""
    photo = conn.execute(
        "SELECT * FROM photos WHERE id = ?", (photo_id,)
    ).fetchone()
    if not photo:
        print(f"Photo ID {photo_id} 不存在")
        return

    tags = conn.execute(
        "SELECT tag_type, tag_value, source, confidence FROM tags WHERE photo_id = ?",
        (photo_id,)
    ).fetchall()

    versions = conn.execute(
        "SELECT version, classifier, primary_category, confidence, source, created_at "
        "FROM photo_versions WHERE photo_id = ? ORDER BY version",
        (photo_id,)
    ).fetchall()

    corrections = conn.execute(
        "SELECT * FROM corrections WHERE photo_id = ?",
        (photo_id,)
    ).fetchall()

    print(f"=== Photo ID {photo_id} ===")
    for key in photo.keys():
        if key != "id":
            print(f"  {key}: {photo[key]}")

    print(f"\n标签 ({len(tags)}):")
    for t in tags:
        print(f"  {t['tag_type']}:{t['tag_value']} (source={t['source']}, conf={t['confidence']})")

    print(f"\n版本历史 ({len(versions)}):")
    for v in versions:
        print(f"  v{v['version']}: {v['classifier']} → {v['primary_category']} "
              f"(conf={v['confidence']:.3f}, source={v['source']}, @ {v['created_at']})")

    print(f"\n纠偏记录 ({len(corrections)}):")
    for c in corrections:
        print(f"  {c['wrong_primary_category']} → {c['correct_primary_category']} "
              f"({c['correction_type']}, reason: {c['reason']})")


def parse_tags_str(tags_str):
    """解析标签字符串 'scene:景区,people:家人,activity:旅行' → [(scene,景区), ...]"""
    if not tags_str:
        return None
    result = []
    pairs = tags_str.split(",")
    for pair in pairs:
        if ":" in pair:
            tt, tv = pair.split(":", 1)
            result.append((tt.strip(), tv.strip()))
        else:
            result.append(("custom", pair.strip()))
    return result


def batch_from_file(conn, filepath):
    """从 JSON 文件批量纠偏。格式:
    [
        {"photo_id": 123, "correct_category": "旅行", "correct_source": "01_Personal",
         "correct_tags": "scene:景区,people:家人", "reason": "误分类"},
        ...
    ]
    """
    with open(filepath, encoding="utf-8") as f:
        corrections = json.load(f)

    applied = 0
    for c in corrections:
        pid = c.get("photo_id")
        if not pid:
            continue
        tags = parse_tags_str(c.get("correct_tags"))
        ok = apply_correction(
            conn, pid,
            correct_category=c.get("correct_category"),
            correct_source=c.get("correct_source"),
            correct_tags=tags,
            correction_type=c.get("correction_type", "all"),
            reason=c.get("reason", "")
        )
        if ok:
            applied += 1

    print(f"\n批量纠偏完成: {applied}/{len(corrections)}")


def batch_from_category(conn, from_cat, to_cat, where_tags=None):
    """类别级批量纠偏：把 from_category 的所有（或含特定标签的）照片改为 to_category。"""
    tags_filter = ""
    if where_tags:
        tag_values = [v.strip() for v in where_tags.split(",")]
        tag_in_clause = ",".join(f"'{v}'" for v in tag_values)
        photo_ids = conn.execute(
            f"SELECT DISTINCT p.id FROM photos p "
            f"JOIN tags t ON p.id = t.photo_id "
            f"WHERE p.primary_category = '{from_cat}' "
            f"AND t.tag_value IN ({tag_in_clause}) "
        ).fetchall()
        target_ids = [r["id"] for r in photo_ids]
    else:
        rows = conn.execute(
            f"SELECT id FROM photos WHERE primary_category = '{from_cat}'"
        ).fetchall()
        target_ids = [r["id"] for r in rows]

    print(f"找到 {len(target_ids)} 张 {from_cat} 类照片需要纠偏 → {to_cat}")
    if not target_ids:
        return

    applied = 0
    for pid in target_ids:
        ok = apply_correction(
            conn, pid,
            correct_category=to_cat,
            correction_type="category",
            reason=f"批量: {from_cat} → {to_cat}" + (f" (含标签: {where_tags})" if where_tags else "")
        )
        if ok:
            applied += 1

    print(f"\n批量纠偏完成: {applied}/{len(target_ids)}")


def main():
    ap = argparse.ArgumentParser(description="人工纠偏工具")
    ap.add_argument("--photo-id", type=int, help="单张照片 ID")
    ap.add_argument("--correct-category", help="正确主类别")
    ap.add_argument("--correct-source", help="正确 source 目录")
    ap.add_argument("--correct-tags", help="正确标签 (格式: scene:景区,people:家人)")
    ap.add_argument("--reason", default="", help="纠偏原因（自然语言）")
    ap.add_argument("--batch", help="从 JSON 文件批量纠偏")
    ap.add_argument("--from-category", help="批量: 原类别")
    ap.add_argument("--to-category", help="批量: 目标类别")
    ap.add_argument("--where-tags-contain", help="批量: 只改含这些标签的")
    ap.add_argument("--show", type=int, help="显示照片状态")
    args = ap.parse_args()

    conn = get_conn()
    ensure_corrections_table(conn)

    if args.show:
        show_photo(conn, args.show)
    elif args.batch:
        batch_from_file(conn, args.batch)
    elif args.from_category and args.to_category:
        batch_from_category(conn, args.from_category, args.to_category, args.where_tags_contain)
    elif args.photo_id:
        tags = parse_tags_str(args.correct_tags)
        apply_correction(
            conn, args.photo_id,
            correct_category=args.correct_category,
            correct_source=args.correct_source,
            correct_tags=tags,
            reason=args.reason
        )
    else:
        print("请指定纠偏方式:")
        print("  --photo-id + --correct-category  单张纠偏")
        print("  --batch corrections.json         批量纠偏")
        print("  --from-category + --to-category  类别级批量")
        print("  --show <id>                      查看状态")

    conn.close()


if __name__ == "__main__":
    main()
