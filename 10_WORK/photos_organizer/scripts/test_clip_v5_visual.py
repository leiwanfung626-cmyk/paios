"""CLIP 最终方案: 视觉导向类别 + 低温度缩放"""
import os, glob
import cn_clip.clip as clip
from cn_clip.clip import load_from_name
from PIL import Image
import torch

DEVICE = "cpu"
MODEL_DIR = r"E:\PAIOS\10_WORK\photos_organizer\models"
TEST_DIR = r"E:\PAIOS\10_WORK\photos_organizer\inputs\clip_test"

# 视觉导向类别: 描述画面里有什么,而不是抽象概念
VISUAL = [
    "一个人的照片",            # 人物肖像
    "多个人在一起的照片",      # 家庭亲子/聚会
    "山水天空花草树木风景",    # 风景自然
    "房间室内桌椅家具",        # 建筑室内
    "餐桌上的饭菜饮料美食",    # 美食饮品
    "猫狗小鸟宠物动物",        # 宠物
    "汽车摩托车交通工具",       # 车辆
    "电脑屏幕手机截图",        # 截图
    "文字表格发票合同文件",    # 文档
    "开会培训讲座现场",        # 工作
    "旅游景点旅行拍照",        # 旅行
    "表情包壁纸网图素材",      # 网络
    "身份证件票证卡片",        # 证件
]

# 映射回标准分类
MAP = {
    0: "人物肖像", 1: "家庭亲子", 2: "风景自然", 3: "建筑室内",
    4: "美食饮品", 5: "宠物动物", 6: "车辆交通", 7: "文档截图",
    8: "工作会议", 9: "旅行出游", 10: "04_Downloads", 11: "04_Downloads",
    12: "05_Documents",
}

TEMPERATURE = 0.015   # 经验最优值: 区分力强但不至于过度自信

def main():
    model, preprocess = load_from_name("ViT-B-16", device=DEVICE, download_root=MODEL_DIR)
    model.eval()
    text = clip.tokenize(VISUAL).to(DEVICE)
    with torch.no_grad():
        text_feat = model.encode_text(text)
        text_feat /= text_feat.norm(dim=-1, keepdim=True)

    # 检查文本相似度是否改善
    t_sim = (text_feat @ text_feat.t()).cpu()
    off_diag = []
    for i in range(len(VISUAL)):
        for j in range(i+1, len(VISUAL)):
            off_diag.append(t_sim[i][j].item())
    print(f"[类别间平均相似度] {sum(off_diag)/len(off_diag):.3f} (之前: 0.758)")
    print(f"{'文件':<30} {'Top1':<18} {'标准类':<12} {'置信度':>6}")
    print("-" * 72)

    files = sorted(glob.glob(os.path.join(TEST_DIR, "*")))
    ok = 0; total = len(files)
    for fp in files:
        name = os.path.basename(fp)[:28]
        img = Image.open(fp).convert("RGB")
        inp = preprocess(img).unsqueeze(0).to(DEVICE)
        with torch.no_grad():
            img_feat = model.encode_image(inp)
            img_feat /= img_feat.norm(dim=-1, keepdim=True)
            logits = (img_feat @ text_feat.t())[0]
            probs = (logits / TEMPERATURE).softmax(dim=-1)
        top_idx = probs.argmax().item()
        top_val = probs[top_idx].item()
        std_cat = MAP.get(top_idx, "其他")
        marker = ""
        if top_val > 0.4:
            marker = " ✓"
            ok += 1
        elif top_val > 0.25:
            marker = " ~"
        else:
            marker = " ?"
        print(f"{name:<30} {VISUAL[top_idx]:<18} {std_cat:<12} {top_val*100:5.1f}%{marker}")

    print(f"\n高置信(>40%): {ok}/{total}  中置信(25-40%): ...  低置信(<25%): ...")

if __name__ == "__main__":
    main()
