---
title: "Pilot Gate — 试点门槛"
status: Active
created: 2026-07-11
related:
  - Architecture-Lifecycle.md
  - Decision-Traceability.md
  - Rollout.md
  - ../Evolution/Phase-B-Core-Workspace-Split.md
---

# Pilot Gate（试点门槛）

> 设计冻结之后、全量推广之前，**必须**经过单实例试点。
> Pilot 不是"感觉没问题就过"，而是**满足固定 Exit Criteria 才过闸**。
> 本规范独立于任何 Phase，Phase B / C / D 复用。

---

## 1. 为什么需要 Pilot Gate

- 设计冻结只证明"文档合理"，不证明"真实运行无碍"。
- 全量推广一旦出错，多实例一起返工，成本高。
- 单实例试点把风险关在最小范围，且天然可利用实例角色差异（无需额外搭环境）。

---

## 2. Pilot Entry（进入试点门槛）

满足以下全部，才能开始 Pilot：

| 条件 | 说明 |
|------|------|
| **Blueprint Frozen** | 设计已冻结（仅文档，未碰物理文件） |
| **Commit Finished** | Establish Boundaries 已提交，备份锚点（如 `pre-phaseb-backup` tag）就位 |
| **Rollback Ready** | 任意一步可 `git tag` / 备份回退，数据零丢失 |

---

## 3. 试点期间验证信号（持续观察）

Pilot 实例需持续正常输出以下信号（以 Phase B 为例，其他 Phase 类同）：

- `collect_manifest.py` 正常生成 manifest（含 `manifest_version`）
- `publish` 正常流入 `F:\Fleet\incoming\`
- `F:\Fleet` 子结构（incoming / history / reports）工作正常
- Registry（如 `scripts.yaml`）读取正常
- `upgrade`（当前版本 → 未来版本）路径无碍

> 信号清单随 Phase 不同而不同，但"持续观察、记录"的原则一致。

---

## 4. Pilot Exit（过闸门槛）

**全部满足**才允许 Rollout：

| 标准 | 阈值 |
|------|------|
| 试点时长 | 连续 **14 天** 无中断 |
| Critical 缺陷 | **0**（无数据丢失、无 manifest 冲突、无 Workspace 泄漏） |
| Data Loss | **0**（物理隔离类操作前已验证磁盘保留） |
| Merge | **Normal**（与远端可分叉正常合并，无 Workspace 写回） |
| Manifest | **Stable**（`manifest_version` 稳定，schema 无漂移） |

> 过闸靠**满足标准**，不靠"感觉"。未满足则延长 Pilot，不强行 Rollout。

---

## 5. 单实例试点模式

利用实例天然角色差异选 Pilot：

- **Phase B**：Pilot = **Case-01（Developer）**——开发者本机，最熟悉变更，出问题易定位。
- 其他 Phase 以此类推：选"最贴近变更、最易观测"的单一实例先跑。

---

## 6. 复用规则

- 任何 L3 级变更：Pilot 不可跳过。
- Pilot 期间发现设计缺陷：回到 Blueprint / ADR 修订，重新 Freeze，不带着缺陷 Rollout。
- 本规范与 `Architecture-Lifecycle.md`（Pilot 阶段）、`Rollout.md`（过闸后）配套。

> **配套操作清单**：`../SOP/SOP-2026-07-11-0003-Pilot-Launch-Checklist.md` — 把本规范 §2/§4 变成可勾选的启动前置 / 每日观察 / Exit Criteria 表，Pilot 期间照此执行。本规范是权威阈值，清单是执行形态。
