# init_db.py — 初始化 photo_index.db（V1.1 扩展 + V1.0-final 补全）
# Schema: photos + tags + vocabulary + jobs + photo_versions
# 核心原则：Metadata Evolves, Assets Don't（元数据演进，资产不变）
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = r"E:\PAIOS\10_WORK\photos_organizer\database\photo_index.db"


def init():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # ── photos 表（V1.0-final 扩展）──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS photos (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        filename          TEXT,
        path              TEXT UNIQUE,
        md5               TEXT,
        phash             TEXT,
        dhash             TEXT,
        date              TEXT,
        camera            TEXT,
        gps               TEXT,
        media_type        TEXT,        -- photo/video/livephoto/raw/document/other
        extension         TEXT,        -- 原始扩展名（.jpg/.heic/.cr2/.mp4 等）
        source            TEXT,        -- 物理目录归属（01_Personal~90_Trash）
        primary_category  TEXT,        -- 主类别（唯一，人物/工作/旅行/文档等）
        confidence        REAL,
        classifier        TEXT,        -- 分类引擎：local_clip/glm4v_flash/heuristic/media_type
        classifier_version TEXT,       -- 引擎版本：ViT-B-16-v1/glm4v-flash-202607
        quality_score     INTEGER,     -- 图片质量 0-100（预留）
        duplicate_group   TEXT,        -- 感知去重组 ID
        master            INTEGER DEFAULT 1,  -- 去重组主图标记：1=主图 0=副本
        value_level       TEXT,        -- 价值分级 A/B/C/D（预留）
        caption           TEXT,        -- 图片描述（预留，仅对 A/B 照片生成）
        batch_id          TEXT,
        created_at        TEXT,
        updated_at        TEXT,
        processed_at      TEXT
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_md5 ON photos(md5);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_path ON photos(path);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_date ON photos(date);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_source ON photos(source);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_primary_category ON photos(primary_category);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_classifier ON photos(classifier);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_extension ON photos(extension);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_duplicate_group ON photos(duplicate_group);")

    # ── tags 表（多标签，EAV 结构）──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tags (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        photo_id  INTEGER NOT NULL,
        tag_type  TEXT NOT NULL,     -- scene/people/object/activity/attribute/event/custom
        tag_value TEXT NOT NULL,     -- 具体标签名（来自词表）
        source    TEXT NOT NULL,     -- 标签来源：ai/heuristic/manual
        confidence REAL DEFAULT 1.0,
        created_at TEXT,
        FOREIGN KEY (photo_id) REFERENCES photos(id)
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tag_photo ON tags(photo_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tag_type ON tags(tag_type);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tag_value ON tags(tag_value);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tag_lookup ON tags(tag_type, tag_value);")

    # ── vocabulary 表（标签词表，约束输出）──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vocabulary (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        tag_type  TEXT NOT NULL,
        tag_value TEXT NOT NULL,
        synonyms  TEXT,              -- 同义词列表（JSON数组）
        mapping   TEXT,              -- 规则映射目标（source 目录名）
        enabled   INTEGER DEFAULT 1,
        UNIQUE(tag_type, tag_value)
    );
    """)

    # ── jobs 表（处理批次审计记录）──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id        TEXT UNIQUE,
        pipeline_version TEXT,       -- v1.0/v1.1/v1.2
        classifier      TEXT,       -- hybrid/local_clip/glm4v_flash
        classifier_version TEXT,
        started_at      TEXT,
        finished_at     TEXT,
        processed_count INTEGER,
        failed_count    INTEGER,
        duration_seconds REAL
    );
    """)

    # ── photo_versions 表（分类历史追踪）──
    # 每次分类更新 = INSERT photo_versions + UPDATE photos（当前值）
    # 永远保留历史，可追溯"谁在什么时候用什么模型分类了这张照片"
    cur.execute("""
    CREATE TABLE IF NOT EXISTS photo_versions (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        photo_id        INTEGER NOT NULL,
        version         INTEGER NOT NULL,  -- 递增版本号（第1次分类=1，第2次=2...）
        classifier      TEXT,              -- 分类引擎名
        classifier_version TEXT,           -- 引擎版本号
        primary_category TEXT,             -- 当时的主类别
        confidence      REAL,              -- 当时的置信度
        tags_json       TEXT,              -- 当时的完整标签快照（JSON）
        caption         TEXT,              -- 当时的描述
        source          TEXT,              -- 当时的目录归属
        created_at      TEXT,
        FOREIGN KEY (photo_id) REFERENCES photos(id)
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pv_photo ON photo_versions(photo_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pv_classifier ON photo_versions(classifier);")

    conn.commit()
    conn.close()
    print(f"DB 初始化完成 (V1.0-final schema): {DB_PATH}")


def seed_vocabulary(conn):
    """预填充标签词表。VLM 从词表中选择标签，而不是自由输出。"""
    cur = conn.cursor()

    # ── scene（场景标签）──
    scenes = [
        ("海边", ["海滩", "沙滩", "海岸"], "01_Personal"),
        ("山顶", ["山峰", "高山", "丘陵"], "01_Personal"),
        ("公园", ["花园", "绿地", "草坪"], "01_Personal"),
        ("校园", ["学校", "教室", "操场"], "01_Personal"),
        ("办公室", ["公司", "职场", "工位"], "02_Work"),
        ("会议室", ["开会", "研讨室"], "02_Work"),
        ("酒店", ["旅馆", "民宿", "客房"], "01_Personal"),
        ("餐厅", ["饭馆", "食堂", "咖啡厅"], "01_Personal"),
        ("厨房", ["灶台", "炊具"], "01_Personal"),
        ("卧室", ["房间", "床铺"], "01_Personal"),
        ("客厅", ["起居室", "沙发"], "01_Personal"),
        ("医院", ["诊所", "病房"], "01_Personal"),
        ("机场", ["航站楼", "登机口"], "01_Personal"),
        ("高铁站", ["火车站", "候车室"], "01_Personal"),
        ("商场", ["购物中心", "超市", "市场"], "01_Personal"),
        ("博物馆", ["展览馆", "画廊"], "01_Personal"),
        ("体育馆", ["健身房", "运动场"], "01_Personal"),
        ("婚礼", ["婚宴", "婚庆"], "01_Personal"),
        ("生日", ["生日派对", "庆生"], "01_Personal"),
        ("春节", ["过年", "除夕", "年夜饭"], "01_Personal"),
        ("中秋", ["月饼", "赏月"], "01_Personal"),
        ("毕业典礼", ["毕业", "学位授予"], "01_Personal"),
        ("雪景", ["冬天", "积雪", "雪地"], "01_Personal"),
        ("夜景", ["夜市", "灯光", "晚景"], "01_Personal"),
        ("农田", ["乡村", "田地", "庄稼"], "01_Personal"),
        ("工地", ["施工现场", "建筑工地"], "02_Work"),
        ("训练场", ["培训基地", "练习场"], "02_Work"),
        ("景区", ["景点", "名胜", "观光"], "01_Personal"),
        ("街道", ["马路", "路口", "人行道"], "01_Personal"),
    ]

    # ── people（人物标签）──
    people = [
        ("自己", ["自拍", "我"], None),
        ("家人", ["亲属", "家人"], None),
        ("父亲", ["爸爸", "老爸"], None),
        ("母亲", ["妈妈", "老妈"], None),
        ("孩子", ["儿子", "女儿", "小孩"], None),
        ("同事", ["搭档", "伙伴"], None),
        ("朋友", ["友人", "同学"], None),
        ("多人", ["一群人", "群体", "人群"], None),
        ("单人", ["一个人", "独照"], None),
        ("情侣", ["夫妻", "伴侣"], None),
    ]

    # ── object（物体标签）──
    objects = [
        ("食物", ["饭菜", "美食", "零食"], "01_Personal"),
        ("宠物", ["猫", "狗", "小动物"], "01_Personal"),
        ("汽车", ["车辆", "轿车", "SUV"], "01_Personal"),
        ("证件", ["身份证", "驾照", "护照", "证书"], "05_Documents"),
        ("发票", ["收据", "账单", "小票"], "05_Documents"),
        ("电脑", ["笔记本", "台式机", "显示器"], "02_Work"),
        ("手机", ["iPhone", "安卓机"], "01_Personal"),
        ("投影仪", ["PPT", "投影", "幻灯片"], "02_Work"),
        ("旗帜", ["横幅", "标语", "宣传"], "02_Work"),
        ("二维码", ["条形码", "扫码"], "03_Screenshots"),
        ("红包", ["微信红包", "转账"], "03_Screenshots"),
        ("衣服", ["服装", "穿搭", "鞋子"], "01_Personal"),
        ("玩具", ["积木", "玩偶"], "01_Personal"),
        ("书籍", ["课本", "杂志", "报纸"], "01_Personal"),
        ("乐器", ["吉他", "钢琴"], "01_Personal"),
        ("花卉", ["花", "玫瑰", "盆栽"], "01_Personal"),
    ]

    # ── activity（活动标签）──
    activities = [
        ("旅行", ["旅游", "出游", "度假"], "01_Personal"),
        ("会议", ["开会", "例会", "研讨"], "02_Work"),
        ("培训", ["学习", "讲座", "授课"], "02_Work"),
        ("聚餐", ["吃饭", "宴席", "团餐"], "01_Personal"),
        ("运动", ["跑步", "健身", "打球", "游泳"], "01_Personal"),
        ("购物", ["逛街", "买菜", "网购"], "01_Personal"),
        ("自拍", ["拍照", "合影"], "01_Personal"),
        ("演讲", ["汇报", "报告", "发言"], "02_Work"),
        ("签到", ["打卡", "报名", "登记"], "02_Work"),
        ("团建", ["集体活动", "拓展"], "02_Work"),
        ("钓鱼", ["垂钓", "捕鱼"], "01_Personal"),
        ("爬山", ["登山", "徒步"], "01_Personal"),
        ("烧烤", ["BBQ", "烤肉"], "01_Personal"),
        ("装修", ["翻新", "施工"], "01_Personal"),
        ("搬砖", ["搬砖", "体力活"], "02_Work"),
    ]

    # ── attribute（属性标签）──
    attributes = [
        ("横屏", ["横屏", "横向"], None),
        ("竖屏", ["竖屏", "纵向"], None),
        ("白天", ["日间", "晴天"], None),
        ("夜晚", ["夜间", "晚上", "暗光"], None),
        ("室内", ["屋内", "室内"], None),
        ("户外", ["室外", "户外"], None),
        ("近景", ["特写", "近距离"], None),
        ("远景", ["全景", "远景", "广角"], None),
        ("模糊", ["不清晰", "抖动"], None),
        ("修图", ["滤镜", "后期", "美颜"], None),
        ("黑白", ["黑白照片", "灰度"], None),
        ("拼图", ["多图拼接", "长图"], None),
        ("水印", ["带水印", "水印"], None),
        ("表情包", ["meme", "搞笑图"], "04_Downloads"),
        ("壁纸", ["壁纸", "背景图", "锁屏"], "04_Downloads"),
    ]

    # ── event（事件标签）──
    events = [
        ("国庆旅行", ["国庆出游", "十一假期"], "01_Personal"),
        ("春节团圆", ["过年回家", "除夕"], "01_Personal"),
        ("公司年会", ["年会", "公司聚餐"], "02_Work"),
        ("项目验收", ["验收", "检查"], "02_Work"),
        ("禁毒宣传", ["禁毒活动", "宣传日"], "02_Work"),
        ("毕业旅行", ["毕业出游"], "01_Personal"),
    ]

    all_tags = []
    for tag_type, tags in [
        ("scene", scenes), ("people", people), ("object", objects),
        ("activity", activities), ("attribute", attributes), ("event", events),
    ]:
        for tag_value, synonyms, mapping in tags:
            all_tags.append((tag_type, tag_value, json.dumps(synonyms), mapping, 1))

    cur.execute("DELETE FROM vocabulary")
    cur.executemany(
        "INSERT OR REPLACE INTO vocabulary (tag_type, tag_value, synonyms, mapping, enabled) VALUES (?,?,?,?,?)",
        all_tags
    )
    conn.commit()
    print(f"词表已填充: {len(all_tags)} 个标签")


if __name__ == "__main__":
    init()
    conn = sqlite3.connect(DB_PATH)
    seed_vocabulary(conn)
    conn.close()
