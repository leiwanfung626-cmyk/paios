#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
review_corrections.py — 人物库内纠偏审查页生成器

针对"已在库但可能误收"的脸，按 人物 + 来源 过滤，生成交互式
accept(保留) / reject(排除) 审查页。导出 judgments.json 直接喂 commit_judgments.py。

用法:
  # 纠偏某人所有可疑来源(下载/截图/文档/待审)
  python review_corrections.py --tag 皓祥 --sources 04_Downloads,03_Screenshots,05_Documents,07_ToReview
  # 只纠偏下载类
  python review_corrections.py --tag 运丰 --sources 04_Downloads
  # 纠偏全部在库脸(不筛选来源)
  python review_corrections.py --tag 皓祥
"""
import os
import sqlite3
import argparse
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
FACE_DB = os.path.join(HERE, "face_index.db")
PHOTO_DB = os.path.join(HERE, "..", "database", "photo_index.db")
FACES_DIR = os.path.join(HERE, "faces")
OUT_DIR = os.path.join(HERE, "retrieval", "corrections")

PERSISTENT_SUSPECT = ["04_Downloads", "03_Screenshots", "05_Documents", "07_ToReview"]


def load_rows(tag, sources):
    fc = sqlite3.connect(FACE_DB)
    fc.execute("ATTACH ? AS ph", (os.path.abspath(PHOTO_DB),))
    pid = fc.execute("SELECT id FROM persons WHERE name=?", (tag,)).fetchone()
    if not pid:
        raise SystemExit(f"人物不存在: {tag}")
    pid = pid[0]
    rows = []
    q = """SELECT f.id, f.photo_id, f.face_idx, f.path, f.age, f.gender, p.source, p.date
           FROM faces f
           LEFT JOIN ph.photos p ON p.path = f.path
           WHERE f.person_id = ?"""
    params = [pid]
    if sources:
        q += " AND p.source IN (%s)" % ",".join("?" * len(sources))
        params += list(sources)
    q += " ORDER BY p.source, p.date"
    for fid, phid, fidx, path, age, gender, src, date in fc.execute(q, params):
        thumb = os.path.join(FACES_DIR, f"{phid}_{fidx}.jpg")
        rows.append({
            "face_id": fid,
            "photo_id": phid,
            "thumb": f"{phid}_{fidx}.jpg" if os.path.exists(thumb) else "",
            "path": path,
            "age": age if age is not None else "",
            "gender": "男" if gender == 1 else ("女" if gender == 0 else ""),
            "source": src or "",
            "date": date or "",
        })
    fc.close()
    return pid, rows


def build_html(tag, rows, sources):
    items = []
    for r in rows:
        items.append({
            "face_id": r["face_id"],
            "sim": 0.0,
            "judgment": "",
            "meta": f'{r["source"]} | {r["date"]} | {r["age"]}岁{r["gender"]}',
            "thumb": r["thumb"],
            "path": r["path"],
        })
    src_filter = ",".join(sources) if sources else "全部来源"
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>纠偏: {tag}</title>
<style>
body{{font-family:system-ui;background:#f5f5f5;color:#222;margin:0;padding:14px}}
h1{{font-size:18px;margin:0 0 4px}}
.sub{{color:#666;font-size:13px;margin-bottom:10px}}
.bar{{position:sticky;top:0;background:#fff;padding:10px;border:1px solid #ddd;border-radius:8px;z-index:10;display:flex;flex-wrap:wrap;gap:8px;align-items:center}}
button{{font-size:13px;padding:6px 12px;border:1px solid #bbb;border-radius:6px;background:#fff;cursor:pointer}}
button.acc{{border-color:#2e7d32;color:#2e7d32}}
button.rej{{border-color:#c62828;color:#c62828}}
button.bulk{{background:#fafafa}}
.grid{{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}}
.cell{{width:160px;border:1px solid #ddd;border-radius:8px;overflow:hidden;background:#fff;position:relative}}
.cell img{{width:160px;height:160px;object-fit:cover;display:block}}
.meta{{font-size:11px;padding:3px 6px;color:#555;line-height:1.3}}
.ctrl{{display:flex;gap:4px;padding:4px 6px}}
.ctrl button{{flex:1;padding:4px;font-size:12px}}
.cell.accepted{{outline:3px solid #2e7d32}}
.cell.rejected{{outline:3px solid #c62828;opacity:.45}}
.cnt{{font-weight:bold}}
</style></head><body>
<h1>纠偏审查：{tag}</h1>
<div class="sub">来源过滤：{src_filter} ｜ 共 {len(rows)} 张待审 ｜ 操作写回 {os.path.basename(FACE_DB)}（原图不改）</div>
<div class="bar">
  <button class="bulk" onclick="bulk('accept')">全部保留</button>
  <button class="bulk" onclick="bulk('reject')">全部排除</button>
  <button class="bulk" onclick="bulk('clear')">清空</button>
  <button class="acc" onclick="exportJSON()">导出 judgments.json</button>
  <span class="cnt">保留 <span id="nAcc">0</span> ｜ 排除 <span id="nRej">0</span></span>
</div>
<div class="grid" id="grid">
"""
    for it in items:
        html += (f'<div class="cell" id="c{it["face_id"]}" data-fid="{it["face_id"]}">'
                 f'<img src="{os.path.join("..","..","faces",it["thumb"]) if it["thumb"] else ""}" '
                 f'onerror="this.style.background=\'#eee\'"/>'
                 f'<div class="meta">{it["meta"]}<br/><a href="file:///{it["path"]}" target="_blank">原图</a></div>'
                 f'<div class="ctrl"><button class="acc" onclick="setJ({it["face_id"]},\'accept\',this)">保留</button>'
                 f'<button class="rej" onclick="setJ({it["face_id"]},\'reject\',this)">排除</button></div></div>\n')
    html += "</div>\n"
    html += f"""<script>
const RESULTS = {items};
const TAg = "{tag}";
const state = {{}};
function setJ(fid, j, btn){{
  state[fid] = j;
  const cell = document.getElementById('c'+fid);
  cell.classList.remove('accepted','rejected');
  if(j==='accept') cell.classList.add('accepted');
  if(j==='reject') cell.classList.add('rejected');
  upd();
}}
function bulk(j){{
  for(const it of RESULTS){{ if(j==='clear'){{ delete state[it.face_id]; }} else {{ state[it.face_id]=j; }} }}
  refreshAll(); upd();
}}
function refreshAll(){{
  for(const it of RESULTS){{
    const cell=document.getElementById('c'+it.face_id);
    cell.classList.remove('accepted','rejected');
    if(state[it.face_id]==='accept') cell.classList.add('accepted');
    if(state[it.face_id]==='reject') cell.classList.add('rejected');
  }}
}}
function upd(){{
  let a=0,r=0; for(const k in state){{ if(state[k]==='accept')a++; else if(state[k]==='reject')r++; }}
  document.getElementById('nAcc').textContent=a;
  document.getElementById('nRej').textContent=r;
}}
function exportJSON(){{
  const items=[];
  for(const it of RESULTS){{ const j=state[it.face_id]; if(j) items.push({{face_id:it.face_id,sim:it.sim,judgment:j}}); }}
  if(items.length===0){{ alert('没有标记任何判定'); return; }}
  const out={{person:TAg, source:'face_correction_review', exported_at:new Date().toISOString(), items}};
  const blob=new Blob([JSON.stringify(out,null,1)],{{type:'application/json'}});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob);
  a.download='corrections_'+TAg+'.json'; a.click();
}}
</script></body></html>"""
    return html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--sources", default=",".join(PERSISTENT_SUSPECT),
                    help="逗号分隔的来源前缀过滤，留空=全部在库脸")
    args = ap.parse_args()
    sources = [s.strip() for s in args.sources.split(",") if s.strip()] or None
    pid, rows = load_rows(args.tag, sources)
    if not rows:
        print(f"[warn] {args.tag} 在来源 {sources} 下没有待纠偏脸")
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    html = build_html(args.tag, rows, sources)
    out = os.path.join(OUT_DIR, f"{args.tag}.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"纠偏页已生成: {out}")
    print(f"  人物={args.tag}(id={pid})  待审={len(rows)}  来源={sources or '全部'}")


if __name__ == "__main__":
    main()
