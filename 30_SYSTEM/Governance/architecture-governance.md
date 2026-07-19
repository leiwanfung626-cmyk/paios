---
title: Architecture Governance
version: "1.1 (2026-07-19 — Added §7 Knowledge→System Promotion Criteria)"
status: baseline
related_invariants: architectural-invariants.md
related_philosophy: paios-philosophy.md
related_adr:
  - ADR-0002
created: 2026-06-29
updated: 2026-07-19
---

# Architecture Governance — 架构治理

> **Governance 1.0 Baseline** — 定义 PAIOS 的基础治理框架。
>
> 后续版本可以在保持 Architectural Invariants 不变的前提下扩展治理能力，
> 例如自动化审查、Agent 协作和多贡献者工作流。

## 1. 目标与范围

### 目标

确保 PAIOS 在长期演化过程中保持：
- **一致性** — 每次变更都符合 Vision、Principles 和现有架构
- **可追溯性** — 任何设计决策都可向上追溯到 Philosophy 或 ADR
- **可维护性** — 系统不会因无序变更而逐渐退化

### 范围（1.0 Baseline）

Governance 1.0 只建立**规范层**，不引入任何自动化：

| 包含 | 不包含 |
|------|--------|
| ✅ 变更分级标准（Impact Levels） | ❌ 自动化审查脚本 |
| ✅ 审查流程定义 | ❌ PR Checklist 工具 |
| ✅ Asset Lifecycle 定义 | ❌ 目录结构校验 |
| ✅ Freeze Policy 关系说明 | ❌ ADR 模板自动校验 |
| | ❌ 架构报告自动生成 |

**治理 2.0**（未来）：当 Agent、脚本、自动化大量使用后，再将本规范转化为工具化流程。

## 2. Impact Levels — 变更影响分级

每次变更先按**影响最大的资产**定级（Highest Impact Wins）。
如果一个变更同时涉及多个级别，按最高级别处理。

| Level | 名称 | 定义 | 审查要求 | 示例 |
|-------|------|------|----------|------|
| **L0** | Documentation | 不影响系统行为的文档变更 | 无审查要求 | 修正拼写、补充 Design Note、完善注释 |
| **L1** | Configuration | 只影响配置，不改变行为逻辑 | Review 即可 | 修改 metadata.yaml、更新 Registry 条目、调整 prompt |
| **L2** | Behavior | 改变 Workflow、Agent、Prompt 的行为 | 架构 Review | 新增 Script、修改 Workflow 逻辑、注册新 Agent |
| **L3** | Architecture | 改变目录、生命周期、Engine 定义 | 必须 ADR | 新增一级目录、修改 Asset Lifecycle、新增 Engine |
| **L4** | Philosophy | 改变 Vision、Principle、Invariant | 重大评审 + ADR | 修改 `paios-philosophy.md`、修改 `Principles.md`、修改 Invariant |

### 定级规则

```
变更内容
    ↓
涉及 L4 资产？  ──Yes──→ L4
    No
    ↓
涉及 L3 资产？  ──Yes──→ L3
    No
    ↓
改变行为逻辑？  ──Yes──→ L2
    No
    ↓
修改配置？     ──Yes──→ L1
    No
    ↓
            L0
```

## 3. Asset Lifecycle — 资产生命周期

> **Lifecycle 描述资产状态，不规定审批权限。**
> 未来 Governance 2.0 的自动化、Agent、多人协作可在此基础上对接，而不被绑死。

以下生命周期适用于所有系统资产：ADR、Principle、Design Note、Workflow、Agent、Capability 等。

```
                  ┌──────────┐
                  │  Draft   │  ← 草稿阶段，未正式采纳
                  └────┬─────┘
                       │
                       ▼
                  ┌───────────┐
                  │ Reviewing │  ← 正在评审
                  └─────┬─────┘
                        │
                  批准？│
                   ┌────┴────┐
                   │         │
                   ▼         ▼
            ┌──────────┐  ┌───────────┐
            │ Approved │  │ Rejected  │  ← 退回，可重新 Draft
            └────┬─────┘  └───────────┘
                 │
                 ▼
            ┌──────────┐
            │  Active  │  ← 当前生效
            └────┬─────┘
                 │
            ┌────┴────┐
            │         │
            ▼         ▼
     ┌──────────┐  ┌──────────┐
     │  Frozen  │  │Deprecated│  ← 仍可参考，但不应在新场景使用
     └────┬─────┘  └────┬─────┘
          │              │
          └──────┬───────┘
                 ▼
            ┌──────────┐
            │ Archived │  ← 历史记录，只读
            └──────────┘
```

### 状态说明

| 状态 | 含义 | 可否修改 | 可否引用 |
|------|------|----------|----------|
| **Draft** | 起草中，未正式采纳 | ✅ | ⚠️ 谨慎引用 |
| **Reviewing** | 正在评审 | ⚠️ 仅评审意见 | ⚠️ 谨慎引用 |
| **Approved** | 已通过评审，待实施 | ✅ 按评审意见修改 | ✅ |
| **Active** | 当前生效 | ✅ | ✅ |
| **Frozen** | 冻结，不允许修改 | ❌ | ✅ |
| **Deprecated** | 已废弃，建议用替代方案 | ❌ | ⚠️ 仅历史参考 |
| **Archived** | 归档，只读 | ❌ | ✅ 历史追溯 |

## 4. Review Process — 审查流程

### 标准审查流水线

```
Proposal（提出变更）
    ↓
Impact Level 判定（按 Highest Impact Wins）
    ↓
L0 ──→ 无需审查，直接实施
L1 ──→ Review（可由提出者自行确认）
L2 ──→ 架构 Review（至少 1 人评审）
L3 ──→ ADR + 架构 Review
L4 ──→ ADR + 重大评审（需记录评审结论）
    ↓
实施
    ↓
Feedback（记录实际效果，供未来演化参考）
```

### 评审检查项（L2 及以上）

每次架构 Review 至少回答以下问题：
1. 这个变更违反任何 Architectural Invariant 吗？
2. 这个变更能追溯到哪个 Vision 或 Principle？
3. 这个变更与现有架构是否兼容？
4. 这个变更是否需要更新关联文档？

## 5. 与 Freeze Policy 的关系

**Freeze Policy 是 Asset Lifecycle 中 `Frozen` 状态的实例化。**

- `ADR-0002`（Automation Platform Freeze）将 40_AUTOMATION 的某些资产置于 `Frozen` 状态，为期 90 天
- Frozen 状态意味着：**不允许修改**，除非满足明确的解冻条件
- 未来可以有其他冻结策略（例如冻结某个 Principle、冻结某个 Design Note），复用相同的 Lifecycle 机制

| 概念 | 职责 | 示例 |
|------|------|------|
| **Asset Lifecycle** | 描述资产从创建到退役的全过程 | Draft → Active → Frozen → Archived |
| **Freeze Policy** | 描述在某个阶段**允许什么、不允许什么** | ADR-0002：90 天内禁止修改目录结构 |

两者互补而非替代：Lifecycle 提供状态机，Freeze Policy 提供该状态下的行为约束。

---

## 6. Governance 1.0 验证指标

本 Baseline 经实际使用验证通过后，方可启动 Governance 2.0 的设计。

| 指标 | 通过标准 |
|------|----------|
| Impact Level 使用 | 新增文档/变更时，实际使用了 Impact Level 定级 |
| Review Process 执行 | 新增架构变更时，实际经过了 Review Process |
| Invariant 稳定性 | 2~4 周内未出现需要修改 Invariant 的情况 |
| 维护成本 | Governance 是否减少了架构分歧，而非增加了日常负担 |

---

## 7. Knowledge → System Promotion Criteria

> 定义：**什么情况下 20_KNOWLEDGE 中的知识资产应该晋升为 30_SYSTEM 的系统原则？**
> 防止 30_SYSTEM 随时间膨胀成第二个知识库（Round 2 Architecture Review — P3 缺口）。

### 7.1 为什么需要这个标准

20_KNOWLEDGE 是已验证的知识经验（"做了什么、怎么做的"）。
30_SYSTEM 是系统运行的治理规则（"必须怎么做、不能怎么做"）。

两者边界模糊的风险：好东西就挪进 System → 30_SYSTEM 膨胀 → 系统变厚→治理成本上升。

### 7.2 晋升四条件

一项知识资产**必须同时满足全部 4 条**才能从 Knowledge 晋升为 System：

| # | 条件 | 判断标准 |
|---|------|---------|
| 1 | **多模块依赖** | 该资产被至少 **2 个** 不同目录（如 20_KNOWLEDGE/Platform 和 40_AUTOMATION）引用或依赖 |
| 2 | **改变运行规则** | 该资产定义了 AI/Agent/工作流**必须遵守**的行为约束，不仅仅是建议性参考 |
| 3 | **有 ADR** | 晋升必须有对应的 ADR 记录决策原因——"为什么这条规则应该成为系统的一部分" |
| 4 | **经冻结** | 晋升完成后，该资产进入 Frozen 状态，修改需要 L3 变更流程 |

### 7.3 不满足后的处理

| 场景 | 处理 |
|------|------|
| 满足 1-2 条但不全 | 留在 20_KNOWLEDGE，标记为 `candidate_for_system` |
| 无人引用但个人觉得重要 | 留在 Knowledge。系统原则不能靠"感觉重要"来决定 |
| 曾经是系统但现在过时 | 走 L3 变更，标记 Deprecated，不移回 Knowledge（历史追溯） |

### 7.4 与现有治理的关系

| 概念 | 关系 |
|------|------|
| Asset Lifecycle（§3） | Promotion Criteria 决定知识能否从 Knowledge 层进入 System 层的 Active 状态 |
| Change Control（L1-L3） | 晋升完成后该资产归 L3 管辖（修改需 ADR） |
| Freeze Policy（§5） | 晋升后自动进入 Frozen 状态，不是"先晋升再决定冻不冻" |
| Pilot-Gate v1.1 | 此标准是双闸门治理的补充：Stability Gate 确保系统稳定，Promotion Criteria 确保系统精炼 |
