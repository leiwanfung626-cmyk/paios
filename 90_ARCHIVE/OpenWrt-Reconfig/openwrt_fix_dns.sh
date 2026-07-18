#!/bin/sh
# OpenWrt 搬移后修复:清旧网段死地址 + WAN DNS 改公共 DNS
# 用法:粘贴到 OpenWrt SSH 终端执行;或 scp 到路由后 `sh openwrt_fix_dns.sh`
# 适用:光猫→主路由→二楼OpenWrt(WAN入,LAN+WiFi出),搬楼层后代理/去广告失效
set -u

OLD_NET="192.168.1"   # 旧网段前缀,若不同请改这一行

echo "=== [1/5] 扫描旧网段残留(揪出写死的死地址) ==="
grep -rn "$OLD_NET\." /etc/ 2>/dev/null || echo "  (无残留)"

echo "=== [2/5] 修复 WAN DNS (peerdns=0 + 公共 DNS) ==="
uci set network.wan.peerdns='0'
uci del network.wan.dns
uci add_list network.wan.dns='223.5.5.5'
uci add_list network.wan.dns='119.29.29.29'
uci commit network
echo "  done: peerdns=0, dns=223.5.5.5 / 119.29.29.29"

echo "=== [3/5] 重启网络(可能短暂断 SSH,重连即可) ==="
service network restart
sleep 3

echo "=== [4/5] 验证出口与解析 ==="
echo "--- resolv.conf ---"; cat /etc/resolv.conf
echo "--- ping 223.5.5.5 ---"; ping -c3 223.5.5.5
echo "--- nslookup ---"; nslookup www.baidu.com

echo "=== [5/5] 复扫确认旧地址已清 ==="
grep -rn "$OLD_NET\." /etc/ 2>/dev/null || echo "  OK: 已无 $OLD_NET.x 残留"

echo "=== DONE ==="
echo "判定:nslookup 返回 IP 且 resolv.conf 无 192.168.1.x => WAN 已恢复"
echo "仍需手动:AdGuard/Clash 上游 DNS 删 192.168.1.x、改公共 DNS、监听绑 0.0.0.0/LAN"
