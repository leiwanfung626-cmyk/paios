# OpenWrt 放二楼 · LAN-LAN 旁路由部署 SOP（最终版）

> 来源 packet：`OPENWRT-FINAL-DEPLOYMENT-ORDER-2026-0714`
> 修订 v2：Buddy @ 2026-07-14，基于 **实际执行经验** 修正 IP 段、补充 reboot 必要条件、修正 sniffing 策略。
> 实测环境：主路由 `192.168.0.1`，OpenWrt 最终 `192.168.0.250`。

---

## 0. 修订摘要（v1→v2）

| # | 问题 | 修订 |
|---|------|------|
| 1 | 原 packet 用 `192.168.1.x` 为例，实际主路由是 `192.168.0.1` | 统一改用 `192.168.0.x`，OpenWrt=`192.168.0.250` |
| 2 | 配置推送后代理全 000 | 拓扑变更后必须 **整机 reboot** 一次（restart nikki 不足，nft 内核状态残留） |
| 3 | TUN 模式在 LAN-LAN 手动代理下有害 | 建议关闭 tun.enable，避免 OpenWrt 自身出站被 TUN 劫持环 |
| 4 | 主路由 DNS 返回 fake-ip | 客户端 DNS 策略简化：代理=OpenWrt，DNS=主路由自动（mihomo SNI 嗅探） |

架构本身（LAN-LAN 旁路由、不动 WAN、不做二级路由）**正确**，且从结构上消灭了之前 `Redirect-DNS` 劫持上游导致的污染 bug。

---

## 1. 最终拓扑

```
光猫
  └─ 主路由 (LAN 192.168.0.1/24, DHCP 由它发)
        ├─ 一楼 PC  (LAN 直连, WiFi 关, 代理=192.168.0.250:7890)
        ├─ 二楼设备 (LAN 直连主路由 或 OpenWrt LAN, 代理=192.168.0.250:7890)
        └─ OpenWrt (二楼, LAN 口接主路由 LAN, IP=192.168.0.250/24, WAN 不用, DHCP 关)
```

流量路径：
```
PC → 主路由交换 → OpenWrt:7890 代理 → 节点 → Internet
```

---

## 2. 部署顺序（已验证）

### step_1 · 二楼物理部署（手动）
- OpenWrt **LAN 口** 接主路由 **LAN 口**。**不接 WAN 口**。
- **注意 WAN/LAN 端口不要插错**：WAN 口通常独立颜色，LAN 口是分组。插错会导致 ARP INCOMPLETE → OpenWrt 找不到网关。

### step_2 · OpenWrt 网络配置
```shell
# 备份
cp /etc/config/network /etc/config/network.bak.$(date +%s)
cp /etc/config/dhcp /etc/config/dhcp.bak.$(date +%s)

# LAN 改为主路由同网段
uci set network.lan.proto='static'
uci set network.lan.ipaddr='192.168.0.250'
uci set network.lan.netmask='255.255.255.0'
uci set network.lan.gateway='192.168.0.1'
uci set network.lan.dns='192.168.0.1'
uci delete network.lan.ip6assign 2>/dev/null || true

# 关 WAN（不做二级路由）
uci set network.wan.disabled='1'
uci set network.wan.proto='none'

# 关 DHCP（避免与主路由冲突）
uci set dhcp.lan.ignore='1'

uci commit network
uci commit dhcp

/etc/init.d/network restart
/etc/init.d/dnsmasq restart
```

### step_3 · 代理服务（Nikki/mihomo）
- **关 TUN**（LAN-LAN 手动代理模式不需要）：
  ```shell
  uci set nikki.@nikki[0].tun_enable='0'
  uci commit nikki
  ```
- 或直接用 sed 改 config.yaml：`sed -i 's/enable: true/enable: false/' /etc/nikki/run/config.yaml`
- **验证**：`allow-lan:true`（✅）、`mixed-port:7890`（✅）、`tun.enable:false`（✅）
- **sniffing**：可选（§3），不启用也能工作（实测通过）

### ⚠ step_3b · 必须整机重启（核心修复）
**网络拓扑变更（WAN→LAN-LAN + IP 变更 + TUN 开关）后，必须 reboot 整台 OpenWrt。** 仅 restart nikki/network 不足以清除残留 nft 内核状态和 cgroup 绑定，会导致所有代理节点不可用（failover 日志记录"所有节点均不可用"）。

```shell
reboot
# 等待约 60s 后重连
```

### step_4 · 二楼设备测试
- 连接：主路由 LAN 或 OpenWrt LAN
- 代理：`192.168.0.250:7890`
- 测试：youtube / google / x.com 通

### step_5 · 一楼 PC 测试
- 连主路由 LAN，**关 WiFi**
- **改回自动获取 IP**（如果之前设了静态 IP）
- 代理：`192.168.0.250:7890`（系统代理或浏览器代理）
- 测试同上

---

## 3. DNS 策略（简化版）

实测结果：**客户端 DNS 用主路由自动（192.168.0.1），代理=192.168.0.250:7890，即可正常工作。** 无需启用 sniffing。

原理：mihomo 接收客户端 `CONNECT youtube.com:443` 时通过 TLS SNI 提取域名，独立于客户端 DNS。所以客户端 DNS 是否污染不影响代理结果。

如果仍需启用 sniffing（强隔离场景）：
```yaml
sniffing:
  enable: true
  sniffing: [tls, http]
  skip-domain: ['+.lan', '+.local', '+.openwrt']
  force-domain: []
```

---

## 4. 常见坑

| 症状 | 根因 | 修复 |
|------|------|------|
| proxy 全部 000，failover 日志"所有节点均不可用" | 拓扑变更后未 reboot | `reboot` 整机重启 |
| SSH 可连但 ARP 网关 INCOMPLETE | 主路由线插在 WAN 口 | 拔到 LAN 口 |
| 客户端 169.254.x.x（无 DHCP） | 网线插在 OpenWrt（DHCP 关）上 | 插回主路由 |
| GitHub 通但 youtube/google 不通 | 同上周的 DNS 污染 | 检查 `firewall.dns_redirect.enabled=0` |
| 代理端口可达但 youtube 000 | TUN 未关，mihomo 自身出站被劫持 | 关 tun.enable → reboot |

---

## 5. 验证清单
- [ ] OpenWrt 自身：`curl -x 127.0.0.1:7890 https://www.youtube.com` → 200
- [ ] 客户端（代理 192.168.0.250:7890）：youtube/google/x.com → 200
- [ ] `nft list table inet nikki` 无指向多余外部 IP 的 Redirect-DNS 规则
- [ ] 主路由 DHCP 正常，OpenWrt DHCP 已关（`uci get dhcp.lan.ignore` → 1）
- [ ] 一楼 PC WiFi 关，仅 LAN，IP 从主路由 DHCP 获取（192.168.0.x）
