# 07_analyze_corrections.py — 纠偏模式分析器
# 从 corrections 表自动提取系统性问题，生成改进建议
# 输出：词表扩展建议、规则映射更新、GLM prompt 微调素材、阈值调整建议
#
# 用法:
#   python 07_analyze_corrections.py                    # 生成完整分析报告
#   python 07_analyze_corrections.py --export-rules     # 导出更新的规则映射 JSON
#   python 07_analyze_corrections.py --export-vocabulary # 导出词表扩展建议
import argparse
import sqlite3
import os
import json
import datetime
from collections import Counter

DB_PATH = r"E:\PAIOS\10_WORK\photos_organizer\database\photo_index.db"
OUTPUT_DIR = r"E:\PAIOS\10_WORK\photos_organizer\outputs"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def analyze_confusion(conn):
    """分析混淆模式：哪两个类别最常被互换（字段级 corrections）。"""
    rows = conn.execute(
        "SELECT old_value, new_value, COUNT(*) "
        "FROM corrections WHERE field = 'category' "
        "GROUP BY old_value, new_value ORDER BY COUNT(*) DESC"
    ).fetchall()

    confusion_pairs = []
    for r in rows:
        confusion_pairs.append({
            "from": r[0],
            "to": r[1],
            "count": r[2],
            "pattern": f"{r[0]} → {r[1]}"
        })
    return confusion_pairs


def analyze_tag_gaps(conn):
    """分析词表缺失：用户纠偏中出现了哪些不在词表中的标签。"""
    # 从 field='tags' 的纠偏记录中提取新标签
    rows = conn.execute(
        "SELECT new_value FROM corrections WHERE field = 'tags'"
    ).fetchall()

    vocab_tags = set()
    vocab_rows = conn.execute("SELECT tag_type, tag_value FROM vocabulary WHERE enabled=1").fetchall()
    for r in vocab_rows:
        vocab_tags.add(f"{r['tag_type']}:{r['tag_value']}")

    missing_tags = Counter()
    for r in rows:
        if not r["new_value"]:
            continue
        try:
            tags = json.loads(r["new_value"])
        except (json.JSONDecodeError, TypeError):
            continue
        for t in tags:
            if isinstance(t, dict):
                key = f"{t.get('tag_type','custom')}:{t.get('tag_value','')}"
            elif isinstance(t, (list, tuple)):
                key = f"{t[0]}:{t[1]}"
            else:
                continue
            if key not in vocab_tags:
                missing_tags[key] += 1

    return [{"tag": tag, "count": cnt} for tag, cnt in missing_tags.most_common(20)]


def analyze_rule_conflicts(conn):
    """分析规则映射冲突：哪些 source 映射需要更新（字段级）。"""
    rows = conn.execute(
        "SELECT old_value, new_value, COUNT(*) "
        "FROM corrections WHERE field = 'source' AND old_value != new_value "
        "GROUP BY old_value, new_value ORDER BY COUNT(*) DESC"
    ).fetchall()

    conflicts = []
    for r in rows:
        conflicts.append({
            "from_source": r[0],
            "to_source": r[1],
            "count": r[2]
        })
    return conflicts


def analyze_threshold_issues(conn):
    """分析阈值问题：哪些类别有大量低置信度照片被纠偏。"""
    rows = conn.execute(
        "SELECT p.primary_category, AVG(p.confidence), MIN(p.confidence), COUNT(*) "
        "FROM photos p "
        "JOIN corrections c ON p.id = c.photo_id AND c.field = 'category' "
        "GROUP BY p.primary_category "
        "ORDER BY AVG(p.confidence) ASC"
    ).fetchall()

    issues = []
    for r in rows:
        issues.append({
            "category": r[0],
            "avg_conf": round(r[1], 3),
            "min_conf": round(r[2], 3),
            "correction_count": r[3]
        })
    return issues


def generate_glm_prompt_examples(conn):
    """从 corrections 中提取 GLM prompt 微调素材。

    选取最典型的纠偏案例作为分类参考。
    关键不是"这张错了"，而是"为什么100张都错"——提取 pattern_id 归组的模式。
    """
    # 先按 pattern_id 分组统计（同一原因的纠偏才是有价值的模式）
    pattern_counts = conn.execute(
        "SELECT pattern_id, COUNT(*) FROM corrections WHERE field = 'category' "
        "GROUP BY pattern_id ORDER BY COUNT(*) DESC LIMIT 10"
    ).fetchall()

    examples = []
    for pc in pattern_counts:
        pid = pc["pattern_id"] if hasattr(pc, "pattern_id") else pc[0]
        cnt = pc["count"] if hasattr(pc, "count") else pc[1]

        # 每个 pattern 取一条典型样本
        row = conn.execute(
            "SELECT c.photo_id, c.old_value, c.new_value, c.reason, p.path "
            "FROM corrections c JOIN photos p ON c.photo_id = p.id "
            "WHERE c.pattern_id = ? AND c.field = 'category' LIMIT 1",
            (pid,)
        ).fetchone()
        if row:
            examples.append({
                "photo_id": row["photo_id"],
                "pattern_id": pid,
                "wrong": row["old_value"],
                "correct": row["new_value"],
                "reason": row["reason"],
                "affected_count": cnt,
                "path": row["path"]
            })
    return examples


def generate_full_report(conn, output_path):
    """生成完整分析报告。"""
    confusion = analyze_confusion(conn)
    tag_gaps = analyze_tag_gaps(conn)
    rule_conflicts = analyze_rule_conflicts(conn)
    threshold_issues = analyze_threshold_issues(conn)
    glm_examples = generate_glm_prompt_examples(conn)

    # 统计
    total_corrections = conn.execute("SELECT COUNT(*) FROM corrections").fetchone()[0]

    report = {
        "generated_at": datetime.datetime.now().isoformat(),
        "total_corrections": total_corrections,
        "confusion_patterns": confusion,
        "tag_gaps": tag_gaps,
        "rule_conflicts": rule_conflicts,
        "threshold_issues": threshold_issues,
        "glm_prompt_examples": glm_examples,
        "recommendations": []
    }

    # 生成改进建议
    recs = []

    # 1. 词表扩展建议
    for gap in tag_gaps:
        recs.append({
            "type": "vocabulary_expansion",
            "action": f"添加词表标签: {gap['tag']} (出现 {gap['count']} 次)",
            "priority": "high" if gap["count"] >= 3 else "medium"
        })

    # 2. 规则映射更新建议
    for conflict in rule_conflicts:
        recs.append({
            "type": "rule_mapping_update",
            "action": f"修改 source 映射: {conflict['from_source']} → {conflict['to_source']} "
                      f"({conflict['count']} 条纠偏支持)",
            "priority": "high" if conflict["count"] >= 5 else "medium"
        })

    # 3. 阈值调整建议
    for issue in threshold_issues:
        if issue["avg_conf"] < 0.6:
            recs.append({
                "type": "threshold_adjustment",
                "action": f"降低 {issue['category']} 的 fallback threshold: "
                          f"avg_conf={issue['avg_conf']}, {issue['correction_count']} 条纠偏",
                "priority": "high"
            })

    # 4. GLM prompt 微调建议
    if glm_examples:
        recs.append({
            "type": "glm_prompt_refinement",
            "action": f"将 {len(glm_examples)} 个纠偏案例加入 GLM prompt 作为参考示例",
            "priority": "medium"
        })

    report["recommendations"] = recs

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"分析报告已生成: {output_path}")
    print(f"\n=== 纠偏模式分析 ===")
    print(f"总纠偏数: {total_corrections}")

    print(f"\n混淆模式 (top 5):")
    for cp in confusion[:5]:
        print(f"  {cp['pattern']}: {cp['count']} 次")

    print(f"\n词表缺失 (top 5):")
    for gap in tag_gaps[:5]:
        print(f"  {gap['tag']}: {gap['count']} 次")

    print(f"\n规则映射冲突:")
    for conflict in rule_conflicts:
        print(f"  {conflict['from_source']} → {conflict['to_source']}: {conflict['count']} 次")

    print(f"\n改进建议 ({len(recs)} 条):")
    for rec in recs:
        print(f"  [{rec['priority']}] {rec['type']}: {rec['action']}")

    return report


def export_updated_rules(conn, output_path):
    """从纠偏数据导出更新的 TAG_TO_SOURCE 规则映射。"""
    conflicts = analyze_rule_conflicts(conn)
    current_rules = {}
    rows = conn.execute(
        "SELECT tag_value, mapping FROM vocabulary WHERE mapping IS NOT NULL AND enabled=1"
    ).fetchall()
    for r in rows:
        current_rules[r["tag_value"]] = r["mapping"]

    # 从纠偏中推断新规则
    rows = conn.execute(
        "SELECT c.correct_tags_json, c.correct_source FROM corrections "
        "WHERE correct_source IS NOT NULL AND correct_tags_json IS NOT NULL"
    ).fetchall()
    inferred_rules = Counter()
    for r in rows:
        tags = json.loads(r["correct_tags_json"])
        source = r["correct_source"]
        for t in tags:
            if isinstance(t, dict):
                tv = t.get("tag_value", "")
            elif isinstance(t, (list, tuple)):
                tv = t[1]
            else:
                continue
            inferred_rules[(tv, source)] += 1

    updated = current_rules.copy()
    for (tag, source), cnt in inferred_rules.most_common():
        if cnt >= 3:  # 至少 3 次纠偏才采纳
            updated[tag] = source

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)
    print(f"规则映射已导出: {output_path} ({len(updated)} 条)")


def export_vocabulary_expansion(conn, output_path):
    """导出词表扩展建议 JSON。"""
    gaps = analyze_tag_gaps(conn)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(gaps, f, ensure_ascii=False, indent=2)
    print(f"词表扩展建议已导出: {output_path} ({len(gaps)} 条)")


def main():
    ap = argparse.ArgumentParser(description="纠偏模式分析器")
    ap.add_argument("--export-rules", action="store_true", help="导出更新的规则映射")
    ap.add_argument("--export-vocabulary", action="store_true", help="导出词表扩展建议")
    args = ap.parse_args()

    conn = get_conn()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 确保 corrections 表存在（字段级 schema）
    conn.execute("""
    CREATE TABLE IF NOT EXISTS corrections (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        photo_id        INTEGER NOT NULL,
        photo_path      TEXT,
        field           TEXT NOT NULL,
        old_value       TEXT,
        new_value       TEXT,
        reason          TEXT,
        pattern_id      TEXT,
        operator        TEXT DEFAULT 'user',
        created_at      TEXT,
        FOREIGN KEY (photo_id) REFERENCES photos(id)
    )
    """)

    if args.export_rules:
        export_updated_rules(conn, os.path.join(OUTPUT_DIR, "updated_rules.json"))
    elif args.export_vocabulary:
        export_vocabulary_expansion(conn, os.path.join(OUTPUT_DIR, "vocabulary_expansion.json"))
    else:
        generate_full_report(conn, os.path.join(OUTPUT_DIR, "correction_analysis.json"))

    conn.close()


if __name__ == "__main__":
    main()
