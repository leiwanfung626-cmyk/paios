---
title: Requirement Emergence
status: validated-by-engineering-practice
category: engineering-discovery
layer: L2
layer_status: active
first_observed: 2026-06-29
validated_by: PAIOS Platform v1.0.0 — whitepaper delivery iteration (Markdown → docx, 3 rounds)
related_principles:
  - Need Driven Promotion
  - Bootstrap First
related_adr:
  - ADR-0010 (Evolution Strategy)
related_engineering:
  - Evidence_Level_System.md
created: 2026-06-29
---

# Requirement Emergence — 需求涌现原则

> **PAIOS Original Engineering Finding**
>
> 本条原则不是外部理论引用，而是在 PAIOS 实际开发过程中通过反复迭代总结出的工程发现。

---

## Status

**Validated by Engineering Practice**

本条原则已经过 PAIOS Platform v1.0.0 的完整开发循环验证，属于经过工程实践检验的设计原则。

---

## Background

在 PAIOS 白皮书从 Markdown 到 Word 的交付过程中，观察到以下现象：

1. **最初的需求**：将标准的 ADR + Whitepaper 结构映射到本地系统
2. **第一次实现**：生成了完整的 Markdown 内容并在对话中交付
3. **反馈**：需要 Word 格式
4. **第二次实现**：生成了 .docx 文件
5. **反馈**：文档内容为空
6. **第三次实现**：诊断发现脚本 bug，重新生成
7. **最终结果**：56KB 完整白皮书，262 段内容，70 张表格

**真正发生变化的不只是输出格式，而是需求定义本身。**

最初的"映射文档结构"在迭代中逐渐展开为：审计现有结构 → 生成白皮书内容 → 生成 ADR 补充 → 输出 Word → 修复空白文档 → 验证内容完整性。

每一次反馈都在修正"到底要什么"这个问题的答案。

---

## Discovery Process

### 触发信号

以下重复出现的模式触发了对这条规律的识别：

| 模式 | 表现 | 频率 |
|------|------|------|
| **需求偏移** | 开始时要 A，做出来发现其实需要 B | 每次迭代 |
| **隐性需求** | 看到中间结果后才意识到"原来我要的是这个" | 循环出现 |
| **标准答案偏差** | 用户最初描述的需求往往不是最终的真实需求 | 规律性 |
| **反馈驱动澄清** | 每次反馈都在缩小问题定义的范围 | 持续 |

### 形成过程

```
阶段一：观察到现象
  "为什么每次用户看到中间结果后都会修改需求？"
    ↓
阶段二：识别模式
  这不是需求分析不足，而是复杂知识工作的固有特征
    ↓
阶段三：提炼为原则
  需求不是输入（Input），而是迭代的产物（Output）
    ↓
阶段四：用 PAIOS 自身演化验证
  知识库 → Prompt → 规则 → Workflow → Governance → Decision Layer
  每一步都是在前一步的产出上发现了更深层的真实需求
```

---

## Principle Statement

> **在复杂知识工作中，用户需求通常不会在任务开始时完整存在。**
>
> 开始时存在的只是一个方向、一种不满意、一个模糊目标。
>
> 真正的需求是在不断看到中间成果后逐步显现的。

PAIOS 不将需求视为固定输入，而将需求收敛作为工作流的重要目标之一。

---

## Dual-Loop Model

```text
┌─────────────────────────────────────────────────┐
│             循环一：修正需求（核心循环）            │
│                                                   │
│  模糊想法                                          │
│      ↓                                            │
│  第一次实现                                        │
│      ↓                                            │
│  看到结果                                          │
│      ↓                                            │
│  发现真正的问题 ←──── 这条最重要                    │
│      ↓                                            │
│  重新定义需求                                      │
│      ↓                                            │
│  再次实现                                          │
│      ↓                                            │
│  真实需求逐渐收敛                                   │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│             循环二：修正实现（传统认知）            │
│                                                   │
│  已知需求                                          │
│      ↓                                            │
│  方案设计                                          │
│      ↓                                            │
│  实现                                              │
│      ↓                                            │
│  验证                                              │
│      ↓                                            │
│  Bug 修复                                          │
│      ↓                                            │
│  完成                                              │
└─────────────────────────────────────────────────┘
```

**很多项目失败，不是实现不好，而是一直在优化一个尚未定义清楚的问题。**

循环一的代价远高于循环二——如果需求定义错了，再多的实现优化都没有意义。

---

## Relation to Need Driven Promotion

| 原则 | 类别 | 关注点 | 回答的问题 |
|------|------|--------|-----------|
| **Need Driven Promotion** | 功能演化原则 | 什么时候应该增加功能 | Feature timing |
| **Requirement Emergence** | 需求发现原则 | 需求是如何形成的 | Need discovery |

两者互补而非重叠：

- Need Driven Promotion 控制**系统的演化速度**——不预判需求，不提前引入复杂度
- Requirement Emergence 解释**需求的形成方式**——需求在迭代中逐步显现

共同构成 PAIOS 在需求管理上的核心工程经验。

---

## System Design Implications

### 1. 对 Workflow 的影响

工作流不应假设"需求 → 分析 → 实现 → 完成"的线性模型。应预留需求澄清和重定义的环节。

### 2. 对 Decision Layer 的影响

Decision Layer 的首要职责不是选择方案，而是**帮助用户发现真正的需求**。这通过持续的 Intent Analysis 和 Verification Feedback 实现。

### 3. 对 Learning Engine 的影响

Feedback 的最大价值不是修正实现（修 Bug），而是**不断修正 Problem Definition**。Learning Engine 应追踪"问题定义的变化"，而非仅追踪"错误率的变化"。

### 4. 对 Prototype 策略的影响

Prototype 的用途不是验证方案的正确性，而是**帮助需求收敛**。一个"失败"的原型如果帮助用户澄清了真实需求，就不是失败。

### 5. 对 Governance 的影响

变更的影响评估（Impact Level）应考虑需求定义的变动成本，而不仅是实现变动的成本。

---

## Validation Evidence

PAIOS 自身的演化路径验证了这一原则：

```text
想做知识库
    ↓
需要统一 Prompt
    ↓
需要统一规则
    ↓
需要 Workflow
    ↓
需要 Governance
    ↓
需要 Decision Layer
```

每一步都不是预先规划的。

每一步都是在前一步的产出上，发现了一个之前不知道存在的真实需求。

这正是 Requirement Emergence 的工程证据。

---

## Related

- `Principles.md` — Requirement Emergence Principle
- `ADR-0010-Evolution-Strategy.md` — Need Driven Promotion
- `Design_Notes/ai-capability-architecture.md` — Decision Layer
- `Vision/02_Principles.md` — 白皮书设计原则章节
