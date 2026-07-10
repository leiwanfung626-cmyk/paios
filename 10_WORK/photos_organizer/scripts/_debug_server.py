import os, urllib.parse

p = os.path.join("E:\\", "待整理照片", "手机相册", "iphone", "最近项目", "2024-06-14 49997.JPG")
print("文件存在:", os.path.exists(p))
print("大小:", os.path.getsize(p) if os.path.exists(p) else "N/A")

url_path = "/%E5%BE%85%E6%95%B4%E7%90%86%E7%85%A7%E7%89%87/%E6%89%8B%E6%9C%BA%E7%9B%B8%E5%86%8C/iphone/%E6%9C%80%E8%BF%91%E9%A1%B9%E7%9B%AE/2024-06-14%2049997.JPG"
decoded = urllib.parse.unquote(url_path, encoding="utf-8")
translated = os.path.normpath(decoded.lstrip("/"))
full = os.path.join("E:\\", translated)
print("解码:", decoded)
print("翻译:", translated)
print("完整:", full)
print("匹配:", full == p)

# 测试服务器实际返回
import urllib.request
try:
    req = urllib.request.urlopen("http://localhost:8080" + url_path)
    data = req.read()
    print("服务器返回状态:", req.status, "字节数:", len(data))
except Exception as e:
    print("服务器错误:", e)
