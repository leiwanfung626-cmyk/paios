"""CLIP 零样本分类 - prompt 模板对比测试 (CPU)"""
import os, time, glob
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

# 两种 prompt 策略
BARE = CATEGORIES
TEMPLATED = [f"一张{c}的照片" for c in CATEGORIES]

def main():
    model, preprocess = load_from_name("ViT-B-16", device=DEVICE, download_root=MODEL_DIR)
    model.eval()

    def classify(prompts):
        text = clip.tokenize(prompts).to(DEVICE)
        with torch.no_grad():
            tf = model.encode_text(text)
            tf /= tf.norm(dim=-1, keepdim=True)
        return tf

    tf_bare = classify(BARE)
    tf_tpl = classify(TEMPLATED)

    files = sorted(glob.glob(os.path.join(TEST_DIR, "*")))[:8]
    for fp in files:
        img = Image.open(fp).convert("RGB")
        inp = preprocess(img).unsqueeze(0).to(DEVICE)
        with torch.no_grad():
            img_feat = model.encode_image(inp)
            img_feat /= img_feat.norm(dim=-1, keepdim=True)
        logits_bare = (img_feat @ tf_bare.t())[0].softmax(dim=-1)
        logits_tpl = (img_feat @ tf_tpl.t())[0].softmax(dim=-1)
        b_top = logits_bare.topk(1)
        t_top = logits_tpl.topk(1)
        name = os.path.basename(fp)[:24]
        print(f"\n{name}")
        print(f"  裸词: {CATEGORIES[b_top.indices[0].item()]:<8} {b_top.values[0].item()*100:5.1f}%  (max分布跨度 {logits_bare.max()-logits_bare.min():.3f})")
        print(f"  模板: {CATEGORIES[t_top.indices[0].item()]:<8} {t_top.values[0].item()*100:5.1f}%  (max分布跨度 {logits_tpl.max()-logits_tpl.min():.3f})")

if __name__ == "__main__":
    main()
