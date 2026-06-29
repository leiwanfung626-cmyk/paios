---
title: AI Capability Architecture
status: accepted
related_philosophy: paios-philosophy.md
related_capability: retrieve
related_adr:
  - ADR-0002
created: 2026-06-29
---

# AI Capability Architecture — AI 能力架构

## 概述

本文档详细阐述 PAIOS 的 AI 能力从何而来、如何组织、以及各层之间的关系。它是 `paios-philosophy.md` 中第一性原理在架构层面的具体展开。

## 四层能力模型

PAIOS 的 AI 能力来源于四层，每一层解决不同的问题：

```
┌─────────────────────────────────────────────────┐
│  L1  Foundation Intelligence（基础智能）           │
│  外部大模型：ChatGPT / Claude / Gemini / DeepSeek │
│  职责：推理、写作、编程、分析、总结                │
├─────────────────────────────────────────────────┤
│  L2  Memory（长期记忆）                           │
│  20_KNOWLEDGE 知识库 + 项目上下文 + 历史决策       │
│  职责：提供与你相关的上下文，让 AI 认识你          │
├─────────────────────────────────────────────────┤
│  L3  Decision Rules（决策规则）                    │
│  ADR + Decision Protocol + 决策模板               │
│  职责：约束 AI 的推理方式，按你的思维做决策        │
├─────────────────────────────────────────────────┤
│  L4  Feedback Loop（反馈闭环）                     │
│  复盘记录 + 踩坑日志 + ROI 评估                    │
│  职责：从经验中学习，持续校正，实现复利效应         │
└─────────────────────────────────────────────────┘
```

### 层间依赖

- L1 是基础，没有大模型就没有智能
- L2 建立在 L1 之上，让通用智能变成个人智能
- L3 建立在 L2 之上，不仅知道事实，还知道如何决策
- L4 是闭环，让系统持续变好，而不是原地踏步

**不可跳过任何一层。** 只有 L1+L2 的系统是"搜索+总结"机器；加入 L3 才能做出判断；加入 L4 才能持续进化。

## 五层数据价值体系

系统中的数据按价值分为五个层级，从通用到个人：

| 层级 | 内容 | 来源 | 稳定性 |
|------|------|------|--------|
| **L1 Foundation** | 大模型的预训练知识 | 外部 | 持续更新（模型升级） |
| **L2 Knowledge** | 事实、资料、项目、文档 | 用户沉淀 | 稳定，需维护 |
| **L3 Decision** | ADR、Decision Log、决策协议 | 用户决策 | 长期稳定 |
| **L4 Feedback** | 结果、复盘、踩坑、ROI | 执行反馈 | 持续增长 |
| **L5 Evolution** | 规则修订、流程优化、最佳实践 | 系统自我改进 | 持续演化 |

```
价值
  ▲
  │            L5 Evolution（系统自我改进）
  │          L4 Feedback（经验复利）
  │        L3 Decision（决策约束）
  │      L2 Knowledge（个人上下文）
  │    L1 Foundation（通用智能）
  └──────────────────────────────→ 个性化程度
```

## 系统三大引擎

从能力模型导出三个核心引擎：

### 1. Memory Engine（记忆引擎）

| 维度 | 说明 |
|------|------|
| **职责** | 统一管理长期知识、项目上下文、经验案例的组织与检索 |
| **对应层级** | L2 Knowledge |
| **关键资产** | 20_KNOWLEDGE、10_WORK 归档、知识元数据 |
| **检索演进** | 参见 `Design_Notes/retrieve-evolution.md` |

### 2. Decision Engine（决策引擎）

| 维度 | 说明 |
|------|------|
| **职责** | 统一决策协议、ADR、风险评估、决策模板 |
| **对应层级** | L3 Decision |
| **关键资产** | ADR、Decision Protocol、决策模板、风险评估框架 |
| **核心产出** | 每次决策都有记录、可追溯、可复用 |

### 3. Learning Engine（学习引擎）

| 维度 | 说明 |
|------|------|
| **职责** | 把复盘、反馈、规则修订、成功经验沉淀为系统资产 |
| **对应层级** | L4 Feedback → L5 Evolution |
| **关键资产** | 复盘记录、踩坑日志、ROI 评估、规则修订记录 |
| **核心产出** | 系统持续自我修正，越来越符合用户风格 |

### 引擎关系

```
Memory Engine ──→ 提供上下文
      │
      ▼
Decision Engine ──→ 做出决策
      │
      ▼
Learning Engine ──→ 复盘优化
      │
      └─────────→ 反馈回 Memory & Decision
```

## DRS 演化映射

DRS 时代的核心概念在 PAIOS 架构中的新位置：

| DRS 概念 | PAIOS 架构位置 | 状态 |
|----------|---------------|------|
| 人格画像 | → Decision Profile（决策偏好） | 重构 |
| 思维模型 | → Decision Engine / Workflow Engine | 保留并升级 |
| 价值观 | → Operating Principles（`paios-philosophy.md`） | 保留并升级 |
| 经验知识 | → 20_KNOWLEDGE + Memory Engine | 保留并升级 |
| 行为习惯 | → Decision Preferences（长期主义 / 风险控制 / ROI 优先） | 重构 |
| 数字分身 | → Personal AI Agent（应用层，未来能力） | 未来 |
| 情感模拟 | → ❌ 不纳入核心架构 | 移除 |
| 意识复制 | → ❌ 不纳入核心架构 | 移除 |

## 统一架构

```
                 PAIOS
      （Personal AI Operating System）
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
Memory Engine    Decision Engine    Workflow Engine
    │                  │                  │
知识与经历         决策规则与ADR       自动化执行
    └──────────────────┼──────────────────┘
                       │
                Personal AI Agent
              （决策数字人 — 应用层）
```

在这个架构中：
- **PAIOS** 是操作系统，不依赖任何单一 AI 工具
- **三大引擎** 是内核模块，各司其职
- **Personal AI Agent** 是应用层（未来的数字人）

---

> **关联文档**
> - `Vision/paios-philosophy.md` — 第一性原理
> - `Vision.md` — 长期愿景
> - `Design_Notes/retrieve-evolution.md` — Retrieve Capability 演进
> - `Principles.md` — 九大核心原则
