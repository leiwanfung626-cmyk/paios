#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
face_extract.py — 全量人脸检测 + 特征提取 + 建库
Phase 1 of Face Retrieval pipeline (PAIOS photos_organizer).

读取 photo_index.db 中 media_type='photo' 且 master=1 的照片（源目录原始图，只读），
用 InsightFace buffalo_l 检测人脸并提取 512 维 embedding，写入独立 face_index.db，
裁切 112x112 人脸缩略图到 faces/ 供人工审查/命名。

特性：
- 增量：processed 表记录已处理 photo_id（含零人脸），重启不重跑
- --limit N 试点
- --reset 清空重来
- 尊重 EXIF 方向（PIL ImageOps.exif_transpose）
- 仅 CPU（onnxruntime），不依赖 CUDA

用法：
  python face_extract.py                # 全量（增量续跑）
  python face_extract.py --limit 50     # 试点 50 张
  python face_extract.py --reset        # 清空后全量
"""
import argparse
import json
import os
import sqlite3
import sys
import time
from datetime import datetime

import numpy as np
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # photos_organizer/
PHOTO_DB = os.path.join(ROOT, "database", "photo_index.db")
FACE_DB = os.path.join(HERE, "face_index.db")
FACES_DIR = os.path.join(HERE, "faces")

DET_SIZE = (640, 640)
EMB_DIM = 512


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def init_face_db(con):
    con.execute("""
    CREATE TABLE IF NOT EXISTS faces (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        photo_id   INTEGER NOT NULL,
        path       TEXT NOT NULL,
        face_idx   INTEGER NOT NULL,
        bbox       TEXT,
        det_score  REAL,
        age        INTEGER,
        gender     INTEGER,
        embedding  BLOB,
        cluster_id INTEGER,
        person_id  INTEGER,
        created_at TEXT
    )""")
    con.execute("CREATE INDEX IF NOT EXISTS idx_faces_photo ON faces(photo_id)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_faces_cluster ON faces(cluster_id)")
    con.execute("""
    CREATE TABLE IF NOT EXISTS processed (
        photo_id  INTEGER PRIMARY KEY,
        face_count INTEGER,
        status    TEXT,
        error_msg TEXT,
        processed_at TEXT
    )""")
    con.execute("""
    CREATE TABLE IF NOT EXISTS persons (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        name     TEXT NOT NULL,
        note     TEXT,
        created_at TEXT
    )""")
    con.execute("""
    CREATE TABLE IF NOT EXISTS meta (
        key TEXT PRIMARY KEY,
        value TEXT
    )""")
    con.commit()


def load_app():
    from insightface.app import FaceAnalysis
    # ctx_id=-1 => CPU (onnxruntime). 无 CUDA 运行时，避免 GPU provider。
    app = FaceAnalysis(name="buffalo_l")
    app.prepare(ctx_id=-1, det_size=DET_SIZE)
    return app


def load_image_rgb(path):
    """用 PIL 读图并尊重 EXIF 方向，返回 RGB numpy (H,W,3) 或 None。"""
    try:
        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im)
            if im.mode in ("RGBA", "P", "LA"):
                im = im.convert("RGB")
            return np.asarray(im.convert("RGB"))
    except Exception:
        return None


def crop_face(rgb, bbox, margin=0.15):
    h, w = rgb.shape[:2]
    x1, y1, x2, y2 = bbox
    bw, bh = x2 - x1, y2 - y1
    x1 = max(0, int(x1 - bw * margin))
    y1 = max(0, int(y1 - bh * margin))
    x2 = min(w, int(x2 + bw * margin))
    y2 = min(h, int(y2 + bh * margin))
    crop = rgb[y1:y2, x1:x2]
    if crop.size == 0:
        return None
    from PIL import Image as PILImage
    cim = PILImage.fromarray(crop).resize((112, 112))
    return cim


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="试点：仅处理前 N 张未处理照片")
    ap.add_argument("--reset", action="store_true", help="清空 faces/processed 后重跑")
    ap.add_argument("--db", default=PHOTO_DB, help="photo_index.db 路径")
    ap.add_argument("--out", default=FACE_DB, help="face_index.db 输出路径")
    args = ap.parse_args()

    os.makedirs(FACES_DIR, exist_ok=True)
    pcon = sqlite3.connect(args.db)
    fcon = sqlite3.connect(args.out)
    init_face_db(fcon)

    if args.reset:
        log("RESET: 清空 faces / processed")
        fcon.execute("DELETE FROM faces")
        fcon.execute("DELETE FROM processed")
        fcon.commit()

    # 已处理集合
    done = set(r[0] for r in fcon.execute("SELECT photo_id FROM processed"))
    # 目标照片
    rows = pcon.execute(
        "SELECT id, path FROM photos WHERE media_type='photo' AND master=1 ORDER BY id"
    ).fetchall()
    targets = [(pid, p) for pid, p in rows if pid not in done]
    log(f"DB 照片总数(photo+master=1)={len(rows)}  已处理={len(done)}  待处理={len(targets)}")

    if args.limit:
        targets = targets[: args.limit]
        log(f"--limit {args.limit} => 本次处理 {len(targets)} 张")

    if not targets:
        log("无待处理照片，退出。")
        return

    app = load_app()
    log("InsightFace buffalo_l 已加载 (CPU)")

    t0 = time.time()
    n_photos = 0
    n_faces = 0
    n_err = 0
    BATCH = 200

    for pid, path in targets:
        face_count = 0
        status = "ok"
        err = None
        try:
            rgb = load_image_rgb(path)
            if rgb is None:
                status = "error"
                err = "decode_failed"
            else:
                # insightface 需要 BGR
                import cv2
                bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
                faces = app.get(bgr)
                face_count = len(faces)
                for fi, f in enumerate(faces):
                    bbox = [float(x) for x in f.bbox]  # [x1,y1,x2,y2]
                    emb = np.ascontiguousarray(f.embedding, dtype=np.float32)
                    # 缩略图
                    cim = crop_face(rgb, f.bbox)
                    thumb_rel = None
                    if cim is not None:
                        thumb_rel = f"{pid}_{fi}.jpg"
                        cim.save(os.path.join(FACES_DIR, thumb_rel), "JPEG", quality=85)
                    fcon.execute(
                        """INSERT INTO faces
                           (photo_id, path, face_idx, bbox, det_score, age, gender, embedding, created_at)
                           VALUES (?,?,?,?,?,?,?,?,?)""",
                        (
                            pid,
                            path,
                            fi,
                            json.dumps(bbox),
                            float(f.det_score),
                            int(getattr(f, "age", -1)),
                            int(getattr(f, "gender", -1)),
                            sqlite3.Binary(emb.tobytes()),
                            datetime.now().isoformat(timespec="seconds"),
                        ),
                    )
                    n_faces += 1
        except Exception as e:
            status = "error"
            err = f"{type(e).__name__}: {e}"[:200]
            n_err += 1

        fcon.execute(
            "INSERT OR REPLACE INTO processed (photo_id, face_count, status, error_msg, processed_at) VALUES (?,?,?,?,?)",
            (pid, face_count, status, err, datetime.now().isoformat(timespec="seconds")),
        )
        n_photos += 1

        if n_photos % BATCH == 0:
            fcon.commit()
            dt = time.time() - t0
            rate = n_photos / dt if dt > 0 else 0
            remain = (len(targets) - n_photos) / rate if rate > 0 else 0
            log(f"进度 {n_photos}/{len(targets)}  人脸={n_faces}  错误={n_err}  "
                f"速度={rate:.1f} 张/s  剩余≈{remain/60:.1f} min")

    fcon.commit()
    dt = time.time() - t0
    log(f"完成。处理 {n_photos} 张，检出人脸 {n_faces}，错误 {n_err}，耗时 {dt/60:.1f} min")
    log(f"人脸库: {args.out}")
    log(f"缩略图: {FACES_DIR}")

    # 记录统计
    fcon.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('last_run_photos',?)", (str(n_photos),))
    fcon.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('last_run_faces',?)", (str(n_faces),))
    fcon.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('last_run_at',?)", (datetime.now().isoformat(timespec='seconds'),))
    fcon.commit()
    pcon.close()
    fcon.close()


if __name__ == "__main__":
    main()
