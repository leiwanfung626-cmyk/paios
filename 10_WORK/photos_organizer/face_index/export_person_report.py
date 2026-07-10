#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_person_report.py — 按人物导出照片清单 + 时间线 (Phase 2 产出)
读取 face_index.db (faces.person_id) 关联 photo_index.db (photos.date/camera/source/category)
产出:
  export/persons/<name>.csv        —— 该人物全部照片(按日期升序): 路径/日期/年份/检测年龄/性别/相机/来源/分类
  export/timeline.html             —— 交互式时间线: 逐年柱状图(各人物计数)+ 每年缩略图样本 + 年×人矩阵表
依赖: 无第三方库(纯 sqlite3 + stdlib)，file:// 直开。
"""
import os
import sqlite3
import csv
import json
from collections import defaultdict, Counter
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
FACE_DB = os.path.join(HERE, "face_index.db")
PHOTO_DB = os.path.join(HERE, "..", "database", "photo_index.db")
FACES_DIR = os.path.join(HERE, "faces")
OUT = os.path.join(HERE, "export")
PERSON_DIR = os.path.join(OUT, "persons")
os.makedirs(PERSON_DIR, exist_ok=True)


def fetch():
    fc = sqlite3.connect(FACE_DB)
    pc = sqlite3.connect(PHOTO_DB)
    persons = fc.execute("SELECT id,name FROM persons WHERE id>0 ORDER BY id").fetchall()
    data = {}
    for pid, name in persons:
        rows = fc.execute(
            "SELECT path,photo_id,face_idx,age,gender,det_score "
            "FROM faces WHERE person_id=?", (pid,)).fetchall()
        recs = []
        for path, photo_id, face_idx, age, gender, det in rows:
            d = pc.execute(
                "SELECT date,camera,source,primary_category FROM photos WHERE path=?",
                (path,)).fetchone()
            date = d[0] if d else None
            recs.append(dict(
                path=path, photo_id=photo_id, face_idx=face_idx,
                date=date, year=(date[:4] if date else "未知"),
                age=age, gender=gender, det=det,
                camera=(d[1] if d else None), source=(d[2] if d else None),
                category=(d[3] if d else None),
                thumb=f"{photo_id}_{face_idx}.jpg"))
        recs.sort(key=lambda r: (r["date"] or "9999-99-99"))
        data[name] = recs
    fc.close(); pc.close()
    return data


def write_csv(data):
    paths = {}
    for name, recs in data.items():
        p = os.path.join(PERSON_DIR, f"{name}.csv")
        with open(p, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["序号", "日期", "年份", "检测年龄", "性别", "置信度",
                        "相机", "来源", "分类", "原图路径", "人脸缩略图"])
            for i, r in enumerate(recs, 1):
                w.writerow([i, r["date"], r["year"], r["age"], r["gender"],
                            f"{r['det']:.3f}" if r["det"] else "",
                            r["camera"], r["source"], r["category"],
                            r["path"], r["thumb"]])
        paths[name] = p
    return paths


def build_timeline(data):
    # 年份范围
    years = set()
    for recs in data.values():
        for r in recs:
            if r["year"] != "未知":
                years.add(int(r["year"]))
    ymin, ymax = (min(years), max(years)) if years else (0, 0)
    yrange = list(range(ymin, ymax + 1))

    # 每年每人计数 + 样本缩略图
    year_count = {name: Counter() for name in data}
    year_samples = {name: defaultdict(list) for name in data}
    for name, recs in data.items():
        for r in recs:
            y = r["year"]
            year_count[name][y] += 1
            if len(year_samples[name][y]) < 12:
                year_samples[name][y].append(r)

    names = list(data.keys())
    colors = {"皓祥": "#2563eb", "运丰": "#dc2626"}
    def color(n): return colors.get(n, "#16a34a")

    # ---- SVG 柱状图 ----
    W, H = 980, 380
    pad_l, pad_b = 50, 40
    plot_w = W - pad_l - 20
    plot_h = H - pad_b - 20
    maxv = max((year_count[n].get(str(y), 0) for n in names for y in yrange), default=1) or 1
    maxv = max(maxv, 1)
    bw = plot_w / max(len(yrange), 1)
    group_w = bw * 0.7
    bar_w = group_w / max(len(names), 1)
    svg = [f'<svg viewBox="0 0 {W} {H}" class="chart">']
    # y 轴网格
    for g in range(0, 6):
        val = int(maxv * g / 5)
        y = 20 + plot_h - (val / maxv) * plot_h
        svg.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{W-20}" y2="{y:.1f}" stroke="#eee"/>')
        svg.append(f'<text x="{pad_l-6}" y="{y+4:.1f}" class="ax">{val}</text>')
    for i, y in enumerate(yrange):
        x0 = pad_l + i * bw + (bw - group_w) / 2
        for j, n in enumerate(names):
            v = year_count[n].get(str(y), 0)
            if v == 0:
                continue
            bh = (v / maxv) * plot_h
            bx = x0 + j * bar_w
            by = 20 + plot_h - bh
            svg.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w-1:.1f}" height="{bh:.1f}" '
                       f'fill="{color(n)}"><title>{y} {n}: {v}</title></rect>')
        # x 标签（每 2~3 年标一次，避免拥挤）
        if len(yrange) <= 30 or i % 2 == 0:
            cx = pad_l + i * bw + bw / 2
            svg.append(f'<text x="{cx:.1f}" y="{H-pad_b+18}" class="ax" text-anchor="middle">{y}</text>')
    svg.append(f'<line x1="{pad_l}" y1="20" x2="{pad_l}" y2="{20+plot_h}" stroke="#ccc"/>')
    svg.append(f'<line x1="{pad_l}" y1="{20+plot_h}" x2="{W-20}" y2="{20+plot_h}" stroke="#ccc"/>')
    svg.append('</svg>')

    # ---- 每年详情(缩略图) ----
    year_blocks = []
    for y in yrange:
        block = [f'<div class="yr"><h3>{y} 年</h3>']
        any_data = False
        for n in names:
            cnt = year_count[n].get(str(y), 0)
            if cnt == 0:
                continue
            any_data = True
            block.append(f'<div class="psn"><span class="tag" style="background:{color(n)}">{n} · {cnt} 张</span>')
            block.append('<div class="thumbs">')
            for r in year_samples[n][str(y)]:
                tp = os.path.join(FACES_DIR, r["thumb"])
                if os.path.exists(tp):
                    src = f"../faces/{r['thumb']}"
                    orig = "file:///" + quote(r["path"].replace("\\", "/"))
                    block.append(f'<a href="{orig}" target="_blank" title="{r["date"]} {r["age"]}岁/{r["gender"]}">'
                                 f'<img src="{src}"/></a>')
            block.append('</div></div>')
        block.append('</div>')
        if any_data:
            year_blocks.append("".join(block))

    # ---- 年×人 矩阵表 ----
    table = ['<table class="mtx"><tr><th>年份</th>']
    for n in names:
        table.append(f'<th style="color:{color(n)}">{n}</th>')
    table.append('<th>合计</th></tr>')
    for y in yrange:
        row = [f'<tr><td>{y}</td>']
        tot = 0
        for n in names:
            v = year_count[n].get(str(y), 0)
            tot += v
            row.append(f'<td>{v}</td>')
        row.append(f'<td><b>{tot}</b></td></tr>')
        table.append("".join(row))
    table.append('</table>')

    # ---- 汇总卡片 ----
    cards = []
    for n in names:
        recs = data[n]
        yrs = [int(r["year"]) for r in recs if r["year"] != "未知"]
        first = min(yrs) if yrs else "—"
        last = max(yrs) if yrs else "—"
        ages = [r["age"] for r in recs if r["age"]]
        age_span = f"{min(ages)}–{max(ages)} 岁" if ages else "—"
        cards.append(f'''<div class="card" style="border-top:4px solid {color(n)}">
            <div class="cname">{n}</div>
            <div class="cnum">{len(recs)}</div><div class="clbl">张照片</div>
            <div class="cmeta">出现年份：{first}–{last}<br/>检测年龄跨度：{age_span}</div>
        </div>''')

    legend = "".join(f'<span class="lg"><i style="background:{color(n)}"></i>{n}</span>' for n in names)

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>人物时间线</title><style>
body{{font-family:system-ui,'Microsoft YaHei',sans-serif;background:#f7f8fa;color:#222;margin:0;padding:24px}}
h1{{font-size:22px;margin:0 0 4px}} .sub{{color:#888;font-size:13px;margin-bottom:20px}}
.legend{{margin:6px 0 18px}} .lg{{margin-right:16px;font-size:13px}} .lg i{{display:inline-block;width:12px;height:12px;border-radius:2px;margin-right:5px;vertical-align:-1px}}
.cards{{display:flex;gap:16px;margin-bottom:24px}} .card{{background:#fff;border-radius:12px;padding:16px 20px;min-width:180px;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
.cname{{font-size:15px;font-weight:600}} .cnum{{font-size:34px;font-weight:700;line-height:1.1}} .clbl{{color:#888;font-size:12px}} .cmeta{{margin-top:8px;font-size:12px;color:#666;line-height:1.6}}
.chart{{background:#fff;border-radius:12px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,.08);max-width:100%}} .ax{{font-size:11px;fill:#999}}
.yr{{background:#fff;border-radius:12px;padding:14px 18px;margin-bottom:14px;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
.yr h3{{margin:0 0 10px;font-size:15px}} .psn{{margin-bottom:10px}} .tag{{display:inline-block;color:#fff;font-size:12px;padding:2px 8px;border-radius:10px;margin-bottom:6px}}
.thumbs{{display:flex;flex-wrap:wrap;gap:6px}} .thumbs a{{display:block}} .thumbs img{{width:64px;height:64px;object-fit:cover;border-radius:6px;display:block}}
.thumbs img:hover{{outline:2px solid #333}}
.mtx{{border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08);font-size:13px}}
.mtx th,.mtx td{{padding:6px 12px;border-bottom:1px solid #eee;text-align:center}} .mtx th{{background:#f0f2f5}} .mtx td:first-child{{font-weight:600}}
</style></head><body>
<h1>家庭照片 · 人物时间线</h1>
<div class="sub">基于 {sum(len(v) for v in data.values())} 张已确认人物照片 · 数据源 face_index.db × photo_index.db</div>
<div class="legend">{legend}</div>
<div class="cards">{''.join(cards)}</div>
<h2 style="font-size:16px">逐年出现次数</h2>
{''.join(svg)}
<h2 style="font-size:16px;margin-top:28px">逐年照片明细（最多每年每人数 12 张样本）</h2>
{''.join(year_blocks)}
<h2 style="font-size:16px;margin-top:28px">年 × 人 矩阵</h2>
{''.join(table)}
</body></html>"""
    out = os.path.join(OUT, "timeline.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out


def main():
    data = fetch()
    csv_paths = write_csv(data)
    tl = build_timeline(data)
    print("=== 按人物照片清单 ===")
    for n, p in csv_paths.items():
        print(f"  {n}: {len(data[n])} 张 -> {p}")
    print(f"\n时间线: {tl}")
    print(f"缩略图目录: {FACES_DIR}")


if __name__ == "__main__":
    main()
