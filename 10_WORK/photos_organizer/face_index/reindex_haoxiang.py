# -*- coding: utf-8 -*-
"""
reindex_haoxiang.py — 皓祥文件夹「重头开始」索引重建
=================================================
不信任任何现有年份标签（被相机时间错误污染），改用：
  1. 可靠文件名日期锚点（YYYY-MM-DD / YYYYMMDD / wx_camera_13位时间戳）
  2. 迭代外观原型（同人脸向量随年龄单调漂移 → argmax 余弦相似）
  3. 出生约束：皓祥生于 2004-09-11，任何文件/文件夹不得早于 2004

产物：
  - 物理重分类到 E:\待整理照片\皓祥/<年份>/  （2004..2026，空年份也建）
  - _preview/index.html + index.csv（缩略图裁剪到皓祥面部）
  - _preview/review.csv（变更 / 低置信，供人审）
  - _preview/undo_map.csv（原路径→新路径，可回滚）

用法：
  --dry   仅计算推断并打印方案，不移动文件
  --run   执行推断 + 移动 + 生成索引
"""
import os, sys, re, json, shutil, argparse, datetime
import numpy as np
from PIL import Image, ImageOps

TARGET = r"E:\待整理照片\皓祥"
FACE_DB = os.path.join(os.path.dirname(__file__), "face_index.db")
REF_PERSON = "皓祥"
BORN = (2004, 9, 11)
YEARS = list(range(2004, 2027))          # 2004..2026
SKIP_DIRS = {"_duplicates", "_preview"}
DETECT_CACHE = os.path.join(TARGET, "_preview", "_detect.json")
ASSIGN_CACHE = os.path.join(TARGET, "_preview", "_assign.json")

# ---------- 工具 ----------
def cos(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))

def parse_reliable_year(name):
    """只信任显式日期模式，避免误匹配 EXIF 时间戳子串（如 2029）。"""
    m = re.search(r'(?:19|20)\d{2}[-_/]?\d{2}[-_/]?\d{2}', name)
    if m:
        y = int(re.search(r'(?:19|20)\d{2}', m.group(0)).group(0))
        if BORN[0] <= y <= 2026:
            return y
    m = re.search(r'wx_camera_(\d{13})', name)
    if m:
        try:
            y = datetime.datetime.fromtimestamp(int(m.group(1)) / 1000).year
            if BORN[0] <= y <= 2026:
                return y
        except Exception:
            pass
    return None

def collect_photos(target):
    out = []
    for root, dirs, names in os.walk(target):
        rel_root = os.path.relpath(root, target)
        if any(seg.startswith("_") for seg in rel_root.split(os.sep)):
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

# ---------- 参考质心 ----------
def load_ref_centroid():
    import sqlite3
    fc = sqlite3.connect(FACE_DB)
    pid = fc.execute("SELECT id FROM persons WHERE name=?", (REF_PERSON,)).fetchone()[0]
    rows = fc.execute("SELECT embedding FROM faces WHERE person_id=? AND embedding IS NOT NULL", (pid,)).fetchall()
    vecs = [np.frombuffer(r[0], dtype=np.float32) for r in rows]
    fc.close()
    return np.mean(vecs, axis=0)

# ---------- 检测 ----------
def detect_all(photos, ref_centroid):
    from insightface.app import FaceAnalysis
    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=0)
    results = []
    for i, p in enumerate(photos):
        rec = {"path": p, "emb": None, "bbox": None, "no_face": False, "reliable_year": parse_reliable_year(os.path.basename(p))}
        try:
            arr = np.asarray(Image.open(p).convert("RGB"))
            bgr = arr[:, :, ::-1].copy()          # InsightFace 需要 BGR，与参考质心一致
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
            # 选皓祥本人脸：与参考质心余弦最高
            best, best_s = None, -2
            for f in img:
                s = cos(f.embedding, ref_centroid)
                if s > best_s:
                    best_s, best = s, f
            if best is not None and best_s > 0.2:
                rec["emb"] = np.asarray(best.embedding, dtype=np.float32).tolist()
                rec["bbox"] = [float(x) for x in best.bbox]
            else:
                rec["no_face"] = True
        results.append(rec)
        if (i + 1) % 50 == 0:
            print(f"  检测 {i+1}/{len(photos)}")
    return results

# ---------- 年份推断 ----------
def infer_years(dets):
    embs = {i: np.asarray(d["emb"], float) for i, d in enumerate(dets) if d["emb"] is not None}
    assign = {}
    locked = {}
    for i, d in enumerate(dets):
        if d["reliable_year"] and BORN[0] <= d["reliable_year"] <= 2026:
            locked[i] = d["reliable_year"]
            assign[i] = d["reliable_year"]
        else:
            assign[i] = current_year_of(d["path"]) or BORN[0]   # 弱先验
    # 迭代 EM
    proto = {}
    for it in range(5):
        # 重建原型（locked + 当前 assign）
        pools = {y: [] for y in YEARS}
        for i, y in assign.items():
            if i in embs:
                pools[y].append(embs[i])
        for y in YEARS:
            proto[y] = np.mean(pools[y], axis=0) if pools[y] else proto.get(y)
        # E-step：浮动样本重新指派（argmax 仅在 YEARS≥2004，天然满足出生约束）
        changed = 0
        for i in embs:
            if i in locked:
                continue
            best_y, best_s = None, -2
            for y in YEARS:
                if proto.get(y) is None:
                    continue
                s = cos(embs[i], proto[y])
                if s > best_s:
                    best_s, best_y = s, y
            if best_y is not None and best_y != assign[i]:
                changed += 1
                assign[i] = best_y
        # 无脸样本：保持弱先验（已是≥2004或BORN[0]）
        for i, d in enumerate(dets):
            if i not in embs:
                assign[i] = current_year_of(d["path"]) or BORN[0]
        if changed == 0:
            break
    # 置信度
    conf = {}
    for i in embs:
        ss = sorted((cos(embs[i], proto[y]) for y in YEARS if proto.get(y) is not None), reverse=True)
        top1 = ss[0]; top2 = ss[1] if len(ss) > 1 else 0
        gap = top1 - top2
        conf[i] = ("high" if gap > 0.04 and top1 > 0.25 else "low", round(top1, 3), round(gap, 3))
    return assign, conf

# ---------- 缩略图（皓祥面部裁剪）----------
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
                # 中心方裁
                s = min(W, H); im = im.crop(((W - s) // 2, (H - s) // 2, (W + s) // 2, (H + s) // 2))
            im.thumbnail((long_side, long_side))
            bg = Image.new("RGB", (long_side, long_side), (255, 255, 255))
            bg.paste(im, ((long_side - im.width) // 2, (long_side - im.height) // 2))
            bg.save(dst, "JPEG", quality=85)
        return True
    except Exception:
        return False

# ---------- 主流程 ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="执行移动+生成索引（默认 dry）")
    args = ap.parse_args()
    do_run = args.run
    os.makedirs(os.path.join(TARGET, "_preview"), exist_ok=True)
    photos = collect_photos(TARGET)
    print(f"扫描到 {len(photos)} 张照片")

    # 检测（带缓存）
    if os.path.exists(DETECT_CACHE):
        dets = json.load(open(DETECT_CACHE, encoding="utf-8"))
        print(f"复用检测缓存 {len(dets)} 条")
    else:
        print("运行人脸检测...")
        ref = load_ref_centroid()
        dets = detect_all(photos, ref)
        json.dump(dets, open(DETECT_CACHE, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"检测完成，写缓存 {DETECT_CACHE}")

    assign, conf = infer_years(dets)
    json.dump({"assign": {str(k): v for k, v in assign.items()},
               "conf": {str(k): v for k, v in conf.items()}},
              open(ASSIGN_CACHE, "w", encoding="utf-8"), ensure_ascii=False)

    # 汇总
    from collections import Counter
    final = Counter(assign.values())
    changed = sum(1 for i, d in enumerate(dets) if current_year_of(d["path"]) != assign[i])
    print(f"\n[{'DRY-RUN' if not do_run else 'RUN'}] 推断年份分布: {dict(sorted(final.items()))}")
    print(f"变更年份的照片: {changed} 张 | 低置信: {sum(1 for v in conf.values() if v[0]=='low')} 张 | 无脸: {sum(1 for d in dets if d['no_face'])} 张")

    if not do_run:
        # 抽样展示：文件名含2026的应回到2026
        print("\n抽样校验（文件名含2026的应推断为2026）:")
        for i, d in enumerate(dets):
            if "2026" in os.path.basename(d["path"]):
                print(f"  {os.path.basename(d['path']):28} 原={current_year_of(d['path'])} -> 推断={assign[i]} ({conf.get(i,( '?',0,0))[0]})")
        print("\nDRY-RUN 完成，未移动任何文件。加 --run 执行。")
        return

    # ---- 执行移动 ----
    undo = []
    moved = 0
    for i, d in enumerate(dets):
        y = assign[i]
        src = d["path"]
        newdir = os.path.join(TARGET, str(y))
        os.makedirs(newdir, exist_ok=True)
        bn = os.path.basename(src)
        dst = os.path.join(newdir, bn)
        if os.path.abspath(src) != os.path.abspath(dst):
            if os.path.exists(dst):
                base, ext = os.path.splitext(bn)
                dst = os.path.join(newdir, f"{base}__{abs(hash(src))&0xffff:04x}{ext}")
            shutil.move(src, dst)
            undo.append((src, dst))
            moved += 1
        d["_new"] = dst
    print(f"移动 {moved} 张")

    # 建空年份文件夹 2004..2026
    for y in YEARS:
        os.makedirs(os.path.join(TARGET, str(y)), exist_ok=True)
    # 清理残留 <2004 目录（应为空）
    for d in os.listdir(TARGET):
        dp = os.path.join(TARGET, d)
        if os.path.isdir(dp) and not d.startswith("_"):
            m = re.match(r'(\d{4})', d)
            if m and int(m.group(1)) < BORN[0] and not os.listdir(dp):
                os.rmdir(dp); print(f"移除空目录 {d}/")

    # ---- 生成索引 ----
    thumbs = os.path.join(TARGET, "_preview", "thumbs")
    os.makedirs(thumbs, exist_ok=True)
    rows = []
    for i, d in enumerate(dets):
        y = assign[i]
        newp = d.get("_new") or d["path"]
        th = os.path.join(thumbs, f"{i:04d}.jpg")
        make_thumb(newp, th, d["bbox"])
        cy = current_year_of(d["path"])
        rows.append({
            "i": i, "new_rel": os.path.relpath(newp, TARGET), "year": y,
            "orig_year": cy, "changed": cy != y,
            "conf": conf.get(i, ("n/a", 0, 0))[0], "sim": conf.get(i, ("n/a", 0, 0))[1],
            "no_face": d["no_face"], "thumb": f"thumbs/{i:04d}.jpg", "abs": newp,
        })
    # 撤销映射
    with open(os.path.join(TARGET, "_preview", "undo_map.csv"), "w", encoding="utf-8-sig", newline="") as f:
        import csv
        w = csv.writer(f); w.writerow(["original_abs", "new_abs"])
        for o, n in undo:
            w.writerow([o, n])
    # 审查清单（变更 + 无脸，按跨度降序，供人审）
    review_rows = [r for r in rows if r["changed"] or r["no_face"]]
    review_rows.sort(key=lambda r: -abs((r["year"] or 0) - (r["orig_year"] or 0)))
    with open(os.path.join(TARGET, "_preview", "review.csv"), "w", encoding="utf-8-sig", newline="") as f:
        import csv
        w = csv.writer(f); w.writerow(["文件", "原年份", "推断年份", "跨度", "置信", "相似度", "无脸", "绝对路径"])
        for r in review_rows:
            jump = (r["year"] or 0) - (r["orig_year"] or 0)
            w.writerow([os.path.basename(r["abs"]), r["orig_year"], r["year"], jump, r["conf"], r["sim"], r["no_face"], r["abs"]])
    # 全量 CSV
    with open(os.path.join(TARGET, "_preview", "index.csv"), "w", encoding="utf-8-sig", newline="") as f:
        import csv
        w = csv.writer(f); w.writerow(["相对路径", "年份", "原文件夹年份", "是否变更", "置信", "相似度", "无脸", "绝对路径"])
        for r in rows:
            w.writerow([r["new_rel"], r["year"], r["orig_year"], r["changed"], r["conf"], r["sim"], r["no_face"], r["abs"]])
    # HTML
    html = build_html(rows)
    with open(os.path.join(TARGET, "_preview", "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"索引已生成: {os.path.join(TARGET, '_preview', 'index.html')}")
    print(f"审查清单: {os.path.join(TARGET, '_preview', 'review.csv')} ({len(review_rows)} 条需关注: 变更+无脸)")
    print(f"撤销映射: {os.path.join(TARGET, '_preview', 'undo_map.csv')} ({len(undo)} 条)")

def build_html(rows):
    from collections import defaultdict
    by_year = defaultdict(list)
    for r in rows:
        by_year[r["year"]].append(r)
    c = {"high": "#1a7f37", "low": "#bc4c00", "n/a": "#6e7781"}
    esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    parts = [f"""<!doctype html><html lang=zh><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>皓祥 文件夹索引（按外观重分类）</title>
<style>
body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f6f8fa;color:#1f2328}}
header{{position:sticky;top:0;background:#fff;border-bottom:1px solid #d0d7de;padding:12px 18px;z-index:10}}
h1{{font-size:18px;margin:0 0 6px}}
.sum{{font-size:13px;color:#57606a;display:flex;gap:14px;flex-wrap:wrap}}
.year{{margin:18px}}
.year h2{{font-size:15px;border-left:4px solid #0969da;padding-left:8px;margin-bottom:10px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}}
.card{{background:#fff;border:1px solid #d0d7de;border-radius:8px;overflow:hidden;text-decoration:none;color:inherit;display:block}}
.card img{{width:100%;height:200px;object-fit:cover;display:block;background:#eee}}
.cap{{padding:6px 8px;font-size:11px;line-height:1.35}}
.cap .nm{{font-weight:600;word-break:break-all}}
.badge{{display:inline-block;margin-top:3px;padding:1px 7px;border-radius:10px;color:#fff;font-size:11px}}
.chg{{color:#cf222e;font-weight:600}}
</style></head><body>"""]
    parts.append(f"""<header><h1>皓祥 文件夹索引（重头开始 · 按外观推断年份）</h1>
<div class=sum>
<span>总照片 <b>{len(rows)}</b></span>
<span>年份文件夹 <b>{len(by_year)}</b>（2004–2026）</span>
<span>变更 <b>{sum(1 for r in rows if r['changed'])}</b></span>
<span>低置信 <b>{sum(1 for r in rows if r['conf']=='low')}</b></span>
<span>无脸 <b>{sum(1 for r in rows if r['no_face'])}</b></span>
<span>生成 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
</div>
<div class=sum style="color:#57606a">缩略图均为皓祥面部裁剪 · 红字=年份较原文件夹变更 · 点缩略图开原图</div>
</header>""")
    for y in sorted(by_year):
        items = by_year[y]
        parts.append(f"<div class=year><h2>{y} （{len(items)}）</h2><div class=grid>")
        for r in items:
            col = c.get(r["conf"], "#6e7781")
            absp = r["abs"].replace("\\", "/")
            chg = f"<span class=chg>原{r['orig_year']}→</span>" if r["changed"] else ""
            nf = " ⚠无脸" if r["no_face"] else ""
            parts.append(
                f"<a class=card href='file:///{absp}'>"
                f"<img loading=lazy src='{r['thumb']}'>"
                f"<div class=cap><div class=nm>{esc(os.path.basename(r['abs']))}</div>"
                f"{chg}<span class=badge style='background:{col}'>{esc(r['year'])}</span> "
                f"<span class=sim>{r['conf']} {r['sim']}{nf}</span></div></a>")
        parts.append("</div></div>")
    parts.append("</body></html>")
    return "\n".join(parts)

if __name__ == "__main__":
    main()
