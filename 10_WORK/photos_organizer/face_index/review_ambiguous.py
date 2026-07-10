#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
review_ambiguous.py — 生成"重叠脸"双人指认页 (皓祥 vs 运丰)
读 AMBIGUOUS_皓祥_运丰_overlap.csv（retrieve 后由重叠分析产出），
生成交互式 HTML：每张脸显示对两人的双相似度，点「是皓祥/是运丰/都不是」，
导出 ambiguous_judgments.json，由 commit_ambiguous.py 回写。

用法：python review_ambiguous.py
"""
import os
import csv
import json

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "retrieval", "AMBIGUOUS_皓祥_运丰_overlap.csv")
OUT_HTML = os.path.join(HERE, "retrieval", "review_ambiguous.html")

TPL = r"""<!doctype html><html><head><meta charset="utf-8">
<title>重叠脸指认：皓祥 vs 运丰</title>
<style>
 body{font-family:system-ui;background:#fff;color:#222;margin:0;padding:16px}
 h1{font-size:18px}
 .bar{position:sticky;top:0;background:#fff;padding:10px 0;border-bottom:1px solid #eee;display:flex;gap:10px;flex-wrap:wrap;align-items:center;z-index:10}
 .grid{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}
 .cell{width:170px;border:1px solid #ddd;border-radius:8px;overflow:hidden;background:#fafafa}
 .cell img{width:170px;height:170px;object-fit:cover;display:block}
 .meta{font-size:11px;padding:4px 6px;color:#555}
 .btns{display:flex;gap:4px;padding:4px 6px}
 .btns button{flex:1;cursor:pointer;border:1px solid #ccc;background:#fff;border-radius:4px;font-size:11px;padding:4px 0}
 .btns button.on-h{background:#2e7d32;color:#fff;border-color:#2e7d32}
 .btns button.on-y{background:#1565c0;color:#fff;border-color:#1565c0}
 .btns button.on-n{background:#c62828;color:#fff;border-color:#c62828}
 .stats{font-size:13px;color:#333}
</style></head><body>
<h1>重叠脸指认：皓祥 vs 运丰（共 __COUNT__ 张，模型分不清，需你定）</h1>
<div class="bar">
  <span class="stats" id="stats"></span>
  <label>模型倾向：
    <select id="filt"><option value="all">全部</option><option value="皓祥">偏皓祥</option><option value="运丰">偏运丰</option></select>
  </label>
  <button onclick="clearAll()">清空</button>
  <button onclick="exportJSON()">导出 ambiguous_judgments.json</button>
</div>
<div class="grid" id="grid"></div>
<script>
const RESULTS=__DATA__;
const HAO="皓祥", YUN="运丰";
const assign={};
function render(){
  const f=document.getElementById('filt').value;
  const g=document.getElementById('grid'); g.innerHTML='';
  let h=0,y=0,n=0;
  RESULTS.forEach(it=>{
    if(f!=='all' && it.model_pick!==f) return;
    const st=assign[it.face_id]||'';
    if(st===HAO)h++; else if(st===YUN)y++; else if(st==='neither')n++;
    const cell=document.createElement('div'); cell.className='cell';
    cell.innerHTML=`<img src="${it.thumb}"/><div class="meta">皓祥 ${it.sim_h} ｜ 运丰 ${it.sim_y}<br/>模型倾向：${it.model_pick}<br/><a href="file:///${it.path}" target="_blank">原图</a></div><div class="btns"><button class="${st===HAO?'on-h':''}" onclick="setA(${it.face_id},'${HAO}')">是皓祥</button><button class="${st===YUN?'on-y':''}" onclick="setA(${it.face_id},'${YUN}')">是运丰</button><button class="${st==='neither'?'on-n':''}" onclick="setA(${it.face_id},'neither')">都不是</button></div>`;
    g.appendChild(cell);
  });
  document.getElementById('stats').textContent=`皓祥 ${h} ｜ 运丰 ${y} ｜ 都不是 ${n} ｜ 显示 ${h+y+n}`;
}
function setA(fid,v){ if(assign[fid]===v) delete assign[fid]; else assign[fid]=v; render(); }
function clearAll(){ for(const k in assign) delete assign[k]; render(); }
function exportJSON(){
  const items=RESULTS.filter(it=>assign[it.face_id]).map(it=>({face_id:it.face_id, assign:assign[it.face_id]}));
  const out={kind:"ambiguous_2way", persons:[HAO,YUN], exported_at:new Date().toISOString(), items};
  const blob=new Blob([JSON.stringify(out,null,2)],{type:'application/json'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='ambiguous_judgments.json'; a.click();
  alert('已导出 '+items.length+' 条判断 → ambiguous_judgments.json');
}
render();
</script></body></html>"""


def main():
    if not os.path.exists(SRC):
        print(f"ERROR: 找不到 {SRC}，请先跑重叠分析（retrieve 后导出）。")
        return
    items = []
    with open(SRC, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            items.append({
                "face_id": int(r["face_id"]),
                "sim_h": r["sim_haoxiang"],
                "sim_y": r["sim_yunfeng"],
                "model_pick": r["model_pick"],
                "thumb": r["thumb"],
                "path": r["path"],
            })
    html = (TPL.replace("__COUNT__", str(len(items)))
                .replace("__DATA__", json.dumps(items, ensure_ascii=False)))
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"交互审查页已生成: {OUT_HTML}")
    print(f"  共 {len(items)} 张重叠脸，打开后逐张点「是皓祥/是运丰/都不是」→ 导出 ambiguous_judgments.json")


if __name__ == "__main__":
    main()
