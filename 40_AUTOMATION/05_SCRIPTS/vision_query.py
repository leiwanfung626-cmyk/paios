#!/usr/bin/env python3
r"""
GLM 视觉版外部调用脚本 — reasonix 带图任务的兜底出口

为什么需要它：
    reasonix 是内置 CLI，调用纯文本模型(deepseek)或某些网关时，会把多模态
    content(image_url) 原样发出，被网关以
    `messages.content.type 参数非法，取值范围 ['text']` 拒绝(HTTP 400)。
    且 reasonix 不可改 → 带图任务只能在 reasonix 外用本脚本处理。

用法：
    # 远程图片 URL
    python vision_query.py --image https://example.com/x.jpg --prompt "描述这张图"
    # 本地图片（自动转 base64）
    python vision_query.py --image ./photo.png --prompt "图里有什么文字"
    # 指定模型 / 端点（默认读环境变量）
    python vision_query.py --image <url> --prompt "..." --model glm5.2 --base-url https://.../v1

环境变量：
    GLM_API_KEY       必填，视觉端点 API Key
    GLM_BASE_URL      选填，OpenAI 兼容 base_url（默认智谱开放平台）
    GLM_VISION_MODEL  选填，视觉模型名（默认 glm-4v-plus；你可用 --model glm5.2 覆盖）

依赖：
    pip install openai

退出码：0 成功 / 1 参数或文件错误 / 2 API 错误 / 3 依赖缺失
"""

import os
import sys
import argparse
import base64
import mimetypes
from pathlib import Path

# ---- 依赖检查（缺失时友好退出，而非抛栈）---------------------------
try:
    from openai import OpenAI
except ImportError:
    sys.stderr.write(
        "缺少依赖 openai，请先安装：\n"
        "    pip install openai\n"
    )
    sys.exit(3)


def build_image_part(image: str) -> dict:
    """返回 OpenAI 多模态 content 的 image_url 部分。

    远程 URL 直接引用；本地文件转 base64 data URI。
    """
    if image.startswith(("http://", "https://")):
        return {"type": "image_url", "image_url": {"url": image}}

    p = Path(image)
    if not p.exists():
        sys.stderr.write(f"[错误] 本地图片不存在: {image}\n")
        sys.exit(1)
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    data_uri = f"data:{mime};base64,{b64}"
    return {"type": "image_url", "image_url": {"url": data_uri}}


def main() -> None:
    ap = argparse.ArgumentParser(
        description="GLM 视觉版外部调用 — reasonix 带图任务兜底出口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--image", required=True,
                    help="图片地址：http(s) URL 或本地文件路径")
    ap.add_argument("--prompt", default="请描述这张图片的内容",
                    help="针对图片的提问（默认：请描述这张图片的内容）")
    ap.add_argument("--model",
                    default=os.environ.get("GLM_VISION_MODEL", "glm-4v-plus"),
                    help="视觉模型名（默认 GLM_VISION_MODEL 或 glm-4v-plus）")
    ap.add_argument("--base-url",
                    default=os.environ.get("GLM_BASE_URL",
                                           "https://open.bigmodel.cn/api/paas/v4"),
                    help="OpenAI 兼容 base_url（默认 GLM_BASE_URL 或智谱开放平台）")
    ap.add_argument("--api-key", default=os.environ.get("GLM_API_KEY"),
                    help="API Key（默认读 GLM_API_KEY 环境变量）")
    args = ap.parse_args()

    if not args.api_key:
        sys.stderr.write(
            "[错误] 未设置 API Key。\n"
            "请设置环境变量 GLM_API_KEY，或用 --api-key 传入。\n"
        )
        sys.exit(1)

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)
    content = [
        {"type": "text", "text": args.prompt},
        build_image_part(args.image),
    ]

    try:
        resp = client.chat.completions.create(
            model=args.model,
            messages=[{"role": "user", "content": content}],
        )
        print(resp.choices[0].message.content)
    except Exception as e:  # 捕获 openai 的 APIError / 网络错误等
        msg = str(e)
        if "content.type" in msg or "取值范围" in msg or "400" in msg:
            sys.stderr.write(
                "[错误] 该端点返回 400，拒绝多模态 content。\n"
                "可能原因：你接入的是纯文本网关/代理，而非视觉端点。\n"
                "请确认 GLM_BASE_URL 指向支持多模态的视觉端点，\n"
                "并用 --model 指定正确的视觉模型名（如 glm5.2）。\n"
                f"原始错误：{msg}\n"
            )
        else:
            sys.stderr.write(f"[错误] API 调用失败：{msg}\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
