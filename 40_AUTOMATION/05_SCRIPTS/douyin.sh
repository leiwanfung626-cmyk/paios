#!/usr/bin/env bash
# douyin.sh — 抖音视频下载+转写一键脚本
# 用法: douyin <抖音链接>
# 示例: douyin https://v.douyin.com/xxx/

python "F:\PAIOS\40_AUTOMATION\09_LEGACY\original\douyin_full_pipeline.py" --url "$1"
