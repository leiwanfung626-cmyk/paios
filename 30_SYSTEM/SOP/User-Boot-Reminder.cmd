@echo off
REM ============================================================
REM PAIOS User Boot Reminder (Case-02 / Case-03)
REM 作用: 每次开机自动打开 "角色模型速览图"，强化铁律记忆
REM 用法: 将此 .cmd 的快捷方式放进 Windows 启动文件夹:
REM   %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
REM 说明: 本文件随 Core 仓库 git pull 到达用户机器，只读运行即可
REM       打开的是同目录下的 User-Role-Model-Speed-View.html
REM ============================================================
start "" "%~dp0User-Role-Model-Speed-View.html"
exit /b
