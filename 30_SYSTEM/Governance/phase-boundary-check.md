# Phase Boundary Check — 阶段边界审查规范

> **来源：** Phase-4 ADR Extraction 执行中发现并修复的治理缺口
> **创建：** 2026-07-16
> **状态：** DRAFT（Phase-4 观察期内验证）
> **关联：** `_RETRACTED-PAIOS-2026-0716-PHASE5-HANDOFF-001`（越界参考）

---

## 1. 背景

Phase-4 ADR Extraction 执行中，Reasonix 生成了一个 Phase-5 Handoff Pocket，
该 Pocket 的内容技术上正确、逻辑上合理，但**治理阶段不匹配**：

- 在 Phase-4（建立认知）阶段提出了 Phase-5（治理决策）的问题
- AI 审查检查了"内容是否正确"，但未检查"这个动作属于当前阶段吗"

此事件暴露了 PAIOS 治理流程中缺少的一层：**Phase Boundary Review**。

---

## 2. 核心原则

> **任何 AI 生成的执行方案，在进入审批前，必须验证其是否越过当前生命周期阶段边界。**

三层验证模型：

```
Layer 1: 内容正确性（现有）
  - 方案是否合理？
  - 是否违反约束？

Layer 2: 阶段边界（新增）
  - 这个动作属于当前 Phase 吗？
  - 是否提前引入了未来阶段的决策？

Layer 3: 人为决策（现有）
  - Evan 最终批准
```

---

## 3. Phase Boundary Check 格式

所有 Pocket 在生成时，应在 YAML 头部增加以下检查块：

```yaml
phase_boundary_review:

  current_phase: "Phase-4-STABILIZE"

  allowed_actions:
    - inventory
    - discovery
    - classification
    - metadata_annotation
    - observation

  denied_actions:
    - migration
    - deletion
    - canonical_selection
    - consolidation
    - restructuring
    - governance_decision
    - phase_transition

  boundary_violation: false

  review_notes: ""
```

---

## 4. 各 Phase 允许/禁止动作矩阵

| 动作 \ Phase | Phase-4 STABILIZE | Phase-5 GOVERNANCE | Phase-6 MIGRATION |
|---|---|---|---|
| inventory | ✅ | ✅ | — |
| discovery | ✅ | ✅ | — |
| classification | ✅ | ✅ | ✅ |
| metadata_annotation | ✅ | ✅ | ✅ |
| observation | ✅ | ✅ | — |
| governance_decision | ❌ | ✅ | — |
| canonical_selection | ❌ | ✅ | — |
| consolidation | ❌ | ⚠️ | ✅ |
| migration | ❌ | ❌ | ✅ |
| deletion | ❌ | ❌ | ⚠️ |
| restructuring | ❌ | ❌ | ⚠️ |

说明：
- ✅ = 允许
- ❌ = 禁止
- ⚠️ = 需 Evan 逐条批准
- — = 不适用

---

## 5. 越界处理流程

当 Phase Boundary Check 检测到越界时：

```yaml
detected:
  action: "Phase-5 Handoff 包含治理决策"
  current_phase: "Phase-4 STABILIZE"
  violated_rules:
    - governance_decision
    - phase_transition

处理步骤:

  1:
    标记 pocket 为越界:
      prefix: "_RETRACTED-"
      status: "BOUNDARY_VIOLATION"

  2:
    保留原文件作为历史审计线索:
      不删除，不改内容

  3:
    记录到 stabilization-log:
      供观察期分析

  4:
    生成替代方案:
      严格限定在 current_phase 允许范围内
```

---

## 6. 执行检查（AI 自检模板）

AI Agent 在生成任何 Pocket 或执行方案前，应执行以下自检：

```yaml
self_check:

  q1: "这个方案修改文件吗？"
  a1: "否/是（仅 90_ARCHIVE）"

  q2: "这个方案删除文件吗？"
  a2: "否"

  q3: "这个方案做治理决策吗？"
  a3: "否（记录发现，不决定归属）"

  q4: "这个方案改变系统结构吗？"
  a4: "否"

  q5: "这个方案属于当前 Phase 的 scope 吗？"
  a5: "是"

  result:
    if all "是/否" 匹配 phase 允许范围:
      → 通过
    else:
      → 标记为 _RETRACTED- 并通知 Evan
```

---

## 7. 本规范的状态

本规范本身在 Phase-4 观察期内提出，不触发任何结构改变。

```yaml
status: DRAFT
phase: Phase-4-STABILIZE
observation_period: 90_days

review_schedule:
  - 30天: 验证检查规则是否足够
  - 60天: 根据观察结果调整矩阵
  - 90天: 决定是否正式纳入 Governance Baseline
```
