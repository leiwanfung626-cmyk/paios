# utils.py — 照片整理工具共享模块
# 提供：配置加载、DB连接、媒体类型识别、md5计算、文件扫描
import os
import sys
import hashlib
import sqlite3
import yaml
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

# 媒体类型 → 扩展名映射（来自 config.yaml media_types，硬编码兜底）
MEDIA_MAP = {
    "video": [".mp4", ".3gp", ".mov", ".avi", ".mkv", ".flv"],
    "livephoto": [".livp"],
    "raw": [".cr2", ".nef", ".arw", ".dng", ".raf"],
    "photo": [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"],
    "document": [".pdf", ".ppt", ".pptx", ".doc", ".docx"],
    "archive": [".rar", ".zip", ".7z"],
}


def load_config(path=CONFIG_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_local_env(env_path=None):
    """从项目根目录 .env 加载密钥到 os.environ（零依赖，不覆盖已有 env）。

    用途：后台 / 非交互 shell 不会继承交互 shell 里 export 的 ZHIPU_API_KEY，
    导致 GLM 补判被静默跳过。把密钥写进 .env 后，所有运行（含后台）都能读到。

    - 仅补充 os.environ 中【不存在】的键，绝不覆盖已设置的环境变量。
    - 忽略空行 / 注释(#) / 无等号的行；自动去除值两端的引号。
    - .env 不应提交到任何版本库（含密钥）。
    """
    if env_path is None:
        env_path = os.path.join(BASE_DIR, ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val


def get_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def classify_media_type(ext):
    ext = ext.lower()
    for t, exts in MEDIA_MAP.items():
        if ext in exts:
            return t
    return "other"


def compute_md5(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def scan_files(root):
    """递归扫描目录下所有文件，返回 Path 生成器"""
    root = Path(root)
    for p in root.rglob("*"):
        if p.is_file():
            yield p


def hamming_similarity(hash1, hash2):
    """返回相似度百分比（0-100），基于汉明距离"""
    if hash1 is None or hash2 is None:
        return 0
    dist = bin(int(hash1, 16) ^ int(hash2, 16)).count("1")
    max_bits = max(len(hash1), len(hash2)) * 4  # hex → bit
    if max_bits == 0:
        return 0
    return round((1 - dist / max_bits) * 100, 1)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
