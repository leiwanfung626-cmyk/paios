#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 P1 优先级审查报告 — 缩略图以 base64 内嵌，完全离线自包含。

不再依赖 HTTP 服务：用 file:// 直接打开也有预览图。
缩略图取自 outputs/thumbs/ 缓存（命名 = md5(源路径).jpg）；
缺失或 0 字节则即时用 PIL 生成（含 HEIC 解码）。
"""
import sqlite3
import os
import base64
import hashlib
import io
import datetime

DB_PATH = r"E:\PAIOS\10_WORK\photos_organizer\database\photo_index.db"
OUTPUT_PATH = r"E:\PAIOS\10_WORK\photos_organizer\outputs\review_P1.html"
THUMB_DIR = r"E:\PAIOS\10_WORK\photos_organizer\outputs\thumbs"
THUMB_W = 400

# HEIC 支持
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except Exception as e:
    print(f"[warn] pillow-heif 不可用，HEIC 缩略图将失败: {e}")

from PIL import Image, ImageOps


def make_thumb_bytes(phys_path):
    """生成 400px 缩略图，返回 JPEG 字节；失败返回 None。"""
    try:
        with Image.open(phys_path) as img:
            try:
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass
            w, h = img.size
            if w > THUMB_W:
                nh = int(h * THUMB_W / w)
                img = img.resize((THUMB_W, nh), Image.LANCZOS)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=82)
            return buf.getvalue()
    except Exception as e:
        print(f"  缩略图失败 {phys_path}: {e}")
        return None


def get_thumb_b64(phys_path):
    """返回 data URI 字符串；找不到/生成失败返回 None。"""
    key = hashlib.md5(phys_path.encode("utf-8")).hexdigest()
    cache_path = os.path.join(THUMB_DIR, key + ".jpg")
    data = None
    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
        with open(cache_path, "rb") as f:
            data = f.read()
    else:
        data = make_thumb_bytes(phys_path)
        if data:
            try:
                with open(cache_path, "wb") as f:
                    f.write(data)
            except Exception:
                pass
    if not data:
        return None
    return "data:image/jpeg;base64," + base64.b64encode(data).decode("ascii")


def main():
    os.makedirs(THUMB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    p1 = conn.execute(
        "SELECT id, path, primary_category, confidence, classifier, source, media_type, extension "
        "FROM photos WHERE source = '07_ToReview' ORDER BY confidence ASC"
    ).fetchall()
    p2 = conn.execute(
        "SELECT id, path, primary_category, confidence, classifier, source, media_type, extension "
        "FROM photos WHERE primary_category = '其他' AND source != '07_ToReview' "
        "ORDER BY confidence ASC LIMIT 200"
    ).fetchall()
    p3 = conn.execute(
        "SELECT id, path, primary_category, confidence, classifier, source, media_type, extension "
        "FROM photos WHERE confidence < 0.4 AND classifier = 'local_clip' "
        "AND source != '07_ToReview' AND primary_category != '其他' "
        "ORDER BY confidence ASC LIMIT 200"
    ).fetchall()

    n1, n2, n3 = len(p1), len(p2), len(p3)
    total = n1 + n2 + n3
    print(f"P1-07_ToReview: {n1}")
    print(f"P2-其他类前200: {n2}")
    print(f"P3-极低CLIP前200: {n3}")
    print(f"核心审查总量: {total}")

    all_ids = [r['id'] for r in p1] + [r['id'] for r in p2] + [r['id'] for r in p3]
    tags_map = {}
    id_list = ','.join(str(x) for x in all_ids)
    tag_rows = conn.execute(
        f"SELECT photo_id, tag_type, tag_value FROM tags WHERE photo_id IN ({id_list})"
    ).fetchall()
    for tr in tag_rows:
        tags_map.setdefault(tr['photo_id'], []).append(f"{tr['tag_type']}:{tr['tag_value']}")

    css = (
        "body{font-family:sans-serif;margin:20px;background:#f5f5f5;max-width:900px}"
        "h1{color:#333}h2{color:#555;margin-top:24px}"
        ".card{margin:8px 0;padding:8px;border:1px solid #ddd;display:flex;align-items:center;"
        "background:#fff;border-radius:6px}"
        ".card img{width:160px;height:120px;object-fit:cover;margin-right:12px;"
        "background:#eee;flex-shrink:0}"
        ".p1{border-left:4px solid #e74c3c}"
        ".p2{border-left:4px solid #f39c12}"
        ".p3{border-left:4px solid #3498db}"
        ".meta{font-size:13px;line-height:1.5}"
        ".tag{display:inline-block;background:#eef;padding:1px 6px;margin:1px;border-radius:3px;"
        "font-size:11px}"
        "a.totop{position:fixed;right:20px;bottom:20px;background:#333;color:#fff;padding:8px 12px;"
        "border-radius:20px;text-decoration:none}"
    )

    parts = []
    parts.append('<!DOCTYPE html><html><head><meta charset="utf-8">'
                 '<title>PAIOS P1审查报告</title>')
    parts.append('<style>' + css + '</style></head><body>')
    parts.append('<h1>PAIOS V1.0 P1审查报告</h1>')
    parts.append(f'<p>生成: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}</p>')
    parts.append(f'<p>核心审查: <b>{total}</b> 张 '
                 f'(P1红:{n1} + P2橙:{n2} + P3蓝:{n3})</p>')
    parts.append('<p style="color:#666">完全离线版，缩略图已内嵌，无需服务器。'
                 '发现错误后告诉 Buddy："photo_id=123 应该是X，不是Y，原因：..."</p>')

    ok = fail = 0

    def render_section(rows, title, level, color):
        nonlocal ok, fail
        parts.append(f'<h2 style="color:{color}">{title}</h2>')
        for r in rows:
            tag_list = tags_map.get(r['id'], [])
            tag_html = ''.join(f'<span class="tag">{t}</span>' for t in tag_list) or '(无标签)'
            ext = r['extension'] or '?'
            b64 = get_thumb_b64(r['path'])
            if b64:
                src = b64
                ok += 1
            else:
                src = (f"data:image/svg+xml;utf8,"
                       f"<svg xmlns='http://www.w3.org/2000/svg' width='160' height='120'>"
                       f"<rect width='100%' height='100%' fill='%23ddd'/>"
                       f"<text x='50%' y='50%' font-size='12' fill='%23999' "
                       f"text-anchor='middle' dominant-baseline='middle'>预览不可用({ext})</text></svg>")
                fail += 1
            parts.append(
                f'<div class="card {level}">'
                f'<img loading="lazy" src="{src}" '
                f'onerror="this.style.background=\'#ddd\';this.alt=\'预览不可用({ext})\'"/>'
                f'<div class="meta">'
                f'<b>ID:{r["id"]}</b> | 当前: <b>{r["primary_category"]}</b> '
                f'(conf={round(r["confidence"],3)}, {r["classifier"]})<br>'
                f'Source: {r["source"]} | Ext: {ext}<br>'
                f'Tags: {tag_html}</div></div>'
            )

    render_section(p1, f'P1 · 07_ToReview ({n1}张) — 系统标记不确定', 'p1', '#e74c3c')
    render_section(p2, f'P2 · "其他"类前200最低置信度 — 最可能误分类', 'p2', '#f39c12')
    render_section(p3, f'P3 · CLIP极低置信度前200 — CLIP最犹豫', 'p3', '#3498db')

    parts.append('<a class="totop" href="#">↑顶部</a>')
    parts.append('</body></html>')

    html = '\n'.join(parts)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    size = os.path.getsize(OUTPUT_PATH)
    print(f"P1报告已生成: {OUTPUT_PATH} ({size/1024/1024:.1f} MB)")
    print(f"缩略图内嵌成功: {ok} | 失败: {fail}")
    conn.close()


if __name__ == '__main__':
    main()
