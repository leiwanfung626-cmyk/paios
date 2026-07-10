#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地审查报告服务 — 根目录 E:\，处理中文路径，支持缩略图按需生成+缓存。

关键能力:
- /thumb/ 路由：按需生成 400px 缩略图并缓存到 outputs/thumbs/
- HEIC 支持：通过 pillow-heif 解码 iPhone 实拍 HEIC（扩展名常误标 .JPG）
- 兜底流式：缩略图生成失败时直接流式返回原图（浏览器可渲染的格式仍能预览）
- 中文/空格路径：urllib.unquote 解码
"""
import http.server
import socketserver
import os
import urllib.parse
import io

# 注册 HEIF/HEIC 解码器（必须在 PIL.Image 导入前/后均可，但需在打开前注册）
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except Exception as e:
    print(f"[warn] pillow-heif 不可用，HEIC 缩略图将失败: {e}")

from PIL import Image

ROOT = "E:\\"
PORT = 8080
THUMB_DIR = os.path.join(ROOT, "PAIOS", "10_WORK", "photos_organizer", "outputs", "thumbs")
THUMB_W = 400
os.makedirs(THUMB_DIR, exist_ok=True)

# 浏览器可直接渲染的源格式 -> content-type（兜底流式用）
DIRECT_CT = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".gif": "image/gif", ".webp": "image/webp", ".bmp": "image/bmp",
}


def make_thumb(src_path):
    """生成缩略图，返回磁盘缓存路径。失败返回 None。"""
    import hashlib
    key = hashlib.md5(src_path.encode("utf-8")).hexdigest()
    cache_path = os.path.join(THUMB_DIR, key + ".jpg")
    if os.path.exists(cache_path):
        return cache_path
    try:
        with Image.open(src_path) as img:
            try:
                from PIL import ImageOps
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass
            w, h = img.size
            if w > THUMB_W:
                nh = int(h * THUMB_W / w)
                img = img.resize((THUMB_W, nh), Image.LANCZOS)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(cache_path, "JPEG", quality=82)
        return cache_path
    except Exception as e:
        print(f"缩略图失败 {src_path}: {e}")
        return None


def _send_file(self, path, content_type):
    try:
        with open(path, "rb") as f:
            data = f.read()
    except Exception as e:
        self.send_response(404)
        self.end_headers()
        return
    self.send_response(200)
    self.send_header("Content-Type", content_type)
    self.send_header("Content-Length", str(len(data)))
    self.send_header("Cache-Control", "max-age=86400")
    self.end_headers()
    self.wfile.write(data)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def translate_path(self, path):
        path = urllib.parse.unquote(path, encoding="utf-8")
        path = path.split("?", 1)[0].split("#", 1)[0]
        path = os.path.normpath(path)
        if path.startswith(("\\\\", "/")):
            path = path.lstrip("\\\\/")
        return os.path.join(ROOT, path)

    def do_GET(self):
        if self.path.startswith("/thumb/"):
            self._serve_thumb()
            return
        super().do_GET()

    def _serve_thumb(self):
        rel = self.path[len("/thumb/"):]
        phys = self.translate_path("/" + rel)
        cache = make_thumb(phys)
        if cache and os.path.exists(cache):
            _send_file(self, cache, "image/jpeg")
            return
        # 兜底：直接流式返回原图（浏览器可渲染的格式仍能预览）
        if os.path.exists(phys):
            ext = os.path.splitext(phys)[1].lower()
            ct = DIRECT_CT.get(ext, "application/octet-stream")
            _send_file(self, phys, ct)
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, fmt, *args):
        pass


def main():
    os.chdir(ROOT)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"审查报告服务已启动: http://localhost:{PORT}")
        print(f"缩略图路由: /thumb/ 前缀，按需生成缓存到 outputs/thumbs/")
        print("按 Ctrl+C 停止")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务已停止")


if __name__ == "__main__":
    main()
