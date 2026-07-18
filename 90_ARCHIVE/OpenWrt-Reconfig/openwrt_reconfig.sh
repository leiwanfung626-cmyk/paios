#!/bin/sh
# ============================================================
# 二楼 OpenWrt 代理节点 — 一键修复脚本（root 执行）
# 用途：启用 WiFi + 校验路由模式 + 确认 LAN 网段
# 注意：设备名（radio0/radio1、eth0.2）按你机器调整，先跑「诊断」段
# ============================================================

echo "========== [诊断] 当前状态 =========="
echo "--- 无线禁用项（有 disabled=1 即关）---"
uci show wireless 2>/dev/null | grep -i disabled || echo "(无 disabled 项)"
echo "--- 网络接口 ---"
uci show network 2>/dev/null | grep -E "lan.ipaddr|wan.proto|wan.device" || true
echo "--- WAN 是否 up ---"
ifstatus wan 2>/dev/null | jsonfilter -e '@.up' 2>/dev/null || echo "wan 未配置/未连"

echo
echo "========== [1/3] 启用 WiFi 射频与 AP =========="
# 启用所有 wifi-device
for d in $(uci show wireless 2>/dev/null | sed -n 's/.*@\(wifi-device\[[0-9]\]\)\.disabled.*/\1/p' | sort -u); do
  uci set wireless.$d.disabled='0'
  echo "  enable $d"
done
# 启用所有 wifi-iface，强制挂 lan + ap 模式
for i in $(uci show wireless 2>/dev/null | sed -n 's/.*@\(wifi-iface\[[0-9]\]\)\.disabled.*/\1/p' | sort -u); do
  uci set wireless.$i.disabled='0'
  uci set wireless.$i.network='lan'
  uci set wireless.$i.mode='ap'
  echo "  enable $i (network=lan, mode=ap)"
done
# 若根本没 disabled 字段，则显式补 0
uci set wireless.@wifi-device[0].disabled='0' 2>/dev/null
uci set wireless.@wifi-iface[0].disabled='0' 2>/dev/null

uci commit wireless
wifi
echo "  无线已重载，等待 8s ..."
sleep 8
echo "  当前 ESSID："
iwinfo 2>/dev/null | grep -i ESSID || echo "  (iwinfo 不可用，请用 LuCI 看无线状态)"

echo
echo "========== [2/3] 校验/修正 LAN 网段（避免与主路由同网段） =========="
# 主路由假设 192.168.1.x；OpenWrt LAN 应为 192.168.2.1
CUR=$(uci get network.lan.ipaddr 2>/dev/null)
if [ "$CUR" = "192.168.1.1" ]; then
  echo "  检测到 LAN=$CUR 与主路由同网段，改为 192.168.2.1"
  uci set network.lan.ipaddr='192.168.2.1'
  uci commit network
  /etc/init.d/network restart
  echo "  网络已重启"
else
  echo "  LAN=$CUR （如非 192.168.2.x 且需代理，请手动改为独立网段）"
fi

echo
echo "========== [3/3] 校验 WAN 出网 =========="
WAN_DEV=$(uci get network.wan.device 2>/dev/null)
echo "  wan.device=$WAN_DEV"
ifstatus wan 2>/dev/null | jsonfilter -e '@.up' 2>/dev/null && \
  echo "  WAN up，出网正常" || echo "  WAN 未 up：检查 uplink 是否插在 WAN 口（或 WAN VLAN）"

echo
echo "========== 完成 =========="
echo "下一步：手机搜 2F-Proxy 连上后，访问 ip111.cn 看出口 IP 是否走 Clash 节点。"
