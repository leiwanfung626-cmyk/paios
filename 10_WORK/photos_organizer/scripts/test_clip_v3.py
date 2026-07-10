"""CLIP 全量测试 - 20张图, 对比真实照片 vs 微信图"""
import os, glob
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
    text = clip.tokenize(CATEGORIES).to(DEVICE)
    with torch.no_grad():
        text_feat = model.encode_text(text)
        text_feat /= text_feat.norm(dim=-1, keepdim=True)

    files = sorted(glob.glob(os.path.join(TEST_DIR, "*")))
    print(f"{'文件':<30} {'类型':<8} {'Top1':<10} {'置信度':>6} {'跨度':>6} {'判定'}")
    print("-" * 80)

    flat_count = 0; peaked_count = 0
    for fp in files:
        name = os.path.basename(fp)[:28]
        is_wechat = "mmexport" in name or "1502" in name[:4]
        img_type = "微信图" if is_wechat else "相机"
        try:
            img = Image.open(fp).convert("RGB")
            inp = preprocess(img).unsqueeze(0).to(DEVICE)
            with torch.no_grad():
                img_feat = model.encode_image(inp)
                img_feat /= img_feat.norm(dim=-1, keepdim=True)
            logits = (img_feat @ text_feat.t())[0].softmax(dim=-1)
            top_idx = logits.argmax().item()
            top_val = logits[top_idx].item()
            span = logits.max() - logits.min()
            verdict = "✓ 区分" if span > 0.05 else "✗ 平坦"
            if span > 0.05: peaked_count += 1
            else: flat_count += 1
            print(f"{name:<30} {img_type:<8} {CATEGORIES[top_idx]:<10} {top_val*100:5.1f}% {span:.3f}   {verdict}")
        except Exception as e:
            print(f"{name:<30} {img_type:<8} ERROR: {e}")

    print(f"\n总计: {len(files)} 张 | 可区分(peaked): {peaked_count} | 平坦(flat): {flat_count}")
    print("判定标准: 跨度 > 0.05 = 有意义区分")

if __name__ == "__main__":
    main()
