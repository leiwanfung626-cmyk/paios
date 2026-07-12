<#
.SYNOPSIS
  PAIOS Case-02 每日 Manifest 发布脚本
.DESCRIPTION
  生成 Case-02 Manifest → 发布到 Fleet（带日期戳 + 最新版）
  由 Windows Task Scheduler 每日触发
.NOTES
  手动推送: cd /d E:\PAIOS && git add Fleet/cases/ && git commit -m "fleet: daily manifest $(Get-Date -Format yyyyMMdd)" && git push
#>

$ErrorActionPreference = "Stop"

$PAIOS_ROOT = "E:\PAIOS"
$FLEET_DIR  = "$PAIOS_ROOT\Fleet\cases"
$SCRIPT     = "$PAIOS_ROOT\40_AUTOMATION\05_SCRIPTS\collect_manifest.py"
$TODAY      = Get-Date -Format "yyyyMMdd"
$LOG_FILE   = "$PAIOS_ROOT\Fleet\logs\fleet-push-$TODAY.log"

# 创建日志目录
$null = New-Item -ItemType Directory -Path "$PAIOS_ROOT\Fleet\logs" -Force

function Write-Log {
    param([string]$Msg)
    $line = "[$(Get-Date -Format 'HH:mm:ss')] $Msg"
    Write-Host $line
    Add-Content -Path $LOG_FILE -Value $line
}

Write-Log "===== PAIOS Case-02 Daily Fleet Push ====="
Write-Log "日期: $TODAY"

# Step 1: 生成 Manifest
Write-Log "[1/3] 运行 collect_manifest.py..."
try {
    $output = & python $SCRIPT 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Log "[ERROR] collect_manifest.py 失败，退出码: $LASTEXITCODE"
        Write-Log $output
        exit $LASTEXITCODE
    }
    Write-Log "[OK] Manifest 已生成"
} catch {
    Write-Log "[ERROR] 异常: $_"
    exit 1
}

# Step 2: 发布到 Fleet
Write-Log "[2/3] 发布到 Fleet..."

# 确保 Fleet 目录存在
$null = New-Item -ItemType Directory -Path $FLEET_DIR -Force

# 带日期戳的历史副本
$datedFile = "$FLEET_DIR\case-02-$TODAY.yaml"
try {
    Copy-Item "$PAIOS_ROOT\30_SYSTEM\PAIOS-Usage\manifest.yaml" -Destination $datedFile -Force
    Write-Log "[OK] 历史副本: case-02-$TODAY.yaml"
} catch {
    Write-Log "[WARN] 历史副本写入失败: $_"
}

# 最新版（始终覆盖）
$latestFile = "$FLEET_DIR\case-02.yaml"
try {
    Copy-Item "$PAIOS_ROOT\30_SYSTEM\PAIOS-Usage\manifest.yaml" -Destination $latestFile -Force
    Write-Log "[OK] 最新版: case-02.yaml"
} catch {
    Write-Log "[WARN] 最新版写入失败: $_"
}

# Step 3: 输出摘要
Write-Log "[3/3] 完成"
Write-Log "Fleet 目录: $FLEET_DIR"
Get-ChildItem "$FLEET_DIR\case-02*.yaml" | ForEach-Object {
    Write-Log "  $($_.Name) ($( '{0:N0}' -f $_.Length ) bytes)"
}

Write-Log "===== 完成 ====="
Write-Log ""
Write-Log "如需推送到远端，请手动执行:"
Write-Log "  cd /d $PAIOS_ROOT"
Write-Log "  git add Fleet/cases/"
Write-Log "  git commit -m `"fleet: daily manifest $TODAY`""
Write-Log "  git push"
