#!/usr/bin/env python3
"""
Reasonix Adapter — read_trace
从 .reasonix/desktop-topic-*.json 读取痕迹记录，返回统一 TraceRecord 格式。
参见 ADR-0017 + adapter-schema.yaml
"""
import json, sys, os
from pathlib import Path
from datetime import datetime

REASONIX_DIR = Path(".reasonix")

def find_session(trace_id=None, date_str=None):
    """查找 Reasonix session JSON 文件"""
    if not REASONIX_DIR.exists():
        print("[]")
        return
    
    # 从话题元数据读取
    meta_file = REASONIX_DIR / "desktop-topic-auto-title-meta.json"
    titles_file = REASONIX_DIR / "desktop-topic-titles.json"
    
    records = []
    
    if meta_file.exists():
        with open(meta_file) as f:
            meta = json.load(f)
        for topic_id, info in meta.items():
            records.append({
                "trace_id": topic_id,
                "engine": "reasonix",
                "timestamp": datetime.fromtimestamp(info.get("updatedAt", 0)/1000).isoformat(),
                "trace_type": "session_checkpoint",
                "summary": f"Reasonix session: stage={info.get('stage')}, turns={info.get('userTurns')}",
                "uri": str(REASONIX_DIR / f"topics/{topic_id}") if (REASONIX_DIR / "topics").exists() else str(meta_file),
                "tags": ["reasonix", "session"]
            })
    
    print(json.dumps(records, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    find_session(*sys.argv[1:])
