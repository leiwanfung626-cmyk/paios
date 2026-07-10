#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_person_gallery.py — 按人物生成带内联缩略图的 HTML 画廊 (CSV 看不了图, 这里补视图)
读取 export/persons/<name>.csv (已由 export_person_report.py 生成, 含缩略图文件名/原图路径/元数据)
产出 export/persons/<name>.html : 缩略图网格 + 来源筛选 + 日期排序, 点缩略图开原图。file:// 直开。
"""
import os
import csv
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
PERSON_DIR = os.path.join(HERE, "export", "persons")
# 从 export/persons/ 到 face_index/faces/ 的相对路径
THUMB_REL = "../../faces/"


def build(name):
    csv_path = os.path.join(PERSON_DIR, f"{name}.csv")
    if not os.path.exists(csv_path):
        print(f"跳过 {name}: 先跑 export_person_report.py 生成 {csv_path}")
        return None
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))

    cards = []
    for r in rows:
        thumb = r.get("人脸缩略图", "")
        orig = "file:///" + quote(r["原图路径"].replace("\\", "/"))
        age = r.get("检测年龄", "")
        gen = "男" if r.get("性别") == "1" else ("女" if r.get("性别") == "0" else "")
        agegen = f"{age}岁/{gen}" if age else gen
        src = r.get("来源", "")
        cat = r.get("分类", "")
        date = r.get("日期", "")
        # 卡片数据用 data-* 便于 JS 筛选
        cards.append(
            f'<a class="card" href="{orig}" target="_blank" data-src="{src}" '
            f'data-cat="{cat}" data-date="{date}">'
            f'<img loading="lazy" src="{THUMB_REL}{thumb}" '
            f'onerror="this.style.visibility=\'hidden\'"/>'
            f'<div class="meta">{date}<br/>{agegen}<br/>'
            f'<span class="tag">{src}/{cat}</span></div></a>')

    # 来源筛选选项
    srcs = sorted({r.get("来源", "") for r in rows})
    btns = "".join(
        f'<button onclick="filter(\'{s}\')" data-s="{s}">{s}</button>'
        for s in srcs)
    total = len(rows)

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>{name} · 照片画廊</title><style>
body{{font-family:system-ui,'Microsoft YaHei',sans-serif;background:#f7f8fa;color:#222;margin:0;padding:20px}}
h1{{font-size:20px;margin:0 0 4px}} .sub{{color:#888;font-size:13px;margin-bottom:14px}}
.bar{{position:sticky;top:0;background:#f7f8fa;padding:8px 0;z-index:5;display:flex;gap:6px;flex-wrap:wrap;align-items:center}}
button{{border:1px solid #ccc;background:#fff;border-radius:14px;padding:4px 12px;font-size:12px;cursor:pointer}}
button.on{{background:#222;color:#fff;border-color:#222}}
.grid{{display:flex;flex-wrap:wrap;gap:10px;margin-top:10px}}
.card{{width:120px;border:1px solid #e3e6ea;border-radius:10px;overflow:hidden;background:#fff;text-decoration:none;color:inherit;display:block}}
.card img{{width:120px;height:120px;object-fit:cover;display:block;background:#eee}}
.card img:hover{{outline:2px solid #222}}
.meta{{font-size:10px;padding:4px 6px;color:#666;line-height:1.4}}
.tag{{display:inline-block;background:#eef1f5;border-radius:8px;padding:1px 5px;margin-top:2px;font-size:9px;color:#555}}
</style></head><body>
<h1>{name} · 照片画廊</h1>
<div class="sub">{total} 张照片 · 缩略图为 AI 人脸裁剪(112×112) · 点图开原图</div>
<div class="bar">
  <button class="on" onclick="filter('__ALL__')">全部</button>
  {btns}
</div>
<div class="grid" id="grid">{''.join(cards)}</div>
<script>
function filter(s){{
  document.querySelectorAll('.bar button').forEach(b=>b.classList.remove('on'));
  event.target.classList.add('on');
  document.querySelectorAll('.card').forEach(c=>{{
    c.style.display = (s==='__ALL__'||c.dataset.src===s)?'':'none';
  }});
}}
</script>
</body></html>"""
    out = os.path.join(PERSON_DIR, f"{name}.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out


def main():
    for name in ["皓祥", "运丰"]:
        p = build(name)
        if p:
            print(f"画廊已生成: {p}")


if __name__ == "__main__":
    main()
