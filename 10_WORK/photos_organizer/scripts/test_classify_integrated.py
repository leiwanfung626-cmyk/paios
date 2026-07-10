"""验证生产版 classify_local_clip (04_classify.py) 在 20 张测试图上的分布"""
import os, glob, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util

spec = importlib.util.spec_from_file_location(
    "cls_mod", os.path.join(os.path.dirname(__file__), "04_classify.py")
)
cls_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cls_mod)

TEST_DIR = r"E:\PAIOS\10_WORK\photos_organizer\inputs\clip_test"
files = sorted(glob.glob(os.path.join(TEST_DIR, "*")))

print(f"{'文件':<28} {'内容标签':<12} {'置信度':>7}  备注")
print("-" * 62)
cat_counter = collections.Counter()
for fp in files:
    name = os.path.basename(fp)[:26]
    cat, conf = cls_mod.classify_local_clip(fp, threshold=0.35)
    cat_counter[cat] += 1
    flag = " ✓" if conf >= 0.4 else (" ~" if conf >= 0.25 else " ?")
    print(f"{name:<28} {cat:<12} {conf*100:6.1f}%{flag}")

print("\n=== 内容标签分布 ===")
for c, n in cat_counter.most_common():
    print(f"  {c:<12} {n:>3}  ({n/len(files)*100:.0f}%)")
print(f"总计: {len(files)}")
