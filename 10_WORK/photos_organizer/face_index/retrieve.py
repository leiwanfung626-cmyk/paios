#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
retrieve.py — 特定人物检索 + 命名 (Phase 2/4 核心工具)
给定目标人物的种子图(文件夹)或一个已聚类簇，在全库人脸中检索最相似者，
返回 TopK 排名(去重到照片级) + 缩略图 + HTML 报告 + CSV。

子命令：
  python retrieve.py --seeds <文件夹> [--tag 儿子] [--topk 300] [--sim-thr 0.30]
        —— 用种子文件夹里所有人脸作为查询(取最大相似)，找目标人物
  python retrieve.py --cluster <cluster_id> [--tag 父亲] [--topk 300]
        —— 直接检索某聚类簇内全部人脸(用于给整簇命名)
  python retrieve.py --name "儿子" --confirm-faceids 12,45,78
        —— 把指定人脸(faces.id)归入人物"儿子"，自动建/复用 persons 行
  python retrieve.py --name "父亲" --confirm-cluster 23
        —— 把某簇全部人脸归入人物"父亲"

输出：
  face_index/retrieval/<tag>/      缩略图 + results.csv + report.html
  report.html 直接 file:// 打开即可逐张审查

注意：种子图若含合影(多人)，建议挑选单人清晰照；脚本对每张种子脸取 max 相似，
       合影稀释影响已被削弱。
"""
import argparse
import os
import sqlite3
import shutil
import json
import numpy as np
import faiss

HERE = os.path.dirname(os.path.abspath(__file__))
FACE_DB = os.path.join(HERE, "face_index.db")
FACES_DIR = os.path.join(HERE, "faces")
EMB_DIM = 512


# ---------- 加载 ----------
def load_index():
    index = faiss.read_index(os.path.join(HERE, "faiss_index.bin"))
    ids = np.load(os.path.join(HERE, "face_ids.npy"))
    return index, ids


def load_app():
    from insightface.app import FaceAnalysis
    app = FaceAnalysis(name="buffalo_l")
    app.prepare(ctx_id=-1, det_size=(640, 640))
    return app


def load_image_rgb(path):
    from PIL import Image, ImageOps
    try:
        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im)
            if im.mode in ("RGBA", "P", "LA"):
                im = im.convert("RGB")
            return np.asarray(im.convert("RGB"))
    except Exception:
        return None


def get_face_embeddings(app, folder):
    """返回文件夹内所有检测到的人脸 embedding (M,512) 归一化，及来源文件清单。"""
    import cv2
    embs = []
    files = []
    for fn in sorted(os.listdir(folder)):
        if not fn.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif")):
            continue
        p = os.path.join(folder, fn)
        rgb = load_image_rgb(p)
        if rgb is None:
            continue
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        faces = app.get(bgr)
        for f in faces:
            e = np.ascontiguousarray(f.embedding, dtype=np.float32)
            n = np.linalg.norm(e)
            if n > 0:
                embs.append(e / n)
                files.append(fn)
    return np.array(embs, dtype="float32"), files


def search_by_seeds(index, ids, seed_embs, topk):
    """seed_embs (M,512) 归一化。返回 {face_id: best_sim}。"""
    k = min(topk, len(ids))
    D, I = index.search(seed_embs, k)
    best = {}
    for s in range(D.shape[0]):
        for j in range(k):
            fid = int(I[s][j])
            sim = float(D[s][j])
            if fid >= 0 and (fid not in best or sim > best[fid]):
                best[fid] = sim
    return best


def search_by_cluster(index, ids, cluster_id, topk):
    con = sqlite3.connect(FACE_DB)
    rows = con.execute("SELECT id FROM faces WHERE cluster_id=?", (cluster_id,)).fetchall()
    con.close()
    cids = [r[0] for r in rows]
    best = {fid: 1.0 for fid in cids}
    return best


def dedup_to_photo(con, best, sim_thr):
    """按 photo_id 去重，保留该照片匹配到的最高分脸。返回 [(photo_id, path, sim, face_id)]"""
    rows = con.execute("SELECT id, photo_id, path FROM faces WHERE id IN (%s)" %
                       ",".join("?" * len(best)), list(best.keys())).fetchall()
    photo_best = {}
    for fid, pid, path in rows:
        sim = best[fid]
        if sim < sim_thr:
            continue
        if pid not in photo_best or sim > photo_best[pid][0]:
            photo_best[pid] = (sim, path, fid)
    out = [(pid, v[1], v[0], v[2]) for pid, v in photo_best.items()]
    out.sort(key=lambda x: x[2], reverse=True)
    return out


INTERACTIVE_HTML = r"""<!doctype html><html><head><meta charset="utf-8">
<title>检索: __TAG__</title>
<style>
 body{font-family:system-ui;background:#fff;color:#222;margin:0;padding:16px}
 h1{font-size:18px}
 .bar{position:sticky;top:0;background:#fff;padding:10px 0;border-bottom:1px solid #eee;display:flex;gap:10px;flex-wrap:wrap;align-items:center;z-index:10}
 .grid{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}
 .cell{width:150px;border:1px solid #ddd;border-radius:8px;overflow:hidden;background:#fafafa}
 .cell img{width:150px;height:150px;object-fit:cover;display:block}
 .meta{font-size:11px;padding:4px 6px;color:#555}
 .btns{display:flex;gap:4px;padding:4px 6px}
 .btns button{flex:1;cursor:pointer;border:1px solid #ccc;background:#fff;border-radius:4px;font-size:12px;padding:3px 0}
 .btns button.on-y{background:#2e7d32;color:#fff;border-color:#2e7d32}
 .btns button.on-n{background:#c62828;color:#fff;border-color:#c62828}
 .btns button.on-u{background:#f9a825;color:#fff;border-color:#f9a825}
 .stats{font-size:13px;color:#333}
 input[type=number]{width:70px}
</style></head><body>
<h1>检索结果：__TAG__（共 __COUNT__ 张照片）</h1>
<div class="bar">
  <span class="stats" id="stats"></span>
  <label>相似度≥<input type="number" id="minSim" value="0.30" step="0.05" min="0" max="1"></label>
  <button onclick="bulkAccept()">全选≥为接受</button>
  <button onclick="clearAll()">清空</button>
  <button onclick="exportJSON()">导出 judgments.json</button>
</div>
<div class="grid" id="grid"></div>
<script>
const PERSON="__TAG__";
const RESULTS=__DATA__;
const judg={};
function render(){
  const min=parseFloat(document.getElementById('minSim').value)||0;
  const g=document.getElementById('grid'); g.innerHTML='';
  let a=0,n=0,u=0;
  RESULTS.forEach(it=>{
    if(it.sim<min) return;
    const st=judg[it.face_id]||'';
    if(st==='accept')a++; else if(st==='reject')n++; else if(st==='unsure')u++;
    const cell=document.createElement('div'); cell.className='cell';
    cell.innerHTML=`<img src="${it.thumb}"/><div class="meta">#${it.rank} sim=${it.sim.toFixed(3)}<br/><a href="file:///${it.path}" target="_blank">原图</a></div><div class="btns"><button class="${st==='accept'?'on-y':''}" onclick="setJ(${it.face_id},'accept')">✓</button><button class="${st==='reject'?'on-n':''}" onclick="setJ(${it.face_id},'reject')">✗</button><button class="${st==='unsure'?'on-u':''}" onclick="setJ(${it.face_id},'unsure')">?</button></div>`;
    g.appendChild(cell);
  });
  document.getElementById('stats').textContent=`接受 ${a} ｜ 排除 ${n} ｜ 存疑 ${u} ｜ 显示 ${a+n+u}`;
}
function setJ(fid,v){ if(judg[fid]===v) delete judg[fid]; else judg[fid]=v; render(); }
function bulkAccept(){ const min=parseFloat(document.getElementById('minSim').value)||0; RESULTS.forEach(it=>{ if(it.sim>=min) judg[it.face_id]='accept'; }); render(); }
function clearAll(){ for(const k in judg) delete judg[k]; render(); }
function exportJSON(){
  const items=RESULTS.filter(it=>judg[it.face_id]).map(it=>({face_id:it.face_id,photo_id:it.photo_id,sim:it.sim,judgment:judg[it.face_id]}));
  const out={person:PERSON,source:"face_retrieval",exported_at:new Date().toISOString(),items};
  const blob=new Blob([JSON.stringify(out,null,2)],{type:'application/json'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='judgments.json'; a.click();
  alert('已导出 '+items.length+' 条判断 → judgments.json');
}
render();
</script></body></html>"""


def export_results(tag, results, best):
    out_dir = os.path.join(HERE, "retrieval", tag)
    os.makedirs(out_dir, exist_ok=True)
    csv_lines = ["rank,photo_id,face_id,sim,path,thumb,judgment"]
    items = []
    con = sqlite3.connect(FACE_DB)
    for rank, (pid, path, sim, fid) in enumerate(results, start=1):
        fidx = con.execute("SELECT face_idx FROM faces WHERE id=?", (fid,)).fetchone()[0]
        thumb_src = os.path.join(FACES_DIR, f"{pid}_{fidx}.jpg")
        thumb_dst = os.path.join(out_dir, f"{rank:04d}_{fid}.jpg")
        if os.path.exists(thumb_src):
            shutil.copy(thumb_src, thumb_dst)
        rel = os.path.basename(thumb_dst)
        csv_lines.append(f"{rank},{pid},{fid},{sim:.4f},{path},{rel},")
        items.append({"rank": rank, "face_id": fid, "photo_id": pid,
                      "sim": round(sim, 4), "thumb": rel, "path": path})
    con.close()
    with open(os.path.join(out_dir, "results.csv"), "w", encoding="utf-8") as f:
        f.write("\n".join(csv_lines))
    # 交互式 HTML（内嵌数据，file:// 直开，无需服务器）
    data_json = json.dumps(items, ensure_ascii=False)
    html = (INTERACTIVE_HTML
            .replace("__TAG__", tag)
            .replace("__COUNT__", str(len(items)))
            .replace("__DATA__", data_json))
    rep = os.path.join(out_dir, "report.html")
    with open(rep, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"结果已导出: {out_dir}")
    print(f"  report.html (交互式): {rep}")
    print(f"  results.csv: {os.path.join(out_dir,'results.csv')}")
    return rep


def assign_person(name, face_ids):
    con = sqlite3.connect(FACE_DB)
    cur = con.execute("SELECT id FROM persons WHERE name=?", (name,))
    row = cur.fetchone()
    if row:
        pid = row[0]
    else:
        cur = con.execute("INSERT INTO persons (name, created_at) VALUES (?, datetime('now'))",
                          (name,))
        pid = cur.lastrowid
    con.executemany("UPDATE faces SET person_id=? WHERE id=?", [(pid, fid) for fid in face_ids])
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM faces WHERE person_id=?", (pid,)).fetchone()[0]
    con.close()
    print(f"人物 '{name}' (id={pid}) 现含 {n} 张人脸。")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", help="种子图文件夹(目标人物清晰照)")
    ap.add_argument("--cluster", type=int, help="直接检索某聚类簇 id")
    ap.add_argument("--tag", help="结果标签(默认 seeds 文件名或 cluster_id)")
    ap.add_argument("--topk", type=int, default=300)
    ap.add_argument("--sim-thr", type=float, default=0.30, help="结果最低相似度")
    ap.add_argument("--name", help="命名：将确认结果归入此人物")
    ap.add_argument("--confirm-faceids", help="逗号分隔的 faces.id，配合 --name")
    ap.add_argument("--confirm-cluster", type=int, help="簇 id，配合 --name 整簇归入")
    args = ap.parse_args()

    if args.name and args.confirm_faceids:
        fids = [int(x) for x in args.confirm_faceids.split(",") if x.strip()]
        assign_person(args.name, fids)
        return
    if args.name and args.confirm_cluster is not None:
        con = sqlite3.connect(FACE_DB)
        fids = [r[0] for r in con.execute(
            "SELECT id FROM faces WHERE cluster_id=?", (args.confirm_cluster,))]
        con.close()
        assign_person(args.name, fids)
        return

    if not (args.seeds or args.cluster is not None):
        print("需提供 --seeds <文件夹> 或 --cluster <id>。命名请用 --name + --confirm-*。")
        return

    index, ids = load_index()
    if args.seeds:
        tag = args.tag or os.path.basename(os.path.normpath(args.seeds))
        app = load_app()
        seed_embs, files = get_face_embeddings(app, args.seeds)
        if len(seed_embs) == 0:
            print(f"ERROR: 种子文件夹未检出任何人脸: {args.seeds}")
            return
        print(f"种子人脸数={len(seed_embs)} (来自 {len(set(files))} 文件)")
        best = search_by_seeds(index, ids, seed_embs, args.topk)
    else:
        tag = args.tag or f"cluster_{args.cluster}"
        best = search_by_cluster(index, ids, args.cluster, args.topk)

    con = sqlite3.connect(FACE_DB)
    results = dedup_to_photo(con, best, args.sim_thr)
    con.close()
    print(f"匹配照片(>= {args.sim_thr}): {len(results)} 张")
    if not results:
        return
    rep = export_results(tag, results, best)
    print(f"打开审查: file:///{rep}")


if __name__ == "__main__":
    main()
