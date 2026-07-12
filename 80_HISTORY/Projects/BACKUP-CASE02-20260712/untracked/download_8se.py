#!/usr/bin/env python3
"""下载8se.me套图 - 李丽珍《Reminicsence》 (102P)"""

import requests
import os
import time
import sys

SAVE_DIR = r"E:\PAIOS\李丽珍_Reminicsence"
BASE_URL = "https://img.xchina.io/photos2/668da3eb393c5/{:04d}.jpg"
TOTAL = 102

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://8se.me/",
}

os.makedirs(SAVE_DIR, exist_ok=True)

success = 0
failed = 0

for i in range(1, TOTAL + 1):
    url = BASE_URL.format(i)
    filename = f"{i:04d}.jpg"
    filepath = os.path.join(SAVE_DIR, filename)

    if os.path.exists(filepath) and os.path.getsize(filepath) > 1024:
        print(f"[SKIP] {filename} 已存在")
        success += 1
        continue

    for attempt in range(3):
        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200 and len(r.content) > 1024:
                with open(filepath, "wb") as f:
                    f.write(r.content)
                size_kb = len(r.content) / 1024
                print(f"[OK] {filename} ({size_kb:.1f} KB)")
                success += 1
                break
            elif r.status_code == 404:
                # Try alternative extension
                url_alt = url.replace(".jpg", ".webp")
                r2 = requests.get(url_alt, headers=headers, timeout=30)
                if r2.status_code == 200 and len(r2.content) > 1024:
                    filepath_alt = os.path.join(SAVE_DIR, f"{i:04d}.webp")
                    with open(filepath_alt, "wb") as f:
                        f.write(r2.content)
                    size_kb = len(r2.content) / 1024
                    print(f"[OK] {i:04d}.webp ({size_kb:.1f} KB)")
                    success += 1
                    break
                else:
                    print(f"[404] {filename} 不存在")
                    failed += 1
                    break
            else:
                print(f"[RETRY {attempt+1}] {filename} HTTP {r.status_code}")
        except Exception as e:
            print(f"[RETRY {attempt+1}] {filename} 错误: {e}")
        time.sleep(1)
    else:
        print(f"[FAIL] {filename} 下载失败")
        failed += 1

    # Small delay between requests
    time.sleep(0.5)

print(f"\n=== 下载完成: 成功 {success}, 失败 {failed} ===")
