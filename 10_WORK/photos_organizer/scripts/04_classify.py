# 04_classify.py — 分类引擎（V1.1 多标签架构）
# 核心变更：
#   1. AI 输出多维度标签（scene/people/object/activity/attribute），不是单一 category
#   2. 规则映射层把标签 → source 目录，AI 和目录组织解耦
#   3. CLIP 保留为 primary_category 快速通道（单标签，但只决定主类别）
#   4. GLM-4V-Flash 输出结构化 JSON + 从词表约束标签
#   5. source 由三层决定：路径启发式 → 标签规则映射 → 降级默认
import sys
import os
import re
import time
import json
import base64

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载项目根目录 .env（后台 shell 不继承交互 shell 的 env 变量，如 ZHIPU_API_KEY）
from utils import load_local_env
load_local_env()


class GLMImageError(Exception):
    """图像无法被 GLM 处理：PIL 解码失败（坏文件）或 API 硬错误（1210 等）。
    与「GLM 正常返回 '其他'」严格区分——前者是不可重试的失败，后者是有效分类结果。"""


# ══════════════════════════════════════════════════════════
# 一、路径启发式 source 推断
# ══════════════════════════════════════════════════════════
def heuristic_source(path, media_type):
    """基于文件名 + 直接父目录关键词推断来源。
    source 是物理目录归属，由路径信息优先决定。
    因为"办公室会议照片"可能是 Work 也可能是 Personal——AI 无法区分。
    """
    p = path.lower().replace("\\", "/")
    fname = os.path.basename(p)
    parent = os.path.basename(os.path.dirname(p))
    scope = fname + "/" + parent

    if media_type == "video":
        return "06_Videos"
    if media_type == "document":
        return "05_Documents"
    if media_type == "livephoto":
        return _livp_source(scope)
    if any(k in scope for k in ["screenshot", "截图", "屏幕截图", "screen"]):
        return "03_Screenshots"
    if any(k in scope for k in ["download", "下载", "wechat", "微信", "image(", "mmexport"]):
        return "04_Downloads"
    if any(k in scope for k in ["work", "工作", "禁毒", "会议", "培训", "签到", "活动", "会议纪要"]):
        return "02_Work"
    return "01_Personal"


def _livp_source(scope):
    if any(k in scope for k in ["wechat", "微信"]):
        return "04_Downloads"
    if any(k in scope for k in ["work", "工作", "禁毒", "会议", "培训"]):
        return "02_Work"
    return "01_Personal"


# ══════════════════════════════════════════════════════════
# 二、标签 → source 规则映射
# ══════════════════════════════════════════════════════════
# 从 vocabulary.mapping 字段读取规则，但这里也硬编码关键映射
# 作为 fallback（数据库未填充时）
TAG_TO_SOURCE_RULES = {
    # scene 标签
    "办公室": "02_Work", "会议室": "02_Work", "工地": "02_Work",
    "训练场": "02_Work", "旗帜": "02_Work",
    # object 标签
    "证件": "05_Documents", "发票": "05_Documents",
    "电脑": "02_Work", "投影仪": "02_Work",
    "二维码": "03_Screenshots", "红包": "03_Screenshots",
    # activity 标签
    "会议": "02_Work", "培训": "02_Work", "签到": "02_Work",
    "演讲": "02_Work", "团建": "02_Work", "禁毒宣传": "02_Work",
    # attribute 标签
    "表情包": "04_Downloads", "壁纸": "04_Downloads",
}

# 主类别列表（8 类，覆盖日常场景）
PRIMARY_CATEGORIES = [
    "人物",   # 人的照片（单人/合照/家庭）
    "工作",   # 工作相关（会议/培训/现场/签到）
    "旅行",   # 旅行出游（景点/风景/度假）
    "美食",   # 餐饮食物
    "文档",   # 截图/证件/发票/带文字
    "网络素材", # 表情包/壁纸/网络图片
    "风景",   # 纯风景（无人物）
    "其他",   # 无法归类
]


def resolve_source(tags, heuristic_src):
    """从多标签推断 source 目录。

    决策优先级：
    1. 标签规则映射（tags 中有明确的 Work/Document/Screenshots 指示）
    2. 路径启发式结果
    3. 默认 01_Personal

    关键设计：只有 tags 明确指向 02_Work/03_Screenshots/05_Documents/04_Downloads 时，
    才会覆盖启发式默认的 01_Personal。否则保留启发式结果。
    """
    # 从标签中查找规则映射
    for tag_type in ["activity", "object", "scene", "attribute"]:
        for tag in tags.get(tag_type, []):
            if tag in TAG_TO_SOURCE_RULES:
                mapped = TAG_TO_SOURCE_RULES[tag]
                # 只有映射到比 Personal 更精确的目录才覆盖
                if heuristic_src == "01_Personal" or mapped in ("02_Work", "03_Screenshots", "05_Documents"):
                    return mapped

    return heuristic_src


def resolve_primary_category(tags):
    """从多标签推断主类别（primary_category）。

    主类别是唯一归属，用于目录名和快速筛选。
    决策逻辑：
    - activity 标签优先（会议→工作，旅行→旅行）
    - 然后看 people 标签（有人物→人物）
    - 然后看 scene/object 标签
    - 兜底→其他
    """
    # activity 优先
    activities = tags.get("activity", [])
    if activities:
        for act in activities:
            if act in ("会议", "培训", "签到", "演讲", "团建", "禁毒宣传"):
                return "工作"
            if act in ("旅行", "爬山", "钓鱼"):
                return "旅行"
            if act in ("聚餐", "烧烤"):
                return "美食"

    # people 标签
    people = tags.get("people", [])
    if people:
        return "人物"

    # object 标签
    objects = tags.get("object", [])
    if objects:
        for obj in objects:
            if obj in ("食物",):
                return "美食"
            if obj in ("证件", "发票", "二维码", "红包"):
                return "文档"
            if obj in ("表情包", "壁纸"):
                return "网络素材"

    # scene 标签（纯风景）
    scenes = tags.get("scene", [])
    if scenes and not people:
        return "风景"

    # attribute 标签
    attrs = tags.get("attribute", [])
    if attrs:
        for attr in attrs:
            if attr in ("表情包", "壁纸"):
                return "网络素材"

    return "其他"


# ══════════════════════════════════════════════════════════
# 三、本地 Chinese-CLIP 零样本分类（主类别快速通道）
# ══════════════════════════════════════════════════════════
# CLIP 仍然输出单标签 → 映射到 primary_category
# 不输出多标签（CLIP 能力不够），但速度极快（3.6s/张 CPU）
# 用于 hybrid 模式的第一层过滤

CLIP_VISUAL_CATEGORIES = [
    "一个人的照片",
    "多个人在一起的合照",
    "山水天空花草树木自然风景",
    "室内房间桌椅家具装修",
    "餐桌上饭菜饮料美食",
    "猫狗小鸟宠物动物",
    "汽车摩托车自行车交通工具",
    "电脑手机屏幕截图或带文字的文档",
    "开会培训讲座工作现场",
    "旅游景点旅行风景拍照",
    "表情包壁纸网络图片素材",
]

CLIP_TO_PRIMARY = {
    0: "人物", 1: "人物", 2: "风景", 3: "风景",
    4: "美食", 5: "其他", 6: "其他", 7: "文档",
    8: "工作", 9: "旅行", 10: "网络素材",
}

CLIP_TO_TAGS = {
    0: {"people": ["单人"]}, 1: {"people": ["多人"]},
    2: {"scene": ["山顶", "海边"], "attribute": ["户外"]},
    3: {"scene": ["办公室"], "attribute": ["室内"]},
    4: {"object": ["食物"]},
    5: {"object": ["宠物"]},
    6: {"object": ["汽车"]},
    7: {"object": ["证件"], "attribute": ["横屏"]},
    8: {"activity": ["会议"], "scene": ["会议室"]},
    9: {"activity": ["旅行"]},
    10: {"attribute": ["表情包"]},
}

CLIP_TEMPERATURE = 0.02
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models")


def classify_local_clip(path, threshold=0.35):
    """本地 CLIP → (primary_category, confidence, tags_dict)
    CLIP 只输出主类别 + 简单标签映射。多标签由 GLM 补判提供。"""
    import torch
    from cn_clip.clip import load_from_name, tokenize
    from PIL import Image as PILImage

    if not hasattr(classify_local_clip, "_cache"):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model, preprocess = load_from_name(
            "ViT-B-16", device=device, download_root=MODEL_DIR
        )
        model.eval()
        text = tokenize(CLIP_VISUAL_CATEGORIES).to(device)
        with torch.no_grad():
            text_feat = model.encode_text(text)
            text_feat /= text_feat.norm(dim=-1, keepdim=True)
        classify_local_clip._cache = (model, preprocess, device, text_feat)
    model, preprocess, device, text_feat = classify_local_clip._cache

    try:
        image = preprocess(PILImage.open(path).convert("RGB")).unsqueeze(0).to(device)
    except Exception:
        return "其他", 0.0, {}

    with torch.no_grad():
        img_feat = model.encode_image(image)
        img_feat /= img_feat.norm(dim=-1, keepdim=True)
        logits = (img_feat @ text_feat.t())[0]
        probs = (logits / CLIP_TEMPERATURE).softmax(dim=-1)
    idx = probs.argmax().item()
    conf = probs[idx].item()
    if conf < threshold:
        return "其他", round(conf, 3), {}
    primary = CLIP_TO_PRIMARY.get(idx, "其他")
    tags = CLIP_TO_TAGS.get(idx, {})
    return primary, round(conf, 3), tags


# ══════════════════════════════════════════════════════════
# 四、GLM-4V-Flash 多标签分类（核心引擎）
# ══════════════════════════════════════════════════════════
# Prompt 要求 VLM 输出结构化 JSON：
#   primary_category: 主类别（8 选 1）
#   scene_tags: 场景标签（从词表选）
#   people_tags: 人物标签
#   object_tags: 物体标签
#   activity_tags: 活动标签
#   attribute_tags: 属性标签
#   description: 一句话描述
#   confidence: 0-1

GLM4V_MULTITAG_PROMPT = """请仔细观察这张照片，进行多维度分析。

**主类别**（必须从以下8个中选择唯一一个）：
- 人物：有人出现的照片（单人照、合照、家庭照、自拍照）
- 工作：与工作相关（会议、培训、签到、现场检查、PPT投影）
- 旅行：旅行出游（景区、景点、度假、观光）
- 美食：食物餐饮（餐桌、菜品、饮料、聚餐）
- 文档：截图、证件、发票、带文字的图片、二维码
- 网络素材：表情包、壁纸、网络图片、素材图
- 风景：纯自然风景（无人物的山水、天空、花草）
- 其他：无法归类的图片

**标签**（从以下词表中选择，每个维度可选0-3个）：
场景(scene)：海边、山顶、公园、校园、办公室、会议室、酒店、餐厅、厨房、卧室、客厅、医院、机场、高铁站、商场、博物馆、体育馆、婚礼、生日、春节、中秋、雪景、夜景、农田、工地、训练场、景区、街道
人物(people)：自己、家人、父亲、母亲、孩子、同事、朋友、多人、单人、情侣
物体(object)：食物、宠物、汽车、证件、发票、电脑、手机、投影仪、旗帜、二维码、红包、衣服、玩具、书籍、乐器、花卉
活动(activity)：旅行、会议、培训、聚餐、运动、购物、自拍、演讲、签到、团建、钓鱼、爬山、烧烤、装修
属性(attribute)：横屏、竖屏、白天、夜晚、室内、户外、近景、远景、模糊、修图、黑白、拼图、水印、表情包、壁纸

请**严格**按以下JSON格式输出（不要添加任何其他文字）：
```json
{
  "primary": "主类别名",
  "scene": ["场景标签1", "场景标签2"],
  "people": ["人物标签1"],
  "object": ["物体标签1", "物体标签2"],
  "activity": ["活动标签1"],
  "attribute": ["属性标签1"],
  "description": "一句话描述",
  "confidence": 0.85
}
```"""


def classify_glm4v_flash(path, api_key, model="glm-4v-flash",
                         max_retries=3, retry_delay=2.0):
    """GLM-4V-Flash 多标签分类。返回 (primary_category, confidence, tags_dict, description)

    tags_dict 结构: {"scene": [...], "people": [...], "object": [...],
                     "activity": [...], "attribute": [...]}

    失败语义（重要）：
      - 返回 ("其他", ...)  ⇢ GLM 正常看到图、但判为不可归类（有效结果，调用方应保留 CLIP）
      - 抛 GLMImageError  ⇢ 坏文件(PIL 打不开) 或 API 硬错误(1210 等)，不可重试，调用方应兜底
    """
    from zhipuai import ZhipuAI

    # 降采样 + 转 JPEG 压到 glm-4v-flash 体积限制内。
    # 原始大图（>~5MB → base64 ~7MB）会触发 1210「参数有误」，必须缩图。
    mime = "image/jpeg"
    try:
        from PIL import Image
        import io
        with Image.open(path) as im:
            im = im.convert("RGB")
            max_side = 1280
            if max(im.size) > max_side:
                r = max_side / max(im.size)
                im = im.resize((int(im.size[0] * r), int(im.size[1] * r)), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=85)
            raw = buf.getvalue()
            q = 85
            while len(raw) > 2_000_000 and q > 40:
                q -= 15
                buf = io.BytesIO()
                im.save(buf, format="JPEG", quality=q)
                raw = buf.getvalue()
        img_b64 = base64.b64encode(raw).decode("utf-8")
    except Exception as e:
        # PIL 都打不开 = 坏文件（corrupt / HEIC 改后缀等），根本不该调 API，直接报错
        raise GLMImageError(f"图像无法解码/转码: {e}")

    client = ZhipuAI(api_key=api_key)

    last_err = None
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime};base64,{img_b64}"
                                },
                            },
                            {
                                "type": "text",
                                "text": GLM4V_MULTITAG_PROMPT,
                            },
                        ],
                    }
                ],
                max_tokens=100,
                temperature=0.1,
            )
            text = response.choices[0].message.content.strip()
            return _parse_glm4v_multitag(text)
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "rate" in err_str.lower():
                wait = retry_delay * (attempt + 1)
                print(f"  GLM-4V 限流，等待 {wait}s ({attempt+1}/{max_retries})", flush=True)
                time.sleep(wait)
                continue
            # 1210/1301 等硬错误：仅多试 1 次吸收瞬时抖动，仍失败则抛出（不 3× 空耗）
            last_err = err_str
            if attempt < 1:
                print(f"  GLM-4V 硬错误(重试1次): {err_str[:120]}", flush=True)
                time.sleep(1.0)
                continue
            raise GLMImageError(f"GLM API 硬错误: {err_str}")

    raise GLMImageError(f"GLM 限流重试耗尽: {last_err}")


def _parse_glm4v_multitag(text):
    """解析 GLM-4V-Flash 返回的多标签 JSON。

    返回 (primary_category, confidence, tags_dict, description)
    """
    # 尝试提取 JSON
    json_match = re.search(r'\{[^{}]+\}', text, re.DOTALL)
    if not json_match:
        # fallback: 尝试从非结构化文本中提取信息
        return _parse_glm4v_fallback(text)

    try:
        data = json.loads(json_match.group())
    except json.JSONDecodeError:
        # JSON 解析失败，尝试修复常见问题
        cleaned = json_match.group()
        cleaned = re.sub(r'[\n\r\t]', '', cleaned)
        cleaned = cleaned.replace('"', '"').replace('"', '"')
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            return _parse_glm4v_fallback(text)

    primary = data.get("primary", "其他")
    confidence = float(data.get("confidence", 0.7))
    confidence = max(0.0, min(1.0, confidence))
    description = data.get("description", "")

    # 归一化 primary_category
    primary = _normalize_primary(primary)

    # 归一化各维度标签 + 词表过滤
    tags = {}
    for key, vocab_key in [
        ("scene", "scene"), ("people", "people"),
        ("object", "object"), ("activity", "activity"),
        ("attribute", "attribute"),
    ]:
        raw_tags = data.get(key, [])
        if isinstance(raw_tags, str):
            raw_tags = [raw_tags]
        normalized = [_normalize_tag(t, vocab_key) for t in raw_tags]
        # 词表过滤：只保留词表中存在的标签（或已归一化到词表的）
        valid_vocab = _get_vocab_set(vocab_key)
        filtered = [t for t in normalized if t in valid_vocab]
        tags[key] = filtered

    return primary, round(confidence, 3), tags, description


def _normalize_primary(raw):
    """归一化主类别到 PRIMARY_CATEGORIES 中的标准名。"""
    raw = raw.strip()
    mapping = {
        "人物肖像": "人物", "人物照": "人物", "人像": "人物", "个人": "人物",
        "工作会议": "工作", "工作照": "工作", "办公": "工作",
        "旅行出游": "旅行", "旅游": "旅行", "出游": "旅行",
        "美食饮品": "美食", "食物": "美食", "餐饮": "美食",
        "文档截图": "文档", "截图": "文档", "证件": "文档",
        "网络素材": "网络素材", "表情包": "网络素材", "壁纸": "网络素材",
        "风景自然": "风景", "自然": "风景", "景色": "风景",
        "家庭亲子": "人物",  # 家庭照归到人物主类别
        "宠物动物": "其他",
        "车辆交通": "其他",
        "建筑室内": "风景",
    }
    for key, std in mapping.items():
        if key in raw or raw in key:
            return std
    if raw in PRIMARY_CATEGORIES:
        return raw
    return "其他"


# 词表缓存（从 DB 或硬编码加载）
_VOCAB_CACHE = {}

# 硬编码词表（作为 DB 未填充时的 fallback）
_HARDCODED_VOCAB = {
    "scene": set(["海边", "山顶", "公园", "校园", "办公室", "会议室", "酒店", "餐厅",
                  "厨房", "卧室", "客厅", "医院", "机场", "高铁站", "商场", "博物馆",
                  "体育馆", "婚礼", "生日", "春节", "中秋", "雪景", "夜景", "农田",
                  "工地", "训练场", "景区", "街道"]),
    "people": set(["自己", "家人", "父亲", "母亲", "孩子", "同事", "朋友", "多人", "单人", "情侣"]),
    "object": set(["食物", "宠物", "汽车", "证件", "发票", "电脑", "手机", "投影仪",
                   "旗帜", "二维码", "红包", "衣服", "玩具", "书籍", "乐器", "花卉"]),
    "activity": set(["旅行", "会议", "培训", "聚餐", "运动", "购物", "自拍", "演讲",
                     "签到", "团建", "钓鱼", "爬山", "烧烤", "装修"]),
    "attribute": set(["横屏", "竖屏", "白天", "夜晚", "室内", "户外", "近景", "远景",
                      "模糊", "修图", "黑白", "拼图", "水印", "表情包", "壁纸"]),
}


def _get_vocab_set(tag_type):
    """获取某维度标签的有效词表集合。
    优先从 DB vocabulary 表读取，fallback 到硬编码词表。
    """
    if tag_type in _VOCAB_CACHE:
        return _VOCAB_CACHE[tag_type]

    # 尝试从 DB 加载
    try:
        import sqlite3
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "..", "database", "photo_index.db")
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            rows = conn.execute(
                "SELECT tag_value, synonyms FROM vocabulary WHERE tag_type=? AND enabled=1",
                (tag_type,)
            ).fetchall()
            vocab = set()
            import json as _json
            for row in rows:
                vocab.add(row[0])
                if row[1]:
                    try:
                        for syn in _json.loads(row[1]):
                            vocab.add(syn)
                    except Exception:
                        pass
            conn.close()
            if vocab:
                _VOCAB_CACHE[tag_type] = vocab
                return vocab
    except Exception:
        pass

    # Fallback: 硬编码词表
    vocab = _HARDCODED_VOCAB.get(tag_type, set())
    _VOCAB_CACHE[tag_type] = vocab
    return vocab


def _normalize_tag(raw, tag_type):
    """归一化标签到词表中的标准名。"""
    raw = raw.strip()
    synonym_map = {
        # scene
        "海滩": "海边", "沙滩": "海边", "海岸": "海边",
        "山峰": "山顶", "高山": "山顶",
        "花园": "公园", "绿地": "公园",
        "学校": "校园", "教室": "校园",
        "公司": "办公室", "职场": "办公室", "工位": "办公室",
        "研讨室": "会议室",
        "旅馆": "酒店", "民宿": "酒店",
        "饭馆": "餐厅", "食堂": "餐厅", "咖啡厅": "餐厅",
        "车展": "商场",
        "展览馆": "博物馆", "画廊": "博物馆",
        "健身房": "体育馆", "运动场": "体育馆",
        "婚宴": "婚礼",
        "过年": "春节", "除夕": "春节", "年夜饭": "春节",
        "冬天": "雪景", "积雪": "雪景",
        "夜市": "夜景",
        # people
        "自拍": "自己", "我": "自己",
        "爸爸": "父亲", "老爸": "父亲",
        "妈妈": "母亲", "老妈": "母亲",
        "儿子": "孩子", "女儿": "孩子", "小孩": "孩子",
        "一群人": "多人", "群体": "多人", "人群": "多人",
        "一个人": "单人", "独照": "单人",
        "夫妻": "情侣", "伴侣": "情侣",
        # object
        "饭菜": "食物", "美食": "食物", "零食": "食物",
        "猫": "宠物", "狗": "宠物",
        "车辆": "汽车", "轿车": "汽车",
        "身份证": "证件", "驾照": "证件", "护照": "证件", "证书": "证件",
        "收据": "发票", "账单": "发票", "小票": "发票",
        "笔记本": "电脑", "台式机": "电脑", "显示器": "电脑",
        "PPT": "投影仪", "投影": "投影仪", "幻灯片": "投影仪",
        "横幅": "旗帜", "标语": "旗帜",
        "条形码": "二维码",
        "微信红包": "红包", "转账": "红包",
        # activity
        "旅游": "旅行", "出游": "旅行", "度假": "旅行",
        "开会": "会议", "例会": "会议", "研讨": "会议",
        "学习": "培训", "讲座": "培训", "授课": "培训",
        "吃饭": "聚餐", "宴席": "聚餐",
        "跑步": "运动", "健身": "运动", "打球": "运动", "游泳": "运动",
        "逛街": "购物", "买菜": "购物",
        "拍照": "自拍", "合影": "自拍",
        "汇报": "演讲", "报告": "演讲", "发言": "演讲",
        "打卡": "签到", "报名": "签到", "登记": "签到",
        "集体活动": "团建", "拓展": "团建",
        "垂钓": "钓鱼",
        "登山": "爬山", "徒步": "爬山",
        "BBQ": "烧烤", "烤肉": "烧烤",
        # attribute
        "横向": "横屏", "纵向": "竖屏",
        "日间": "白天", "晴天": "白天",
        "夜间": "夜晚", "晚上": "夜晚", "暗光": "夜晚",
        "屋内": "室内",
        "室外": "户外",
        "特写": "近景", "近距离": "近景",
        "全景": "远景", "广角": "远景",
        "不清晰": "模糊", "抖动": "模糊",
        "滤镜": "修图", "后期": "修图", "美颜": "修图",
        "meme": "表情包", "搞笑图": "表情包",
        "背景图": "壁纸", "锁屏": "壁纸",
    }
    if raw in synonym_map:
        return synonym_map[raw]
    return raw


def _parse_glm4v_fallback(text):
    """非结构化文本 fallback 解析。"""
    primary = "其他"
    tags = {}
    confidence = 0.5

    # 尝试从文本中提取已知标签
    for cat in PRIMARY_CATEGORIES:
        if cat in text:
            primary = cat
            break

    # 从文本中搜索各维度标签
    for tag_type, vocab in [
        ("scene", ["海边", "山顶", "公园", "校园", "办公室", "会议室", "餐厅", "酒店"]),
        ("people", ["自己", "家人", "朋友", "同事", "多人", "单人", "孩子", "父亲", "母亲"]),
        ("object", ["食物", "宠物", "汽车", "证件", "发票", "电脑", "手机", "二维码"]),
        ("activity", ["旅行", "会议", "培训", "聚餐", "运动", "自拍", "签到"]),
        ("attribute", ["横屏", "竖屏", "白天", "夜晚", "室内", "户外", "模糊"]),
    ]:
        found = [v for v in vocab if v in text]
        if found:
            tags[tag_type] = found

    return primary, confidence, tags, text[:50]


# ══════════════════════════════════════════════════════════
# 五、百度图像识别（备用）
# ══════════════════════════════════════════════════════════
def classify_baidu(path, api_key_str, endpoint):
    import requests

    headers = {}
    url = endpoint
    if api_key_str.startswith("bce-v3/"):
        headers["Authorization"] = f"Bearer {api_key_str}"
    else:
        parts = api_key_str.split(",", 1)
        if len(parts) == 2:
            ak, sk = parts[0], parts[1]
            token = get_baidu_token(ak, sk)
            url = f"{endpoint}?access_token={token}"
        else:
            return "其他", 0.0, {}

    with open(path, "rb") as f:
        r = requests.post(url, headers=headers, files={"image": f}, timeout=15)
    data = r.json()
    if "result" in data and data["result"]:
        top = data["result"][0]
        keyword = top.get("keyword", "")
        score = float(top.get("score", 0))
        primary = _normalize_primary(keyword)
        return primary, round(score, 3), {"object": [keyword]}, keyword
    return "其他", 0.0, {}


def get_baidu_token(api_key, secret_key):
    import requests
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": api_key, "client_secret": secret_key}
    r = requests.get(url, params=params, timeout=10)
    return r.json()["access_token"]


# ══════════════════════════════════════════════════════════
# 六、统一分类入口
# ══════════════════════════════════════════════════════════
def classify_image(path, media_type, cfg):
    """返回 (source, primary_category, confidence, tags_dict, description, method)

    V1.1 多标签架构：
    1. 非照片类型 → 启发式路由 + 固定标签
    2. Hybrid 模式：CLIP 先出 primary_category → 低置信度时 GLM 补判多标签
    3. source 由三层决定：路径启发式 → 标签规则映射 → 默认
    4. primary_category 由标签推断
    5. tags 写入 DB tags 表
    """
    # ── Step 1: 启发式 source ──
    heuristic_src = heuristic_source(path, media_type)

    # ── Step 2: 非 photo 类型直接返回 ──
    if media_type == "video":
        return heuristic_src, "其他", 1.0, {"activity": ["视频"]}, "视频文件", "media_type"
    if media_type == "document":
        return heuristic_src, "文档", 1.0, {"object": ["文档"]}, "文档文件", "media_type"
    if media_type == "livephoto":
        return heuristic_src, "人物", 1.0, {"attribute": ["LivePhoto"]}, "Live Photo", "media_type"
    if media_type == "raw":
        return heuristic_src, "风景", 1.0, {"attribute": ["RAW"]}, "RAW照片", "media_type"
    if media_type == "other":
        return heuristic_src, "其他", 1.0, {}, "其他文件", "media_type"

    # ── Step 3: photo → AI 分类 ──
    cls_cfg = cfg.get("classification", {})
    provider = cls_cfg.get("provider", "hybrid")
    threshold = cls_cfg.get("confidence_threshold", 0.35)
    fallback_threshold = cls_cfg.get("fallback_threshold", 0.40)

    primary = "其他"
    confidence = 0.0
    tags = {}
    description = ""
    method = "heuristic"

    # ── Hybrid 模式 ──
    if provider == "hybrid":
        try:
            clip_primary, clip_conf, clip_tags = classify_local_clip(path, threshold)
            method = "local_clip"
            primary = clip_primary
            confidence = clip_conf
            tags = clip_tags
        except Exception:
            primary, confidence, tags = "其他", 0.0, {}

        # CLIP 置信度低 → GLM 多标签补判
        if confidence < fallback_threshold:
            glm_cfg = cls_cfg.get("glm4v_flash", {})
            api_key = os.environ.get(glm_cfg.get("api_key_env", "ZHIPU_API_KEY"))
            if api_key:
                try:
                    glm_primary, glm_conf, glm_tags, glm_desc = classify_glm4v_flash(
                        path, api_key,
                        model=glm_cfg.get("model", "glm-4v-flash"),
                        max_retries=glm_cfg.get("max_retries", 3),
                        retry_delay=glm_cfg.get("retry_delay", 2.0),
                    )
                    if glm_primary != "其他":
                        primary, confidence, tags, description, method = (
                            glm_primary, glm_conf, glm_tags, glm_desc, "glm4v_flash"
                        )
                except Exception:
                    pass

    # ── 纯 CLIP ──
    elif provider == "local_clip":
        try:
            primary, confidence, tags = classify_local_clip(path, threshold)
            method = "local_clip"
        except Exception:
            primary, confidence, tags = "其他", 0.0, {}

    # ── 纯 GLM ──
    elif provider == "glm4v_flash":
        glm_cfg = cls_cfg.get("glm4v_flash", {})
        api_key = os.environ.get(glm_cfg.get("api_key_env", "ZHIPU_API_KEY"))
        if api_key:
            try:
                primary, confidence, tags, description = classify_glm4v_flash(
                    path, api_key,
                    model=glm_cfg.get("model", "glm-4v-flash"),
                    max_retries=glm_cfg.get("max_retries", 3),
                    retry_delay=glm_cfg.get("retry_delay", 2.0),
                )
                method = "glm4v_flash"
            except Exception:
                primary, confidence, tags, description = "其他", 0.0, {}, ""

    # ── 百度 ──
    elif provider == "baidu":
        baidu_cfg = cls_cfg.get("baidu", {})
        api_key_str = os.environ.get(baidu_cfg.get("api_key_env", "BAIDU_API_KEY"))
        ak = os.environ.get(baidu_cfg.get("secret_key_env", "BAIDU_SECRET_KEY"))
        if api_key_str:
            if api_key_str.startswith("bce-v3/"):
                auth_str = api_key_str
            elif ak:
                auth_str = f"{api_key_str},{ak}"
            else:
                auth_str = api_key_str
            try:
                primary, confidence, tags, description = classify_baidu(
                    path, auth_str, baidu_cfg.get("endpoint",
                    "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general")
                )
                method = "baidu"
            except Exception as e:
                print(f"  百度分类失败: {e}")

    # ── Step 4: 低置信度 → 07_ToReview ──
    if confidence < threshold and method not in ("heuristic", "media_type"):
        primary = "其他"
        heuristic_src = "07_ToReview"

    # ── Step 5: 标签 → source 规则映射 ──
    # 关键：只有 tags 明确指向非 Personal 时才覆盖启发式
    source = resolve_source(tags, heuristic_src)

    # ── Step 6: 标签 → primary_category 推断 ──
    # 如果 GLM 已输出 primary，直接用；否则从 tags 推断
    if method in ("local_clip", "heuristic") and tags:
        primary = resolve_primary_category(tags)

    return source, primary, confidence, tags, description, method


if __name__ == "__main__":
    import argparse
    from utils import load_config

    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--provider", default=None)
    args = ap.parse_args()
    cfg = load_config()
    if args.provider:
        cfg["classification"]["provider"] = args.provider
    ext = os.path.splitext(args.path)[1].lower()
    from utils import classify_media_type
    mt = classify_media_type(ext)
    result = classify_image(args.path, mt, cfg)
    src, primary, conf, tags, desc, method = result
    print(f"source={src}  primary={primary}  conf={conf}  method={method}")
    print(f"tags={json.dumps(tags, ensure_ascii=False)}")
    print(f"desc={desc}")
