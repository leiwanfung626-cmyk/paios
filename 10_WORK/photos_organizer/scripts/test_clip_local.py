"""本地 Chinese-CLIP 零样本分类实测 (CPU)"""
import os, time, glob
import cn_clip.clip as clip
from cn_clip.clip import load_from_name
from PIL import Image
import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_DIR = r"E:\PAIOS\10_WORK\photos_organizer\models"
TEST_DIR = r"E:\PAIOS\10_WORK\photos_organizer\inputs\clip_test"

# 分类类别（零样本，自定义中文）
CATEGORIES = [
    "人物肖像", "家庭亲子", "风景自然", "建筑室内", "美食饮品",
    "宠物动物", "车辆交通", "文档截图", "工作会议", "活动宣传",
    "旅行出游", "网络图片素材", "证件发票", "其他",
]

def main():
    print(f"[*] device = {DEVICE}")
    t0 = time.time()
    model, preprocess = load_from_name("ViT-B-16", device=DEVICE, download_root=MODEL_DIR)
    model.eval()
    print(f"[*] 模型加载耗时: {time.time()-t0:.1f}s")

    text = clip.tokenize(CATEGORIES).to(DEVICE)
    with torch.no_grad():
        text_features = model.encode_text(text)
        text_features /= text_features.norm(dim=-1, keepdim=True)

    files = sorted(glob.glob(os.path.join(TEST_DIR, "*")))[:8]
    print(f"[*] 测试图片: {len(files)} 张\n")

    total = 0.0
    for fp in files:
        img = Image.open(fp).convert("RGB")
        inp = preprocess(img).unsqueeze(0).to(DEVICE)
        t1 = time.time()
        with torch.no_grad():
            img_feat = model.encode_image(inp)
            img_feat /= img_feat.norm(dim=-1, keepdim=True)
            logits = (img_feat @ text_features.t())[0]
            probs = logits.softmax(dim=-1)
        dt = time.time() - t1
        total += dt
        top3 = probs.topk(3)
        name = os.path.basename(fp)
        print(f"{name[:28]:<30} {dt*1000:6.0f}ms")
        for i in range(3):
            idx = top3.indices[i].item()
            print(f"      -> {CATEGORIES[idx]:<12} {top3.values[i].item()*100:5.1f}%")

    print(f"\n[*] 平均单张: {total/len(files)*1000:.0f}ms  (即 {1/(total/len(files)):.2f} 张/秒)")

if __name__ == "__main__":
    main()
