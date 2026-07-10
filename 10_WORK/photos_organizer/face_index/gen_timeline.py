# -*- coding: utf-8 -*-
"""
gen_timeline.py — 根据照片索引生成「可编辑人生大事记时间线」HTML
===============================================================
读取 _preview/index.csv（年份 / 缩略图 / 原图相对链接 / 标记），
按年份聚合，生成 timeline.html：
  · 竖直时间轴，每个年份一个节点
  · 节点内：年份大标题 + 照片数/标记分布 + 「添加事件」+ 多个事件卡片
            （每卡：标题 + 描述 + 已关联照片缩略图，可移除）
  · 当年照片墙带勾选框，「关联到事件」下拉把勾选照片挂到指定事件
  · 编辑内容自动存浏览器 localStorage；支持「导出大事记」/「导入」JSON 持久化
  · 缩略图/原图全相对路径，整包复制可移植

数据模型（localStorage / 导出 JSON）：
  events = { "<year>": [ {"id","title","desc","photos":[filename,...]}, ... ] }
  照片可出现在多个事件下；filename 为当年照片 basename，渲染时从索引取缩略图/原图。

用法:
  <venv-python> gen_timeline.py --person 运丰
  <venv-python> gen_timeline.py --target "E:\待整理照片\运丰"
"""
import os, csv, json, argparse
from collections import defaultdict

BASE = r"E:\待整理照片"

FLAG_CN = {"ok": "本人", "low": "疑似非本人", "none": "无人脸/非主脸"}


def build_data(target):
    pv = os.path.join(target, "_preview")
    csv_path = os.path.join(pv, "index.csv")
    if not os.path.exists(csv_path):
        raise SystemExit(f"[错误] 找不到 {csv_path}，请先跑「重建索引」。")
    groups = defaultdict(list)
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            y = r["年份"]
            groups[y].append({
                "n": os.path.basename(r["相对路径"]),
                "t": r["缩略图"],          # 相对 _preview，如 thumbs/0000.jpg
                "o": r["原图相对链接"],     # 相对 _preview，如 ../2011/xxx.jpg
                "s": r["相似度"],
                "f": r["标记"],
            })
    years = sorted(groups.keys(), key=lambda x: int(x) if x.isdigit() else 9999)
    data = []
    for y in years:
        photos = groups[y]
        dist = {k: sum(1 for p in photos if p["f"] == k) for k in FLAG_CN}
        data.append({"year": y, "count": len(photos), "dist": dist, "photos": photos})
    return data


def gen_html(person, data, out_path):
    payload = json.dumps(data, ensure_ascii=False)
    n_years = len(data)
    n_photos = sum(d["count"] for d in data)
    low_total = sum(d["dist"].get("low", 0) for d in data)
    none_total = sum(d["dist"].get("none", 0) for d in data)
    html = _TPL.replace("__PERSON__", person).replace("__NYEARS__", str(n_years))\
        .replace("__NPHOTOS__", str(n_photos)).replace("__LOW__", str(low_total))\
        .replace("__NONE__", str(none_total)).replace("__DATA__", payload)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


_TPL = r"""<!doctype html><html lang=zh><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>__PERSON__ · 人生大事记时间线</title>
<style>
*{box-sizing:border-box}
body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f6f8fa;color:#1f2328}
header{position:sticky;top:0;background:#fff;border-bottom:1px solid #d0d7de;padding:14px 20px;z-index:20}
h1{font-size:18px;margin:0 0 6px}
.sum{font-size:13px;color:#57606a;display:flex;gap:16px;flex-wrap:wrap}
.toolbar{margin-top:10px;display:flex;gap:8px;flex-wrap:wrap}
button{font-size:13px;padding:5px 12px;border:1px solid #d0d7de;border-radius:6px;background:#f6f8fa;cursor:pointer}
button.primary{background:#0969da;color:#fff;border-color:#0969da}
.tip{color:#57606a;font-size:12px;margin-top:6px}
.wrap{max-width:1080px;margin:24px auto;padding:0 18px;position:relative}
.axis{position:absolute;left:90px;top:0;bottom:0;width:3px;background:#d0d7de}
.node{position:relative;margin:0 0 30px 120px;padding-left:8px}
.yrtag{position:absolute;left:-120px;top:0;width:84px;text-align:right;font-size:22px;font-weight:700;color:#0969da}
.yrtag .cnt{display:block;font-size:12px;font-weight:400;color:#57606a;margin-top:2px}
.card{background:#fff;border:1px solid #d0d7de;border-radius:10px;padding:14px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.card:before{content:"";position:absolute;left:-33px;top:6px;width:14px;height:14px;border-radius:50%;background:#0969da;border:3px solid #fff;box-shadow:0 0 0 2px #0969da}
.dist{font-size:12px;color:#57606a;margin-bottom:8px}
.dist span{display:inline-block;margin-right:10px}
.addEv{margin:4px 0 10px;background:#0969da;color:#fff;border-color:#0969da}
.evlist{display:flex;flex-direction:column;gap:10px;margin-bottom:10px}
.evcard{border:1px solid #d0d7de;border-radius:8px;padding:10px;background:#fafbfc;position:relative}
.evtitle{width:100%;font-size:14px;font-weight:600;border:1px solid #d0d7de;border-radius:6px;padding:5px 8px;margin-bottom:6px}
.evdesc{width:100%;min-height:46px;border:1px solid #d0d7de;border-radius:6px;padding:5px 8px;font-family:inherit;font-size:13px;resize:vertical}
.evphotos{display:flex;flex-wrap:wrap;gap:5px;margin-top:6px}
.ep{position:relative;width:62px;height:62px}
.ep img{width:62px;height:62px;object-fit:cover;border-radius:6px;cursor:zoom-in;display:block;background:#eee}
.epx{position:absolute;top:-6px;right:-6px;width:18px;height:18px;background:#cf222e;color:#fff;border-radius:50%;text-align:center;line-height:18px;font-size:12px;cursor:pointer}
.evph{color:#9aa0a6;font-size:12px}
.evdel{margin-top:6px;font-size:12px;padding:3px 9px;color:#cf222e;border-color:#cf222e;background:#fff}
.linkbar{display:flex;gap:8px;align-items:center;margin:4px 0 8px;flex-wrap:wrap}
.linkbar select{padding:4px 6px;border:1px solid #d0d7de;border-radius:6px;max-width:240px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px;margin-top:6px}
.wcell{position:relative}
.wcell img{width:100%;height:120px;object-fit:cover;border-radius:6px;background:#eee;cursor:zoom-in;display:block}
.wchk{position:absolute;top:4px;left:4px;width:18px;height:18px;accent-color:#0969da;cursor:pointer;z-index:2}
#lb{position:fixed;inset:0;background:rgba(0,0,0,.88);z-index:100;display:none;align-items:center;justify-content:center;flex-direction:column}
#lb.on{display:flex}
#lb img{max-width:94vw;max-height:86vh;object-fit:contain;box-shadow:0 4px 30px rgba(0,0,0,.6)}
#lb .lbcap{color:#fff;font-size:13px;margin-top:10px;text-align:center;word-break:break-all;max-width:90vw}
#lb .lbx{position:absolute;top:14px;right:20px;color:#fff;font-size:30px;cursor:pointer;line-height:1}
#lb .lberr{color:#ff9;font-size:13px;margin-top:8px}
</style></head><body>
<header>
<h1>__PERSON__ · 人生大事记时间线</h1>
<div class=sum>
<span>年份 <b>__NYEARS__</b></span>
<span>照片 <b>__NPHOTOS__</b></span>
<span style="color:#bc4c00">疑似非本人 <b>__LOW__</b></span>
<span style="color:#cf222e">无人脸 <b>__NONE__</b></span>
</div>
<div class=toolbar>
<button class=primary onclick="exportEvents()">导出大事记(JSON)</button>
<button onclick="importEvents()">导入</button>
<button onclick="clearAll()">清空编辑</button>
<input id=file type=file accept=.json style="display:none" onchange="loadFile(this)">
</div>
<div class=tip>每一年可添加多个「事件」（标题+描述），从下方照片墙勾选后「关联到事件」；同一张照片可挂多个事件。编辑自动存本浏览器，导出 JSON 可携带。缩略图点开看原图（须整包复制）。</div>
</header>
<div class=wrap>
<div class=axis></div>
<div id=timeline></div>
</div>
<div id=lb onclick="if(event.target.id==='lb')closeLB()">
<span class=lbx onclick="closeLB()">×</span>
<img id=lbimg src="" alt="">
<div class=lbcap id=lbcap></div>
</div>
<script>
const DATA = __DATA__;
const PERSON = "__PERSON__";
const LS_KEY = "timeline_events_v2_" + PERSON;
let events = {};
try { events = JSON.parse(localStorage.getItem(LS_KEY) || "{}"); } catch(e){ events = {}; }
const PMAP = {};
DATA.forEach(d=>{ PMAP[d.year]={}; d.photos.forEach(p=>PMAP[d.year][p.n]=p); });

function uid(){ return Date.now().toString(36)+Math.random().toString(36).slice(2,6); }
function save(){ localStorage.setItem(LS_KEY, JSON.stringify(events)); }
function escAttr(s){ return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function escHtml(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function evsOf(year){ return events[year]||(events[year]=[]); }

function distHTML(d){
  const parts=[];
  for(const k in d){ if(d[k]>0) parts.push(`<span style="color:${k==='ok'?'#1a7f37':k==='low'?'#bc4c00':'#cf222e'}">${k==='ok'?'本人':k==='low'?'疑似':'无脸'} ${d[k]}</span>`); }
  return parts.join("");
}
function render(){
  const tl=document.getElementById('timeline');
  tl.innerHTML = DATA.map(d=>{
    const evs = evsOf(d.year);
    const cards = evs.map(ev=>{
      const thumbs = (ev.photos||[]).map(n=>{
        const p=PMAP[d.year][n]; if(!p) return '';
        return `<div class=ep><img src="${p.t}" data-full="${p.o}" data-nm="${encodeURIComponent(n)}" onclick="openLB(this)">
          <span class=epx data-y="${d.year}" data-id="${ev.id}" data-n="${escAttr(n)}">×</span></div>`;
      }).join('');
      return `<div class=evcard data-id="${ev.id}">
        <input class=evtitle placeholder="事件标题，如：大学毕业 / 出国 / 婚礼" value="${escAttr(ev.title||'')}" oninput="upd('${d.year}','${ev.id}','title',this.value)">
        <textarea class=evdesc placeholder="事件描述…" oninput="upd('${d.year}','${ev.id}','desc',this.value)">${escHtml(ev.desc||'')}</textarea>
        <div class=evphotos>${thumbs||'<span class=evph>尚未关联照片（在下方勾选后关联）</span>'}</div>
        <button class=evdel onclick="delEv('${d.year}','${ev.id}')">删除事件</button>
      </div>`;
    }).join('');
    const opts = evs.length ? evs.map(ev=>`<option value="${ev.id}">${escHtml(ev.title||'(未命名事件)')}</option>`).join('')
                            : '<option value="">（先点「添加事件」）</option>';
    const wall = d.photos.map(p=>`<div class=wcell><input type=checkbox class=wchk data-n="${escAttr(p.n)}"><img loading=lazy src="${p.t}" data-full="${p.o}" data-nm="${encodeURIComponent(p.n)}" onclick="openLB(this)"></div>`).join('');
    return `<div class=node>
      <div class=yrtag>${d.year}<span class=cnt>${d.count} 张</span></div>
      <div class=card>
        <div class=dist>${distHTML(d.dist)}</div>
        <button class=addEv onclick="addEv('${d.year}')">+ 添加事件</button>
        <div class=evlist>${cards}</div>
        <div class=linkbar>
          <select id="sel_${d.year}">${opts}</select>
          <button onclick="linkSel('${d.year}')">把勾选照片关联到事件</button>
        </div>
        <div class=grid id="wall_${d.year}">${wall}</div>
      </div>
    </div>`;
  }).join('');
}
function addEv(year){ evsOf(year).push({id:uid(),title:'',desc:'',photos:[]}); save(); render(); }
function delEv(year,id){ events[year]=events[year].filter(e=>e.id!==id); save(); render(); }
function upd(year,id,field,val){ const ev=events[year].find(e=>e.id===id); if(ev){ ev[field]=val; save(); } }
function detach(y,id,n){ const ev=events[y].find(e=>e.id===id); if(ev){ ev.photos=(ev.photos||[]).filter(x=>x!==n); save(); render(); } }
function linkSel(year){
  const sel=document.getElementById('sel_'+year);
  const id=sel.value;
  if(!id){ alert('请先点「添加事件」并选择目标事件'); return; }
  const names=[...document.querySelectorAll('#wall_'+year+' .wchk:checked')].map(c=>c.dataset.n);
  if(!names.length){ alert('请先在照片墙勾选要关联的照片'); return; }
  const ev=events[year].find(e=>e.id===id);
  ev.photos=[...new Set([...(ev.photos||[]), ...names])];
  save(); render();
}
document.addEventListener('click',e=>{
  const x=e.target.closest('.epx');
  if(x) detach(x.dataset.y, x.dataset.id, x.dataset.n);
});
function openLB(img){
  const lb=document.getElementById('lb'), li=document.getElementById('lbimg'), lc=document.getElementById('lbcap');
  li.src=img.dataset.full;
  const nm=decodeURIComponent(img.dataset.nm);
  li.onerror=function(){ lc.innerHTML=nm+'<div class=lberr>原图未找到（须与年份文件夹整包一起打开）</div>'; };
  li.onload=function(){ lc.textContent=nm; };
  lb.classList.add('on');
}
function closeLB(){ document.getElementById('lb').classList.remove('on'); document.getElementById('lbimg').src=''; }
document.addEventListener('keydown',e=>{ if(e.key==='Escape')closeLB(); });
function exportEvents(){
  const out={person:PERSON, version:2, events:events, exported:new Date().toISOString().slice(0,10)};
  const blob=new Blob([JSON.stringify(out,null,2)],{type:'application/json'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob);
  a.download=PERSON+'_大事记.json'; a.click();
}
function importEvents(){ document.getElementById('file').click(); }
function loadFile(input){
  const f=input.files[0]; if(!f) return;
  const r=new FileReader();
  r.onload=function(){
    try{
      const obj=JSON.parse(r.result);
      events=obj.events||{};
      localStorage.setItem(LS_KEY, JSON.stringify(events));
      render();
      alert('已导入 '+Object.keys(events).length+' 个年份的事件');
    }catch(e){ alert('导入失败：'+e.message); }
  };
  r.readAsText(f);
}
function clearAll(){
  if(!confirm('确定清空所有已填写的事件与关联？（仅清文本/关联，照片不变）')) return;
  events={}; localStorage.removeItem(LS_KEY); render();
}
render();
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser(description="生成可编辑人生大事记时间线")
    ap.add_argument("--person", help="人物名（默认 运丰）")
    ap.add_argument("--target", help="人物文件夹绝对路径（覆盖 --person）")
    args = ap.parse_args()
    if args.target:
        target = args.target
        person = os.path.basename(target.rstrip("\\/"))
    else:
        person = args.person or "运丰"
        target = os.path.join(BASE, person)
    if not os.path.isdir(target):
        raise SystemExit(f"[错误] 目录不存在: {target}")
    data = build_data(target)
    out = os.path.join(target, "_preview", "timeline.html")
    gen_html(person, data, out)
    print(f"已生成时间线: {out}")
    print(f"  年份 {len(data)} | 照片 {sum(d['count'] for d in data)}")
    print(f"  事件卡片模式：每年来源可加多个事件并关联照片；编辑自动存浏览器 localStorage；可导出/导入 JSON。")


if __name__ == "__main__":
    main()
