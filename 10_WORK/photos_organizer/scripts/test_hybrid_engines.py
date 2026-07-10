"""验证双引擎分类：CLIP-only / GLM-only / Hybrid 各跑 clip_test 20张"""
import os, glob, sys, collections, importlib.util, time

SPEC_DIR = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "cls_mod", os.path.join(SPEC_DIR, "04_classify.py")
)
cls_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cls_mod)

# 加载配置
spec2 = importlib.util.spec_from_file_location(
    "utils_mod", os.path.join(SPEC_DIR, "utils.py")
)
utils_mod = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(utils_mod)

TEST_DIR = r"E:\PAIOS\10_WORK\photos_organizer\inputs\clip_test"
files = sorted(glob.glob(os.path.join(TEST_DIR, "*")))

# 检查是否有智谱 API Key
ZHIPU_KEY = os.environ.get("ZHIPU_API_KEY", "")
GLM_AVAILABLE = bool(ZHIPU_KEY)

print(f"测试图片: {len(files)} 张")
print(f"智谱 API Key: {'已设置 ✓' if GLM_AVAILABLE else '未设置 — GLM 模式跳过'}")
print("=" * 72)

# ── 1. CLIP-only ──
print("\n[1] CLIP-only 模式")
print(f"{'文件':<28} {'类别':<12} {'置信度':>7}  备注")
print("-" * 62)
clip_counter = collections.Counter()
for fp in files:
    name = os.path.basename(fp)[:26]
    cat, conf = cls_mod.classify_local_clip(fp, threshold=0.35)
    clip_counter[cat] += 1
    flag = " ✓" if conf >= 0.4 else (" ~" if conf >= 0.25 else " ?")
    print(f"{name:<28} {cat:<12} {conf*100:6.1f}%{flag}")

print("\nCLIP 分布:")
for c, n in clip_counter.most_common():
    print(f"  {c:<12} {n:>3}  ({n/len(files)*100:.0f}%)")

# ── 2. GLM-4V-Flash only（仅当 API Key 可用）──
if GLM_AVAILABLE:
    print("\n[2] GLM-4V-Flash only 模式")
    print(f"{'文件':<28} {'类别':<12} {'置信度':>7}  描述(截断)")
    print("-" * 72)
    glm_counter = collections.Counter()
    for fp in files:
        name = os.path.basename(fp)[:26]
        cat, conf = cls_mod.classify_glm4v_flash(fp, ZHIPU_KEY)
        glm_counter[cat] += 1
        desc = ""  # GLM 返回无 desc（只 category+conf）
        print(f"{name:<28} {cat:<12} {conf*100:6.1f}%")
        time.sleep(0.3)  # 简单限流保护

    print("\nGLM 分布:")
    for c, n in glm_counter.most_common():
        print(f"  {c:<12} {n:>3}  ({n/len(files)*100:.0f}%)")
else:
    print("\n[2] GLM-4V-Flash — 跳过（需设置 ZHIPU_API_KEY 环境变量）")
    print("    获取方式: https://open.bigmodel.cn/ → 注册 → 控制台 → API密钥")

# ── 3. Hybrid 模式 ──
cfg = utils_mod.load_config()
cfg["classification"]["provider"] = "hybrid"

print(f"\n[3] Hybrid 模式 (CLIP主力 + GLM补判, fallback_threshold={cfg['classification']['fallback_threshold']})")
print(f"{'文件':<28} {'类别':<12} {'置信度':>7} {'方法':<15} 备注")
print("-" * 72)
hybrid_counter = collections.Counter()
method_counter = collections.Counter()
for fp in files:
    name = os.path.basename(fp)[:26]
    ext = os.path.splitext(fp)[1].lower()
    mt = utils_mod.classify_media_type(ext)
    source, cat, conf, method = cls_mod.classify_image(fp, mt, cfg)
    hybrid_counter[cat] += 1
    method_counter[method] += 1
    flag = " ✓" if conf >= 0.4 else (" ~" if conf >= 0.25 else " ?")
    print(f"{name:<28} {cat:<12} {conf*100:6.1f}% {method:<15}{flag}")
    if method == "glm4v_flash":
        time.sleep(0.3)

print("\nHybrid 分布:")
for c, n in hybrid_counter.most_common():
    print(f"  {c:<12} {n:>3}  ({n/len(files)*100:.0f}%)")
print("\n引擎使用率:")
for m, n in method_counter.most_common():
    print(f"  {m:<15} {n:>3}  ({n/len(files)*100:.0f}%)")

# ── 对比汇总 ──
print("\n" + "=" * 72)
print("对比汇总:")
print(f"  CLIP '未分类': {clip_counter.get('未分类', 0)}/{len(files)}")
if GLM_AVAILABLE:
    print(f"  GLM  '未分类': {glm_counter.get('未分类', 0)}/{len(files)}")
print(f"  Hybrid '未分类': {hybrid_counter.get('未分类', 0)}/{len(files)}")
print(f"  Hybrid GLM补判次数: {method_counter.get('glm4v_flash', 0)}/{len(files)}")
