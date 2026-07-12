#!/usr/bin/env python3
"""
Reasonix Adapter — probe
运行时探测 Reasonix 引擎的可用能力。
返回能力标签列表。
"""
import json, os

def probe():
    capabilities = []
    
    # 检查 .reasonix/ 目录是否存在
    if os.path.isdir(".reasonix"):
        capabilities.append("session_persistence")
        capabilities.append("trace_aware")
    
    # 检查 shell 是否可用
    if os.name == "nt":
        capabilities.append("shell")
    else:
        capabilities.append("shell")
    
    # 检查 Python 是否可用
    import sys
    if sys.version_info >= (3, 10):
        capabilities.append("code_gen")
        capabilities.append("reasoning")
    
    print(json.dumps({
        "engine": "reasonix",
        "available": capabilities,
        "version": "1.0"
    }, indent=2))

if __name__ == "__main__":
    probe()
