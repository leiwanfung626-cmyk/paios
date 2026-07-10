#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_person_folder.py — 文件夹级审计：去重 + 人脸核验 + 预览索引

对某个"已按人物导出"的文件夹（如 E:\待整理照片\皓祥）做：
  1. 内容哈希去重（重复移到 _duplicates/，原结构不动）
  2. 重新跑 InsightFace，逐张与 face_index.db 中该人物的参考向量比对
     -> 四级判定：皓祥 / 存疑 / 非皓祥(混入) / 无人脸
  3. 生成 _preview/index.html（按年份分组缩略图画廊 + 状态色标 + 点开原图）
     + _preview/index.csv

用法：
  python audit_person_folder.py --person 皓祥 --target "E:\待整理照片\皓祥"
  python audit_person_folder.py --person 运丰 --target "E:\待整理照片\运丰"
"""
import argparse
import os
import re
import sqlite3
import sys
import time
import shutil
import hashlib
from datetime import datetime

import numpy as np
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FACE_DB = os.path.join(HERE, "face_index.db")
PHOTO_DB = os.path.join(ROOT, "database", "photo_index.db")

EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tif", ".tiff"}
SIM_CONFIRM = 0.35   # >= 此值 => 皓祥
SIM_DOUBT = 0.30     # 此值~CONFIRM => 存疑; 低于 => 非皓祥


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def content_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_year(path, pc):
    """返回 (year_or_None, source)。优先级：EXIF > 文件名显式日期 > 微信时间戳 > DB basename兜底。
    source 用于判断年份是否可靠（DB 兜底对短名易误匹配，移动时仅采纳 exif/filename/wechat）。"""
    import re
    bn = os.path.basename(path)
    # 1) EXIF（拍摄时间最权威）
    try:
        with Image.open(path) as im:
            ex = im.getexif()
            for tid in (36867, 306):
                v = ex.get(tid)
                if v:
                    y = str(v)[:4]
                    if y.isdigit() and 1990 <= int(y) <= 2026:
                        return y, "exif"
    except Exception:
        pass
    # 2) 微信相机时间戳 wx_camera_<13位毫秒epoch>（须在通用文件名正则前，避免误匹配子串）
    wm = re.search(r"wx_camera_(\d{13})", bn)
    if wm:
        try:
            import datetime as _dt
            y = _dt.datetime.fromtimestamp(int(wm.group(1)) / 1000).year
            if 1990 <= y <= 2026:
                return str(y), "wechat"
        except Exception:
            pass
    # 3) 文件名显式日期 YYYY-MM-DD / YYYYMMDD
    m = re.search(r"(?:19|20)\d{2}[-_/]?\d{1,2}[-_/]?\d{1,2}", bn)
    if m:
        y = re.search(r"(?:19|20)\d{2}", m.group(0)).group(0)
        return y, "filename"
    # 4) DB basename 反查（兜底，短名易误匹配）
    try:
        row = pc.execute("SELECT date FROM photos WHERE path LIKE ?", (f"%{bn}",)).fetchone()
        if row and row[0] and len(row[0]) >= 4 and row[0][:4].isdigit():
            return row[0][:4], "db"
    except Exception:
        pass
    return None, None
    return None


def load_app():
    from insightface.app import FaceAnalysis
    app = FaceAnalysis(name="buffalo_l")
    app.prepare(ctx_id=-1, det_size=(640, 640))
    return app


def load_image_rgb(path):
    try:
        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im)
            if im.mode in ("RGBA", "P", "LA"):
                im = im.convert("RGB")
            return np.asarray(im.convert("RGB"))
    except Exception:
        return None


def collect_images(target):
    out = []
    for root, dirs, names in os.walk(target):
        dirs[:] = [d for d in dirs if not d.startswith("_")]  # 跳过 _duplicates/_preview
        for n in names:
            if os.path.splitext(n)[1].lower() in EXTS:
                out.append(os.path.join(root, n))
    return sorted(out)


def make_thumb(src, dest, long_side=260):
    try:
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            im.thumbnail((long_side, long_side))
            im.save(dest, "JPEG", quality=82)
        return True
    except Exception:
        return False


def _write_outputs(results, PREVIEW, PERSON, dup_count):
    """重建 CSV + HTML 预览（与核验解耦，支持 --from-cache）。"""
    import csv
    csv_path = os.path.join(PREVIEW, "index.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["相对路径", "年份", "判定", "最大相似度", "人脸数", "绝对路径"])
        for r in results:
            w.writerow([r["rel"], r["year"], r["verdict"], r["sim"], r["nface"], r["path"]])

    from collections import Counter
    vc = Counter(r["verdict"] for r in results)
    by_year = {}
    for r in results:
        by_year.setdefault(r["year"], []).append(r)

    color = {"皓祥": "#1a7f37", "存疑": "#bc4c00", "非皓祥": "#cf222e",
             "无人脸": "#6e7781", "读取失败": "#6e7781"}
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    parts = []
    parts.append(f"""<!doctype html><html lang=zh><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{esc(PERSON)} 文件夹审计预览</title>
<style>
body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f6f8fa;color:#1f2328}}
header{{position:sticky;top:0;background:#fff;border-bottom:1px solid #d0d7de;padding:12px 18px;z-index:10}}
h1{{font-size:18px;margin:0 0 6px}}
.sum{{font-size:13px;color:#57606a;display:flex;gap:14px;flex-wrap:wrap}}
.sum b{{color:#1f2328}}
.year{{margin:18px;}}
.year h2{{font-size:15px;border-left:4px solid #0969da;padding-left:8px;margin-bottom:10px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}}
.card{{background:#fff;border:1px solid #d0d7de;border-radius:8px;overflow:hidden;text-decoration:none;color:inherit;display:block}}
.card img{{width:100%;height:150px;object-fit:cover;display:block;background:#eee}}
.cap{{padding:6px 8px;font-size:11px;line-height:1.35}}
.cap .nm{{font-weight:600;word-break:break-all}}
.badge{{display:inline-block;margin-top:3px;padding:1px 7px;border-radius:10px;color:#fff;font-size:11px}}
.sim{{color:#57606a}}
.warn{{background:#fff8c5;border:1px solid #d4a72c;padding:10px 14px;margin:10px 18px;border-radius:6px;font-size:13px}}
</style></head><body>""")

    parts.append(f"""<header><h1>{esc(PERSON)} 文件夹审计预览</h1>
<div class=sum>
<span>总照片 <b>{len(results)}</b></span>
<span>去重移除 <b>{dup_count}</b></span>
<span style="color:{color['皓祥']}">皓祥 <b>{vc.get('皓祥',0)}</b></span>
<span style="color:{color['存疑']}">存疑 <b>{vc.get('存疑',0)}</b></span>
<span style="color:{color['非皓祥']}">非皓祥 <b>{vc.get('非皓祥',0)}</b></span>
<span style="color:{color['无人脸']}">无人脸 <b>{vc.get('无人脸',0)}</b></span>
<span>生成 {datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
</div></header>""")

    alerts = [r for r in results if r["verdict"] in ("非皓祥", "无人脸", "读取失败")]
    if alerts:
        parts.append("<div class=warn><b>⚠ 需关注（疑似混入 / 无人脸）：</b><br>")
        for r in alerts:
            parts.append(f"&nbsp;• [{esc(r['verdict'])}] sim={r['sim']} — {esc(r['rel'])}<br>")
        parts.append("</div>")

    for yr in sorted(by_year.keys()):
        items = by_year[yr]
        yr = yr.strip() or "others"
        parts.append(f"<div class=year><h2>{esc(yr)} （{len(items)}）</h2><div class=grid>")
        for r in items:
            c = color.get(r["verdict"], "#6e7781")
            abspath = r["path"].replace("\\", "/")
            parts.append(
                f"<a class=card href='file:///{abspath}'>"
                f"<img loading=lazy src='{r['thumb']}'>"
                f"<div class=cap><div class=nm>{esc(os.path.basename(r['path']))}</div>"
                f"<span class=badge style='background:{c}'>{esc(r['verdict'])}</span> "
                f"<span class=sim>sim={r['sim']}</span></div></a>"
            )
        parts.append("</div></div>")

    parts.append("</body></html>")
    html_path = os.path.join(PREVIEW, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))

    log(f"预览索引: {html_path}")
    log(f"CSV 清单: {csv_path}")
    log(f"判定统计: {dict(vc)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--person", default="皓祥")
    ap.add_argument("--target", default=None)
    ap.add_argument("--skip-dedup", action="store_true")
    ap.add_argument("--from-cache", action="store_true",
                    help="跳过核验，直接用上次 _results.json 重建预览")
    args = ap.parse_args()
    PERSON = args.person
    TARGET = args.target or os.path.join(r"E:\待整理照片", PERSON)
    PREVIEW = os.path.join(TARGET, "_preview")
    THUMB_DIR = os.path.join(PREVIEW, "thumbs")
    DUP_DIR = os.path.join(TARGET, "_duplicates")
    os.makedirs(THUMB_DIR, exist_ok=True)

    pc = sqlite3.connect(PHOTO_DB)
    fc = sqlite3.connect(FACE_DB)

    # ---- 0. 参考向量 ----
    pid = fc.execute("SELECT id FROM persons WHERE name=?", (PERSON,)).fetchone()
    if not pid:
        print("ERROR: face_index.db 找不到人物", PERSON); return
    pid = pid[0]
    emb_rows = fc.execute(
        "SELECT embedding FROM faces WHERE person_id=?", (pid,)
    ).fetchall()
    if not emb_rows:
        print("ERROR: 该人物无参考向量"); return
    refs = np.array(
        [np.frombuffer(r[0], dtype=np.float32) for r in emb_rows], dtype=np.float32
    )
    refs /= np.linalg.norm(refs, axis=1, keepdims=True)
    log(f"参考向量: {len(refs)} 张 {PERSON} 人脸")

    cache_path = os.path.join(PREVIEW, "_results.json")
    if args.from_cache and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            results = __import__("json").load(f)
        log(f"--from-cache: 载入 {len(results)} 条历史核验结果, 跳过去重+核验")
        # 写 CSV + HTML
        _write_outputs(results, PREVIEW, PERSON, 0)
        log("完成（仅重建预览）")
        pc.close(); fc.close()
        return

    # ---- 1. 去重 ----
    all_imgs = collect_images(TARGET)
    log(f"扫描到图片: {len(all_imgs)} 张")
    kept, dup_actions = [], []
    if not args.skip_dedup:
        seen = {}
        for fp in all_imgs:
            h = content_hash(fp)
            if h in seen:
                os.makedirs(DUP_DIR, exist_ok=True)
                base = os.path.basename(fp)
                dest = os.path.join(DUP_DIR, base)
                c = 1
                while os.path.exists(dest):
                    c += 1
                    dest = os.path.join(DUP_DIR, f"{os.path.splitext(base)[0]}__{c}{os.path.splitext(base)[1]}")
                shutil.move(fp, dest)
                dup_actions.append((fp, dest, seen[h]))
            else:
                seen[h] = fp
                kept.append(fp)
        log(f"去重完成: 保留 {len(kept)} 张, 移入 _duplicates {len(dup_actions)} 张")
    else:
        kept = all_imgs
        log("跳过去重 (--skip-dedup)")

    # ---- 2. 人脸核验 ----
    app = load_app()
    log("InsightFace 已加载 (CPU)")
    results = []
    t0 = time.time()
    import cv2
    for i, fp in enumerate(kept):
        # 年份：优先取物理文件夹名（结构即真相），否则回退 resolve_year
        rel = os.path.relpath(fp, TARGET)
        top = rel.split(os.sep)[0]
        if re.match(r"^(19|20)\d{2}$", top):
            year, ysrc = top, "path"
        else:
            (year, ysrc) = resolve_year(fp, pc)
            year = year or "others"
        rgb = load_image_rgb(fp)
        verdict, sim, nface = "读取失败", 0.0, 0
        if rgb is not None:
            try:
                bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
                faces = app.get(bgr)
                nface = len(faces)
                if nface == 0:
                    verdict = "无人脸"
                else:
                    maxsim = -1.0
                    for f in faces:
                        e = np.ascontiguousarray(f.embedding, dtype=np.float32)
                        e /= np.linalg.norm(e)
                        s = float(np.max(refs @ e))
                        maxsim = max(maxsim, s)
                    sim = maxsim
                    if sim >= SIM_CONFIRM:
                        verdict = "皓祥"
                    elif sim >= SIM_DOUBT:
                        verdict = "存疑"
                    else:
                        verdict = "非皓祥"
            except Exception as e:
                verdict = f"识别错误:{type(e).__name__}"
        # 缩略图
        thname = f"{hashlib.md5(fp.encode()).hexdigest()[:12]}.jpg"
        make_thumb(fp, os.path.join(THUMB_DIR, thname))
        results.append({
            "path": fp,
            "rel": os.path.relpath(fp, TARGET),
            "year": year or "others",
            "ysrc": ysrc or "",
            "verdict": verdict,
            "sim": round(sim, 3),
            "nface": nface,
            "thumb": f"thumbs/{thname}",
        })
        if (i + 1) % 25 == 0:
            dt = time.time() - t0
            log(f"核验 {i+1}/{len(kept)}  耗时 {dt/60:.1f}min")
    log(f"核验完成: {len(results)} 张")

    # ---- 3. 写 CSV + HTML（落盘缓存 + 调函数） ----
    import json as _json
    with open(os.path.join(PREVIEW, "_results.json"), "w", encoding="utf-8") as f:
        _json.dump(results, f, ensure_ascii=False)
    _write_outputs(results, PREVIEW, PERSON, len(dup_actions))
    pc.close(); fc.close()


if __name__ == "__main__":
    main()
