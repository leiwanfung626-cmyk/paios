---
title: "SOP-2026-07-11-0003 — Pilot 启动清单（Case-01 单实例 14 天）"
status: Active
created: 2026-07-11
related:
  - ../Governance/Pilot-Gate.md
  - ../Governance/Architecture-Lifecycle.md
  - ../Governance/Rollout.md
  - ../ADR/ADR-0018-Multi-Instance-Role-Model.md
  - ../Governance/Operating-Model.md
---

# SOP-2026-07-11-0003 — Pilot 启动清单

> **用途**：Phase B 设计已冻结（ADR-0017 平台纯度 + ADR-0018 角色模型 + Operating-Model + 用户侧 SOP 全链），在 **全量推广前** 必须用单实例跑通 14 天。
> 本 SOP 是 `Pilot-Gate.md` 的**操作 companion**——把"持续观察什么、怎么判过闸"变成可勾选的清单。
> **本文件不修改任何冻结文档，仅提供执行层勾选表。**

- **Pilot 实例**：Case-01（Developer / Platform Maintainer，本机）
- **观察期**：连续 **14 天**，无中断
- **Owner**：Evan（兼任 Architect / Developer / Maintainer）
- **权威阈值**：以 `Pilot-Gate.md §4` 为准；本表是其可勾选形态

---

## 1. 启动前置（Day 0 — 勾完才开工）

进入 Pilot 前，**全部满足**：

- [ ] **Blueprint Frozen** — 设计仅文档，未碰物理文件（ADR-0017/0018 已 commit 冻结）
- [ ] **Commit Finished** — Establish Boundaries 已提交，备份锚点 `pre-phaseb-backup` tag 就位
- [ ] **Rollback Ready** — 任意一步可 `git tag` / 备份回退，数据零丢失
- [ ] **本地领先远端的治理链已 commit 未 push** — 当前 HEAD 领先 `origin/master` 13 提交（含本 SOP），按纪律暂不 push
- [ ] **本机即 Pilot 实例** — Case-01 本机最熟悉变更，出问题易定位（契合 Pilot-Gate §5 单实例模式）

> 上述任一项未勾，不得开始 Day 1。

---

## 2. 每日观察项（Day 1–14，每天收工前勾）

复制下方模板，每天填一份。重点验证两件事：**①Core 写入口唯一性（角色模型生效）②Workspace 日常写入不被 Purity 卡住（不会误伤正常使用）**。

```
─── Day __ / 14  （日期：____-__-__） ──────────────────────────
□ 今日 Core（30_SYSTEM / 40_AUTOMATION / RELEASES / CHANGELOG / ADR）提交仅来自 Case-01
    → git log --since="today 00:00" --oneline  提交人/实例 = Case-01  ✓/✗
□ 今日无任何"用户侧 push Core"尝试（含本机误 push）
    → 本机为 Developer，此项天然满足；仅记录是否曾误操作  ✓/NA
□ collect_manifest.py 正常生成 manifest（含 manifest_version）
    → 运行结果：manifest_version = ____  稳定 ✓ / 漂移 ✗
□ publish 正常流入 F:\Fleet\incoming\
    → 文件落盘：是 ✓ / 否 ✗
□ F:\Fleet 子结构（incoming / history / reports）工作正常
    → 正常 ✓ / 异常 ✗
□ Registry（如 scripts.yaml）读取正常
    → 正常 ✓ / 异常 ✗
□ Workspace 日常写入顺畅，未被 Purity 误卡
    → 写入目录：10_WORK/ □  20_KNOWLEDGE/Personal/ □  Today.md □  Archive □  Projects □
    → 是否遇到"该写却因 Purity 被拒"：是（记详情）/ 否 ✓
□ 升级路径无碍（git pull 当前版本正常，无异常冲突）
    → 正常 ✓ / 异常 ✗
□ 黄金纪律未被违反（Workspace 每天变 / Platform 只走 Release）
    → 今日有无"绕 Release 直接改平台"：有（记详情）/ 无 ✓
□ 交叉审查原则（§7）是否被触发
    → 今日有无引擎改架构：有（是否已另一引擎审查 ✓/未 ✗）/ 无 NA
─── 当日备注（异常/摩擦/灵感）──────────────────────────────────
```

> **记录位置**：日志写在 `70_TMP/Pilot-DayNN-Log.md`（临时，不进 Core 历史）；异常达 Major 级立即记 Evidence 并暂停。

---

## 3. 每周回顾（Day 7 / Day 14）

- [ ] **Day 7 回顾**：前 7 天 0 Critical、0 Data Loss；观察项无系统性摩擦；Manifest Stable
- [ ] **Day 14 回顾**：14 天全周期复盘，确认无遗漏观察项
- [ ] 若发现设计缺陷 → **回 Blueprint / ADR 修订，重新 Freeze**，不带着缺陷进 Rollout
- [ ] 若仅局部摩擦但无违约 → 记为 Observation，留待 Retrospective 处理

---

## 4. Exit Criteria 勾选表（过闸门槛 — 全满足才 Rollout）

依据 `Pilot-Gate.md §4`，**全部 ✓ 才允许过闸**：

| # | 标准 | 阈值 | 勾选 |
|---|------|------|------|
| 1 | 试点时长 | 连续 **14 天** 无中断 | [ ] |
| 2 | Critical 缺陷 | **0**（无数据丢失 / 无 manifest 冲突 / 无 Workspace 泄漏） | [ ] |
| 3 | Data Loss | **0**（物理隔离类操作前已验证磁盘保留） | [ ] |
| 4 | Merge | **Normal**（与远端可分叉正常合并，无 Workspace 写回） | [ ] |
| 5 | Manifest | **Stable**（`manifest_version` 稳定，schema 无漂移） | [ ] |
| 6 | 观察项完整 | 14 天每日模板 + 2 次周回顾已全部填写 | [ ] |

> 任一项未勾 → **延长 Pilot，不强行 Rollout**。过闸靠满足标准，不靠感觉。

---

## 5. 过闸后动作（Post-gate — 不在此 SOP 执行）

Exit Criteria 全满足后，按 `Architecture-Lifecycle.md` Rollout 阶段展开为 Git History 四段：

1. **Commit 3 — Git Cleanup**：`git merge origin/master`（分叉点 `f9edc9f`），解决 CASE-001 锁定的 8 个远端历史债务提交，清理互推/merge/manifest 回传污染
2. **Commit 4 — Physical Separation**：`git rm --cached` 移除 Workspace 类路径（物理隔离，Core 不再含用户内容）
3. **Rollout → Case-02 / Case-03**：分发 Release（含用户须知模板 + 开机提醒），它们 `git pull` 升级
4. **Validate**：连续多版本观察，缺陷不再复现
5. **Retrospective → CASE-002**：回顾结论（Accepted / Adjusted / Rejected / Deferred），判定是否进入 Phase C

---

## 6. 铁律提醒（Pilot 期间）

- **不 push**：Pilot 期间所有本地提交保持未 push，等 Git Cleanup 阶段统一处理远端分叉
- **不 merge 远端**：Pilot 期间不与 `origin/master` 合并，避免污染观察样本
- **不 rm cached**：物理隔离留到 Commit 4，Pilot 只验证"逻辑边界 + 角色模型"是否成立
- **异常即停**：出现 Critical（真实数据丢失）立即暂停相关流程，优先修复并记 Evidence

---

_本 SOP 是 Pilot-Gate 的执行层清单。平台侧发布见 `SOP-2026-07-10-0001-Release-Flow.md`；用户侧操作见 `SOP-2026-07-11-0001-User-Daily-Operations.md`；角色模型速览见 `User-Role-Model-Speed-View.html`。_
