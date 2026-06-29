---
title: Necessity-Gated Architecture Principle
status: proposed
evidence: observed
confidence: high
category: engineering-candidate
layer: L3
layer_status: candidate
positioning: high-level structural admission control rule
validation_window: one-full-operational-cycle
first_observed: 2026-06-29
related_principles:
  - Stability Discipline
  - Need Driven Promotion
related_engineering:
  - engineering/evidence-level-system
  - engineering/stability-discipline
created: 2026-06-29
---

# Necessity-Gated Architecture Principle — 必要性门控架构原则（候选）

> **Status**: Candidate — observed, not yet validated by engineering practice.
> **Confidence**: High — complete operational spec, but uncycled.
>
> 本条记录是高质量待验证核心规则，在经历至少一个完整运行周期后重新评估是否晋级。

---

## 1. 原则定义

PAIOS 系统中的任何结构扩展（包括但不限于：模块、子系统、抽象层、流程节点、规则、自动化机制），**必须以现实可验证需求为唯一触发条件**。

系统禁止基于推测性价值或理论完备性进行结构扩展。

---

## 2. 强制约束（Hard Constraints）

以下行为在 PAIOS 中被明确禁止：

- 禁止基于"未来可能需要"添加结构
- 禁止基于 AI 推断的潜在需求进行架构扩展
- 禁止为提高"系统完整性"或"通用性"而引入抽象层
- 禁止无实际运行路径支撑的模块设计
- 禁止在无真实使用场景下进行流程预设

---

## 3. 结构引入判定标准（Admission Criteria）

任何新增结构必须同时满足以下四项条件：

### 3.1 现实触发（Reality Trigger）

必须存在以下任一证据：

- 已发生的具体问题或失败案例
- 已观察到的重复性操作成本
- 已执行流程中的明确缺口

### 3.2 现有系统不可替代性（Non-Substitutability）

新增功能必须证明：

- 不能通过修改现有结构解决
- 或修改现有结构的代价显著高于新增

### 3.3 可验证收益（Verifiable Benefit）

新增结构必须定义至少一个：

- 可度量效率提升
- 可降低错误率或复杂度
- 可减少重复劳动

### 3.4 非推测性（Anti-Speculation Constraint）

明确禁止以下作为理由：

- "未来扩展可能需要"
- "为了通用性/兼容性"
- "AI 认为应该有"
- "理论上更优"

---

## 4. 审查机制（Architecture Admission Review）

所有新增结构必须通过以下流程：

1. **需求来源声明**
   - 必须引用具体行为或记录，而非假设

2. **替代方案说明**
   - 必须说明为何现有结构无法覆盖

3. **收益证明**
   - 必须说明具体改善指标或行为变化

4. **最小化设计原则检查**
   - 是否可以更简单实现同等效果

---

## 5. 最小结构原则（Minimal Structural Footprint）

在所有满足条件的设计中，应优先选择：

- 最少抽象层
- 最少新概念引入
- 最少跨模块依赖
- 最少运行路径复杂度

---

## 6. 系统哲学约束（Core Doctrine）

> PAIOS is a usage-driven system, not a design-driven system.
> Structure must emerge from observed necessity, not anticipated possibility.

工程化表达：

> **No observed demand → No structural existence.**

---

## 7. 违规处理（Violation Handling）

若发现违反本原则的结构：

- 标记为 **Speculative Artifact（推测性结构）**
- 不进入核心系统
- 优先进入 Legacy / Candidate 状态
- 在下一轮架构评审中必须重新论证存在性

---

## 8. Negative Case Log（反例日志）

所有被拒绝的结构提案必须记录 rejection reason，用于反向校准规则阈值。

### 记录格式

| 字段 | 说明 |
|------|------|
| **提案名称** | 被拒绝的结构提案名称 |
| **时间** | 拒绝日期 |
| **结构类型** | 模块 / 抽象层 / 流程节点 / 规则 / 自动化机制 |
| **拒绝原因** | 触发了哪条 Admission Criteria |
| **后续处理** | 是否通过替代方案解决 |

### 审查周期

系统应定期审查 Negative Case Log，识别以下模式：

- 某条 Admission Criteria 过于严格 → 适当放宽阈值
- 某类结构频繁被拒 → 表明需要系统级而非局部改进
- 被拒提案通过替代方案解决 → 验证规则的校准效果

---

## Minimum Promotion Criteria

满足以下最低条件后，可获得 Engineering Evidence Review 资格：

1. **至少 1 个**因遵守本原则而避免的不必要结构扩展案例
2. **无**因遵守本原则而导致的重大功能延误
3. Negative Case Log 中至少有 3 条记录（表明审查机制实际运转过）

> ⚠️ 满足最低条件并不自动晋升，仍需经过 Engineering Evidence Review。
> 评审通过后状态变更为 `validated-by-engineering-practice`。

---

**Related**: `engineering/evidence-level-system` | `engineering/stability-discipline` | `ADR-0010-Evolution-Strategy`
