#!/usr/bin/env bash
# ============================================================
# PAIOS 电脑身份一键配置脚本
# 用法：bash scripts/setup-computer.sh <代号>
#       代号：evan -> 新电脑（E盘）
#              feng -> 老电脑（F盘）
# ============================================================

set -e

show_usage() {
    echo "用法：bash setup-computer.sh <代号>"
    echo "      代号：evan  -> 新电脑（E盘）"
    echo "             feng -> 老电脑（F盘）"
    exit 1
}

# ---- 检查参数 ----
ID="$1"
if [ "$ID" != "evan" ] && [ "$ID" != "feng" ]; then
    show_usage
fi

# ---- 确定电脑信息 ----
if [ "$ID" = "evan" ]; then
    LABEL="新电脑"
    DRIVE="E"
else
    LABEL="老电脑"
    DRIVE="F"
fi

echo ""
echo "========================================"
echo "  配置：$LABEL . 代号 $ID"
echo "  PAIOS 位置：${DRIVE}:/PAIOS"
echo "========================================"
echo ""

# ---- 1. 创建身份标识文件 ----
echo "[1/4] 创建 ~/.computer-identity ..."
echo "$ID" > "$HOME/.computer-identity"
echo "      -> 内容: $(cat $HOME/.computer-identity)"
echo ""

# ---- 2. 配置 Git hooks 路径 ----
echo "[2/4] 配置仓库使用 .githooks/ ..."
cd "$(dirname "$0")/.."
git config core.hooksPath .githooks
echo "      -> core.hooksPath = $(git config core.hooksPath)"
echo ""

# ---- 3. 配置 .bashrc（身份提示 + 盘符变量） ----
echo "[3/4] 配置 ~/.bashrc 终端提示 + 盘符变量 ..."

BASHRC_MARKER="# PAIOS-IDENTITY"

if grep -q "$BASHRC_MARKER" "$HOME/.bashrc" 2>/dev/null; then
    echo "      -> .bashrc 已有身份配置，跳过"
else
    cat >> "$HOME/.bashrc" << 'BASHRC_EOF'

# ============================================
# PAIOS-IDENTITY 电脑身份提示（由 setup 脚本添加）
# ============================================
if [ -f "$HOME/.computer-identity" ]; then
    COMPUTER_ID=$(cat "$HOME/.computer-identity")
    COMPUTER_NAME=""
    COMPUTER_LABEL=""
    case "$COMPUTER_ID" in
        evan) COMPUTER_NAME="新电脑"; COMPUTER_LABEL="evan" ;;
        feng) COMPUTER_NAME="老电脑"; COMPUTER_LABEL="feng" ;;
    esac
fi

if [ -n "$COMPUTER_NAME" ]; then
    echo ""
    echo "========================================="
    echo "  当前：$COMPUTER_NAME  .  代号 $COMPUTER_LABEL"
    echo "========================================="
    echo ""
fi

__paios_identity_prompt() {
    if [ -n "$COMPUTER_LABEL" ]; then
        case "$PWD" in
            */paios*|*/PAIOS*)
                echo -n "【$COMPUTER_NAME . $COMPUTER_LABEL】"
                ;;
        esac
    fi
}

if [ -n "$PROMPT_COMMAND" ]; then
    PROMPT_COMMAND='PS1="$(__paios_identity_prompt)$PS1"; '"$PROMPT_COMMAND"
else
    PROMPT_COMMAND='PS1="$(__paios_identity_prompt)$PS1"'
fi

# 盘符变量（evan=E, feng=F）
export PAIOS_DRIVE="$DRIVE"
BASHRC_EOF
    echo "      -> 已追加到 ~/.bashrc"
    echo "      -> export PAIOS_DRIVE=$DRIVE"
fi

# ---- 4. 设置当前会话环境变量 ----
export PAIOS_DRIVE="$DRIVE"
echo "      -> 当前会话 PAIOS_DRIVE=$DRIVE (已生效)"

echo ""
echo "========================================"
echo "  OK! 配置完成"
echo "  盘符变量 PAIOS_DRIVE=$DRIVE"
echo "  请重启 Git Bash 或执行："
echo "     source ~/.bashrc"
echo "========================================"
