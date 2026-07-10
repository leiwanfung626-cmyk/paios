# 05_review_report.py — 智能抽样审查报告生成器
# 目的：从 15530 张照片中提取 ~300 张代表性样本，让用户高效审查
# 不需要翻阅所有照片，只审查"最可能出错"的子集
#
# 用法:
#   python 05_review_report.py                     # 生成完整审查报告
#   python 05_review_report.py --category 其他     # 只审查"其他"类
#   python 05_review_report.py --format html        # 输出 HTML（带图片预览）
#   python 05_review_report.py --format csv         # 输出 CSV
import argparse
import sqlite3
import os
import sys
import json
import csv
import datetime
from pathlib import Path

DB_PATH = r"E:\PAIOS\10_WORK\photos_organizer\database\photo_index.db"
OUTPUT_DIR = r"E:\PAIOS\10_WORK\photos_organizer\outputs"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def sample_to_review(conn, category=None):
    """智能抽样：返回最可能被误分类的照片列表。

    抽样策略（5层叠加）:
    1. 07_ToReview 全部（系统已标记为不确定）
    2. 低置信度 <0.6（CLIP 不确定的）
    3. "其他"类全部（最可能被误分类的垃圾桶）
    4. 每个类别抽样 20 张（按置信度从低到高）
    5. CLIP/GLM 分歧照片（两引擎给了不同类别）
    """
    samples = []
    seen_ids = set()

    # Layer 1: 07_ToReview 全部
    query = "SELECT id, path, filename, primary_category, confidence, classifier, source, media_type, extension FROM photos WHERE source = '07_ToReview'"
    if category:
        query += f" AND primary_category = '{category}'"
    rows = conn.execute(query).fetchall()
    for r in rows:
        if r["id"] not in seen_ids:
            samples.append(dict(r))
            samples[-1]["review_reason"] = "to_review"
            seen_ids.add(r["id"])

    # Layer 2: 低置信度
    query = "SELECT id, path, filename, primary_category, confidence, classifier, source, media_type, extension FROM photos WHERE confidence < 0.6 AND classifier = 'local_clip'"
    if category:
        query += f" AND primary_category = '{category}'"
    query += " ORDER BY confidence ASC LIMIT 100"
    rows = conn.execute(query).fetchall()
    for r in rows:
        if r["id"] not in seen_ids:
            samples.append(dict(r))
            samples[-1]["review_reason"] = "low_confidence"
            seen_ids.add(r["id"])

    # Layer 3: "其他"类全部（最可疑的垃圾桶）
    if not category or category == "其他":
        rows = conn.execute(
            "SELECT id, path, filename, primary_category, confidence, classifier, source, media_type, extension "
            "FROM photos WHERE primary_category = '其他' ORDER BY confidence ASC"
        ).fetchall()
        for r in rows:
            if r["id"] not in seen_ids:
                samples.append(dict(r))
                samples[-1]["review_reason"] = "catch_all_category"
                seen_ids.add(r["id"])

    # Layer 4: 每类别抽样 20（低置信度优先）
    categories = conn.execute(
        "SELECT DISTINCT primary_category FROM photos WHERE primary_category IS NOT NULL"
    ).fetchall()
    for cat_row in categories:
        cat = cat_row["primary_category"]
        if category and cat != category:
            continue
        rows = conn.execute(
            f"SELECT id, path, filename, primary_category, confidence, classifier, source, media_type, extension "
            f"FROM photos WHERE primary_category = '{cat}' AND id NOT IN ({','.join(str(x) for x in seen_ids) if seen_ids else '0'}) "
            f"ORDER BY confidence ASC LIMIT 20"
        ).fetchall()
        for r in rows:
            if r["id"] not in seen_ids:
                samples.append(dict(r))
                samples[-1]["review_reason"] = "category_sample"
                seen_ids.add(r["id"])

    # Layer 5: GLM 补判的照片（CLIP 不确定，两引擎可能分歧）
    rows = conn.execute(
        "SELECT id, path, filename, primary_category, confidence, classifier, source, media_type, extension "
        "FROM photos WHERE classifier = 'glm4v_flash'"
    ).fetchall()
    for r in rows:
        if r["id"] not in seen_ids:
            samples.append(dict(r))
            samples[-1]["review_reason"] = "glm_supplement"
            seen_ids.add(r["id"])

    return samples


def get_tags_for_photos(conn, photo_ids):
    """批量获取照片的多标签。"""
    tags_map = {}
    for pid in photo_ids:
        rows = conn.execute(
            "SELECT tag_type, tag_value, source, confidence FROM tags WHERE photo_id = ?",
            (pid,)
        ).fetchall()
        tags_map[pid] = [dict(r) for r in rows]
    return tags_map


def get_confusion_matrix(conn):
    """生成分类混淆矩阵：哪两个类别最容易混淆。"""
    # 基于 GLM 补判的照片，CLIP 的初判和 GLM 的终判不同 = 混淆
    # 目前只有 primary_category，没有 CLIP 初判记录
    # 改为按置信度分布分析
    matrix = {}
    rows = conn.execute(
        "SELECT primary_category, AVG(confidence), MIN(confidence), MAX(confidence), COUNT(*) "
        "FROM photos WHERE classifier = 'local_clip' GROUP BY primary_category "
        "ORDER BY AVG(confidence) ASC"
    ).fetchall()
    for r in rows:
        matrix[r[0]] = {
            "avg_conf": r[1], "min_conf": r[2], "max_conf": r[3],
            "count": r[4]
        }
    return matrix


def generate_csv_report(samples, tags_map, output_path):
    """生成 CSV 审查报告。"""
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([
            "photo_id", "path", "filename", "current_category", "confidence",
            "classifier", "source", "media_type", "extension", "review_reason",
            "tags_scene", "tags_people", "tags_object", "tags_activity", "tags_attribute",
            "correct_category", "correct_source", "correct_tags", "notes"
        ])
        for s in samples:
            pid = s["id"]
            t = tags_map.get(pid, [])
            tag_dict = {}
            for trow in t:
                tt = trow["tag_type"]
                tv = trow["tag_value"]
                if tt not in tag_dict:
                    tag_dict[tt] = []
                tag_dict[tt].append(tv)

            w.writerow([
                pid, s["path"], s["filename"], s["primary_category"],
                f"{s['confidence']:.3f}", s["classifier"], s["source"],
                s["media_type"], s["extension"], s["review_reason"],
                "|".join(tag_dict.get("scene", [])),
                "|".join(tag_dict.get("people", [])),
                "|".join(tag_dict.get("object", [])),
                "|".join(tag_dict.get("activity", [])),
                "|".join(tag_dict.get("attribute", [])),
                "", "", "", ""  # 用户填写的纠偏列
            ])


def generate_html_report(samples, tags_map, confusion, output_path):
    """生成 HTML 审查报告（带图片预览）。"""
    input_dir = r"E:\待整理照片"

    # 混淆矩阵摘要
    confusion_html = "<h2>分类置信度分析</h2><table border='1' cellpadding='4'>"
    confusion_html += "<tr><th>类别</th><th>平均置信度</th><th>最低</th><th>最高</th><th>数量</th></tr>"
    for cat, info in sorted(confusion.items(), key=lambda x: x[1]["avg_conf"]):
        confusion_html += (
            f"<tr><td>{cat}</td><td>{info['avg_conf']:.3f}</td>"
            f"<td>{info['min_conf']:.3f}</td><td>{info['max_conf']:.3f}</td>"
            f"<td>{info['count']}</td></tr>"
        )
    confusion_html += "</table>"

    # 照片审查表
    photos_html = "<h2>需审查照片（按置信度排序）</h2>"
    for s in sorted(samples, key=lambda x: x["confidence"]):
        pid = s["id"]
        t = tags_map.get(pid, [])
        tag_str = ", ".join(f"{trow['tag_type']}:{trow['tag_value']}" for trow in t)

        # 相对路径用于图片预览
        img_src = s["path"]

        ext_display = s["extension"] or "unknown"
        photos_html += (
            f"<div style='margin:8px 0; padding:8px; border:1px solid #ddd; display:flex; align-items:center;'>"
            f"<img src='{img_src}' style='max-height:120px; max-width:160px; margin-right:12px;' "
            f"onerror=\"this.src=''; this.alt='no preview'\" />"
            f"<div>"
            f"<b>[{s['review_reason']}]</b> "
            f"ID:{pid} | 当前: {s['primary_category']} (conf={s['confidence']:.3f}, {s['classifier']}) | "
            f"Source: {s['source']} | Type: {s['media_type']} | Ext: {ext_display}"
            f"<br>Tags: {tag_str}"
            f"<br>Path: {s['path']}"
            f"</div></div>"
        )

    now_str = datetime.datetime.now().isoformat()
    n_samples = len(samples)

    html = (
        '<!DOCTYPE html>\n'
        '<html><head><meta charset="utf-8"><title>PAIOS 照片审查报告</title>\n'
        '<style>\n'
        'body { font-family: sans-serif; margin: 20px; background: #f5f5f5; }\n'
        'h1 { color: #333; }\n'
        'h2 { color: #555; margin-top: 20px; }\n'
        'table { background: white; }\n'
        '</style></head><body>\n'
        '<h1>PAIOS V1.0 照片审查报告</h1>\n'
        '<p>生成时间: ' + now_str + '</p>\n'
        '<p>总审查样本: ' + str(n_samples) + ' 张</p>\n\n'
        + confusion_html + '\n\n'
        '<h2>审查策略说明</h2>\n<ul>\n'
        '<li><b>to_review</b>: 系统标记为不确定（07_ToReview）</li>\n'
        '<li><b>low_confidence</b>: CLIP 置信度 &lt;0.6</li>\n'
        '<li><b>catch_all_category</b>: "其他"类（最可能误分类）</li>\n'
        '<li><b>category_sample</b>: 每类别抽样 20</li>\n'
        '<li><b>glm_supplement</b>: GLM 补判照片（CLIP 初判不确定）</li>\n'
        '</ul>\n\n'
        + photos_html + '\n\n'
        '<h2>纠偏说明</h2>\n'
        '<p>发现误分类后，用自然语言告诉 PAIOS：</p>\n<ul>\n'
        '<li>单张: "photo_id=123 应该是旅行+人物, 不是风景"</li>\n'
        '<li>批量: "所有其他类里的美食照片都改为美食"</li>\n'
        '<li>规则: "饮料和甜点也应该归美食类"</li>\n'
        '</ul>\n\n'
        '</body></html>'
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    ap = argparse.ArgumentParser(description="生成照片审查报告")
    ap.add_argument("--category", default=None, help="只审查指定类别")
    ap.add_argument("--format", default="html", choices=["html", "csv"], help="输出格式")
    ap.add_argument("--limit", type=int, default=0, help="限制样本数量")
    args = ap.parse_args()

    conn = get_conn()
    samples = sample_to_review(conn, args.category)

    if args.limit:
        samples = samples[:args.limit]

    tags_map = get_tags_for_photos(conn, [s["id"] for s in samples])
    confusion = get_confusion_matrix(conn)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if args.format == "html":
        out_path = os.path.join(OUTPUT_DIR, "review_report.html")
        generate_html_report(samples, tags_map, confusion, out_path)
    else:
        out_path = os.path.join(OUTPUT_DIR, "review_report.csv")
        generate_csv_report(samples, tags_map, out_path)

    conn.close()

    print(f"审查报告已生成: {out_path}")
    print(f"总审查样本: {len(samples)}")
    print(f"审查原因分布:")
    reasons = {}
    for s in samples:
        r = s["review_reason"]
        reasons[r] = reasons.get(r, 0) + 1
    for r, cnt in sorted(reasons.items(), key=lambda x: -x[1]):
        print(f"  {r}: {cnt}")


if __name__ == "__main__":
    main()
