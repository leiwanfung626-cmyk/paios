# Today — 2026-07-10

> **Phase**: Platform Operations v1.0 — Daily Operations
> **Computer**: evan (E:\PAIOS)
> **Git**: ✅ 已提交并推送（f56008a + merge f9edc9f）

## Today's Plan

- [x] 运丰文件夹三级优先级重分类（EXIF > 文件名 > embedding）
- [x] 增量全量扫描 + 去重分类（批次 20260710）
- [x] GLM 补判 0 根因排查与修复（1210/1301 伪装"其他"）
- [x] OpenWrt 二级路由搬移后代理修复 + 分流验证
- [x] PAIOS 全面审计 — 扫描所有工作归档状态
- [x] 系统性复盘 + 架构审查 + 问题修复
- [x] Git 提交全部变更

## Completed

- [x] 运丰重分类：23 张候选（watermark 6 + meta 1 + age 16），用户全勾选执行，22 张移动
- [x] 运丰删除审查：25 条疑似/无脸核对
- [x] 运丰可编辑人生大事记时间线（gen_timeline.py）
- [x] 增量扫描：15,530 文件，GLM 补判修复（3 层根因排查）
- [x] 照片整理 SOP + Skill 梳理产出
- [x] 架构评审吸收 → SOP v1.1 重构
- [x] OpenWrt 网络配置重置：WAN/LAN/WiFi/DNS/代理全部修复，分流验证通过
- [x] PAIOS 审计：识别 10 项问题（Git 滞后、openwrt 未归档、notes.md 滞后、根目录杂散等）
- [x] 复盘评估报告：30_SYSTEM/Evolution/PAIOS-Retrospective-2026-07-10.md
- [x] 根目录清理：删除 Claw/、e/、2026-07-03-21-12-55/、nul、test_small.bin
- [x] openwrt 归档到 90_ARCHIVE/
- [x] 70_TMP 清理：删除 4 个早期探索脚本
- [x] photos_organizer/notes.md 补全（4 天缺失进展）
- [x] v1.1_plan.md 从 30_SYSTEM 移回项目
- [x] scripts 临时产物清理
- [x] Today/Metrics/Goals/Inbox 刷新
- [x] Git merge 冲突解决（Inbox/Today/reasonix.toml）

## feng 归档记录（2026-07-08，覆盖 7/6–7/8）

远端合并入的归档记录（来自老电脑 feng）：
- **References 补录**：REF-0008 OpenWRT 教程、REF-0009 Codex 最佳实践
- **Decision 新增**：DEC-2026-07-08-0001 — 360 T7 OpenWrt 代理+去广告架构
- **游离清理**：根目录 `2026-07-06-11-47-18/` 已移入 `70_TMP/archive-cleanup-2026-07-08/`
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
- [x] **视频转写 SOP（REF-0015）**：抖音「山岳老师」数据科学考研择校/27难度视频 → 按 Video-to-Knowledge-Pipeline 入库（⚠️ 本沙箱缺 whisper/ffmpeg，Step 2b 未跑，WebSearch 兜底+多源验证；主服务器 F:\PAIOS 可执行真实转写）


## Status Snapshot

| Check | Value |
|-------|-------|
| Git | ✅ f56008a + merge f9edc9f，已推送 |
| Directories | 根目录已清理，7层结构完整 |
| Inbox | 已清空 |
| Memory | 2026-07-10.md 已更新 |
| 归档 | openwrt → 90_ARCHIVE/ ✅ |
| 审计 | 复盘报告已归档至 Evolution/ |
