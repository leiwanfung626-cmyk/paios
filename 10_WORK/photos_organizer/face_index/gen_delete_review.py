# -*- coding: utf-8 -*-
"""
gen_delete_review.py — 生成「删除审查页」(覆盖全部 370 张)
========================================================
交互式 file:// 直开页面：每张照片带 ✗删除 开关，可按标记筛选，
点「导出删除清单」下载 delete_list.json = [{rel,abs,year,sim}]。
用户勾完把 json 发回，apply_delete.py 执行回收站删除 + 重建预览。
"""
import os, re, json, datetime
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
        sim = round(d.get("sim", 0.0), 3)
        if d.get("no_face"):
            flag = "none"
        elif sim < SIM_LOW:
            flag = "low"
        else:
            flag = "ok"
        rows.append({
            "i": i, "rel": rel, "abs": d["path"], "year": y,
            "sim": sim, "flag": flag, "thumb": f"thumbs/{i:04d}.jpg",
        })
    data_json = json.dumps(rows, ensure_ascii=False)

    esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = f"""<!doctype html><html lang=zh><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>皓祥 · 删除审查页（全部 370 张）</title>
<style>
*{{box-sizing:border-box}}
body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f6f8fa;color:#1f2328}}
header{{position:sticky;top:0;background:#fff;border-bottom:1px solid #d0d7de;padding:10px 16px;z-index:20}}
h1{{font-size:16px;margin:0 0 6px}}
.bar{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;font-size:13px}}
button{{font-size:13px;padding:5px 12px;border:1px solid #d0d7de;border-radius:6px;background:#f6f8fa;cursor:pointer}}
button.primary{{background:#cf222e;color:#fff;border-color:#cf222e}}
button:hover{{filter:brightness(.97)}}
.tip{{color:#57606a;font-size:12px;margin-top:4px}}
.main{{display:flex;min-height:calc(100vh - 90px)}}
#side{{width:170px;flex:none;padding:12px;border-right:1px solid #d0d7de;background:#fff;position:sticky;top:90px;height:calc(100vh - 90px);overflow:auto}}
#side label{{display:block;font-size:13px;margin:6px 0;cursor:pointer}}
#grid{{flex:1;padding:14px}}
.filters{{margin-bottom:10px;display:flex;gap:8px;flex-wrap:wrap}}
.filters button.on{{background:#0969da;color:#fff;border-color:#0969da}}
.year{{margin:10px 0 4px;font-size:14px;font-weight:600;border-left:4px solid #0969da;padding-left:8px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px}}
.card{{position:relative;background:#fff;border:1px solid #d0d7de;border-radius:8px;overflow:hidden}}
.card img{{width:100%;height:170px;object-fit:cover;display:block;background:#eee}}
.card.del{{outline:3px solid #cf222e}}
.cap{{padding:5px 7px;font-size:11px;line-height:1.3}}
.cap .nm{{font-weight:600;word-break:break-all}}
.chk{{position:absolute;top:6px;right:6px;width:22px;height:22px;cursor:pointer;accent-color:#cf222e}}
.pill{{display:inline-block;padding:1px 7px;border-radius:10px;color:#fff;font-size:11px}}
</style></head><body>
<header>
<h1>皓祥 · 删除审查页（全部 {len(rows)} 张）</h1>
<div class=bar>
<button class=primary onclick="exportList()">导出删除清单（<span id=selcnt>0</span>）</button>
<button onclick="selectAll()">全选当前筛选</button>
<button onclick="clearSel()">清空选择</button>
<span class=tip>勾选混进来的照片 → 导出 delete_list.json 发回即可。删除走回收站，可回收。</span>
</div>
</header>
<div class=main>
<div id=side>
<b>筛选</b>
<label><input type=radio name=f value=all checked onchange="applyFilter()"> 全部 {len(rows)}</label>
<label><input type=radio name=f value=low onchange="applyFilter()"> 疑似非本人 ({sum(1 for r in rows if r['flag']=='low')})</label>
<label><input type=radio name=f value=none onchange="applyFilter()"> 无人脸/非主脸 ({sum(1 for r in rows if r['flag']=='none')})</label>
<label><input type=radio name=f value=ok onchange="applyFilter()"> 皓祥本人({sum(1 for r in rows if r['flag']=='ok')})</label>
<hr>
<b>搜索文件名</b>
<input id=search placeholder="含关键词…" oninput="applyFilter()" style="width:100%;padding:4px;margin-top:4px">
</div>
<div id=grid>
<div class=filters></div>
<div id=list></div>
</div>
</div>
<script>
const DATA = {data_json};
const flagColor = {{ok:'#1a7f37', low:'#bc4c00', none:'#cf222e'}};
const flagText = {{ok:'皓祥', low:'疑似非本人', none:'无人脸'}};
function esc(s){{return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}}
function cardHTML(r){{
  return `<div class=card data-flag="${{r.flag}}" data-nm="${{esc(r.rel.toLowerCase())}}">
    <input class=chk type=checkbox onchange="onChk(this)" data-abs="${{esc(r.abs)}}" data-rel="${{esc(r.rel)}}" data-year="${{r.year}}" data-sim="${{r.sim}}">
    <img loading=lazy src="${{r.thumb}}">
    <div class=cap><div class=nm>${{esc(r.rel.split('/').pop())}}</div>
    <span class=pill style="background:${{flagColor[r.flag]}}">${{flagText[r.flag]}} ${{r.sim}}</span>
    <div style="color:#57606a">${{r.year}}</div></div></div>`;
}}
function render(){{
  const f = document.querySelector('input[name=f]:checked').value;
  const q = document.getElementById('search').value.toLowerCase();
  const byYear = {{}};
  DATA.forEach(r=>{{
    if(f!=='all' && r.flag!==f) return;
    if(q && !r.rel.toLowerCase().includes(q)) return;
    (byYear[r.year] = byYear[r.year]||[]).push(r);
  }});
  let html='';
  Object.keys(byYear).sort().forEach(y=>{{
    html += `<div class=year>${{y}} （${{byYear[y].length}}）</div><div class=cards>`;
    html += byYear[y].map(cardHTML).join('');
    html += `</div>`;
  }});
  document.getElementById('list').innerHTML = html;
  // 恢复已勾选状态
  document.querySelectorAll('.chk').forEach(c=>{{
    if(checked.has(c.dataset.abs)) c.checked=true;
  }});
  syncCnt();
}}
const checked = new Set();
function onChk(c){{ if(c.checked) checked.add(c.dataset.abs); else checked.delete(c.dataset.abs); syncCnt(); }}
function syncCnt(){{ document.getElementById('selcnt').textContent = checked.size; }}
function selectAll(){{ document.querySelectorAll('.chk').forEach(c=>{{c.checked=true; checked.add(c.dataset.abs);}}); syncCnt(); }}
function clearSel(){{ checked.clear(); document.querySelectorAll('.chk').forEach(c=>c.checked=false); syncCnt(); }}
function applyFilter(){{ render(); }}
function exportList(){{
  if(checked.size===0){{ alert('还没勾选任何照片'); return; }}
  const arr = DATA.filter(r=>checked.has(r.abs)).map(r=>({{rel:r.rel, abs:r.abs, year:r.year, sim:r.sim}}));
  const blob = new Blob([JSON.stringify(arr,null,2)], {{type:'application/json'}});
  const a = document.createElement('a'); a.href=URL.createObjectURL(blob);
  a.download='delete_list.json'; a.click();
  alert('已导出 '+arr.length+' 张待删除清单，发回给我执行回收站删除。');
}}
render();
</script>
</body></html>"""
    out = os.path.join(PV, "delete_review.html")
    open(out, "w", encoding="utf-8").write(html)
    print(f"已生成删除审查页: {out}（{len(rows)} 张，可按标记/搜索筛选）")

if __name__ == "__main__":
    main()
