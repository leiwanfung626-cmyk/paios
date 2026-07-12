@echo off
setlocal enabledelayedexpansion

set PAIOS_ROOT=E:\PAIOS
set FLEET_DIR=%PAIOS_ROOT%\Fleet\cases
set LOG_DIR=%PAIOS_ROOT%\Fleet\logs
set FLEET_EXCHANGE=E:\FleetExchange\Case-02

REM --- get date ---
for /f "tokens=1-3 delims=/-. " %%a in ('echo %date%') do (
    set YYYY=%%a
    set MM=%%b
    set DD=%%c
)
set TODAY=%YYYY%%MM%%DD%

REM --- create directories ---
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%FLEET_DIR%" mkdir "%FLEET_DIR%"
if not exist "%FLEET_EXCHANGE%" mkdir "%FLEET_EXCHANGE%"

set LOG_FILE=%LOG_DIR%\fleet-push-%TODAY%.log
echo [%TIME%] ===== PAIOS Case-02 Daily Fleet Push ===== > "%LOG_FILE%"
echo [%TIME%] Date: %TODAY% >> "%LOG_FILE%"

REM --- Step 1: generate manifest ---
echo [%TIME%] [1/3] Running collect_manifest.py... >> "%LOG_FILE%"
echo [1/3] Generating manifest...
cd /d "%PAIOS_ROOT%"
python 40_AUTOMATION\05_SCRIPTS\collect_manifest.py >> "%LOG_FILE%" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [%TIME%] [ERROR] collect_manifest.py failed >> "%LOG_FILE%"
    echo [ERROR] Failed with code: %ERRORLEVEL%
    type "%LOG_FILE%"
    pause
    exit /b %ERRORLEVEL%
)
echo [%TIME%] [OK] Manifest generated >> "%LOG_FILE%"
echo [OK] Manifest generated

REM --- Step 2: publish to FleetExchange ---
echo [%TIME%] [2/3] Publishing to FleetExchange... >> "%LOG_FILE%"
echo [2/3] Publishing to FleetExchange...
copy /Y "%PAIOS_ROOT%\PAIOS-Usage\manifest.yaml" "%FLEET_EXCHANGE%\manifest.yaml" > nul
if %ERRORLEVEL% equ 0 (
    echo [%TIME%] [OK] FleetExchange: manifest.yaml >> "%LOG_FILE%"
    echo [OK] FleetExchange: manifest.yaml
) else (
    echo [%TIME%] [WARN] FleetExchange write failed >> "%LOG_FILE%"
    echo [WARN] FleetExchange write failed
)

REM --- Step 3: local archive ---
echo [%TIME%] [3/3] Local archive... >> "%LOG_FILE%"
echo [3/3] Local archive...
copy /Y "%PAIOS_ROOT%\PAIOS-Usage\manifest.yaml" "%FLEET_DIR%\case-02-%TODAY%.yaml" > nul
if %ERRORLEVEL% equ 0 (
    echo [%TIME%] [OK] Archive: case-02-%TODAY%.yaml >> "%LOG_FILE%"
    echo [OK] Archive: case-02-%TODAY%.yaml
) else (
    echo [%TIME%] [WARN] Archive write failed >> "%LOG_FILE%"
    echo [WARN] Archive write failed
)
copy /Y "%PAIOS_ROOT%\PAIOS-Usage\manifest.yaml" "%FLEET_DIR%\case-02.yaml" > nul
if %ERRORLEVEL% equ 0 (
    echo [%TIME%] [OK] Latest: case-02.yaml >> "%LOG_FILE%"
    echo [OK] Latest: case-02.yaml
) else (
    echo [%TIME%] [WARN] Latest write failed >> "%LOG_FILE%"
    echo [WARN] Latest write failed
)

REM --- summary ---
echo [%TIME%] Done >> "%LOG_FILE%"
echo.
echo ============================================
echo FleetExchange (shared):
dir /B "E:\FleetExchange\Case-02\manifest.yaml" 2>nul
echo.
echo Local archive:
dir /B "%FLEET_DIR%\case-02*.yaml" 2>nul
echo ============================================
echo.
echo Sync FleetExchange via: Quark / Tailscale / LAN
echo Case-01 reads: E:\FleetExchange\Case-02\manifest.yaml
echo.

endlocal
