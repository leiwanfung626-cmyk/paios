---
title: "Pilot Gate — 试点门槛"
status: Active
version: "v1.1 (2026-07-19 — Phase-4 Dual Gate Model)"
created: 2026-07-11
updated: 2026-07-19
related:
  - Architecture-Lifecycle.md
  - Decision-Traceability.md
  - Rollout.md
  - ../Evolution/Phase-B-Core-Workspace-Split.md
  - PAIOS-2026-0719-STRICT-REVIEW-RESPONSE-001
---

# Pilot Gate（试点门槛）—— Engineering Pilot

> **Engineering Pilot**（工程试运行）：设计冻结之后、全量推广之前，必须经过工程试运行。
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

| 类别 | 标准 | 阈值 |
|------|------|------|
| 技术 | Critical 缺陷 | **0**（无数据丢失、无 manifest 冲突、无 Workspace 泄漏） |
| 数据 | Data Loss | **0**（物理隔离类操作前已验证磁盘保留） |
| Git | 分支污染 | **0**（与远端可分叉正常合并，无 Workspace 写回）；**无长期未解决的 merge conflict** |
| Git | 时间 | 连续 **14 天** 无中断 |
| Manifest | Schema 稳定性 | **Stable**（`manifest_version` 稳定，schema 无漂移） |
| 治理 | ADR / SOP / Stories | 能支撑真实开发（至少 1 次完整 Proposal→Dev→Review→Audit→Merge 流程验证） |
| AI | AI Operating Model | 至少完整跑通 **3 次** 任务路由（Idea→Proposal→Dev→Review→Audit→Maintainer） |
| Human | 多实例流程 | Case-01/02/03 角色验证完成（每个角色至少 1 次按 Operating Model 操作） |

> 过闸靠**满足标准**，不靠"感觉"。未满足则延长 Pilot，不强行 Rollout。

---

## 5. Engineering Pilot 里程碑

14 天 Pilot 不是等待时间，而是完成 5 个里程碑：

| 里程碑 | 内容 | 完成标志 |
|--------|------|----------|
| **M1** | 单实例治理稳定 | 治理体系（ADR/SOP/Stories/Journal/Pilot Report）能在 Case-01 上正常运行 3 天 |
| **M2** | AI Operating Model 跑通 | 至少 1 次完整流程：Idea -> Proposal -> Dev -> Review -> Audit -> Maintainer |
| **M3** | Case-02 Developer 验证 | Case-02 按 Developer 角色完成 1 次 Feature Branch + Proposal 流程 |
| **M4** | Case-03 Pilot User 验证 | Case-03 按 Pilot User 角色完成升级 + 使用 + Issue 反馈流程 |
| **M5** | Engineering Pilot Exit | 全部 Exit Criteria 满足，pilot 分支合并回 master |

### Daily Pilot Cycle

每天形成完整闭环：

```
上午：WorkBuddy 日常工作
  |  发现需求
  v
ChatGPT 架构讨论 -> Proposal
  v
Reasonix 开发实现
  v
ChatGPT Review + Code Review
  v
Commit 到 pilot 分支
  v
Pilot Report（每天一篇）
  v
结束
```

**纪律**：每天结束前，`pilot` 分支必须能独立运行——不可留下半成品代码导致无法工作。

---

## 6. 单实例试点模式

利用实例天然角色差异选 Pilot：

- **Phase B**：Pilot = **Case-01（Developer）**——开发者本机，最熟悉变更，出问题易定位。
- 其他 Phase 以此类推：选"最贴近变更、最易观测"的单一实例先跑。

---

## 7. 复用规则

- 任何 L3 级变更：Pilot 不可跳过。
- Pilot 期间发现设计缺陷：回到 Blueprint / ADR 修订，重新 Freeze，不带着缺陷 Rollout。
- 本规范与 `Architecture-Lifecycle.md`（Pilot 阶段）、`Rollout.md`（过闸后）配套。

> **配套操作清单**：`../SOP/SOP-2026-07-11-0003-Pilot-Launch-Checklist.md` — 把本规范 §2/§4 变成可勾选的启动前置 / 每日观察 / Exit Criteria 表，Pilot 期间照此执行。本规范是权威阈值，清单是执行形态。

---

## 8. Phase-4 Exit Gates（双闸门模型）

> Phase-4 STABILIZE 的出口从单一 Pilot Gate 升级为双闸门模型（Dual Gate Model），
> 同时验证**系统稳定性**和**业务价值**，两门全过才允许进入 Phase-5。

### 8.1 为什么需要双闸门

- 单一 Pilot Gate 只回答"系统能稳定运行吗？"（工程正确性）
- 30 天价值度量冲刺引入后，PAIOS 可以额外回答"系统值得继续投入吗？"（投资回报率）
- 两个问题互相独立：稳定的系统不一定有价值，有价值的系统必须稳定

### 8.2 双闸门时序

两门从 Day 0 **并发启动**，非串行：

```
Day 0 ─────────────────────────────────────────── Day 30
        │                                         │
        ├── Gate-1 Stability (14 days) ──────┤    │
        │   （连续稳定无 Critical）                │    │
        │                                         │
        ├── Gate-2 Value (30 days) ─────────────────┤
        │   （A-1~A-7 价值度量）                      │
        │                                         │
        ↓                                         ↓
   Day 14: Gate-1 通过               Day 30: Gate-2 通过
   （等 Gate-2 完成）                         Phase-5 Entry
```

### 8.3 Gate-1: Stability Gate（14 天）

**目标：** 验证系统能否可靠运行。

**周期：** 14 天连续观测。

**指标（复用 §4 Pilot Exit Criteria）：**

| 类别 | 阈值 | 说明 |
|------|------|------|
| Critical 缺陷 | **0** | 无数据丢失、无 manifest 冲突、无 Workspace 泄漏 |
| 连续天数 | **14 天** | 从 Day 0 起连续无中断 |
| Core 未污染 | **0** | git diff 20_KNOWLEDGE + 30_SYSTEM/ADR 无引擎导致的变更 |
| 自动化脚本无退化 | **稳定** | capture / build / record 三条主脚本运行正常 |
| AI 协作闭环 | **≥1 次** | 至少一次完整 Proposal→Review→Implement→Acceptance 流程 |

**性质：** 被动观测，非主动建设。不要求新增能力、不跑通 Fleet、不做 Phase B 拆分。

**失败处理：** 中间产生 Critical → 从该日起重新计算 14 天，Gate-2 继续不受影响。

### 8.4 Gate-2: Value Gate（30 天）

**目标：** 验证 PAIOS 是否值得继续投入。

**周期：** 30 天价值度量冲刺（A-1~A-7）。

**核心问题（C4）：**

| Q | 问题 | 测量方式 |
|---|------|---------|
| Q1 | PAIOS 是否减少真实任务时间？ | 完成时间 / 返工次数 / 遗漏信息数量（3 任务对照） |
| Q2 | AI 是否真正利用历史知识？ | Usage Trace 记录 / resolve_node 调用次数 / ADR 复用率 |
| Q3 | 维护成本是否可接受？ | 每周维护小时数 / Trace 数量 / 孤儿率变化 |

**三色决策阈值：**

| Q | Green（过） | Yellow（延 14 天） | Red（收缩） |
|---|-------------|-------------------|-------------|
| Q1 时间减少 | ≥2/3 任务时间减少 ≥15% | 1/3 减少 | 无减少或变慢 |
| Q1 返工减少 | ≥2/3 任务返工 ≤1 次 | 1/3 减少 | 返工增多 |
| Q2 知识复用 | trace 中知识复用 ≥5 次 | 1-4 次 | 0 次 |
| Q3 维护成本 | <2h/周 | 2-5h/周 | >5h/周 |

**决策路径：**

```
Green → Phase-5 Entry
Yellow → 延长 Value Sprint 14 天再评
Red → 架构评审，考虑向方法论框架收缩
```

### 8.5 两门失败处理规则

```yaml
gate_failure_policy:
  stability_failed_during_value:
    action:
      - continue_value_measurement     # Value Gate 不受影响
      - restart_stability_counter      # 从失败日重新计 14 天

  stability_failed_after_value_pass:
    action:
      - block_phase5                   # Phase-5 Entry 不批准
      - recover_stability              # 修复后重新过 Stability Gate

  value_yellow_stability_passed:
    action:
      - extend_sprint_14_days          # 延长再评

  value_red_stability_passed:
    action:
      - architecture_review            # 治理评审：收缩方向

  both_failed:
    action:
      - governance_review              # 系统既不稳定也无价值
```

### 8.6 对 §1-§7 的关系

- §1-§7 全部保留，**不作修改**，作为 Phase-B/C/D 的通用 Pilot Gate 规范
- §8 是 **Phase-4 专用的出口模型**，不取代 §4 Pilot Exit Criteria 的通用性
- 后续 Phase（B/C/D）入口时，可根据需要复用双闸门模型或退回单一 Pilot Gate

