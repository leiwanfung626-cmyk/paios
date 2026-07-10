# 二楼 OpenWrt 代理路由 — 配置记录

> 拓扑：光猫 → 主路由(TP-Link 7DR6430, 192.168.0.1) LAN → OpenWrt WAN → OpenWrt LAN(192.168.1.1) + WiFi
> 一楼设备直连主路由（不过代理），二楼设备接 OpenWrt（全走 Nikki/mihomo 代理 + AdGuard 广告过滤）

## 最终配置状态（2026-07-10 21:35）

### 网络配置
- **WAN**: DHCP, IP 192.168.0.100, 网关 192.168.0.1, DNS 223.5.5.5/119.29.29.29
- **LAN**: 192.168.1.1/24, DHCP server, br-lan 桥接 lan1/lan2/lan3
- **WiFi 2.4G**: SSID Evan-2.4G, channel 11, HE20, WPA2/3 sae-mixed
- **WiFi 5G**: SSID Evan-5G, channel 149, HE40, WPA2/3 sae-mixed
- **WiFi 密码**: Lyf201314lyf

### DNS 链路（关键）
```
Client → dnsmasq(:53) → AdGuard(:5353) → mihomo(:1053) → upstream(223.5.5.5等)
```
- **AdGuard**: 拦截广告域 → 0.0.0.0（StevenBlack 78,464 rules）
- **mihomo**: fake-ip 模式，正常域 → 198.18.x.x
- **Nikki DNS hijack**: 已禁用（ipv4=0, ipv6=0），让 DNS 走 dnsmasq → AdGuard → mihomo
- **Firewall DNS redirect**: LAN port 53 → DNAT 到 192.168.1.1:53（防止客户端绕过）

### 代理配置
- **Nikki (mihomo)**: 38 个 VMess 节点，当前选 🇭🇰 B1002 香港
- **代理模式**: TCP redirect(tproxy :7891) + UDP tun(:7892)
- **机场**: rabbitpro，订阅 URL 8.148.211.250:21312
- **mihomo API**: http://192.168.1.1:9090, secret=223862
- **AdGuard Web**: http://192.168.1.1:3000

### 服务自启
- Nikki: S99（最后启动）
- AdGuard: S19（先于 Nikki）
- 两者均 `enable` 状态

## 关键配置文件
- `/etc/config/network` — WAN/LAN 接口
- `/etc/config/wireless` — WiFi 射频与 AP
- `/etc/config/firewall` — 防火墙 + DNS redirect 规则
- `/etc/config/dhcp` — dnsmasq (noresolv=1, server=127.0.0.1#5353)
- `/etc/adguardhome.yaml` — AdGuard 配置（schema 29, 不含 clients 字段）
- `/etc/nikki/run/config.yaml` — mihomo 运行时配置（Nikki 自动生成）
- `/etc/config/nikki` — Nikki UCI 配置

## 验证结果
| 测试项 | 结果 |
|--------|------|
| WiFi 广播 | ✅ Evan-2.4G + Evan-5G |
| WAN 联网 | ✅ 192.168.0.100, ping 8.8.8.8 OK |
| DNS 解析 | ✅ dnsmasq → AdGuard → mihomo |
| AdGuard 拦截 | ✅ ads.google.com → 0.0.0.0 |
| 代理(百度) | ✅ HTTPS 200 in 0.125s |
| 代理(Google) | ✅ HTTPS 200 in 5.671s |
| 代理(YouTube) | ✅ HTTPS 200 in 0.762s |
| 代理(GitHub) | ✅ HTTPS 200 in 0.657s |
| tproxy | ✅ LAN TCP → :7891 |
| 开机自启 | ✅ Nikki + AdGuard |

## 踩坑记录
1. **AdGuard schema 29 不兼容 `clients: []`**：必须省略 clients 字段，否则 YAML 解析失败
2. **Nikki DNS hijack 绕过 AdGuard**：hijack 将 port 53 直接重定向到 mihomo:1053，跳过 dnsmasq 和 AdGuard。解决方案：禁用 hijack，用 firewall DNAT 规则替代
3. **pyyaml 未安装**：OpenWrt 上无法用 Python 修改 YAML，需手动写配置文件
4. **BusyBox nc 不可靠**：端口测试用 nc 结果不准确，mihomo API health check 更可靠
5. **mihomo API 需要认证**：`Authorization: Bearer 223862` header
