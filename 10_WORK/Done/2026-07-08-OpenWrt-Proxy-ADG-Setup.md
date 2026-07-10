# OpenWrt 代理 + 去广告 DNS 配置完成

> **日期**：2026-07-08
> **设备**：PC (192.168.1.100) → OpenWrt (192.168.1.1)
> **状态**：✅ 已完成

## 网络拓扑

```
主路由 (192.168.110.0/24)
  └── OpenWrt WAN: 192.168.110.96/24 (DHCP)
       └── OpenWrt LAN: 192.168.1.1/24 (br-lan: lan1~3 + phy0-ap0 + phy1-ap0)
            ├── PC 有线: 192.168.1.100
            └── WiFi: Evan-2.4G / Evan-5G
```

## 完成工作

### 1. 网络路由
- PC 有线连接 OpenWrt LAN，静态 IP 192.168.1.100
- 默认网关 192.168.1.1 (OpenWrt)
- DNS: 114.114.114.114 / 114.114.115.115
- 无线已关闭，路由表无冲突

### 2. SSH 免密登录
- 公钥 `id_ed25519` → `/etc/dropbear/authorized_keys`
- 可直接 `ssh root@192.168.1.1` 无需密码

### 3. mihomo/nikki 代理 (v1.26.1)
| 项目 | 值 |
|------|-----|
| 核心 | Mihomo Meta alpha-1686d56 |
| 管理器 | nikki 2026.04.08 |
| 节点数 | 36（港/新/美/日/台/韩/马/加/泰/澳/德/英/印/土/阿/菲/越/印尼） |
| 运行模式 | Rule（规则分流） |
| 混合端口 | 7890（认证: nikki:223862） |
| TUN 模式 | mixed，设备名 nikki |
| 开机自启 | ✅ |

分流规则：
- 国内域名/IP → DIRECT（直连）
- 国外域名 → Proxy（走代理）
- OpenAI / Netflix 可单独指定节点

### 4. AdGuard Home (v0.107.57)
| 项目 | 值 |
|------|-----|
| Web 管理 | http://192.168.1.1:3000 |
| 登录 | admin / Lyf201314lyf |
| DNS 端口 | 5353 |
| 上游 DNS | 127.0.0.1:1053 (mihomo) |
| 广告过滤 | AdGuard DNS filter + anti-ad |
| 开机自启 | ✅ |

### 5. DNS 链
```
用户设备 → dnsmasq(:53) → AdGuard Home(:5353) → mihomo(:1053)
                              ↓                      ↓
                          去广告过滤              分流决策
                          (ad filter)        (国内直连/国外代理)
```

## 访问入口

| 服务 | 地址 | 账号 |
|------|------|------|
| OpenWrt LuCI | http://192.168.1.1 | root / SSH key |
| AdGuard Home | http://192.168.1.1:3000 | admin / Lyf201314lyf |
| nikki 代理 | LuCI → 服务 → nikki | — |
| mihomo API | :9090 | secret: 223862 |

## 备注
- Windows 防火墙屏蔽了 ICMP (ping)，但 HTTP/DNS/SSH 正常
- AdGuard Home 首次安装时 API 路径为 `/control/install/configure`（非 `installation`）
- 配置通过直接写入 YAML + bcrypt 密码哈希完成，绕过了 Web 向导的 CORS/TUN 拦截问题
