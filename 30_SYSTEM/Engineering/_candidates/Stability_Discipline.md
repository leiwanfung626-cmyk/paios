---
title: Stability Discipline
status: proposed
evidence: observed
category: engineering-candidate
layer: L3
layer_status: candidate
first_observed: 2026-06-29
related_principles:
  - Requirement Emergence
  - Need Driven Promotion
related_engineering:
  - engineering/evidence-level-system
  - engineering/requirement-emergence
validation_target:
  - Complete at least one full operational cycle
  - Record modification decisions deferred by the discipline
  - Evaluate impact on system stability vs. missed opportunities
  - Conduct evidence review before promoting
created: 2026-06-29
---

# Stability Discipline — 稳定性纪律（候选）

> **Status**: Candidate — observed, not yet validated by engineering practice.
>
> 本条记录不是正式 Engineering Finding，而是一个被观察到但尚未经验证的工程假设。
> 它将在经历至少一个完整运行周期后重新评估是否晋级。

---

## Hypothesis（假设）

> **在没有新的工程证据之前，不因为新的想法而修改系统。**

## Rationale（推理性据）

这条假设基于 Requirement Emergence 的推论：

- 如果需求是在迭代中涌现的（Requirement Emergence）
- 那么新想法本质上是未经验证的需求假设
- 在没有真实使用证据之前，不应该因为假设而修改系统

## Current Evidence（当前证据等级：observed）

目前仅有：

- 这是一个逻辑上合理的推论
- 它与已有原则（Need Driven Promotion、Architecture Freeze）方向一致
- 双方（提出者与审阅者）都认为它合理

**缺少的证据：**

- ❌ 没有经历一个完整运行周期
- ❌ 没有因违反这条纪律而踩坑的案例
- ❌ 没有因遵守这条纪律而受益的案例
- ❌ 没有多个独立案例支持

## Validation Plan（验证计划）

| 条件 | 验证方法 |
|------|---------|
| 完成一个完整运行周期 | 系统持续运行至少一个周期（当前：约 90 天） |
| 记录被纪律推迟的修改 | 维护 Decision Log，标记 `deferred-by-stability-discipline` |
| 评估对系统稳定性的影响 | 回顾被推迟的修改：哪些后来证明是不必要的，哪些错过了 |
| 评估是否错过了紧急修改 | 检查是否有应该立即修改却被纪律延误的 case |

## Minimum Promotion Criteria（最低晋升条件）

满足以下最低条件后，可获得 Engineering Evidence Review 资格：

1. **至少 2 个**因遵守纪律而避免的不必要修改案例
2. **无**因遵守纪律而导致的重大延误或损失
3. 系统稳定性有可观察的提升

> ⚠️ **满足最低条件并不自动晋升**，仍需经过 Engineering Evidence Review。
> 评审通过后状态变更为 `validated-by-engineering-practice`。
>
> 注意：不同 Candidate 的晋升标准可能不同。
> 例如 Requirement Emergence 需要多轮开发和案例支持，
> 而某个 Automation Principle 可能需要实际部署和性能数据。
> Minimum Promotion Criteria 允许按文档定义，不强制统一标准。

---

**Related**: `engineering/evidence-level-system` — 证据等级体系定义了本候选文档的晋级路径
