# Today — 2026-07-08

> **Phase**: Platform Operations v1.0 — Daily Operations
> **Computer**: feng (F:\PAIOS)
> **Git**: ✅ 已归档提交（7/6–7/8 累积）

## Today's Plan

- [x] PC 网络路由配置 → OpenWrt 网关
- [x] SSH 免密登录 OpenWrt
- [x] 安装 mihomo/nikki 代理客户端
- [x] 安装 AdGuard Home 去广告 DNS
- [x] 配置 DNS 链：dnsmasq → ADG → mihomo
- [x] git commit + push（归档 7/6–7/8 累积工作）

## 归档记录（2026-07-08，覆盖 7/6–7/8）

将本周散落工作统一归档进 PAIOS 知识库并 git 提交：

- **References 补录**：REF-0008 OpenWRT 教程（原未编号）、REF-0009 Codex 最佳实践（原游离在根目录 `2026-07-06-11-47-18/`，已移入 `20_KNOWLEDGE/References/` 并编号）
- **Decision 新增**：DEC-2026-07-08-0001 — 360 T7 OpenWrt 代理+去广告架构（nikki/mihomo + AdGuardHome，512MB RAM 支撑内核跑 RAM）
- **游离清理**：根目录 `2026-07-06-11-47-18/` 整体软删除至 `70_TMP/archive-cleanup-2026-07-08/`
- **索引更新**：References / Decisions 两处 `_index.md` 已同步
- 既有资产：REF-0006 Codex CLI、REF-0007 WorkBuddy 省积分、KB-2026-07-06-0001 方法、7/8 执行归档 `10_WORK/Done/`

## Completed（2026-07-08）

- [x] **网络路由**：PC 有线连接 OpenWrt LAN，默认网关 192.168.1.1
  - 无线已关闭，路由表无冲突
  - 静态 IP 192.168.1.100，DNS 114.114.114.114
- [x] **SSH 免密**：`id_ed25519` → OpenWrt `/etc/dropbear/authorized_keys`
- [x] **mihomo/nikki 代理** (v1.26.1)
  - Mihomo Meta alpha-1686d56，36 个代理节点（港/新/美/日/台/韩/加/澳/德/英等）
  - Rule 模式，国内直连 + 国外代理
  - TUN mixed 模式，混合端口 7890
- [x] **AdGuard Home** (v0.107.57)
  - Web 管理 http://192.168.1.1:3000 (admin / Lyf201314lyf)
  - DNS 端口 5353，上游 127.0.0.1:1053 (mihomo)
  - 广告过滤规则已加载
- [x] **DNS 链**：dnsmasq(53) → AGH(5353) → mihomo(1053) 全链路打通

## Status Snapshot

| Check | Value |
|-------|-------|
| New Completed | OpenWrt 路由 + mihomo 代理 + AdGuard Home |
| OpenWrt | 24.10.5, aarch64_cortex-a53 |
| mihomo | 36 nodes, Rule mode, TUN mixed |
| AGH | :3000(Web) / :5353(DNS) |
| Git | ✅ 已提交并推送（7/6–7/8 归档） |
