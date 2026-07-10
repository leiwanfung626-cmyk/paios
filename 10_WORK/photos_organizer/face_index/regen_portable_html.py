# -*- coding: utf-8 -*-
"""
regen_portable_html.py — 把 index.html 改成「完全可移植」
====================================================
读取已生成的 _detect.json（不重检测），重建 index.html：
  - 缩略图：相对路径 thumbs/{i:04d}.jpg
  - 点开原图：相对路径 ../{年份}/{文件}（HTML 在 _preview/ 下，上跳一级）
  -> 整个 皓祥 文件夹复制/移动到任意位置或别的电脑，预览页都能正常打开+点击。

同时把 index.csv 的「绝对路径」列改为「相对路径」，便于跨机使用。
"""
import os, re, json, csv, datetime
from collections import defaultdict
from urllib.parse import quote

TARGET = r"E:\待整理照片\皓祥"
PV = os.path.join(TARGET, "_preview")
DETECT_JSON = os.path.join(PV, "_detect.json")
SIM_NO_FACE = 0.20
SIM_LOW = 0.35
BORN = (2004, 9, 11)

def current_year_of(path):
    rel = os.path.relpath(path, TARGET)
    m = re.match(r'(\d{4})', rel.split(os.sep)[0])
    return int(m.group(1)) if m else BORN[0]

def main():
    dets = json.load(open(DETECT_JSON, encoding="utf-8"))
    rows = []
    for i, d in enumerate(dets):
        y = current_year_of(d["path"])
        rel = os.path.relpath(d["path"], TARGET).replace("\\", "/")
        sim = round(d.get("sim", 0.0), 3) if not d.get("no_face") else round(d.get("sim", 0.0), 3)
        if d.get("no_face"):
            flag = "none"
        elif sim < SIM_LOW:
            flag = "low"
        else:
            flag = "ok"
        rows.append({
            "i": i, "rel": rel, "year": y, "sim": sim, "flag": flag,
            "thumb": f"thumbs/{i:04d}.jpg",
            "orig_href": "../" + quote(rel),          # 相对原图（便携）
            "abs": d["path"],
        })

    # 重建 HTML
    by_year = defaultdict(list)
    for r in rows:
        by_year[r["year"]].append(r)
    flag_color = {"ok": "#1a7f37", "low": "#bc4c00", "none": "#cf222e"}
    esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    parts = ["""<!doctype html><html lang=zh><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>皓祥 文件夹索引（可移植版）</title>
<style>
body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f6f8fa;color:#1f2328}
header{position:sticky;top:0;background:#fff;border-bottom:1px solid #d0d7de;padding:12px 18px;z-index:10}
h1{font-size:18px;margin:0 0 6px}
.sum{font-size:13px;color:#57606a;display:flex;gap:14px;flex-wrap:wrap}
.year{margin:18px}
.year h2{font-size:15px;border-left:4px solid #0969da;padding-left:8px;margin-bottom:10px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}
.card{background:#fff;border:1px solid #d0d7de;border-radius:8px;overflow:hidden;text-decoration:none;color:inherit;display:block}
.card img{width:100%;height:200px;object-fit:cover;display:block;background:#eee}
.cap{padding:6px 8px;font-size:11px;line-height:1.35}
.cap .nm{font-weight:600;word-break:break-all}
.badge{display:inline-block;margin-top:3px;padding:1px 7px;border-radius:10px;color:#fff;font-size:11px}
</style></head><body>"""]
    n_ok = sum(1 for r in rows if r["flag"] == "ok")
    n_low = sum(1 for r in rows if r["flag"] == "low")
    n_none = sum(1 for r in rows if r["flag"] == "none")
    parts.append(f"""<header><h1>皓祥 文件夹索引（手动调整后重建 · 可移植版）</h1>
<div class=sum>
<span>总照片 <b>{len(rows)}</b></span>
<span>年份文件夹 <b>{len(by_year)}</b></span>
<span style="color:#1a7f37">皓祥本人 <b>{n_ok}</b></span>
<span style="color:#bc4c00">疑似非本人 <b>{n_low}</b></span>
<span style="color:#cf222e">无人脸/非主脸 <b>{n_none}</b></span>
<span>生成 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
</div>
<div class=sum style="color:#57606a">年份=当前物理文件夹 · 缩略图=皓祥面部裁剪 · 全部相对路径，复制/移动到任意位置均可打开 · 点缩略图开原图</div>
</header>""")
    for y in sorted(by_year):
        items = by_year[y]
        parts.append(f"<div class=year><h2>{y} （{len(items)}）</h2><div class=grid>")
        for r in items:
            col = flag_color.get(r["flag"], "#6e7781")
            absp = r["abs"].replace("\\", "/")
            parts.append(
                f"<a class=card href='{r['orig_href']}'>"
                f"<img loading=lazy src='{r['thumb']}'>"
                f"<div class=cap><div class=nm>{esc(os.path.basename(r['abs']))}</div>"
                f"<span class=badge style='background:{col}'>{r['flag']} {r['sim']}</span></div></a>")
        parts.append("</div></div>")
    parts.append("</body></html>")
    open(os.path.join(PV, "index.html"), "w", encoding="utf-8").write("\n".join(parts))

    # 更新 index.csv：相对路径列（便携）
    with open(os.path.join(PV, "index.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["相对路径", "年份", "皓祥相似度", "标记", "缩略图", "原图相对链接"])
        for r in rows:
            w.writerow([r["rel"], r["year"], r["sim"], r["flag"], r["thumb"], r["orig_href"]])

    print(f"已生成可移植版 index.html（{len(rows)} 张，原图链接全部相对化）")
    print(f"  index.csv 也已改为相对路径")

if __name__ == "__main__":
    main()
