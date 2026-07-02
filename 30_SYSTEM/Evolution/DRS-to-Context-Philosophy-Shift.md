---
title: "From DRS to Context — PAIOS 核心理念转向"
type: philosophy-milestone
phase: ideation-to-architecture
date: 2026-07-02
related:
  - ADR-0010-Evolution-Strategy.md
  - Vision/paios-philosophy.md
  - Vision/01_Background.md
  - Vision/08_Evolution_Model.md
---

# Evolution Note: 从 DRS 到 Context

## 背景

PAIOS 早期曾探索过 DRS（数字人）方向，希望通过沉淀开发者的知识、经验和决策方式，构建能够长期协助用户的个人 AI 助手。

随着系统不断实践，这一方向逐渐被放弃，并最终从正式架构中移除。

## 关键认识

实践证明，PAIOS 的长期价值并不在于"复制一个人"，而在于"构建一个任何 AI 都能理解的工作环境"。

真正需要沉淀的不是开发者的人格，而是：

- 稳定的 Context
- 可验证的知识
- 清晰的工作流程
- 可追溯的架构决策
- 可复用的方法论

AI 不需要成为开发者，只需要能够基于相同的 Context 做出一致、可解释的协作。

## 为什么这是 Evolution 而非 ADR

这不是一次具体的架构决策（ADR），也不是某个模块的设计说明，而是**产品理念演进的里程碑**。几年后再回头看，这会解释后来很多为什么做减法、为什么强调 Context、为什么不再追求数字人的原因。

## 架构影响

这一认识推动了 PAIOS 的整体收敛：

- DRS 相关设计逐步退出正式架构
- 系统重心从 Persona 转向 Context
- 从依赖个人经验，转向依赖治理机制（ADR、Freeze、Impact、Knowledge Trust 等）
- 产品定位由"复制开发者"演化为"增强使用者"

## 意义

这是 PAIOS 发展过程中的一次重要哲学转向。

它标志着系统从"以人为中心的 AI"演化为"以 Context 为中心的 AI 协作框架"。

这一转变也奠定了后续 Architecture、Governance、Knowledge 等模块的发展方向，使 PAIOS 逐渐形成了 **"Context > Model"** 的核心理念。

---

**Location Rationale**: 放置在 `30_SYSTEM/Evolution/` 而非 `ADR/`，因为这不是可撤销或重新评估的架构决策，而是定义系统身份的理念里程碑。它解释的是"为什么系统是这样"，而不是"系统做了哪个选择"。
