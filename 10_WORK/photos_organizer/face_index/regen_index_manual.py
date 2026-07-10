# -*- coding: utf-8 -*-
"""
regen_index_manual.py — 手动调整后的「索引重建（不移动）」
========================================================
前提：用户已在 E:\待整理照片\皓祥 里手动移动/增删文件。
本脚本只做：重扫磁盘 → 人脸检测（缩略图用）→ 按当前物理文件夹定年份
→ 重建 _preview/index.csv + index.html + thumbs。
**绝不推断年份、绝不移动文件**，尊重人工调整。

额外产出：
  - _preview/review.csv：对 皓祥 相似度低/无人脸 的文件单列，供你核对
    手动调整是否误带进非皓祥照片（不移动、只报告）。

用法：直接运行。
"""
import os, re, json, shutil, csv, datetime
import numpy as np
from PIL import Image, ImageOps

TARGET = r"E:\待整理照片\皓祥"
FACE_DB = os.path.join(os.path.dirname(__file__), "face_index.db")
REF_PERSON = "皓祥"
BORN = (2004, 9, 11)
SKIP_DIRS = {"_duplicates", "_preview", "_rejected"}
PV = os.path.join(TARGET, "_preview")
DETECT_JSON = os.path.join(PV, "_detect.json")
THUMBS = os.path.join(PV, "thumbs")
SIM_NO_FACE = 0.20      # 低于此判定「无人脸/非皓祥主脸」
SIM_LOW = 0.35          # 低于此但>NO_FACE 判「疑似非本人」

# ---------- 工具 ----------
def cos(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))

def collect_photos(target):
    out = []
    for root, dirs, names in os.walk(target):
        rel = os.path.relpath(root, target)
        if any(seg.startswith("_") for seg in rel.split(os.sep)):
            continue
        for n in names:
            if n.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff")):
                out.append(os.path.join(root, n))
    return out

def current_year_of(path):
    rel = os.path.relpath(path, TARGET)
    top = rel.split(os.sep)[0]
    m = re.match(r'(\d{4})', top)
    return int(m.group(1)) if m else None

def load_ref_centroid():
    import sqlite3
    fc = sqlite3.connect(FACE_DB)
    pid = fc.execute("SELECT id FROM persons WHERE name=?", (REF_PERSON,)).fetchone()[0]
    rows = fc.execute("SELECT embedding FROM faces WHERE person_id=? AND embedding IS NOT NULL", (pid,)).fetchall()
    vecs = [np.frombuffer(r[0], dtype=np.float32) for r in rows]
    fc.close()
    return np.mean(vecs, axis=0)

def detect_all(photos, ref_centroid):
    from insightface.app import FaceAnalysis
    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=0)
    results = []
    for i, p in enumerate(photos):
        rec = {"path": p, "emb": None, "bbox": None, "sim": 0.0, "no_face": False}
        try:
            arr = np.asarray(Image.open(p).convert("RGB"))
            bgr = arr[:, :, ::-1].copy()
            img = app.get(bgr)
        except Exception:
            try:
                import cv2
                img = app.get(cv2.imread(p))
            except Exception:
                img = []
        if not img:
            rec["no_face"] = True
        else:
            best, best_s = None, -2
            for f in img:
                s = cos(f.embedding, ref_centroid)
                if s > best_s:
                    best_s, best = s, f
            if best is not None and best_s > SIM_NO_FACE:
                rec["emb"] = np.asarray(best.embedding, dtype=np.float32).tolist()
                rec["bbox"] = [float(x) for x in best.bbox]
                rec["sim"] = round(best_s, 3)
            else:
                rec["no_face"] = True
                rec["sim"] = round(best_s, 3) if best is not None else 0.0
        results.append(rec)
        if (i + 1) % 50 == 0:
            print(f"  检测 {i+1}/{len(photos)}")
    return results

def make_thumb(src, dst, bbox, long_side=260):
    try:
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            W, H = im.size
            if bbox:
                x1, y1, x2, y2 = bbox
                bw, bh = x2 - x1, y2 - y1
                x1 = max(0, x1 - bw * 0.25); y1 = max(0, y1 - bh * 0.25)
                x2 = min(W, x2 + bw * 0.25); y2 = min(H, y2 + bh * 0.25)
                im = im.crop((int(x1), int(y1), int(x2), int(y2)))
            else:
                s = min(W, H); im = im.crop(((W - s)//2, (H - s)//2, (W+s)//2, (H+s)//2))
            im.thumbnail((long_side, long_side))
            bg = Image.new("RGB", (long_side, long_side), (255, 255, 255))
            bg.paste(im, ((long_side - im.width)//2, (long_side - im.height)//2))
            bg.save(dst, "JPEG", quality=85)
        return True
    except Exception:
        return False

def build_html(rows):
    from collections import defaultdict
    by_year = defaultdict(list)
    for r in rows:
        by_year[r["year"]].append(r)
    flag_color = {"ok": "#1a7f37", "low": "#bc4c00", "none": "#cf222e"}
    esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    parts = ["""<!doctype html><html lang=zh><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>皓祥 文件夹索引（手动调整后重建）</title>
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
    parts.append(f"""<header><h1>皓祥 文件夹索引（手动调整后重建）</h1>
<div class=sum>
<span>总照片 <b>{len(rows)}</b></span>
<span>年份文件夹 <b>{len(by_year)}</b></span>
<span style="color:#1a7f37">皓祥本人 <b>{n_ok}</b></span>
<span style="color:#bc4c00">疑似非本人 <b>{n_low}</b></span>
<span style="color:#cf222e">无人脸/非主脸 <b>{n_none}</b></span>
<span>生成 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
</div>
<div class=sum style="color:#57606a">年份=当前物理文件夹（尊重手动调整）· 缩略图裁剪皓祥面部 · 点缩略图开原图 · 标红项见 review.csv</div>
</header>""")
    for y in sorted(by_year):
        items = by_year[y]
        parts.append(f"<div class=year><h2>{y} （{len(items)}）</h2><div class=grid>")
        for r in items:
            col = flag_color.get(r["flag"], "#6e7781")
            absp = r["abs"].replace("\\", "/")
            parts.append(
                f"<a class=card href='file:///{absp}'>"
                f"<img loading=lazy src='{r['thumb']}'>"
                f"<div class=cap><div class=nm>{esc(os.path.basename(r['abs']))}</div>"
                f"<span class=badge style='background:{col}'>{r['flag']} {r['sim']}</span></div></a>")
        parts.append("</div></div>")
    parts.append("</body></html>")
    return "\n".join(parts)

def main():
    os.makedirs(PV, exist_ok=True)
    photos = collect_photos(TARGET)
    print(f"扫描到 {len(photos)} 张照片（已排除 _ 开头的辅助目录）")

    print("运行人脸检测（重新检测，不依赖旧缓存）...")
    ref = load_ref_centroid()
    dets = detect_all(photos, ref)
    json.dump(dets, open(DETECT_JSON, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"检测完成 {len(dets)} 张，写 {DETECT_JSON}")

    # 重建 thumbs（清旧的，避免孤儿）
    if os.path.isdir(THUMBS):
        shutil.rmtree(THUMBS)
    os.makedirs(THUMBS, exist_ok=True)

    rows = []
    review_rows = []
    for i, d in enumerate(dets):
        y = current_year_of(d["path"])
        if y is None:
            y = BORN[0]
        th = os.path.join(THUMBS, f"{i:04d}.jpg")
        make_thumb(d["path"], th, d["bbox"])
        if d["no_face"]:
            flag = "none"
        elif d["sim"] < SIM_LOW:
            flag = "low"
        else:
            flag = "ok"
        rec = {
            "i": i, "rel": os.path.relpath(d["path"], TARGET), "year": y,
            "sim": d["sim"], "no_face": d["no_face"], "flag": flag,
            "thumb": f"thumbs/{i:04d}.jpg", "abs": d["path"],
        }
        rows.append(rec)
        if flag in ("low", "none"):
            review_rows.append(rec)

    # 全量 CSV
    with open(os.path.join(PV, "index.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["相对路径", "年份", "皓祥相似度", "标记", "缩略图", "绝对路径"])
        for r in rows:
            w.writerow([r["rel"], r["year"], r["sim"], r["flag"], r["thumb"], r["abs"]])

    # review.csv
    with open(os.path.join(PV, "review.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["文件", "当前年份", "皓祥相似度", "标记", "绝对路径"])
        for r in sorted(review_rows, key=lambda x: x["sim"]):
            w.writerow([os.path.basename(r["abs"]), r["year"], r["sim"], r["flag"], r["abs"]])

    html = build_html(rows)
    with open(os.path.join(PV, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n索引已生成")
    print(f"  总照片: {len(rows)} | 年份文件夹: {len(set(r['year'] for r in rows))}")
    print(f"  皓祥本人(ok): {sum(1 for r in rows if r['flag']=='ok')}")
    print(f"  疑似非本人(low): {sum(1 for r in rows if r['flag']=='low')}")
    print(f"  无人脸/非主脸(none): {sum(1 for r in rows if r['flag']=='none')}")
    print(f"  review.csv 需核对: {len(review_rows)} 张")
    print(f"  index.html: {os.path.join(PV, 'index.html')}")

if __name__ == "__main__":
    main()
