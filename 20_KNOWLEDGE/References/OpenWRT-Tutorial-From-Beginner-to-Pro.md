---
ref_id: "REF-0008"
schema_version: 2
title: "OpenWRT 从入门到精通 — 教程与玩法大全"
type: "reference"
lifecycle: "active"
created: "2026-07-06"
updated: "2026-07-08"
source: [openwrt-official, learnopenwrt, chinese-community]
tags: [openwrt, router, 360t7, mt7981, opkg, luci, network, proxy, adguardhome, usb]
keywords: [OpenWRT, 360 T7, MT7981, 刷机, opkg, LuCI, 广告过滤, 科学上网, 内网穿透, USB扩展, 策略路由]
summary: "OpenWRT 四阶段系统教程（入门→进阶→高级→精通），含 360 T7 专属信息与实用插件推荐清单，是本次路由器改造的底层参考。"
abstract: >
  综合 openwrt.org 官方文档、learnopenwrt.com 及中文社区整理的 OpenWRT 全栈教程。覆盖安装/LuCI/包管理/SSH 基础，
  多拨、访客隔离、DDNS、策略路由、定时任务等进阶配置，以及广告过滤、科学上网、内网穿透、流量监控、USB 扩展、
  Docker、自定义固件编译、UCI 配置、网络调试、备份恢复等高级玩法。末尾专设 360 T7 章节（MT7981 双核 A53、256MB RAM、
  128MB NAND、Breed 刷机）与实用插件速查表。文末指出 PAIOS 尚未有 SSH 连路由器自动装插件的脚本，为后续自动化预留。
---

# OpenWRT 从入门到精通 — 教程与玩法大全

> **来源**：openwrt.org 官方文档 + learnopenwrt.com + 中文社区
> **创建日期**：2026-07-06
> **状态**：✅ 已归档

---

## 目录

- [第一阶段：新手入门](#第一阶段新手入门)
- [第二阶段：进阶配置](#第二阶段进阶配置)
- [第三阶段：高级玩法](#第三阶段高级玩法)
- [第四阶段：精通与开发](#第四阶段精通与开发)
- [360 T7 路由器相关](#360-t7-路由器相关)
- [实用插件推荐](#实用插件推荐)
- [学习资源汇总](#学习资源汇总)

---

## 第一阶段：新手入门

### 1.1 OpenWRT 是什么

OpenWRT 是一个针对嵌入式设备的 Linux 操作系统，用于替代路由器原厂固件。它提供：
- **完整的可写文件系统** — 不像原厂固件只能升级不能定制
- **包管理机制** (`opkg`) — 像手机装 App 一样安装功能
- **持续安全更新** — 即使厂商停止支持，OpenWRT 仍在维护

> 当前稳定版：OpenWRT 24.10（安全维护中，预计 2026 年 9 月 EoL）
> 最新开发版：25.x 系列

### 1.2 安装 OpenWRT

**准备工作：**
1. 确认你的路由器型号在 [OpenWRT 支持列表](https://openwrt.org/supported_devices)中
2. 下载对应固件（`.bin` 或 `.img` 文件）
3. 校验文件哈希确保下载完整
4. 准备网线（刷机建议有线连接）

**刷机方式因设备而异，常见方法：**
- 在原厂 Web 管理界面上传固件升级
- 使用 `tftp` 刷入
- 使用 `breed`（不死鸟）引导加载器刷入（MTK/Qualcomm 设备常见）

**首次启动：**
- 默认 IP：`192.168.1.1`
- 默认用户名：`root`，无密码
- SSH 登录：`ssh root@192.168.1.1`

### 1.3 安装 LuCI Web 界面

如果固件没有自带 LuCI（Web 管理界面）：

```bash
opkg update
opkg install luci
/etc/init.d/uhttpd enable
/etc/init.d/uhttpd start
```

### 1.4 基础配置

**设置 Wi-Fi：**
- 进入 **Network → Wireless**
- 编辑无线网络，设置 SSID（Wi-Fi 名称）
- 设置加密方式（WPA2-PSK 或 WPA3）
- 设置密码
- 点击 **Save & Apply**

**设置上网（WAN）：**
- 进入 **Network → Interfaces**
- WAN 接口默认 DHCP（自动获取 IP，适合光猫拨号）
- 如需 PPPoE 拨号：
  - 编辑 WAN 接口
  - 协议选择 PPPoE
  - 输入宽带账号密码

**设置时区：**
- 进入 **System → System**
- Timezone 选择 `Asia/Shanghai`（中国）

### 1.5 包管理基础

```bash
# 更新软件包列表
opkg update

# 安装软件
opkg install 包名

# 移除软件
opkg remove 包名

# 列出已安装
opkg list-installed

# 搜索可用包
opkg find 关键词
```

### 1.6 SSH 管理

```bash
# 登录路由器
ssh root@192.168.1.1

# 查看系统信息
cat /proc/cpuinfo
free -m
df -h

# 查看网络状态
ifconfig
iwconfig
```

---

## 第二阶段：进阶配置

### 2.1 多拨（Load Balancing）

在单线多拨支持的地区，可叠加带宽：

```bash
opkg install mwan3 luci-app-mwan3
```

配置多 WAN 接口 → mwan3 负载均衡 → 带宽叠加

### 2.2 访客网络隔离

为访客创建独立网络，隔离内网访问：
1. **Firewall → 新建 Zone** — GuestZone（input reject, forward reject）
2. **Network → 新建接口** — guest（`192.168.10.1/24`）
3. **Wireless → 添加新 SSID** — 绑定到 guest 接口
4. **Traffic Rules** — 允许 DHCP/DNS（端口 53,67,68）

### 2.3 DDNS（动态域名）

```bash
opkg install luci-app-ddns
```

配置：填入域名、DDNS 服务商（如 noip、dnspod）、认证信息

### 2.4 静态路由 / 策略路由

**静态路由：**
- Network → Routes → 添加静态路由
- 用于多网段互通

**策略路由：**
- 指定某些 IP/域名走特定出口
- 常用插件：`mwan3`、`v2ray` 策略路由

### 2.5 定时任务（Cron）

```bash
# 编辑定时任务
crontab -e

# 示例：每天凌晨3点重启
0 3 * * * /sbin/reboot

# 示例：每小时清理缓存
0 * * * * echo 3 > /proc/sys/vm/drop_caches
```

---

## 第三阶段：高级玩法

### 3.1 广告过滤

**AdGuard Home：**
```bash
opkg install luci-app-adguardhome
```
- DNS 级广告过滤
- 可自定义过滤规则
- 提供统计面板

**Adbyby：**
```bash
opkg install luci-app-adbyby-plus
```
- HTTP 代理过滤
- 适合视频广告

### 3.2 科学上网

常用插件（需自行添加软件源）：
- **PassWall** — 支持多种协议（SS/SSR/V2Ray/Trojan）
- **Hello World** — 功能全面的代理工具
- **OpenClash** — Clash 内核，规则丰富
- **SSR Plus+** — 简单易用

安装方式（以 PassWall 为例）：
```bash
opkg install luci-app-passwall
```

### 3.3 内网穿透

- **Frp（Fast Reverse Proxy）**
  ```bash
  opkg install luci-app-frp
  ```
  配置：服务端地址、远程端口、本地映射

- **ZeroTier**
  ```bash
  opkg install luci-app-zerotier
  ```
  组建虚拟局域网，异地组网

- **Tailscale**
  ```bash
  opkg install luci-app-tailscale
  ```
  基于 WireGuard 的零配置组网

### 3.4 流量统计与监控

```bash
opkg install luci-app-statistics luci-app-nlbwmon
```

- **Statistics** — CPU/内存/网络流量图表
- **NLBWMon** — 按设备统计流量
- **vnstat** — 命令行流量统计

### 3.5 USB 扩展功能

如果路由器有 USB 口：
```bash
# 挂载 U 盘 / 硬盘
opkg install block-mount kmod-usb-storage kmod-fs-ext4

# 打印机共享
opkg install luci-app-p910nd

# 4G 上网卡
opkg install kmod-usb-net kmod-usb-serial-option
```

### 3.6 Docker 容器（x86 软路由）

如果是 x86 软路由：
```bash
opkg install luci-app-dockerman docker-compose
```

适合跑轻量服务：HomeAssistant、AdGuard Home、文件服务器等

---

## 第四阶段：精通与开发

### 4.1 编译自定义固件

**环境要求：** Ubuntu/Debian Linux

```bash
# 克隆源码
git clone https://github.com/openwrt/openwrt.git
cd openwrt

# 更新 feeds
./scripts/feeds update -a
./scripts/feeds install -a

# 配置
make menuconfig

# 编译（-j 后面是 CPU 核心数）
make -j$(nproc)
```

编译选项：
- **Target System** — 选择 CPU 架构（如 IPQ807x、MT7981）
- **Target Profile** — 选择具体设备型号
- **LuCI → Applications** — 选择要集成的插件
- **Kernel modules** — 选择内核模块

### 4.2 在线定制固件

如果不想自己折腾编译环境：

- **OpenWRT.AI** (`https://openwrt.ai`) — 在线定制，已适配 1200+ 设备
- **ImmortalWRT** — 国内常用定制版
- **LEDE** — 老牌定制固件

### 4.3 编写自定义脚本

**开机自启脚本：**

```bash
cat > /etc/init.d/my_custom_service << 'EOF'
#!/bin/sh /etc/rc.common
START=99

start() {
    # 你的脚本
    echo "Custom service started"
}

stop() {
    echo "Custom service stopped"
}
EOF

chmod +x /etc/init.d/my_custom_service
/etc/init.d/my_custom_service enable
```

**UCI 配置系统：**

UCI（Unified Configuration Interface）是 OpenWRT 的统一配置系统：

```bash
# 查看配置
uci show network

# 修改配置
uci set network.lan.ipaddr='192.168.2.1'
uci commit network
/etc/init.d/network reload
```

### 4.4 网络调试命令

```bash
# 抓包分析
tcpdump -i br-lan port 53

# 路由追踪
traceroute -n 8.8.8.8

# 查看 ARP 表
arp -n

# DNS 查询
nslookup google.com

# 带宽测试
iperf3 -c 服务器IP
```

### 4.5 备份与恢复

```bash
# 备份配置
sysupgrade -b /tmp/backup.tar.gz

# 恢复配置（升级后）
sysupgrade -r /tmp/backup.tar.gz

# 备份到远程
scp /tmp/backup.tar.gz root@192.168.x.x:/path/
```

---

## 360 T7 路由器相关

### 基本信息

- **CPU**：联发科 MT7981（Filogic 820），双核 A53 @ 1.3GHz
- **RAM**：256MB
- **ROM**：128MB SPI NAND Flash
- **Wi-Fi**：MT7976CN，双频 AX3000（2.4G + 5G）
- **刷机方式**：通过 Breed（不死鸟）引导加载器刷入

### 常用固件

| 固件 | 特点 |
|------|------|
| **OpenWRT 官方** | 稳定，功能精简，需自行装插件 |
| **ImmortalWRT** | 含常用插件，中文社区维护 |
| **OpenWRT.AI 定制** | 在线选插件生成固件 |
| **237 大佬固件** | 360 T7 专用优化版 |

### 注意事项

- 360 T7 刷机前需要先刷入 **Breed** 作为引导
- 固件选择 **immortalwrt-mediatek-mt7981** 或 **openwrt-mediatek-filogic** 系列
- 5G Wi-Fi 频宽建议设置 **80MHz**（160MHz 可能不稳定）
- 散热：360 T7 原厂散热一般，建议加散热片

---

## 实用插件推荐

### 网络优化

| 插件 | 功能 | 安装命令 |
|------|------|---------|
| `luci-app-mwan3` | 多拨/负载均衡 | `opkg install luci-app-mwan3` |
| `luci-app-sqm` | 智能 QoS 限速 | `opkg install luci-app-sqm` |
| `luci-app-eqos` | 简易 QoS | `opkg install luci-app-eqos` |
| `luci-app-flowoffload` | 硬件流量卸载加速 | `opkg install luci-app-flowoffload` |
| `luci-app-turboacc` | 加速模块合集 | `opkg install luci-app-turboacc` |

### 安全与隐私

| 插件 | 功能 |
|------|------|
| `luci-app-adguardhome` | DNS 广告过滤 |
| `luci-app-vnstat` | 流量监控 |
| `luci-app-wol` | 网络唤醒 |
| `luci-app-nlbwmon` | 设备流量统计 |

### 存储与文件

| 插件 | 功能 |
|------|------|
| `luci-app-aria2` | 离线下载 |
| `luci-app-transmission` | BT 下载 |
| `luci-app-filetransfer` | 文件传输 |
| `luci-app-minidlna` | DLNA 媒体服务器 |
| `luci-app-samba4` | 文件共享（SMB） |

### 实用工具

| 插件 | 功能 |
|------|------|
| `luci-app-upnp` | UPnP 端口映射 |
| `luci-app-wifischedule` | Wi-Fi 定时开关 |
| `luci-app-commands` | Web 执行自定义命令 |
| `luci-app-attendedsysupgrade` | 在线升级固件 |

---

## 学习资源汇总

### 官方资源

| 资源 | 链接 |
|------|------|
| OpenWRT 官网 | [https://openwrt.org](https://openwrt.org) |
| OpenWRT 官方文档 | [https://openwrt.org/docs/start](https://openwrt.org/docs/start) |
| 快速入门指南 | [https://openwrt.org/docs/guide-quick-start/start](https://openwrt.org/docs/guide-quick-start/start) |
| 支持设备列表 | [https://openwrt.org/supported_devices](https://openwrt.org/supported_devices) |
| GitHub 源码 | [https://github.com/openwrt/openwrt](https://github.com/openwrt/openwrt) |
| OpenWRT 论坛 | [https://forum.openwrt.org](https://forum.openwrt.org) |

### 第三方教程

| 资源 | 链接 | 说明 |
|------|------|------|
| LearnOpenWRT | [https://learnopenwrt.com](https://learnopenwrt.com) | 英文图文教程，适合进阶 |
| OpenWRT.AI 定制 | [https://openwrt.ai](https://openwrt.ai) | 在线定制编译固件 |
| ImmortalWRT | [https://immortalwrt.org](https://immortalwrt.org) | 中文定制固件 |
| 恩山无线论坛 | [https://www.right.com.cn/forum/](https://www.right.com.cn/forum/) | 中文最大路由器论坛 |
| 哔哩哔哩 | B 站搜索「OpenWRT」 | 视频教程众多 |

### 关键命令速查

```bash
# 系统
cat /proc/cpuinfo         # 查看 CPU
free -m                   # 查看内存
df -h                     # 查看存储
uname -a                  # 查看内核版本
uptime                    # 查看运行时间

# 网络
ifconfig                  # 查看接口
iwconfig                  # 查看无线接口
ip addr                   # IP 地址
ip route                  # 路由表
ping -c 4 8.8.8.8         # 测试连通性

# 包管理
opkg update               # 更新列表
opkg list-installed       # 已安装包
opkg install 包名          # 安装
opkg remove 包名           # 移除

# 服务管理
/etc/init.d/服务名 start   # 启动
/etc/init.d/服务名 stop    # 停止
/etc/init.d/服务名 enable  # 开机自启
/etc/init.d/网络/ restart  # 如 network 重启

# UCI 配置
uci show                  # 查看所有配置
uci show network          # 查看网络配置
uci set network.lan.ipaddr='192.168.1.1'
uci commit network        # 提交更改
/etc/init.d/network reload  # 重载
```

---

> **关于 WorkBuddy 自动装插件**：目前 PAIOS 还没有 SSH 连接路由器的脚本。
> 后续可以写一个脚本，通过 SSH 连到 OpenWRT 路由器自动执行 `opkg install`。
> 需要知道路由器的管理 IP 和 root 密码后才能实现。
