"""定时归档 WorkBuddy 产出到 H 盘统一目录。
设计为 Windows 任务计划程序调用，与 flag_timer.py 同一体系。
运行方式: python archive_workbuddy.py
"""
import os, shutil, glob, json
from datetime import datetime

WB_SRC = r"C:\Users\liyun\WorkBuddy"
ARCHIVE_DST = r"H:\workspace\Infrastructure\data\workbuddy_output"
LOG_FILE = r"H:\workspace\Infrastructure\data\workbuddy_output\_archive_log.jsonl"

os.makedirs(ARCHIVE_DST, exist_ok=True)

# 读取已归档记录
archived = set()
if os.path.isfile(LOG_FILE):
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    archived.add(entry.get("name"))
                except:
                    pass

# 扫描 WorkBuddy workspace 中的会话目录
new_count = 0
for item in os.listdir(WB_SRC):
    item_path = os.path.join(WB_SRC, item)
    if not os.path.isdir(item_path):
        continue
    if item in ("Claw",):
        continue
    if item.startswith("20") and len(item) >= 10:
        if item not in archived:
            dst_path = os.path.join(ARCHIVE_DST, item)
            if not os.path.exists(dst_path):
                shutil.copytree(item_path, dst_path)
            # 记录日志
            log_entry = {
                "name": item,
                "archived_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": os.path.join(WB_SRC, item),
                "destination": dst_path
            }
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            new_count += 1
            print(f"  archived: {item}")

if new_count == 0:
    print("  no new WorkBuddy outputs found")
else:
    print(f"  total new: {new_count}")
