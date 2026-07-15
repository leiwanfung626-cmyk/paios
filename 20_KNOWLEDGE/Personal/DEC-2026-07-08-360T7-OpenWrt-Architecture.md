---
type: decisions
topic: "360 T7 OpenWrt 代理+去广告架构 — nikki(mihomo) + AdGuardHome"
lifecycle: accepted
id: "DEC-2026-07-08-0001"
created: "2026-07-08"
updated: "2026-07-08"
source: "推演对话(7/6) + 实际部署(7/8) + REF-0008 OpenWRT 教程"
tags: [decisions, openwrt, 360t7, mihomo, nikki, adguardhome, proxy, network, router]
attributes:
  trigger: "360 T7 改 512MB 内存 + 刷 OpenWRT 后，需确定代理/去广告方案"
  decision_type: "implementation（实施决策，已落地）"
  priority: "P1 — 已实施，记录以供后续复用"
  related_model: ""
extensions:
  related_refs: ["REF-0008"]
  related_files: ["10_WORK/Done/2026-07-08-OpenWrt-Proxy-ADG-Setup.md"]
  related_principles: ["Necessity_Gated_Architecture"]
---

# 决策记录：360 T7 OpenWrt 代理 + 去广告架构

## 背景

360 T7 (联发科 MT7981B，双核 A53) 硬件改造：**内存由 256MB 扩至 512MB**，并刷入 OpenWRT 24.10.5 (aarch64_cortex-a53)。
设备角色定位为**次级网关 / 代理出口**（WAN 接主路由 192.168.110.0/24，LAN 192.168.1.0/24）。
需确定代理客户端与去广告 DNS 的整体方案。

## 决策

采用 **nikki（Mihomo 管理器）+ Mihomo 内核** 做代理，**AdGuard Home** 做 DNS 级去广告，三者串联：

```
用户设备 → dnsmasq(:53) → AdGuard Home(:5353) → mihomo(:1053)
                            ↓ 去广告过滤        ↓ 分流决策
                          (ad filter)     (国内直连 / 国外代理)
```

- **mihomo/nikki** (Meta alpha-1686d56)：36 节点，Rule 模式，TUN mixed，混合端口 7890
- **AdGuard Home** (v0.107.57)：DNS :5353，上游指向 mihomo :1053
- 部署日期 2026-07-08，详见 `10_WORK/Done/2026-07-08-OpenWrt-Proxy-ADG-Setup.md`

## 选项对比与取舍

| 维度 | 选项 | 结论 |
|------|------|------|
| 代理前端 | OpenClash vs nikki | 选 **nikki**（轻量 LuCI 前端，内核跑 RAM，契合低闪存） |
| 去广告 | AdGuard Home vs adbyby | 选 **AGH**（DNS 级过滤，规则丰富，与代理解耦） |
| 内核落盘 | 常驻闪存 vs 跑 RAM(tmpfs) | 选 **跑 RAM**（闪存余量紧张，内核 ~25MB 不适合常驻） |

## 关键理由

1. **512MB 内存是前提条件**：Mihomo 内核二进制约 25MB，内部闪存余量有限；内存扩容后内核可常驻 RAM，仅 LuCI 管理 app 占闪存（~2MB）。**这正是改内存的直接价值**。
2. **无 USB 也能跑代理**：RAM 化内核不依赖外部存储，纯代理场景无需 USB 扩展。
3. **DNS 链分层解耦**：dnsmasq → AGH（去广告）→ mihomo（分流），每层职责清晰，AGH 与代理可独立替换/升级，不互相绑架。
4. **Rule + TUN mixed**：国内直连 / 国外代理自动分流，TUN 透明代理使局域网设备免客户端配置。

## 边界：何时才需要 USB

若后续要跑**重持久化服务**——AGH 完整规则库（数百 MB）、BT/离线下载机、轻 NAS、Docker——才需加 USB + extroot 扩容。
**当前纯代理 + DNS 去广告场景，不需要 USB。**

## 后续可演进

- 加 `luci-app-nlbwmon` / `sqm-scripts` 做流量统计与 QoS（512MB 内存可扛）
- 若加 USB：评估 extroot 把 overlay 扩到 U 盘，解除闪存天花板
- PAIOS 侧：补一个 SSH 连路由器、幂等执行 `opkg install` 的自动化脚本（REF-0008 文末已预留此议题）
