# -*- coding: utf-8 -*-
"""
photo_tool.py — 人物照片文件夹 统一工具（整合版）
====================================================
把原先分散的 5 个脚本合并为一个「可选择」的工具：
  reindex_haoxiang.py / regen_index_manual.py / regen_portable_html.py
  / gen_delete_review.py / apply_decisions(删除) 的公共逻辑收敛为一套。

功能（菜单编号）：
  1 重建索引（尊重物理文件夹，不移动文件）——重检人脸 + 建可移植预览
  2 按外观推断年份重分类（会移动文件，慎用）——重检 + EM原型推断 + 移动 + 预览
  3 生成「删除审查页」delete_review.html（勾选混入照片导出清单）
  4 执行删除清单 delete_list.json（永久删 / 移到 _rejected）+ 重建预览
  5 仅重生成可移植预览页（不重检测，读缓存 _detect.json）

两种用法：
  A. 交互菜单（无参数直接运行）：
     <venv-python> photo_tool.py
  B. 命令行参数（脚本化）：
     photo_tool.py --person 皓祥 --action reindex
     photo_tool.py --person 皓祥 --action reclassify
     photo_tool.py --person 皓祥 --action gendelete
     photo_tool.py --person 皓祥 --action applydelete --list "D:/.../delete_list.json" --mode reject
     photo_tool.py --person 皓祥 --action regenhtml

依赖 insightface，必须用带该库的 venv：
  C:\\Users\\liyun\\.workbuddy\\binaries\\python\\envs\\default\\Scripts\\python.exe
"""
import os, re, json, shutil, csv, argparse, datetime
import numpy as np
from PIL import Image, ImageOps
from urllib.parse import quote

# ---------- 全局约定 ----------
BASE = r"E:\待整理照片"
FACE_DB = os.path.join(os.path.dirname(__file__), "face_index.db")
SIM_NO_FACE = 0.20      # 与参考质心低于此 → 判无人脸/非主脸
SIM_LOW = 0.35          # 高于 NO_FACE 但低于此 → 疑似非本人
# 已知出生日期（约束年份下界）；未列出的人无下界（用 2000）
BORN_MAP = {"皓祥": (2004, 9, 11), "运丰": (1979, 6, 26)}
# 已知照片最早年份（重分类年份下界）；早于它不可能出现该人照片
EARLIEST_MAP = {"运丰": 2002}
THIS_YEAR = datetime.datetime.now().year


def target_of(person):
    return os.path.join(BASE, person)

def born_of(person):
    return BORN_MAP.get(person)

def year_range(person):
    b = born_of(person)
    lo = b[0] if b else 2000
    lo = max(lo, EARLIEST_MAP.get(person, lo))
    return list(range(lo, THIS_YEAR + 1)), lo

# ---------- 通用工具 ----------
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

def current_year_of(path, target, lo):
    rel = os.path.relpath(path, target)
    m = re.match(r'(\d{4})', rel.split(os.sep)[0])
    if m:
        return int(m.group(1))
    # 首段非年份（如 others/）→ 回退文件名可靠日期；仍无则下界
    y = parse_reliable_year(os.path.basename(path), lo)
    return y if y else lo

def parse_reliable_year(name, lo):
    """信任显式日期模式：文件名 YYYY[-_/.]MM[-_/.]DD，或 wx_camera_/mmexport + 13位毫秒时间戳。
    注意：这是文件名日期（视作"照片时间水印"代理），与 EXIF 元数据分开处理。"""
    m = re.search(r'(?:19|20)\d{2}[-_/.]?\d{2}[-_/.]?\d{2}', name)
    if m:
        y = int(re.search(r'(?:19|20)\d{2}', m.group(0)).group(0))
        if lo <= y <= THIS_YEAR:
            return y
    m = re.search(r'(?:wx_camera_|mmexport)(\d{13})', name)
    if m:
        try:
            y = datetime.datetime.fromtimestamp(int(m.group(1)) / 1000).year
            if lo <= y <= THIS_YEAR:
                return y
        except Exception:
            pass
    return None

def load_ref_centroid(person):
    import sqlite3
    fc = sqlite3.connect(FACE_DB)
    row = fc.execute("SELECT id FROM persons WHERE name=?", (person,)).fetchone()
    if not row:
        fc.close()
        raise SystemExit(f"[错误] face_index.db 中没有人物「{person}」。可用: " +
                         ", ".join(r[0] for r in sqlite3.connect(FACE_DB).execute("SELECT name FROM persons").fetchall()))
    pid = row[0]
    rows = fc.execute("SELECT embedding FROM faces WHERE person_id=? AND embedding IS NOT NULL", (pid,)).fetchall()
    fc.close()
    vecs = [np.frombuffer(r[0], dtype=np.float32) for r in rows]
    if not vecs:
        raise SystemExit(f"[错误] 人物「{person}」在库中无 embedding，无法建参考质心。")
    return np.mean(vecs, axis=0)

def detect_all(photos, ref_centroid):
    from insightface.app import FaceAnalysis
    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=0)
    results = []
    for i, p in enumerate(photos):
        rec = {"path": p, "emb": None, "bbox": None, "sim": 0.0, "no_face": False,
               "reliable_year": None}
        try:
            arr = np.asarray(Image.open(p).convert("RGB"))
            bgr = arr[:, :, ::-1].copy()          # InsightFace 需要 BGR
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

def run_detect(person, target, lo, use_cache=False):
    """返回 dets。use_cache=True 且缓存存在时直接读缓存。"""
    pv = os.path.join(target, "_preview")
    os.makedirs(pv, exist_ok=True)
    cache = os.path.join(pv, "_detect.json")
    if use_cache and os.path.exists(cache):
        dets = json.load(open(cache, encoding="utf-8"))
        print(f"复用检测缓存 {len(dets)} 条")
        return dets
    photos = collect_photos(target)
    print(f"扫描到 {len(photos)} 张照片，开始人脸检测（CPU，约每50张十几秒）...")
    ref = load_ref_centroid(person)
    dets = detect_all(photos, ref)
    for d in dets:
        d["reliable_year"] = parse_reliable_year(os.path.basename(d["path"]), lo)
    json.dump(dets, open(cache, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"检测完成 {len(dets)} 张，写缓存 {cache}")
    return dets

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

def flag_of(d, sim):
    if d.get("no_face"):
        return "none"
    return "low" if sim < SIM_LOW else "ok"

# ---------- 预览页（可移植：全部相对路径）----------
def build_preview_html(rows, person):
    from collections import defaultdict
    by_year = defaultdict(list)
    for r in rows:
        by_year[r["year"]].append(r)
    fc = {"ok": "#1a7f37", "low": "#bc4c00", "none": "#cf222e"}
    ft = {"ok": person, "low": "疑似非本人", "none": "无人脸"}
    esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    n_ok = sum(1 for r in rows if r["flag"] == "ok")
    n_low = sum(1 for r in rows if r["flag"] == "low")
    n_none = sum(1 for r in rows if r["flag"] == "none")
    parts = ["""<!doctype html><html lang=zh><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>""" + esc(person) + """ 文件夹索引（可移植版）</title>
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
    parts.append(f"""<header><h1>{esc(person)} 文件夹索引（可移植版）</h1>
<div class=sum>
<span>总照片 <b>{len(rows)}</b></span>
<span>年份文件夹 <b>{len(by_year)}</b></span>
<span style="color:#1a7f37">{esc(person)}本人 <b>{n_ok}</b></span>
<span style="color:#bc4c00">疑似非本人 <b>{n_low}</b></span>
<span style="color:#cf222e">无人脸/非主脸 <b>{n_none}</b></span>
<span>生成 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
</div>
<div class=sum style="color:#57606a">年份=当前物理文件夹 · 缩略图=面部裁剪 · 全部相对路径，复制/移动到任意位置均可打开 · 点缩略图开原图</div>
</header>""")
    for y in sorted(by_year):
        items = by_year[y]
        parts.append(f"<div class=year><h2>{y} （{len(items)}）</h2><div class=grid>")
        for r in items:
            col = fc.get(r["flag"], "#6e7781")
            parts.append(
                f"<a class=card href='{r['orig_href']}'>"
                f"<img loading=lazy src='{r['thumb']}'>"
                f"<div class=cap><div class=nm>{esc(os.path.basename(r['abs']))}</div>"
                f"<span class=badge style='background:{col}'>{ft.get(r['flag'])} {r['sim']}</span></div></a>")
        parts.append("</div></div>")
    parts.append("</body></html>")
    return "\n".join(parts)

def write_index_outputs(target, rows, person):
    """写 index.html(可移植) + index.csv + review.csv。"""
    pv = os.path.join(target, "_preview")
    with open(os.path.join(pv, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_preview_html(rows, person))
    with open(os.path.join(pv, "index.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["相对路径", "年份", "相似度", "标记", "缩略图", "原图相对链接"])
        for r in rows:
            w.writerow([r["rel"], r["year"], r["sim"], r["flag"], r["thumb"], r["orig_href"]])
    review = [r for r in rows if r["flag"] in ("low", "none")]
    with open(os.path.join(pv, "review.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["文件", "当前年份", "相似度", "标记", "绝对路径"])
        for r in sorted(review, key=lambda x: x["sim"]):
            w.writerow([os.path.basename(r["abs"]), r["year"], r["sim"], r["flag"], r["abs"]])
    return len(review)

def dets_to_rows(dets, target, lo):
    """把检测结果转成预览行（年份=物理文件夹），并重建 thumbs。"""
    pv = os.path.join(target, "_preview")
    thumbs = os.path.join(pv, "thumbs")
    if os.path.isdir(thumbs):
        shutil.rmtree(thumbs)
    os.makedirs(thumbs, exist_ok=True)
    rows = []
    for i, d in enumerate(dets):
        y = current_year_of(d["path"], target, lo)
        make_thumb(d["path"], os.path.join(thumbs, f"{i:04d}.jpg"), d.get("bbox"))
        rel = os.path.relpath(d["path"], target).replace("\\", "/")
        sim = round(d.get("sim", 0.0), 3)
        rows.append({
            "i": i, "rel": rel, "abs": d["path"], "year": y, "sim": sim,
            "flag": flag_of(d, sim), "thumb": f"thumbs/{i:04d}.jpg",
            "orig_href": "../" + quote(rel),
        })
    return rows

def rows_from_cache(dets, target, lo):
    """仅读缓存重建行（不重生成缩略图，沿用已有 thumbs 扫描序 i）。"""
    rows = []
    for i, d in enumerate(dets):
        y = current_year_of(d["path"], target, lo)
        rel = os.path.relpath(d["path"], target).replace("\\", "/")
        sim = round(d.get("sim", 0.0), 3)
        rows.append({
            "i": i, "rel": rel, "abs": d["path"], "year": y, "sim": sim,
            "flag": flag_of(d, sim), "thumb": f"thumbs/{i:04d}.jpg",
            "orig_href": "../" + quote(rel),
        })
    return rows

# ==================== 功能 1：重建索引（不移动）====================
def cmd_reindex(person, use_cache=False):
    target = target_of(person)
    _, lo = year_range(person)
    dets = run_detect(person, target, lo, use_cache=use_cache)
    rows = dets_to_rows(dets, target, lo)
    n_review = write_index_outputs(target, rows, person)
    # 落盘检测缓存，供 reclassify 复用
    pv = os.path.join(target, "_preview")
    json.dump(dets, open(os.path.join(pv, "_detect.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(f"\n[重建索引完成] {person}")
    print(f"  总照片 {len(rows)} | 年份 {len(set(r['year'] for r in rows))}")
    print(f"  本人 {sum(1 for r in rows if r['flag']=='ok')} | 疑似 {sum(1 for r in rows if r['flag']=='low')} | 无脸 {sum(1 for r in rows if r['flag']=='none')}")
    print(f"  待核对 review.csv: {n_review}")
    print(f"  预览页: {os.path.join(target, '_preview', 'index.html')}")

# ==================== 功能 2：按外观推断年份重分类（移动）========
def infer_years(dets, years, lo, target):
    embs = {i: np.asarray(d["emb"], float) for i, d in enumerate(dets) if d.get("emb") is not None}
    assign, locked = {}, {}
    for i, d in enumerate(dets):
        ry = d.get("reliable_year")
        if ry and lo <= ry <= THIS_YEAR:
            locked[i] = ry; assign[i] = ry
        else:
            y0 = current_year_of(d["path"], target, lo)
            assign[i] = y0 if y0 in years else lo   # 当前年份低于下界→归入下界年
    proto = {}
    for _ in range(5):
        pools = {y: [] for y in years}
        for i, y in assign.items():
            if i in embs:
                pools[y].append(embs[i])
        for y in years:
            proto[y] = np.mean(pools[y], axis=0) if pools[y] else proto.get(y)
        changed = 0
        for i in embs:
            if i in locked:
                continue
            best_y, best_s = None, -2
            for y in years:
                if proto.get(y) is None:
                    continue
                s = cos(embs[i], proto[y])
                if s > best_s:
                    best_s, best_y = s, y
            if best_y is not None and best_y != assign[i]:
                changed += 1; assign[i] = best_y
        for i, d in enumerate(dets):
            if i not in embs:
                y0 = current_year_of(d["path"], target, lo)
                assign[i] = y0 if y0 in years else lo
        if changed == 0:
            break
    return assign

def read_exif_year(path):
    """读 EXIF 拍摄年份（DateTimeOriginal/Digitized/DateTime）。无效或异常返回 None。"""
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        im = Image.open(path)
        ex = im._getexif() or {}
        for tid, val in ex.items():
            if TAGS.get(tid) in ("DateTimeOriginal", "DateTimeDigitized", "DateTime"):
                m = re.search(r"(?:19|20)\d{2}", str(val))
                if m:
                    y = int(m.group(0))
                    if 1990 <= y <= THIS_YEAR:
                        return y
    except Exception:
        pass
    return None

def resolve_priority(dets, years, lo, target):
    """三级优先级定年份：EXIF元数据 > 文件名日期(水印代理) > 年龄推断(embedding EM)。
    返回 (assign, src)：assign[i]=年份，src[i]∈{meta,watermark,age,fallback}。
    - meta: EXIF 年份有效（lo≤y≤THIS_YEAR）
    - watermark: 无 EXIF 但文件名含可靠日期（wx_camera/YYYY-MM-DD 等）
    - age: 两者皆无，用已锁定照片的 embedding 均值原型做余弦最近推断（记 _sim 作置信）
    - fallback: 无 embedding 或原型为空，回退当前目录年份
    """
    assign, src = {}, {}
    for i, d in enumerate(dets):
        ey = read_exif_year(d["path"])
        if ey and lo <= ey <= THIS_YEAR:
            assign[i] = ey; src[i] = "meta"; continue
        fy = parse_reliable_year(os.path.basename(d["path"]), lo)
        if fy and fy in years:
            assign[i] = fy; src[i] = "watermark"; continue
        assign[i] = None; src[i] = "age"
    # 建 EM 原型（仅用已锁定照片的 embedding）
    proto = {}
    for i, d in enumerate(dets):
        if src[i] == "age" or d.get("emb") is None:
            continue
        proto.setdefault(assign[i], []).append(np.asarray(d["emb"], float))
    proto = {y: np.mean(v, axis=0) for y, v in proto.items() if v}
    # 对 age 类照片用原型推断
    for i, d in enumerate(dets):
        if src[i] != "age":
            continue
        if d.get("emb") is None or not proto:
            assign[i] = current_year_of(d["path"], target, lo); src[i] = "fallback"; continue
        emb = np.asarray(d["emb"], float)
        best_y, best_s = None, -2
        for y, p in proto.items():
            s = cos(emb, p)
            if s > best_s:
                best_s, best_y = s, y
        if best_y is None:
            assign[i] = current_year_of(d["path"], target, lo); src[i] = "fallback"
        else:
            assign[i] = best_y; src[i] = "age"; d["_sim"] = round(float(best_s), 3)
    return assign, src

def cmd_reclassify(person, assume_yes=False, dry_run=False, use_cache=False):
    target = target_of(person)
    years, lo = year_range(person)
    dets = run_detect(person, target, lo, use_cache=use_cache)
    assign = infer_years(dets, years, lo, target)
    # 汇总移动方案
    moves = []
    for i, d in enumerate(dets):
        y = assign[i]; src = d["path"]
        cur = current_year_of(src, target, lo)
        if y != cur:
            moves.append((cur, y, os.path.relpath(src, target).replace("\\", "/"), round(d.get("sim", 0.0), 3)))
    print(f"\n[重分类方案] {person} 共 {len(dets)} 张 | 将移动 {len(moves)} 张（其余 {len(dets)-len(moves)} 张年份不变）")
    if moves:
        from collections import Counter
        span = Counter((o, n) for o, n, _, _ in moves)
        print("  年份变更分布:")
        for (o, n), c in sorted(span.items()):
            print(f"    {o} → {n}: {c} 张")
        big = [(o, n, p, s) for o, n, p, s in moves if abs(n - o) >= 3]
        print(f"  大跨度（≥3 年）移动 {len(big)} 张（建议人工核对）:")
        for o, n, p, s in big[:40]:
            print(f"    {o}→{n}  sim={s}  {p}")
        if len(big) > 40:
            print(f"    ... 共 {len(big)} 张大跨度")
    if dry_run:
        print("\n[DRY-RUN] 未移动任何文件。复核方案后加 --yes 执行实际移动。")
        return
    if not assume_yes:
        print(f"[警告] 即将按外观推断【移动】{len(moves)} 张照片到年份文件夹（不可逆，但可经 undo_map.csv 还原）。")
        if input("确认继续？输入 y 执行，其他取消: ").strip().lower() != "y":
            print("已取消。"); return
    # 实际移动
    undo, moved = [], 0
    for i, d in enumerate(dets):
        y = assign[i]; src = d["path"]
        newdir = os.path.join(target, str(y)); os.makedirs(newdir, exist_ok=True)
        bn = os.path.basename(src); dst = os.path.join(newdir, bn)
        if os.path.abspath(src) != os.path.abspath(dst):
            if os.path.exists(dst):
                base, ext = os.path.splitext(bn)
                dst = os.path.join(newdir, f"{base}__{abs(hash(src))&0xffff:04x}{ext}")
            shutil.move(src, dst); undo.append((src, dst)); moved += 1
        d["path"] = dst          # 更新为新路径，供缩略图/预览
    pv = os.path.join(target, "_preview")
    json.dump(dets, open(os.path.join(pv, "_detect.json"), "w", encoding="utf-8"), ensure_ascii=False)
    with open(os.path.join(pv, "undo_map.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["original_abs", "new_abs"])
        for o, n in undo:
            w.writerow([o, n])
    rows = dets_to_rows(dets, target, lo)
    n_review = write_index_outputs(target, rows, person)
    print(f"\n[重分类完成] 移动 {moved} 张 | 待核对 {n_review} | 撤销映射 undo_map.csv")
    print(f"  预览页: {os.path.join(pv, 'index.html')}")

# ==================== 功能 2b：生成重分类「确认页」+ 执行确认的移动 ====================
def cmd_gen_reclassify(person, use_cache=False):
    """生成重分类确认页：列出所有「推断年≠当前年」的照片，逐张勾选确认移动。默认不勾选（安全）。"""
    target = target_of(person)
    years, lo = year_range(person)
    dets = run_detect(person, target, lo, use_cache=use_cache)
    assign, src = resolve_priority(dets, years, lo, target)
    # 重建 thumbs 保证与 dets 索引对齐（确认页缩略图用）
    pv = os.path.join(target, "_preview"); thumbs = os.path.join(pv, "thumbs")
    if os.path.isdir(thumbs): shutil.rmtree(thumbs)
    os.makedirs(thumbs, exist_ok=True)
    SRC_LABEL = {"meta": "元数据(EXIF)", "watermark": "时间水印(文件名)", "age": "年龄推断", "fallback": "当前目录"}
    cands = []
    for i, d in enumerate(dets):
        new = assign[i]
        rel = os.path.relpath(d["path"], target).replace("\\", "/")
        top = rel.split("/")[0]
        in_year = bool(re.match(r"\d{4}", top))
        cur_num = current_year_of(d["path"], target, lo)
        cur_disp = cur_num if in_year else top
        if in_year and new == cur_num:
            continue
        # EXIF 与文件名日期冲突时标注，避免相机时钟错误导致的误移
        srclabel = SRC_LABEL.get(src[i], src[i])
        if src[i] == "meta":
            fy = parse_reliable_year(os.path.basename(d["path"]), lo)
            if fy and fy != new:
                srclabel = f"元数据(EXIF {new})⚠文件名{fy}"
        make_thumb(d["path"], os.path.join(thumbs, f"{i:04d}.jpg"), d.get("bbox"))
        cands.append({
            "rel": rel,
            "abs": d["path"], "cur": cur_disp, "new": new,
            "sim": round(d.get("sim", 0.0), 3), "span": abs(new - cur_num),
            "src": src[i], "srclabel": srclabel,
            "conf": round(d.get("_sim", 0.0), 3) if src[i] == "age" else "",
            "thumb": f"thumbs/{i:04d}.jpg",
        })
    # 持久化候选（含全部字段），供 apply 直接读，不必重算
    json.dump(cands, open(os.path.join(pv, "_reclassify_cands.json"), "w", encoding="utf-8"), ensure_ascii=False)
    data_json = json.dumps(cands, ensure_ascii=False)
    n_big = sum(1 for c in cands if c["span"] >= 3)
    hi = THIS_YEAR
    html = _RECLASSIFY_HTML.replace("__PERSON__", person).replace("__TOTAL__", str(len(cands)))\
        .replace("__NBIG__", str(n_big)).replace("__NSMALL__", str(len(cands) - n_big))\
        .replace("__LO__", str(lo)).replace("__HI__", str(hi)).replace("__DATA__", data_json)
    out = os.path.join(pv, "reclassify_review.html")
    open(out, "w", encoding="utf-8").write(html)
    print(f"已生成重分类确认页: {out}（{len(cands)} 张待移动，其中大跨度≥3年 {n_big} 张）")
    print("  逐张勾选要移动的项 → 导出 reclassify_decisions.json，再用「applyreclassify」执行。")
    print("  （默认全部不勾选，安全优先；可一键「全选小跨度」再手动勾大跨度）")

def cmd_apply_reclassify(person, list_path):
    """读确认页导出的 reclassify_decisions.json，仅移动用户勾选的项。"""
    target = target_of(person)
    _, lo = year_range(person)
    if not os.path.exists(list_path):
        print(f"[错误] 清单不存在: {list_path}"); return
    items = json.load(open(list_path, encoding="utf-8"))
    exist = [it for it in items if os.path.isfile(it["abs"])]
    print(f"清单 {len(items)} 张，存在 {len(exist)} 张，缺失 {len(items)-len(exist)} 张")
    if not exist:
        print("无可处理文件。"); return
    print("\n将移动：")
    for it in exist:
        uy = it.get("user_year")
        new = uy if (isinstance(uy, int) and 1900 <= uy <= 2100) else it["new"]
        print(f"  {it['cur']} → {new}  sim={it.get('sim')}  {os.path.basename(it['abs'])}")
    undo, moved, src2dst = [], 0, {}
    for it in exist:
        uy = it.get("user_year")
        new = uy if (isinstance(uy, int) and 1900 <= uy <= 2100) else it["new"]
        src = it["abs"]
        newdir = os.path.join(target, str(new)); os.makedirs(newdir, exist_ok=True)
        bn = os.path.basename(src); dst = os.path.join(newdir, bn)
        if os.path.abspath(src) != os.path.abspath(dst):
            if os.path.exists(dst):
                base, ext = os.path.splitext(bn)
                dst = os.path.join(newdir, f"{base}__{abs(hash(src))&0xffff:04x}{ext}")
            shutil.move(src, dst); undo.append((src, dst)); src2dst[os.path.abspath(src)] = dst; moved += 1
    print(f"\n移动 {moved} 张")
    # 更新 _detect.json 路径 + 重建预览
    pv = os.path.join(target, "_preview"); cache = os.path.join(pv, "_detect.json")
    if os.path.exists(cache):
        dets = json.load(open(cache, encoding="utf-8"))
        for d in dets:
            a = os.path.abspath(d["path"])
            if a in src2dst:
                d["path"] = src2dst[a]
        json.dump(dets, open(cache, "w", encoding="utf-8"), ensure_ascii=False)
        rows = dets_to_rows(dets, target, lo)
        n_review = write_index_outputs(target, rows, person)
        print(f"重建预览：{len(rows)} 张 | 待核对 {n_review}")
    if undo:
        with open(os.path.join(pv, "undo_map.csv"), "a", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            for o, n in undo:
                w.writerow([o, n])
        print("撤销映射已追加到 undo_map.csv")
    print(f"预览页: {os.path.join(pv, 'index.html')}")

_RECLASSIFY_HTML = r"""<!doctype html><html lang=zh><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>__PERSON__ · 重分类确认页（__TOTAL__ 张待移动）</title>
<style>
*{box-sizing:border-box}
body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f6f8fa;color:#1f2328}
header{position:sticky;top:0;background:#fff;border-bottom:1px solid #d0d7de;padding:10px 16px;z-index:20}
h1{font-size:16px;margin:0 0 6px}
.bar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;font-size:13px}
button{font-size:13px;padding:5px 12px;border:1px solid #d0d7de;border-radius:6px;background:#f6f8fa;cursor:pointer}
button.primary{background:#0969da;color:#fff;border-color:#0969da}
.tip{color:#57606a;font-size:12px;margin-top:4px}
.main{display:flex;min-height:calc(100vh - 90px)}
#side{width:180px;flex:none;padding:12px;border-right:1px solid #d0d7de;background:#fff;position:sticky;top:90px;height:calc(100vh - 90px);overflow:auto}
#side label{display:block;font-size:13px;margin:6px 0;cursor:pointer}
#grid{flex:1;padding:14px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px}
.card{position:relative;background:#fff;border:1px solid #d0d7de;border-radius:8px;overflow:hidden}
.card.big{border-color:#cf222e;border-width:2px}
.card img{width:100%;height:180px;object-fit:cover;display:block;background:#eee;cursor:zoom-in}
#lb{position:fixed;inset:0;background:rgba(0,0,0,.88);z-index:100;display:none;align-items:center;justify-content:center;flex-direction:column}
#lb.on{display:flex}
#lb img{max-width:94vw;max-height:86vh;object-fit:contain;box-shadow:0 4px 30px rgba(0,0,0,.6)}
#lb .lbcap{color:#fff;font-size:13px;margin-top:10px;text-align:center;word-break:break-all;max-width:90vw}
#lb .lbx{position:absolute;top:14px;right:20px;color:#fff;font-size:30px;cursor:pointer;line-height:1;user-select:none}
#lb .lberr{color:#ff9;font-size:13px;margin-top:8px}
.cap{padding:5px 7px;font-size:11px;line-height:1.3}
.cap .nm{font-weight:600;word-break:break-all}
.move{display:flex;align-items:center;gap:4px;font-size:12px;margin-top:3px}
.arr{color:#0969da;font-weight:700}
.pill{display:inline-block;padding:1px 7px;border-radius:10px;color:#fff;font-size:11px}
.chk{position:absolute;top:6px;right:6px;width:22px;height:22px;cursor:pointer;accent-color:#0969da}
.yr{width:62px;padding:2px 4px;font-size:13px;border:1px solid #d0d7de;border-radius:4px;text-align:center}
.yr:focus{outline:2px solid #0969da;border-color:#0969da}
.hint{color:#57606a;font-size:12px;margin-left:6px}
.srcbadge{display:inline-block;padding:1px 7px;border-radius:10px;color:#fff;font-size:11px;margin-top:4px;white-space:nowrap}
</style></head><body>
<header>
<h1>__PERSON__ · 重分类确认页（__TOTAL__ 张待移动，其中大跨度≥3年 __NBIG__ 张）</h1>
<div class=bar>
<button class=primary onclick="exportList()">导出移动清单（<span id=selcnt>0</span>）</button>
<button onclick="selSmall()">全选小跨度(≤2年)</button>
<button onclick="selBig()">全选大跨度(≥3年)</button>
<button onclick="clearSel()">清空选择</button>
<span class=tip>年份判定优先级：<b>元数据(EXIF) &gt; 时间水印(文件名) &gt; 年龄推断</b>。徽章绿=EXIF硬证据 / 蓝=文件名日期 / 橙=年龄推断(低置信,可手填)。勾选要移动的项，可在「→」后改目标年份。默认不勾选。</span>
</div>
</header>
<div class=main>
<div id=side>
<b>筛选</b>
<label><input type=radio name=f value=all checked onchange="render()"> 全部 __TOTAL__</label>
<label><input type=radio name=f value=big onchange="render()"> 大跨度≥3年 (__NBIG__)</label>
<label><input type=radio name=f value=small onchange="render()"> 小跨度≤2年 (__NSMALL__)</label>
<hr><b>搜索文件名</b>
<input id=search placeholder="含关键词…" oninput="render()" style="width:100%;padding:4px;margin-top:4px">
</div>
<div id=grid><div id=list></div></div>
</div>
<div id=lb onclick="if(event.target.id==='lb')closeLB()">
<span class=lbx onclick="closeLB()">×</span>
<img id=lbimg src="" alt="">
<div class=lbcap id=lbcap></div>
</div>
<script>
const DATA = __DATA__;
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
const checked = new Set();
function cardHTML(r){
  const big = r.span>=3;
  const srcColor={meta:'#1a7f37',watermark:'#0969da',age:'#bc4c00',fallback:'#57606a'}[r.src]||'#57606a';
  return `<div class="card${big?' big':''}"><input class=chk type=checkbox onchange="onChk(this)" data-abs="${esc(r.abs)}">
    <img loading=lazy src="${r.thumb}" data-full="${esc('../'+r.rel)}" data-nm="${esc(r.rel)}" onclick="openLB(this)">
    <div class=cap><div class=nm>${esc(r.rel.split('/').pop())}</div>
    <div class=move><span>${r.cur}</span><span class=arr>→</span><input class=yr type=number min="__LO__" max="__HI__" value="${r.new}" data-abs="${esc(r.abs)}"><span class=hint>年</span>
      <span class=pill style="background:${big?'#cf222e':'#57606a'}">${big?'⚠大跨度':'跨'+r.span+'年'}</span></div>
    <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-top:3px">
      <span class=srcbadge style="background:${srcColor}">${r.srclabel}${r.conf?(' · sim '+r.conf):''}</span>
      <span style="color:#57606a;font-size:12px">现相似度 ${r.sim}</span>
    </div></div></div>`;
}
function render(){
  const f = document.querySelector('input[name=f]:checked').value;
  const q = document.getElementById('search').value.toLowerCase();
  const byYear = {};
  DATA.forEach(r=>{
    if(f==='big' && r.span<3) return;
    if(f==='small' && r.span>=3) return;
    if(q && !r.rel.toLowerCase().includes(q)) return;
    (byYear[r.cur] = byYear[r.cur]||[]).push(r);
  });
  let html='';
  Object.keys(byYear).sort().forEach(y=>{
    html += `<div style="margin:10px 0 4px;font-size:14px;font-weight:600;border-left:4px solid #0969da;padding-left:8px">当前 ${y} （${byYear[y].length}）</div><div class=cards>`;
    html += byYear[y].map(cardHTML).join('') + `</div>`;
  });
  document.getElementById('list').innerHTML = html;
  document.querySelectorAll('.chk').forEach(c=>{ if(checked.has(c.dataset.abs)) c.checked=true; });
  syncCnt();
}
function openLB(img){
  const lb=document.getElementById('lb'), li=document.getElementById('lbimg'), lc=document.getElementById('lbcap');
  li.src=img.dataset.full;
  li.onerror=function(){ lc.innerHTML=img.dataset.nm+'<div class=lberr>原图未找到（须与年份文件夹整包一起打开）</div>'; };
  li.onload=function(){ lc.textContent=img.dataset.nm; };
  lb.classList.add('on');
}
function closeLB(){ document.getElementById('lb').classList.remove('on'); document.getElementById('lbimg').src=''; }
document.addEventListener('keydown',e=>{ if(e.key==='Escape')closeLB(); });
function onChk(c){ if(c.checked) checked.add(c.dataset.abs); else checked.delete(c.dataset.abs); syncCnt(); }
function syncCnt(){ document.getElementById('selcnt').textContent = checked.size; }
function selSmall(){ document.querySelectorAll('.chk').forEach(c=>{ const r=DATA.find(x=>x.abs===c.dataset.abs); if(r && r.span<3){c.checked=true;checked.add(c.dataset.abs);} }); syncCnt(); }
function selBig(){ document.querySelectorAll('.chk').forEach(c=>{ const r=DATA.find(x=>x.abs===c.dataset.abs); if(r && r.span>=3){c.checked=true;checked.add(c.dataset.abs);} }); syncCnt(); }
function clearSel(){ checked.clear(); document.querySelectorAll('.chk').forEach(c=>c.checked=false); syncCnt(); }
function exportList(){
  if(checked.size===0){ alert('还没勾选任何照片'); return; }
  const arr = DATA.filter(r=>checked.has(r.abs)).map(r=>{
    const inp = [...document.querySelectorAll('input.yr')].find(x=>x.dataset.abs===r.abs);
    let uy = inp ? parseInt(inp.value,10) : NaN;
    if(isNaN(uy) || uy < __LO__ || uy > __HI__){ uy = r.new; }
    return {rel:r.rel, abs:r.abs, cur:r.cur, new:r.new, user_year:uy, sim:r.sim};
  });
  const blob = new Blob([JSON.stringify(arr,null,2)], {type:'application/json'});
  const a = document.createElement('a'); a.href=URL.createObjectURL(blob);
  a.download='reclassify_decisions.json'; a.click();
  alert('已导出 '+arr.length+' 张待移动清单（目标年以你填的为准，未填则用默认）。');
}
render();
</script></body></html>"""

# ==================== 功能 3：生成删除审查页 ====================
def cmd_gen_delete(person):
    target = target_of(person)
    _, lo = year_range(person)
    pv = os.path.join(target, "_preview")
    cache = os.path.join(pv, "_detect.json")
    if not os.path.exists(cache):
        print("[提示] 无检测缓存，先跑「重建索引」。"); return
    dets = json.load(open(cache, encoding="utf-8"))
    rows = rows_from_cache(dets, target, lo)
    data_json = json.dumps([{"rel": r["rel"], "abs": r["abs"], "year": r["year"],
                             "sim": r["sim"], "flag": r["flag"], "thumb": r["thumb"]} for r in rows],
                           ensure_ascii=False)
    n_low = sum(1 for r in rows if r["flag"] == "low")
    n_none = sum(1 for r in rows if r["flag"] == "none")
    n_ok = sum(1 for r in rows if r["flag"] == "ok")
    html = _DELETE_HTML.replace("__PERSON__", person).replace("__TOTAL__", str(len(rows)))\
        .replace("__NLOW__", str(n_low)).replace("__NNONE__", str(n_none))\
        .replace("__NOK__", str(n_ok)).replace("__DATA__", data_json)
    out = os.path.join(pv, "delete_review.html")
    open(out, "w", encoding="utf-8").write(html)
    print(f"已生成删除审查页: {out}（{len(rows)} 张）")
    print("  勾选混入照片 → 导出 delete_list.json，再用「执行删除清单」。")

# ==================== 功能 4：执行删除清单 ====================
def cmd_apply_delete(person, list_path, mode):
    """mode: 'reject' 移到 _rejected（可恢复）; 'purge' 永久删除（不可恢复）"""
    target = target_of(person)
    _, lo = year_range(person)
    if not os.path.exists(list_path):
        print(f"[错误] 清单不存在: {list_path}"); return
    items = json.load(open(list_path, encoding="utf-8"))
    abses = [it["abs"] for it in items]
    exist = [p for p in abses if os.path.isfile(p)]
    print(f"清单 {len(abses)} 张，存在 {len(exist)} 张，缺失 {len(abses)-len(exist)} 张")
    if not exist:
        print("无可处理文件。"); return
    print("\n将处理：")
    for p in exist:
        print("  " + os.path.relpath(p, target))
    if mode == "purge":
        print(f"\n[⚠️ 永久删除] {len(exist)} 张，不进回收站、不可恢复！")
        if input(f'确认请输入人物名「{person}」: ').strip() != person:
            print("已取消。"); return
        done = 0
        for p in exist:
            try:
                os.remove(p); done += 1
            except Exception as e:
                print(f"  FAIL {p}: {e}")
        print(f"永久删除 {done}/{len(exist)}")
    else:  # reject 移到 _rejected
        rej = os.path.join(target, "_rejected"); os.makedirs(rej, exist_ok=True)
        done = 0
        for p in exist:
            bn = os.path.basename(p); dst = os.path.join(rej, bn)
            if os.path.exists(dst):
                base, ext = os.path.splitext(bn)
                dst = os.path.join(rej, f"{base}__{abs(hash(p))&0xffff:04x}{ext}")
            try:
                shutil.move(p, dst); done += 1
            except Exception as e:
                print(f"  FAIL {p}: {e}")
        print(f"移到 _rejected {done}/{len(exist)}（可恢复）")
    # 重建索引（重检剩余）
    print("\n重建索引中...")
    cmd_reindex(person)

# ==================== 功能 5：仅重生成可移植预览 ====================
def cmd_regen_html(person):
    target = target_of(person)
    _, lo = year_range(person)
    pv = os.path.join(target, "_preview")
    cache = os.path.join(pv, "_detect.json")
    if not os.path.exists(cache):
        print("[提示] 无检测缓存，先跑「重建索引」。"); return
    dets = json.load(open(cache, encoding="utf-8"))
    rows = rows_from_cache(dets, target, lo)
    n_review = write_index_outputs(target, rows, person)
    print(f"[已重生成可移植预览] {len(rows)} 张 | 待核对 {n_review}")
    print(f"  {os.path.join(pv, 'index.html')}")

# ---------- 删除审查页 HTML 模板（占位符替换）----------
_DELETE_HTML = r"""<!doctype html><html lang=zh><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>__PERSON__ · 删除审查页（全部 __TOTAL__ 张）</title>
<style>
*{box-sizing:border-box}
body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f6f8fa;color:#1f2328}
header{position:sticky;top:0;background:#fff;border-bottom:1px solid #d0d7de;padding:10px 16px;z-index:20}
h1{font-size:16px;margin:0 0 6px}
.bar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;font-size:13px}
button{font-size:13px;padding:5px 12px;border:1px solid #d0d7de;border-radius:6px;background:#f6f8fa;cursor:pointer}
button.primary{background:#cf222e;color:#fff;border-color:#cf222e}
.tip{color:#57606a;font-size:12px;margin-top:4px}
.main{display:flex;min-height:calc(100vh - 90px)}
#side{width:170px;flex:none;padding:12px;border-right:1px solid #d0d7de;background:#fff;position:sticky;top:90px;height:calc(100vh - 90px);overflow:auto}
#side label{display:block;font-size:13px;margin:6px 0;cursor:pointer}
#grid{flex:1;padding:14px}
.year{margin:10px 0 4px;font-size:14px;font-weight:600;border-left:4px solid #0969da;padding-left:8px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px}
.card{position:relative;background:#fff;border:1px solid #d0d7de;border-radius:8px;overflow:hidden}
.card img{width:100%;height:170px;object-fit:cover;display:block;background:#eee;cursor:zoom-in}
#lb{position:fixed;inset:0;background:rgba(0,0,0,.88);z-index:100;display:none;align-items:center;justify-content:center;flex-direction:column}
#lb.on{display:flex}
#lb img{max-width:94vw;max-height:86vh;object-fit:contain;box-shadow:0 4px 30px rgba(0,0,0,.6)}
#lb .lbcap{color:#fff;font-size:13px;margin-top:10px;text-align:center;word-break:break-all;max-width:90vw}
#lb .lbx{position:absolute;top:14px;right:20px;color:#fff;font-size:30px;cursor:pointer;line-height:1;user-select:none}
#lb .lberr{color:#ff9;font-size:13px;margin-top:8px}
.cap{padding:5px 7px;font-size:11px;line-height:1.3}
.cap .nm{font-weight:600;word-break:break-all}
.chk{position:absolute;top:6px;right:6px;width:22px;height:22px;cursor:pointer;accent-color:#cf222e}
.pill{display:inline-block;padding:1px 7px;border-radius:10px;color:#fff;font-size:11px}
</style></head><body>
<header>
<h1>__PERSON__ · 删除审查页（全部 __TOTAL__ 张）</h1>
<div class=bar>
<button class=primary onclick="exportList()">导出删除清单（<span id=selcnt>0</span>）</button>
<button onclick="selectAll()">全选当前筛选</button>
<button onclick="clearSel()">清空选择</button>
<span class=tip>勾选混入照片 → 导出 delete_list.json 发回执行删除。</span>
</div>
</header>
<div class=main>
<div id=side>
<b>筛选</b>
<label><input type=radio name=f value=all checked onchange="render()"> 全部 __TOTAL__</label>
<label><input type=radio name=f value=low onchange="render()"> 疑似非本人 (__NLOW__)</label>
<label><input type=radio name=f value=none onchange="render()"> 无人脸/非主脸 (__NNONE__)</label>
<label><input type=radio name=f value=ok onchange="render()"> 本人 (__NOK__)</label>
<hr><b>搜索文件名</b>
<input id=search placeholder="含关键词…" oninput="render()" style="width:100%;padding:4px;margin-top:4px">
</div>
<div id=grid><div id=list></div></div>
</div>
<div id=lb onclick="if(event.target.id==='lb')closeLB()">
<span class=lbx onclick="closeLB()">×</span>
<img id=lbimg src="" alt="">
<div class=lbcap id=lbcap></div>
</div>
<script>
const DATA = __DATA__;
const fc = {ok:'#1a7f37', low:'#bc4c00', none:'#cf222e'};
const ft = {ok:'本人', low:'疑似非本人', none:'无人脸'};
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
const checked = new Set();
function cardHTML(r){
  return `<div class=card><input class=chk type=checkbox onchange="onChk(this)" data-abs="${esc(r.abs)}">
    <img loading=lazy src="${r.thumb}" data-full="${esc('../'+r.rel)}" data-nm="${esc(r.rel)}" onclick="openLB(this)">
    <div class=cap><div class=nm>${esc(r.rel.split('/').pop())}</div>
    <span class=pill style="background:${fc[r.flag]}">${ft[r.flag]} ${r.sim}</span>
    <div style="color:#57606a">${r.year}</div></div></div>`;
}
function render(){
  const f = document.querySelector('input[name=f]:checked').value;
  const q = document.getElementById('search').value.toLowerCase();
  const byYear = {};
  DATA.forEach(r=>{
    if(f!=='all' && r.flag!==f) return;
    if(q && !r.rel.toLowerCase().includes(q)) return;
    (byYear[r.year] = byYear[r.year]||[]).push(r);
  });
  let html='';
  Object.keys(byYear).sort().forEach(y=>{
    html += `<div class=year>${y} （${byYear[y].length}）</div><div class=cards>`;
    html += byYear[y].map(cardHTML).join('') + `</div>`;
  });
  document.getElementById('list').innerHTML = html;
  document.querySelectorAll('.chk').forEach(c=>{ if(checked.has(c.dataset.abs)) c.checked=true; });
  syncCnt();
}
function openLB(img){
  const lb=document.getElementById('lb'), li=document.getElementById('lbimg'), lc=document.getElementById('lbcap');
  li.src=img.dataset.full;
  li.onerror=function(){ lc.innerHTML=img.dataset.nm+'<div class=lberr>原图未找到（须与年份文件夹整包一起打开）</div>'; };
  li.onload=function(){ lc.textContent=img.dataset.nm; };
  lb.classList.add('on');
}
function closeLB(){ document.getElementById('lb').classList.remove('on'); document.getElementById('lbimg').src=''; }
document.addEventListener('keydown',e=>{ if(e.key==='Escape')closeLB(); });
function onChk(c){ if(c.checked) checked.add(c.dataset.abs); else checked.delete(c.dataset.abs); syncCnt(); }
function syncCnt(){ document.getElementById('selcnt').textContent = checked.size; }
function selectAll(){ document.querySelectorAll('.chk').forEach(c=>{c.checked=true; checked.add(c.dataset.abs);}); syncCnt(); }
function clearSel(){ checked.clear(); document.querySelectorAll('.chk').forEach(c=>c.checked=false); syncCnt(); }
function exportList(){
  if(checked.size===0){ alert('还没勾选任何照片'); return; }
  const arr = DATA.filter(r=>checked.has(r.abs)).map(r=>({rel:r.rel, abs:r.abs, year:r.year, sim:r.sim}));
  const blob = new Blob([JSON.stringify(arr,null,2)], {type:'application/json'});
  const a = document.createElement('a'); a.href=URL.createObjectURL(blob);
  a.download='delete_list.json'; a.click();
  alert('已导出 '+arr.length+' 张待删除清单。');
}
render();
</script></body></html>"""

# ==================== 交互菜单 ====================
def list_persons():
    import sqlite3
    try:
        rows = sqlite3.connect(FACE_DB).execute(
            "SELECT name,(SELECT COUNT(*) FROM faces WHERE person_id=persons.id) FROM persons ORDER BY name").fetchall()
        return [(n, c) for n, c in rows]
    except Exception:
        return []

def interactive():
    print("=" * 52)
    print(" 人物照片文件夹 统一工具  photo_tool.py")
    print("=" * 52)
    persons = list_persons()
    if persons:
        print("库中人物：", "  ".join(f"{n}({c})" for n, c in persons))
    person = input("\n请输入人物名（默认 皓祥）: ").strip() or "皓祥"
    target = target_of(person)
    if not os.path.isdir(target):
        print(f"[警告] 目录不存在: {target}")
    print(f"\n目标文件夹: {target}")
    b = born_of(person)
    print(f"出生约束: {'%d-%02d-%02d' % b if b else '无（年份下界 2000）'}")
    print("""
选择操作：
  1  重建索引（尊重物理文件夹，不移动文件）★常用
  2  按外观推断年份重分类（会移动文件，慎用）
  3  生成删除审查页（勾选混入照片导出清单）
  4  执行删除清单（永久删 / 移到 _rejected）
  5  仅重生成可移植预览页（不重检测，秒出）
  0  退出
""")
    ch = input("输入编号: ").strip()
    if ch == "1":
        cmd_reindex(person)
    elif ch == "2":
        cmd_reclassify(person)
    elif ch == "3":
        cmd_gen_delete(person)
    elif ch == "4":
        lp = input("delete_list.json 路径: ").strip().strip('"')
        m = input("方式 [1] 移到_rejected(可恢复,默认) / [2] 永久删除: ").strip()
        cmd_apply_delete(person, lp, "purge" if m == "2" else "reject")
    elif ch == "5":
        cmd_regen_html(person)
    else:
        print("已退出。")

def main():
    ap = argparse.ArgumentParser(description="人物照片文件夹统一工具")
    ap.add_argument("--person", help="人物名（如 皓祥）")
    ap.add_argument("--action", choices=["reindex", "reclassify", "genreclassify", "applyreclassify", "gendelete", "applydelete", "regenhtml"],
                    help="操作")
    ap.add_argument("--list", dest="list_path", help="applydelete 的 delete_list.json 路径")
    ap.add_argument("--mode", choices=["reject", "purge"], default="reject",
                    help="applydelete 方式：reject=移_rejected(默认) / purge=永久删")
    ap.add_argument("--yes", action="store_true", help="reclassify 跳过确认直接移动")
    ap.add_argument("--dry-run", action="store_true", help="reclassify 只算方案不移动（默认安全）")
    ap.add_argument("--use-cache", action="store_true", help="reclassify/reindex 复用 _detect.json 缓存，省去重检")
    args = ap.parse_args()
    if not args.action or not args.person:
        interactive(); return
    if args.action == "reindex":
        cmd_reindex(args.person, use_cache=args.use_cache)
    elif args.action == "reclassify":
        cmd_reclassify(args.person, assume_yes=args.yes, dry_run=args.dry_run, use_cache=args.use_cache)
    elif args.action == "genreclassify":
        cmd_gen_reclassify(args.person, use_cache=args.use_cache)
    elif args.action == "applyreclassify":
        if not args.list_path:
            print("[错误] applyreclassify 需 --list 路径"); return
        cmd_apply_reclassify(args.person, args.list_path)
    elif args.action == "gendelete":
        cmd_gen_delete(args.person)
    elif args.action == "applydelete":
        if not args.list_path:
            print("[错误] applydelete 需 --list 路径"); return
        cmd_apply_delete(args.person, args.list_path, args.mode)
    elif args.action == "regenhtml":
        cmd_regen_html(args.person)

if __name__ == "__main__":
    main()
