# PAIOS 技术白皮书 v1.0 — 治理体系

> **来源**：`architecture-governance.md` + `architectural-invariants.md`

## 6.1 治理架构概览

PAIOS 治理体系由三层构成：

```
┌────────────────────────────────────┐
│  Architectural Invariants（约束层）  │  ← 5条不可违反的系统约束
├────────────────────────────────────┤
│  Governance Framework（规范层）     │  ← Impact Levels + Review Process
├────────────────────────────────────┤
│  Freeze Policy（冻结策略）          │  ← 当前：ADR-0002（90天冻结）
└────────────────────────────────────┘
```

## 6.2 五大架构不变量（Invariants）

| # | Invariant | 含义 | 违反后果 |
|---|-----------|------|---------|
| 1 | **Vision 高于一切实现** | 所有实现必须能追溯到 Vision | 直接驳回 |
| 2 | **实现必须可追溯到 Principle** | 每个实现关联至少一条 Principle | 不可接受 |
| 3 | **平台不依赖任何特定 AI 模型** | 开放格式，工具无关 | 违反 Principle #8 |
| 4 | **知识与自动化解耦** | 20_KNOWLEDGE 不包含自动化逻辑 | 架构污染 |
| 5 | **重大架构调整必须留下 ADR** | 新增目录/修改生命周期必须 ADR | 治理失效 |

## 6.3 Impact Levels（变更影响分级）

每次变更按**影响最大的资产**定级（Highest Impact Wins）：

| Level | 名称 | 定义 | 审查要求 | 示例 |
|-------|------|------|----------|------|
| **L0** | Documentation | 不影响系统行为的文档变更 | 无审查 | 修正拼写、补充注释 |
| **L1** | Configuration | 只影响配置，不改变行为逻辑 | Review 即可 | 修改 metadata.yaml |
| **L2** | Behavior | 改变 Workflow、Agent、Prompt 的行为 | 架构 Review | 新增 Script、修改 Workflow |
| **L3** | Architecture | 改变目录、生命周期、Engine 定义 | **必须 ADR** | 新增一级目录、修改 Engine |
| **L4** | Philosophy | 改变 Vision、Principle、Invariant | **重大评审 + ADR** | 修改 Invariant、修改 Philosophy |

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

## 6.4 Asset Lifecycle（资产生命周期）

适用于所有系统资产：ADR、Principle、Design Note、Workflow、Agent、Capability 等。

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

## 6.5 审查流程（Review Process）

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

## 6.6 当前冻结策略

| 冻结 | 范围 | 期限 | 解冻条件 |
|------|------|------|---------|
| ADR-0001 | Core API | 90天 | 技术缺陷/需求不满足/显著降低成本 |
| ADR-0002 | Automation Platform 目录结构 | 90天（至2026-09-29） | 同上 |

**核心规则**：不可因为"更优雅"而解冻。

---

**关联文档**：[05_Decision_Layer.md](05_Decision_Layer.md) | [07_Automation.md](07_Automation.md) | `architecture-governance.md` | `architectural-invariants.md` | `ADR-0007-Governance-Model`
