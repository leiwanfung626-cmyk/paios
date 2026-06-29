---
title: Layer Integrity Map
status: audit
evidence: observed
category: engineering-discovery
layer: L1
layer_status: observation
first_observed: 2026-06-29
related_engineering:
  - engineering/evidence-level-system
  - engineering/requirement-emergence
  - engineering/necessity-gated-architecture
created: 2026-06-29
---

# PAIOS Layer Integrity Map v0.1 — 层级完整性图

> **Status**: Audit — initial observation, not governance rule.
>
> 本图检测 PAIOS 是否发生"层级污染 / 职责漂移 / 权限上浮或下沉"。
> 它不评价好坏，只回答：这个模块应该在哪一层、现在在哪一层、两者是否一致。

---

## Standard Layer Model（标准分层模型）

PAIOS 抽象为 5 层结构：

| Layer | Name | Definition | Contains | Prohibits |
|-------|------|-----------|----------|-----------|
| **L0** | Reality Layer | 不可被系统建模改变的事实源 | 真实问题、失败案例、使用行为、运行日志 | ❌ 规则、抽象设计、推理结构 |
| **L1** | Observation Layer | 对现实的"描述"，不做设计解释 | Migration_Log、行为记录、使用频率、问题现象 | ❌ 原因解释、设计方案 |
| **L2** | Design Layer | 对观察的"可能解决方案空间" | Design Notes、Architecture experiments、Candidates | ❌ 强制规则、治理决策 |
| **L3** | Governance Layer | 系统行为约束规则（强制执行） | Stability Discipline、Need Driven Promotion | 特征：可阻断行为、不可随意修改、必须经过验证周期 |
| **L4** | Execution Layer | 自动化/工具/runtime 行为 | automation scripts、tools、workflows | ❌ 设计决策、治理规则 |

---

## Audit Results（审计结果）

### ADR（架构决策记录）

| Field | Value |
|-------|-------|
| **Current layer** | L1 |
| **Correct layer** | L1 |
| **Verdict** | ✅ Correct — 决策历史，不可替代 |
| **Risk** | 若 ADR 开始记录"推测性设计"，会污染决策源 |

### Migration_Log

| Field | Value |
|-------|-------|
| **Current layer** | L1 |
| **Correct layer** | L1 |
| **Verdict** | ✅ Correct |

### Governance / architecture-governance.md

| Field | Value |
|-------|-------|
| **Current layer** | L3 |
| **Correct layer** | L3 |
| **Verdict** | ✅ Correct |

### Governance / architectural-invariants.md

| Field | Value |
|-------|-------|
| **Current layer** | L3 |
| **Correct layer** | L3 |
| **Verdict** | ✅ Correct |

### Engineering / Evidence_Level_System.md

| Field | Value |
|-------|-------|
| **Content layer** | L3（定义证据等级，属于治理规则） |
| **Physical location** | L2（Engineering/ 是工程发现层） |
| **Verdict** | ⚠️ **Potential mismatch** — L3 content in L2 container |
| **Note** | Engineering Findings 是介于 L1 和 L3 之间的过渡层——观察经过验证后上升为治理规则。当前状态合理，但需要跟踪。 |

### Engineering / Requirement_Emergence.md

| Field | Value |
|-------|-------|
| **Content layer** | L2（设计原则级洞察） |
| **Physical location** | L2 |
| **Verdict** | ✅ Correct |

### _candidates / Stability_Discipline.md

| Field | Value |
|-------|-------|
| **Content layer** | L3（行为约束规则） |
| **Physical location** | L2（_candidates/） |
| **Verdict** | ⚠️ **Layer drift detected** — L3 content in L2 container |
| **Note** | 作为候选合理，但晋升后需迁移至 Governance/ |

### _candidates / Necessity_Gated_Architecture.md

| Field | Value |
|-------|-------|
| **Content layer** | L3（结构准入控制规则） |
| **Physical location** | L2（_candidates/） |
| **Verdict** | ⚠️ **Layer drift detected** — L3 content in L2 container |
| **Note** | 与 Stability Discipline 同为"治理规则候选"，不应在 L2 长期停留 |

### Design_Notes / ai-capability-architecture.md

| Field | Value |
|-------|-------|
| **Content layer** | L2（设计探索） |
| **Physical location** | L2 |
| **Verdict** | ✅ Correct |
| **Risk** | 偶发 L3 语气——部分段落从"设计建议"滑向"设计规范" |

### Design_Notes / retrieve-evolution.md

| Field | Value |
|-------|-------|
| **Content layer** | L2（设计探索） |
| **Physical location** | L2 |
| **Verdict** | ✅ Correct |

---

## Layer Contamination Summary（层级污染总结）

### Detected events

| ID | Type | Source | Target | Severity |
|----|------|--------|--------|----------|
| LC-001 | L2→L3 上浮 | Stability Discipline (_candidates/) | Governance rule | Medium |
| LC-002 | L2→L3 上浮 | Necessity-Gated Architecture (_candidates/) | Governance rule | Medium |
| LC-003 | L2↔L3 边界模糊 | Evidence_Level_System.md (Engineering/) | Governance content in discovery container | Low |
| LC-004 | L1→L2 漂移 | Design_Notes (偶发) | Observation → Design justification | Low |

### Layer Boundary Rule（层级边界规则）

基于审计发现，以下规则应在运行周期验证后强制执行：

```
L3 只能接受已验证设计（evidence ≥ validated-by-engineering-practice）
L2 不能包含治理规则的强制执行逻辑
_candidates/ 不能成为准治理层
L1 不能包含设计意图
```

---

## Layer Tag Registry

每个模块的标准 layer tag 值：

| Tag | Meaning | Applies to |
|-----|---------|------------|
| `layer: L0` | Reality fact | raw logs, failure records |
| `layer: L1` | Observation record | Migration_Log, ADR |
| `layer: L2` | Design exploration | Design_Notes, _candidates, Engineering Findings |
| `layer: L3` | Governance rule | Principles, Governance/, validated Engineering Findings |
| `layer: L4` | Execution | automation scripts, workflows |

### layer_status values

| Value | Meaning |
|-------|---------|
| `active` | In correct layer, actively used |
| `candidate` | Intended for higher layer, awaiting validation |
| `observation` | Audit record, no enforcement intent |

---

## Necessity Impact Observations（必要性影响观察）

> ⚠️ 观察和裁决必须分离。
> 当前仅为观察记录，不构成任何 freeze/downgrade 动作。
> 实际处置需等待 Necessity-Gated Principle 完成验证成为正式治理规则后执行。

### 处理原则

- **现在**：仅记录影响观察，不做结构变更
- **未来**：如需处置，由 Necessity 驱动，非时间驱动

### OBS-001: Stability Discipline L2→L3 上浮

| Field | Value |
|-------|-------|
| **Type** | layer mismatch: content is governance-level, located in L2 container |
| **If Necessity-Gated becomes active** | likely affected — would need to either validate or demote |
| **Current status** | `layer: L3, layer_status: candidate` (already tagged) |
| **Observation** | 内容属治理规则，但所在位置（_candidates/）正确。晋升路径已通过 layer_status: candidate 标记。 |

### OBS-002: Necessity-Gated Architecture L2→L3 上浮

| Field | Value |
|-------|-------|
| **Type** | governance premature promotion |
| **If Necessity-Gated becomes active** | likely affected — self-consistency issue: a principle governing structure admission is itself unvalidated |
| **Current status** | `layer: L3, layer_status: candidate` (already tagged) |
| **Observation** | 作为待验证原则存在于 _candidates/ 中正确。晋升 Governance 层前需经过完整运行周期。 |

### OBS-003: Evidence_Level_System L2↔L3 边界模糊

| Field | Value |
|-------|-------|
| **Type** | documentation contamination |
| **If Necessity-Gated becomes active** | unlikely affected — pure classification system, no enforcement logic |
| **Current status** | `layer: L2, layer_status: active` |
| **Observation** | 当前状态合理。约束：不可加入强制执行逻辑。 |

### OBS-004: Design_Notes L1→L2 漂移

| Field | Value |
|-------|-------|
| **Type** | observation → design drift |
| **If Necessity-Gated becomes active** | low impact — occasional stylistic issue, not structural |
| **Current status** | no tag applied (Design_Notes not in Engineering/ scope) |
| **Observation** | 偶发现象，长期可关注。当前不需要结构变更。 |

---

## Timing as Observational Metadata（时间作为观测元数据）

> ⚠️ 时间周期是观测参考，不是治理门控（gate）。
> 决策的唯一依据是 Necessity，而非时间。

### 优先级顺序

```
Necessity（必要性）
  > Layer Integrity（层级完整性）
    > Stability（稳定性）
      > Timing（时间）
```

### 当前观测状态（非治理规则）

```
t0 观测点
  ├── Necessity tagging 完成 ✅
  ├── layer tags 应用完成 ✅
  └── Necessity Impact Observations 完成 ✅

t0 + 1 cycle 观测点（预计 ~90 天后）
  ├── 行为观察：哪些 LC 模式稳定重复？
  ├── 标记修正：基于观测数据调整分类
  ├── 影响评估（由 Necessity 驱动，非时间驱动）
  └── 候选原则晋升评估（由 Evidence 驱动，非时间驱动）

t0 + 2 cycles 观测点
  └── 治理收敛评估
```

### 约束规则

1. **时间只是 metadata，不是 gate** — 到达观测点不自动触发任何行动
2. **Necessity > Timing** — 如果 Necessity 触发，可以在任意时间点行动；如果未触发，到达观测点也不行动
3. **不可形成无限延迟闭环** — 如果到达观测点且 Necessity 条件满足，必须执行评估，不可自动延期

---

**Related**: `_candidates/Necessity_Gated_Architecture.md` | `_candidates/Stability_Discipline.md` | `engineering/evidence-level-system` | `engineering/layer-integrity-map`
