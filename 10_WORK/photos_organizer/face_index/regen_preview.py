# -*- coding: utf-8 -*-
"""用已更新的 index.csv + _detect.json 反查缩略图键，重生成 index.html。
不动任何磁盘文件，仅重建预览页，使其与最终文件夹结构一致。"""
import csv, os, json
from collections import defaultdict

TARGET = r"E:\待整理照片\皓祥"
PV = os.path.join(TARGET, "_preview")
INDEX = os.path.join(PV, "index.csv")
DETECT = os.path.join(PV, "_detect.json")
OUT = os.path.join(PV, "index.html")

# 1) 反查 文件名 -> 缩略图扫描序 i
dets = json.load(open(DETECT, encoding="utf-8"))
name2i = {}
for i, d in enumerate(dets):
    name2i[os.path.basename(d["path"])] = i

# 2) 读已更新的 index.csv
rows_raw = list(csv.DictReader(open(INDEX, encoding="utf-8-sig")))
rows = []
missing_thumb = []
for r in rows_raw:
    name = os.path.basename(r["绝对路径"].strip())
    i = name2i.get(name)
    if i is None:
        missing_thumb.append(name)
        thumb = ""
    else:
        thumb = f"thumbs/{i:04d}.jpg"
    rows.append({
        "year": r["年份"].strip(),
        "orig_year": r["原文件夹年份"].strip(),
        "changed": r["是否变更"].strip().lower() == "true",
        "conf": r["置信"].strip(),
        "sim": r["相似度"].strip(),
        "no_face": r["无脸"].strip().lower() == "true",
        "thumb": thumb,
        "abs": r["绝对路径"].strip(),
    })

# 3) 重建 HTML（复用 reindex 样式）
c = {"high": "#1a7f37", "low": "#bc4c00", "n/a": "#6e7781"}
esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
by_year = defaultdict(list)
for r in rows:
    by_year[r["year"]].append(r)
parts = ["""<!doctype html><html lang=zh><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>皓祥 文件夹索引（按外观重分类 · 已应用人工回交）</title>
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
.chg{color:#cf222e;font-weight:600}
</style></head><body>"""]
parts.append(f"""<header><h1>皓祥 文件夹索引（重头开始 · 按外观推断年份 · 已应用人工回交）</h1>
<div class=sum>
<span>总照片 <b>{len(rows)}</b></span>
<span>年份文件夹 <b>{len(by_year)}</b>（2004–2026）</span>
<span>变更 <b>{sum(1 for r in rows if r['changed'])}</b></span>
<span>低置信 <b>{sum(1 for r in rows if r['conf']=='low')}</b></span>
<span>无脸 <b>{sum(1 for r in rows if r['no_face'])}</b></span>
</div>
<div class=sum style="color:#57606a">缩略图均为皓祥面部裁剪 · 红字=年份较原文件夹变更 · 点缩略图开原图 · 已按 decisions 回交修正</div>
</header>""")
for y in sorted(by_year):
    items = by_year[y]
    parts.append(f"<div class=year><h2>{y} （{len(items)}）</h2><div class=grid>")
    for r in items:
        col = c.get(r["conf"], "#6e7781")
        absp = r["abs"].replace("\\", "/")
        chg = f"<span class=chg>原{r['orig_year']}→</span>" if r["changed"] else ""
        nf = " ⚠无脸" if r["no_face"] else ""
        imgsrc = r["thumb"] if r["thumb"] else "data:,"  # 无缩略图则空白
        parts.append(
            f"<a class=card href='file:///{absp}'>"
            f"<img loading=lazy src='{imgsrc}'>"
            f"<div class=cap><div class=nm>{esc(os.path.basename(r['abs']))}</div>"
            f"{chg}<span class=badge style='background:{col}'>{esc(r['year'])}</span> "
            f"<span class=sim>{r['conf']} {r['sim']}{nf}</span></div></a>")
    parts.append("</div></div>")
parts.append("</body></html>")
open(OUT, "w", encoding="utf-8").write("\n".join(parts))
print(f"已重生成 {OUT}")
print(f"  卡片数: {len(rows)} | 年份组: {len(by_year)} | 缺缩略图: {len(missing_thumb)}")
if missing_thumb:
    print("  缺缩略图文件:", missing_thumb)
