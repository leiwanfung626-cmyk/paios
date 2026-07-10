"""CLIP 最终诊断: 温度缩放 + 原始相似度 + 参数验证"""
import os, glob, math
import cn_clip.clip as clip
from cn_clip.clip import load_from_name
from PIL import Image
import torch

DEVICE = "cpu"
MODEL_DIR = r"E:\PAIOS\10_WORK\photos_organizer\models"
TEST_DIR = r"E:\PAIOS\10_WORK\photos_organizer\inputs\clip_test"

CATEGORIES = [
    "人物肖像", "家庭亲子", "风景自然", "建筑室内", "美食饮品",
    "宠物动物", "车辆交通", "文档截图", "工作会议", "活动宣传",
    "旅行出游", "网络图片素材", "证件发票", "其他",
]

def main():
    model, preprocess = load_from_name("ViT-B-16", device=DEVICE, download_root=MODEL_DIR)
    model.eval()

    # [诊断1] 参数量验证
    params = sum(p.numel() for p in model.parameters())
    print(f"[诊断1] 模型参数量: {params:,} (预期 ~150M)")

    # [诊断2] 编码文本
    text = clip.tokenize(CATEGORIES).to(DEVICE)
    with torch.no_grad():
        text_feat = model.encode_text(text)
        text_feat /= text_feat.norm(dim=-1, keepdim=True)

    # [诊断3] 文本间余弦相似度矩阵 (看类别是否区分开)
    t_sim = (text_feat @ text_feat.t()).cpu()
    print(f"\n[诊断3] 类别间文本相似度 (对角=1.0)")
    off_diag = []
    for i in range(len(CATEGORIES)):
        for j in range(i+1, len(CATEGORIES)):
            s = t_sim[i][j].item()
            off_diag.append(s)
            if s > 0.85:
                print(f"  ⚠ {CATEGORIES[i]} ↔ {CATEGORIES[j]} = {s:.3f}")
    print(f"  平均非对角: {sum(off_diag)/len(off_diag):.3f}  最大: {max(off_diag):.3f}")

    # [诊断4] 选 3 张清晰图测不同温度
    test_files = [
        f for f in sorted(glob.glob(os.path.join(TEST_DIR, "*")))
        if "IMG_20170718_141359" in f or "IMG_20170719_152611" in f or "IMG_20170726_092037" in f
    ]
    temps = [1.0, 0.1, 0.05, 0.02, 0.01]

    print(f"\n[诊断4] 温度对比 (3张真实照片)")
    print(f"{'文件':<30} {'温度':>5} {'Top1':<10} {'置信度':>6} {'跨度':>6}")
    for fp in test_files:
        img = Image.open(fp).convert("RGB")
        inp = preprocess(img).unsqueeze(0).to(DEVICE)
        with torch.no_grad():
            img_feat = model.encode_image(inp)
            img_feat /= img_feat.norm(dim=-1, keepdim=True)
            logits_raw = (img_feat @ text_feat.t())[0]
        name = os.path.basename(fp)[:28]
        for T in temps:
            probs = (logits_raw / T).softmax(dim=-1)
            top_idx = probs.argmax().item()
            top_val = probs[top_idx].item()
            span = probs.max() - probs.min()
            marker = " ✓" if span > 0.15 else ""
            print(f"{name:<30} {T:>5.2f} {CATEGORIES[top_idx]:<10} {top_val*100:5.1f}% {span:.3f}{marker}")
        print(f"  (原始logits范围): [{logits_raw.min():.3f}, {logits_raw.max():.3f}]")

if __name__ == "__main__":
    main()
