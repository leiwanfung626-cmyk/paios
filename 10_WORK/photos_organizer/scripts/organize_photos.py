# organize_photos.py — 照片整理统一入口（V1.1 多标签架构）
# 用法:
#   python organize_photos.py                      # 全量（增量模式，hybrid 多标签）
#   python organize_photos.py --limit 50           # 测试
#   python organize_photos.py --dry-run            # 预演
#   python organize_photos.py --provider glm4v_flash  # 纯 GLM 多标签
import argparse
import os
import sys
import shutil
import csv
import json
import datetime
import importlib.util
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from utils import (
    load_config,
    get_db,
    compute_md5,
    scan_files,
    classify_media_type,
    ensure_dir,
    hamming_similarity,
    load_local_env,
)
from tqdm import tqdm


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(BASE_DIR, filename)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


exif_mod = load_module("exif_mod", "01_extract_exif.py")
md5_mod = load_module("md5_mod", "02_md5_dedup.py")
phash_mod = load_module("phash_mod", "03_phash_dedup.py")
cls_mod = load_module("cls_mod", "04_classify.py")


def write_tags(conn, photo_id, tags, method):
    """将多标签写入 tags 表。"""
    now = datetime.datetime.now().isoformat()
    for tag_type in ("scene", "people", "object", "activity", "attribute", "event"):
        for tag_value in tags.get(tag_type, []):
            conn.execute(
                "INSERT INTO tags (photo_id, tag_type, tag_value, source, confidence, created_at) "
                "VALUES (?,?,?,?,?,?)",
                (photo_id, tag_type, tag_value, method, 1.0, now)
            )


def _write_photo_version(conn, photo_id, version, classifier, classifier_version,
                         primary_category, confidence, tags, caption, source, created_at):
    """写入 photo_versions 表，记录分类历史。"""
    tags_json = json.dumps(tags, ensure_ascii=False) if tags else "{}"
    conn.execute(
        "INSERT INTO photo_versions "
        "(photo_id, version, classifier, classifier_version, primary_category, "
        "confidence, tags_json, caption, source, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (photo_id, version, classifier, classifier_version, primary_category,
         confidence, tags_json, caption, source, created_at)
    )


def export_csv(conn, output_base):
    """导出 CSV 报表，含多标签信息。"""
    out = os.path.join(output_base, "index.csv")
    rows = conn.execute(
        "SELECT id, filename, path, md5, date, media_type, source, "
        "primary_category, confidence, classifier, quality_score, "
        "duplicate_group, master, value_level, caption FROM photos ORDER BY date, source"
    ).fetchall()

    if not rows:
        return

    # 为每行附加标签
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([
            "id", "filename", "path", "md5", "date", "media_type", "source",
            "primary_category", "confidence", "classifier", "quality_score",
            "duplicate_group", "master", "value_level", "caption",
            "tags_scene", "tags_people", "tags_object",
            "tags_activity", "tags_attribute"
        ])
        for r in rows:
            photo_id = r["id"]
            tag_rows = conn.execute(
                "SELECT tag_type, tag_value FROM tags WHERE photo_id=?",
                (photo_id,)
            ).fetchall()
            tag_dict = {}
            for tr in tag_rows:
                tt = tr["tag_type"]
                tv = tr["tag_value"]
                if tt not in tag_dict:
                    tag_dict[tt] = []
                tag_dict[tt].append(tv)

            w.writerow([
                r["id"], r["filename"], r["path"], r["md5"], r["date"],
                r["media_type"], r["source"], r["primary_category"],
                r["confidence"], r["classifier"], r["quality_score"],
                r["duplicate_group"], r["master"], r["value_level"], r["caption"],
                "|".join(tag_dict.get("scene", [])),
                "|".join(tag_dict.get("people", [])),
                "|".join(tag_dict.get("object", [])),
                "|".join(tag_dict.get("activity", [])),
                "|".join(tag_dict.get("attribute", [])),
            ])
    print(f"CSV 导出: {out} ({len(rows)} 行)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?", default=None)
    ap.add_argument("output", nargs="?", default=None)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--use-local-clip", action="store_true")
    ap.add_argument("--provider", default=None,
                    help="hybrid|local_clip|glm4v_flash|baidu")
    args = ap.parse_args()

    cfg = load_config()
    load_local_env()  # 从项目根 .env 加载密钥（后台 shell 不继承交互 shell 的 env）

    # ── GLM / 百度 密钥可用性自检（避免静默跳过云端补判）──
    cls_cfg = cfg.get("classification", {})
    provider = args.provider or cls_cfg.get("provider", "hybrid")
    glm_cfg = cls_cfg.get("glm4v_flash", {})
    if provider in ("hybrid", "glm4v_flash"):
        key_env = glm_cfg.get("api_key_env", "ZHIPU_API_KEY")
        if not os.environ.get(key_env):
            print(f"⚠️  WARNING: provider={provider} 但环境变量 {key_env} 缺失！")
            print(f"   GLM-4V-Flash 补判将被跳过（仅本地 CLIP 分类）。")
            print(f"   修复：把 `{key_env}=你的key` 写入 {os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')}")
    if provider in ("hybrid", "baidu"):
        b_cfg = cls_cfg.get("baidu", {})
        bk = b_cfg.get("api_key_env", "BAIDU_API_KEY")
        if not os.environ.get(bk):
            print(f"ℹ️  INFO: 百度分类未启用（{bk} 缺失），将跳过。")

    input_dir = args.input or cfg["paths"]["input"]
    output_base = args.output or cfg["paths"]["output"]
    db_path = cfg["paths"]["db"]
    if args.use_local_clip:
        cfg["classification"]["provider"] = "local_clip"
    if args.provider:
        cfg["classification"]["provider"] = args.provider

    if not os.path.isdir(input_dir):
        print(f"输入目录不存在: {input_dir}")
        sys.exit(1)

    conn = get_db(db_path)
    batch_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # ── 记录 job ──
    start_time = datetime.datetime.now()
    pipeline_version = "v1.1"
    classifier_name = cfg.get("classification", {}).get("provider", "hybrid")
    classifier_version = "multitag-hybrid-20260707"

    all_files = list(scan_files(input_dir))
    print(f"扫描到 {len(all_files)} 个文件 @ {input_dir}")

    # 排除已知工作产物目录（人物策展输出 / 预览缓存），避免污染索引。
    # 这些目录建在源目录内（如 E:\待整理照片\运丰\_preview），其内部的 csv/json/缩略图
    # 不是照片资产。运丰内真照片均来自已索引原库（md5 命中→master=0），排除不影响去重。
    EXCLUDE_DIRS = {"_preview", "运丰"}
    _before = len(all_files)
    all_files = [p for p in all_files if not (set(p.parts) & EXCLUDE_DIRS)]
    if _before != len(all_files):
        print(f"排除工作产物目录 {EXCLUDE_DIRS}：跳过 {_before - len(all_files)} 个非资产文件")

    processed = set(r[0] for r in conn.execute("SELECT path FROM photos").fetchall())
    to_process = [p for p in all_files if str(p) not in processed]
    print(f"待处理（增量，已排除 {len(processed)} 个已处理）: {len(to_process)}")

    if args.limit:
        to_process = to_process[:args.limit]

    batch_md5 = {}
    stats = {
        "processed": 0, "md5_dup": 0, "perceptual_dup": 0,
        "video": 0, "document": 0, "errors": 0,
        "clip_count": 0, "glm_count": 0, "tags_total": 0,
    }
    err_log = os.path.join(os.path.dirname(db_path), "errors.log")

    for p in tqdm(to_process, desc="整理"):
        path = str(p)
        try:
            ext = p.suffix.lower()
            media_type = classify_media_type(ext)
            md5 = compute_md5(path)
            # 保存原始扩展名（与 media_type 解耦：.heic → photo, .cr2 → raw）

            # 精确去重
            is_dup, _ = md5_mod.find_batch_duplicate(batch_md5, md5)
            if is_dup:
                stats["md5_dup"] += 1
                continue
            batch_md5[md5] = path

            is_dup2, _ = md5_mod.check_md5_dup(conn, md5)
            if is_dup2:
                stats["md5_dup"] += 1
                continue

            # EXIF
            meta = exif_mod.extract_exif(path)

            # pHash（仅 photo 类型）
            phash = dhash = None
            if media_type == "photo":
                try:
                    phash = phash_mod.compute_phash(path)
                    dhash = phash_mod.compute_dhash(path)
                except Exception:
                    pass

            # 感知去重
            dup_id = sim = None
            if phash:
                dup_id, sim = phash_mod.find_perceptual_duplicate(
                    conn, phash, media_type, cfg["dedup"]["phash_threshold"]
                )

            # ── 多标签分类 ──
            source, primary, confidence, tags, description, method = cls_mod.classify_image(
                path, media_type, cfg
            )

            if method == "local_clip":
                stats["clip_count"] += 1
            elif method == "glm4v_flash":
                stats["glm_count"] += 1

            # 感知重复处理
            duplicate_group = None
            master = 1
            if dup_id:
                # 标记当前为副本（master=0），主图由分辨率/质量决定
                # 后续可批量更新：选出每组中分辨率最高的作为 master
                duplicate_group = f"pg_{dup_id}"
                master = 0
                stats["perceptual_dup"] += 1

            if media_type == "video":
                stats["video"] += 1
            elif media_type == "document":
                stats["document"] += 1

            # 统计标签数
            tag_count = sum(len(v) for v in tags.values())
            stats["tags_total"] += tag_count

            year = (meta["date"] or "Unknown")[:4]

            if not args.dry_run:
                # 复制文件到归档目录
                dest_dir = os.path.join(output_base, source, year)
                ensure_dir(dest_dir)
                dest = os.path.join(dest_dir, p.name)
                if os.path.exists(dest):
                    dest = os.path.join(dest_dir, f"{p.stem}_{md5[:6]}{p.suffix}")
                shutil.copy2(path, dest)

                now = datetime.datetime.now().isoformat()

                # 写入 photos 表（25列，不含id：新增 extension 字段）
                cur = conn.execute(
                    """INSERT INTO photos
                       (filename,path,md5,phash,dhash,date,camera,gps,media_type,extension,
                        source,primary_category,confidence,classifier,classifier_version,
                        quality_score,duplicate_group,master,value_level,caption,
                        batch_id,created_at,updated_at,processed_at)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        p.name, path, md5, phash, dhash,
                        meta["date"], meta["camera"], meta["gps"],
                        media_type, ext,  # extension 与 media_type 解耦
                        source, primary, confidence,
                        method, classifier_version,
                        None,  # quality_score 预留
                        duplicate_group, master,
                        None,  # value_level 预留
                        description if method == "glm4v_flash" else None,
                        batch_id, now, now, now,
                    ),
                )
                photo_id = cur.lastrowid

                # 写入 tags 表
                if tags:
                    write_tags(conn, photo_id, tags, method)

                # 写入 photo_versions 表（V1.0-final：记录分类历史）
                _write_photo_version(conn, photo_id, 1, method, classifier_version,
                                     primary, confidence, tags, description, source, now)

                conn.commit()

            stats["processed"] += 1
        except Exception as e:
            stats["errors"] += 1
            with open(err_log, "a", encoding="utf-8") as ef:
                ef.write(f"{path}\t{str(e)}\n")

    # ── 写入 job 记录 ──
    if not args.dry_run:
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        conn.execute(
            "INSERT INTO jobs (batch_id, pipeline_version, classifier, classifier_version, "
            "started_at, finished_at, processed_count, failed_count, duration_seconds) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (batch_id, pipeline_version, classifier_name, classifier_version,
             start_time.isoformat(), end_time.isoformat(),
             stats["processed"], stats["errors"], duration)
        )
        conn.commit()
        export_csv(conn, output_base)

    conn.close()

    print("=" * 60)
    print(f"批次: {batch_id} | 版本: {pipeline_version}")
    print(f"新处理: {stats['processed']}")
    print(f"MD5 重复跳过: {stats['md5_dup']}")
    print(f"感知重复标记: {stats['perceptual_dup']}")
    print(f"视频: {stats['video']} | 文档: {stats['document']}")
    print(f"CLIP 分类: {stats['clip_count']} | GLM 补判: {stats['glm_count']}")
    print(f"总标签数: {stats['tags_total']} (平均 {stats['tags_total']/max(stats['processed'],1):.1f} 张/照片)")
    print(f"错误: {stats['errors']}")
    if args.dry_run:
        print("[DRY-RUN] 未写入数据库，未复制文件")


if __name__ == "__main__":
    main()
