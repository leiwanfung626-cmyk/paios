# reclassify_lowconf_glm.py — GLM-4V-Flash 补判回填（修复缺失的云端分类）
#
# 背景：2026-07-10 增量扫描时后台 shell 缺失 ZHIPU_API_KEY，
#       导致 278 张 CLIP 低置信度照片（confidence < 0.40）未走 GLM 补判。
#       本脚本精准回填这些行，不改变原图、不重跑去重。
#
# 目标集合：
#   SELECT * FROM photos
#   WHERE classifier='local_clip' AND confidence < 0.40 AND media_type='photo'
#
# 行为：
#   - 对每张重跑 classify_glm4v_flash；若返回有效 primary（≠ 其他），更新该行：
#       classifier='glm4v_flash', primary_category, confidence, caption, source（按标签重映射）
#       重写 tags 表 + 追加 photo_versions 历史（保留 CLIP 旧版本可追溯）
#   - 若 GLM 失败 / 返回 其他，保留原 CLIP 结果（不恶化）
#
# 用法：
#   python reclassify_lowconf_glm.py                 # 实际回填
#   python reclassify_lowconf_glm.py --dry-run      # 仅统计，不写库
#   python reclassify_lowconf_glm.py --limit 20     # 限量测试
#   python reclassify_lowconf_glm.py --threshold 0.40
import argparse
import os
import sys
import json
import time
import datetime
import importlib.util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from utils import load_config, get_db, load_local_env
load_local_env()

# 加载分类模块（04_classify.py 顶部已 load_local_env，确保 ZHIPU_API_KEY 就位）
spec = importlib.util.spec_from_file_location("cls_mod", os.path.join(BASE_DIR, "04_classify.py"))
cls_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cls_mod)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--threshold", type=float, default=0.40,
                    help="CLIP 置信度低于此值才视为 GLM 候选（默认 0.40，与 config 一致）")
    ap.add_argument("--all-local-clip", action="store_true",
                    help="不限置信度，对全部 classifier='local_clip' 的 photo 重跑 GLM")
    args = ap.parse_args()

    cfg = load_config()
    db_path = cfg["paths"]["db"]
    glm_cfg = cfg.get("classification", {}).get("glm4v_flash", {})
    key_env = glm_cfg.get("api_key_env", "ZHIPU_API_KEY")
    api_key = os.environ.get(key_env)
    model = glm_cfg.get("model", "glm-4v-flash")

    if not api_key:
        print(f"❌ ERROR: 环境变量 {key_env} 缺失，无法调用 GLM。")
        print(f"   修复：把 `{key_env}=你的key` 写入 {os.path.join(os.path.dirname(BASE_DIR), '.env')}")
        sys.exit(1)

    conn = get_db(db_path)

    if args.all_local_clip:
        where = "classifier='local_clip' AND media_type='photo'"
    else:
        where = f"classifier='local_clip' AND confidence < {args.threshold} AND media_type='photo'"

    rows = conn.execute(
        f"SELECT id, path, primary_category, confidence, source FROM photos WHERE {where}"
    ).fetchall()
    total = len(rows)
    print(f"GLM 候选（待补判）: {total} 张  |  model={model}  |  {'[DRY-RUN]' if args.dry_run else '实际执行'}")

    if args.limit:
        rows = rows[:args.limit]

    updated = 0
    skipped = 0          # GLM 正常返回"其他"（有效结果，保留 CLIP）
    errored = 0          # 其他未知异常
    unreadable = 0       # 坏文件 / API 硬错误（GLMImageError），留痕不重试

    unreadable_log = os.path.join(BASE_DIR, "glm_unreadable.txt")
    if not args.limit and os.path.exists(unreadable_log):
        os.remove(unreadable_log)  # 整跑重建清单；分块(--limit)则追加

    start = time.time()
    for i, r in enumerate(rows, 1):
        pid, path, old_primary, old_conf, old_source = r
        try:
            if not os.path.exists(path):
                print(f"[{i}/{len(rows)}] 原图不存在，跳过 id={pid}", flush=True)
                skipped += 1
                continue

            # 可能抛 GLMImageError（坏文件/API硬错）—— 下方单独捕获，不重试
            glm_primary, glm_conf, glm_tags, glm_desc = cls_mod.classify_glm4v_flash(
                path, api_key, model=model
            )

            if glm_primary == "其他":
                # GLM 正常看了图、判为不可归类 → 保留 CLIP（有效结果）
                print(f"[{i}/{len(rows)}] 保留CLIP(其他) id={pid}", flush=True)
                skipped += 1
                continue

            # 重新计算 source（标签 → 规则映射）
            heuristic_src = cls_mod.heuristic_source(path, "photo")
            new_source = cls_mod.resolve_source(glm_tags, heuristic_src)

            if args.dry_run:
                print(f"[DRY {i}/{len(rows)}] id={pid} {old_primary}({old_conf}) → {glm_primary}({glm_conf}) "
                      f"src:{old_source}→{new_source}", flush=True)
                updated += 1
                continue

            now = datetime.datetime.now().isoformat()
            conn.execute(
                """UPDATE photos SET classifier='glm4v_flash', primary_category=?,
                          confidence=?, caption=?, source=?, updated_at=? WHERE id=?""",
                (glm_primary, glm_conf, glm_desc, new_source, now, pid)
            )
            # 重写 tags（先清旧，再写新）
            conn.execute("DELETE FROM tags WHERE photo_id=?", (pid,))
            for tag_type in ("scene", "people", "object", "activity", "attribute", "event"):
                for tag_value in glm_tags.get(tag_type, []):
                    conn.execute(
                        "INSERT INTO tags (photo_id, tag_type, tag_value, source, confidence, created_at) "
                        "VALUES (?,?,?,?,?,?)",
                        (pid, tag_type, tag_value, "glm4v_flash", 1.0, now)
                    )
            # 追加 photo_versions 历史
            vcount = conn.execute("SELECT COUNT(*) FROM photo_versions WHERE photo_id=?", (pid,)).fetchone()[0]
            conn.execute(
                """INSERT INTO photo_versions
                   (photo_id, version, classifier, classifier_version, primary_category,
                    confidence, tags_json, caption, source, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (pid, vcount + 1, "glm4v_flash", "multitag-hybrid-20260707",
                 glm_primary, glm_conf, json.dumps(glm_tags, ensure_ascii=False),
                 glm_desc, new_source, now)
            )
            conn.commit()
            updated += 1
            elapsed = time.time() - start
            rate = updated / elapsed if elapsed > 0 else 0
            eta = (len(rows) - i) / rate / 60 if rate > 0 else 0
            print(f"[{i}/{len(rows)}] ✓ id={pid} → {glm_primary}({glm_conf:.2f}) | 累计{updated} "
                  f"速率{rate:.2f}/s ETA{eta:.1f}min", flush=True)

            time.sleep(0.4)  # 基础间隔；遇 429 由 classify_glm4v_flash 内部退避接管

        except cls_mod.GLMImageError as ge:
            # 坏文件(PIL打不开) 或 API 硬错误(1210) —— 保留 CLIP，不重试（重试必然失败）
            unreadable += 1
            with open(unreadable_log, "a", encoding="utf-8") as f:
                f.write(f"{pid}\t{path}\t{str(ge)[:200]}\n")
            print(f"[{i}/{len(rows)}] ⚠ 不可读 id={pid}: {str(ge)[:70]}", flush=True)

        except Exception as e:
            errored += 1
            conn.rollback()  # 回滚本行未提交事务，避免污染后续写入
            print(f"[错误 {i}/{len(rows)}] id={pid}: {e}", flush=True)

    print(f"\n=== 完成 ===")
    print(f"候选总数: {total}")
    print(f"  更新(GLM补判成功): {updated}")
    print(f"  跳过(保留CLIP/其他): {skipped}")
    print(f"  不可读(坏文件/API硬错, 已留痕): {unreadable}  -> {unreadable_log}")
    print(f"  其他错误: {errored}")


if __name__ == "__main__":
    main()
