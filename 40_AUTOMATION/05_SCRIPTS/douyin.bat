@echo off
REM douyin.bat — 抖音视频下载+转写一键脚本
REM 用法: douyin <抖音链接>
REM 示例: douyin https://v.douyin.com/xxx/

if defined PAIOS_DRIVE (
    set PAIOS_PATH=%PAIOS_DRIVE%:\PAIOS
) else (
    set PAIOS_PATH=F:\PAIOS
)

python "%PAIOS_PATH%\40_AUTOMATION\09_LEGACY\original\douyin_full_pipeline.py" --url %1
