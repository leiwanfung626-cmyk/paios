# ADR-0009: 治理模型（Governance Model）

## Status
Accepted

---

## Context
PAIOS 需要正式治理框架来规范所有变更，确保系统在长期演化过程中保持一致性、可追溯性和可维护性。

---

## Decision
建立三层治理体系：

```
┌────────────────────────────────────┐
│  Architectural Invariants（约束层）  │  ← 5条不可违反的系统约束
├────────────────────────────────────┤
│  Governance Framework（规范层）     │  ← Impact Levels + Review Process
├────────────────────────────────────┤
│  Freeze Policy（冻结策略）          │  ← 当前：ADR-0002（90天冻结）
└────────────────────────────────────┘
```

### Impact Levels（变更影响分级）

| Level | 名称 | 审查要求 | 示例 |
|-------|------|---------|------|
| L0 | Documentation | 无审查 | 修正拼写 |
| L1 | Configuration | Review | 修改 metadata.yaml |
| L2 | Behavior | 架构 Review | 新增 Script |
| L3 | Architecture | **必须 ADR** | 新增目录 |
| L4 | Philosophy | 重大评审 + ADR | 修改 Invariant |

### Governance 1.0 范围

| 包含 | 不包含 |
|------|--------|
| ✅ 变更分级标准 | ❌ 自动化审查脚本 |
| ✅ 审查流程定义 | ❌ PR Checklist 工具 |
| ✅ Asset Lifecycle | ❌ 目录结构校验 |
| ✅ Freeze Policy | ❌ ADR 模板自动校验 |

---

## Rationale
- Invariants 设底线（不可违反），Governance 定流程（按级审查），Freeze Policy 控制节奏（何时不可改）
- Governance 1.0 只建立规范层，不引入任何自动化，避免过早工具化
- Highest Impact Wins 原则简化定级决策

---

## Consequences
### Positive
- 变更有清晰的分级和流程
- 三权分立防止单一机制失效

### Negative
- L2+ 变更增加了前置评审成本
- 短期内治理流程可能感觉"重"

---

## Alternatives Considered
- **无正式治理** — 系统在长期演化中必然退化
- **纯自动化治理** — 过度工程化，不适合 Governance 1.0 阶段
- **单层治理** — 约束、规范、冻结混在一起，权责不清

---

## Related
- ADR-0007: Lifecycle Model
- Invariant #5: Major architectural changes require ADR
- `architecture-governance.md`
- `architectural-invariants.md`
