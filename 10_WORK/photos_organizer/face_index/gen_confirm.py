# -*- coding: utf-8 -*-
"""生成皓祥文件夹的「人工确认页」：只列需人眼把关的 23 张（大跨度变更 + 无脸）。
交互：点 ✅/❌ → 导出 decisions.json，回交给 AI 收口。
纯静态 HTML，file:// 直开。
"""
import csv, os, json

TARGET = r"E:\待整理照片\皓祥"
PV = os.path.join(TARGET, "_preview")
CSV = os.path.join(PV, "review.csv")
TH = "thumbs"

def span(r):
    try: return abs(int(r["推断年份"]) - int(r["原年份"]))
    except: return -1
def isnoface(r): return r["无脸"].strip().lower() == "true"

rows = list(csv.DictReader(open(CSV, encoding="utf-8-sig")))
# review.csv 与检测同序 → 行 i 对应 thumbs/{i:04d}.jpg
items = []
for i, r in enumerate(rows):
    if isnoface(r):
        kind = "无脸"
    elif span(r) >= 3:
        kind = "大跨度"
    else:
        continue  # 小跨度低风险，不列入
    items.append({
        "i": i,
        "file": r["文件"],
        "orig": r["原年份"],
        "infer": r["推断年份"],
        "sim": r["相似度"],
        "conf": r["置信"],
        "kind": kind,
        "abs": r["绝对路径"],
        "thumb": f"{TH}/{i:04d}.jpg",
    })

big = [x for x in items if x["kind"] == "大跨度"]
nof = [x for x in items if x["kind"] == "无脸"]
# 大跨度里相似度<0.5的标为高风险
for x in big:
    try: x["risk"] = "high" if float(x["sim"]) < 0.5 else "ok"
    except: x["risk"] = "ok"

esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

cards = []
for x in items:
    if x["kind"] == "大跨度":
        q = f"年份 {esc(x['orig'])}→{esc(x['infer'])} 对吗？"
        btns = f'''<button onclick="dec({x['i']},'ok')">✅ 年份正确</button>
<button class="no" onclick="dec({x['i']},'bad')">❌ 不对</button>'''
        badge = f'<span class="b {"risk" if x["risk"]=="high" else "ok"}">{x["kind"]} {"⚠低置信" if x["risk"]=="high" else ""}</span>'
    else:
        q = "照片里确有皓祥吗？"
        btns = f'''<button onclick="dec({x['i']},'has')">✅ 含皓祥</button>
<button class="no" onclick="dec({x['i']},'nohas')">❌ 无皓祥</button>'''
        badge = f'<span class="b noface">无脸(非主脸)</span>'
    cards.append(f'''<div class="card" id="c{x['i']}">
  <img src="{x['thumb']}" loading=lazy>
  <div class="meta">
    <div class="nm">{esc(x['file'])}</div>
    {badge}
    <div class="yr">{esc(x['orig'])} → <b>{esc(x['infer'])}</b> <span class="sim">sim={esc(x['sim'])}</span></div>
    <div class="q">{q}</div>
    <div class="btns">{btns}</div>
    <div class="st" id="s{x['i']}"></div>
  </div></div>''')

html = f'''<!doctype html><html lang=zh><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>皓祥文件夹 人工确认</title>
<style>
body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f6f8fa;color:#1f2328}}
header{{position:sticky;top:0;background:#fff;border-bottom:1px solid #d0d7de;padding:12px 18px;z-index:10}}
h1{{font-size:17px;margin:0 0 4px}}
.sum{{font-size:13px;color:#57606a}}
.bar{{margin-top:8px;display:flex;gap:10px;flex-wrap:wrap}}
.bar button{{font-size:13px;padding:5px 12px;border:1px solid #d0d7de;border-radius:6px;background:#f6f8fa;cursor:pointer}}
.bar button.primary{{background:#1f883d;color:#fff;border-color:#1f883d}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px;padding:18px}}
.card{{background:#fff;border:1px solid #d0d7de;border-radius:10px;overflow:hidden}}
.card.done{{opacity:.45}}
.card img{{width:100%;height:200px;object-fit:cover;background:#eee;display:block}}
.meta{{padding:8px 10px}}
.nm{{font-weight:600;font-size:12px;word-break:break-all}}
.b{{display:inline-block;margin:4px 0;padding:1px 8px;border-radius:10px;color:#fff;font-size:11px}}
.b.risk{{background:#cf222e}} .b.ok{{background:#1a7f37}} .b.noface{{background:#6e7781}}
.yr{{font-size:12px;margin:3px 0}} .sim{{color:#57606a}}
.q{{font-size:12px;color:#57606a;margin:4px 0}}
.btns{{display:flex;gap:6px}} .btns button{{flex:1;font-size:12px;padding:5px;border-radius:6px;border:1px solid #d0d7de;background:#f6f8fa;cursor:pointer}}
.btns button.no{{background:#ffebe9;color:#cf222e}}
.st{{font-size:12px;margin-top:4px;min-height:16px;color:#1a7f37}}
</style></head><body>
<header>
<h1>皓祥文件夹 · 人工确认（{len(items)} 张需把关）</h1>
<div class=sum>大跨度变更 <b>{len(big)}</b>（⚠低置信 {sum(1 for x in big if x['risk']=='high')}）｜ 无脸 <b>{len(nof)}</b> ｜ 小跨度 {len(rows)-len(items)} 张已默认接受</div>
<div class=bar>
<button onclick="allOk()">全部标记为正确</button>
<button class="primary" onclick="exportJson()">导出 decisions.json</button>
<button onclick="copySummary()">复制文本摘要</button>
</div></header>
<div class=grid>
{''.join(cards)}
</div>
<script>
var D={{}};
function dec(i, v){{
  D[i]=v;
  var c=document.getElementById('c'+i), s=document.getElementById('s'+i);
  c.classList.add('done');
  s.textContent = (v==='ok'||v==='has') ? '✅ 已确认' : '❌ 已标记';
}}
function allOk(){{
  {''.join(f"dec({x['i']},'{('has' if x['kind']=='无脸' else 'ok')}');" for x in items)}
}}
function exportJson(){{
  var out=[];
  for(var k in D) out.push({{idx:+k, decision:D[k]}});
  var blob=new Blob([JSON.stringify(out,null,2)],{{type:'application/json'}});
  var a=document.createElement('a'); a.href=URL.createObjectURL(blob);
  a.download='haoxiang_decisions.json'; a.click();
}}
function copySummary(){{
  var lines=[];
  for(var k in D) lines.push('idx '+k+' -> '+D[k]);
  navigator.clipboard.writeText(lines.join('\\n')); alert('已复制 '+lines.length+' 条');
}}
</script></body></html>'''

out = os.path.join(PV, "confirm.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print(f"已生成确认页: {out}")
print(f"  含 {len(items)} 张 (大跨度 {len(big)} / 无脸 {len(nof)})")
print(f"  其中大跨度低置信(⚠): {sum(1 for x in big if x['risk']=='high')} 张")
