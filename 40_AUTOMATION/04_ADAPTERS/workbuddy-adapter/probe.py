#!/usr/bin/env python3
"""
WorkBuddy Adapter — probe
运行时探测 WorkBuddy 引擎的可用能力。
"""
import json, os

def probe():
    capabilities = []
    
    if os.path.isdir(".workbuddy"):
        capabilities.append("memory_access")
        capabilities.append("trace_aware")
    
    if os.path.isdir(".workbuddy/memory"):
        capabilities.append("daily_log")
        capabilities.append("state_tracking")
    
    if os.path.isdir("40_AUTOMATION"):
        capabilities.append("automation")
        capabilities.append("orchestration")
    
    print(json.dumps({
        "engine": "workbuddy",
        "available": capabilities,
        "version": "1.0"
    }, indent=2))

if __name__ == "__main__":
    probe()
