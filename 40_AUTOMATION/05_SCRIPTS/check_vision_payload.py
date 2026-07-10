#!/usr/bin/env python3
"""
Reasonix 多模态 400 诊断工具
检查 payload 中的 content 结构是否可能被 API 网关拒绝。

用法:
    python check_vision_payload.py "<paste the JSON payload here>"

原理:
    纯文本模型端点只接受 content 为字符串。
    如果 content 是数组且包含 image_url 类型 → 必报 400。
"""

import json
import sys


def check_payload(payload_str: str) -> int:
    try:
        data = json.loads(payload_str)
    except json.JSONDecodeError as e:
        print(f"[错误] JSON 解析失败: {e}")
        return 1

    messages = data.get("messages", [])
    if not messages:
        print("[信息] payload 中没有 messages 字段")
        return 0

    has_issues = False
    for i, msg in enumerate(messages):
        content = msg.get("content")
        role = msg.get("role", "?")
        if isinstance(content, list):
            types = [p.get("type") for p in content if isinstance(p, dict)]
            if "image_url" in types:
                print(f"[⚠️ 危险] messages[{i}] (role={role}): content 包含 image_url！")
                print(f"         纯文本模型端点将返回 400")
                has_issues = True
            else:
                print(f"[OK] messages[{i}] (role={role}): 数组内容类型 = {types}")
        elif isinstance(content, str):
            print(f"[OK] messages[{i}] (role={role}): content 是字符串 ✓")
        else:
            print(f"[?] messages[{i}] (role={role}): content 类型异常 = {type(content).__name__}")

    if has_issues:
        print()
        print("==> 建议：")
        print("    - 如果目标是纯文本模型 → 去掉 image_url")
        print("    - 如果目标是视觉模型 → 检查 toml 中 vision_models 是否包含该模型名")
        print("    - 兜底：走 F:\\PAIOS\\40_AUTOMATION\\05_SCRIPTS\\vision_query.py")
        return 2

    print()
    print("==> payload 检查通过，无多模态冲突。")
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    return check_payload(sys.argv[1])


if __name__ == "__main__":
    sys.exit(main())
