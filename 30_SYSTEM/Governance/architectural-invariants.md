---
title: Architectural Invariants
status: active
related_governance: architecture-governance.md
related_philosophy: paios-philosophy.md
related_adr:
  - ADR-0002
created: 2026-06-29
---

# Architectural Invariants — 架构不变量

> **Architectural Invariants 是不可违反的系统约束（constraints），而不是设计原则（principles）。**
>
> Principles 指导设计——告诉你应该往哪个方向走。
> Invariants 限制设计——告诉你绝对不能跨过哪条线。
>
> 任何提案、评审、实施，若违反任一条 Invariant，必须直接驳回。

## Invariant 1：Vision 高于一切实现

所有实现决策必须能追溯到 PAIOS 的 Vision（`paios-philosophy.md` 或 `Vision.md`）。
如果一个功能无法回答"它为什么符合 PAIOS 的定位"，则不应引入。

## Invariant 2：实现必须可追溯到 Principle

任何实现——Capability、Agent、Script、Workflow——都必须能明确定位到 `Principles.md` 中的至少一条。
如果一个实现违反某条 Principle，则不可接受。
如果一个实现不关联任何 Principle，则说明缺乏必要性。

## Invariant 3：平台不依赖任何特定 AI 模型

PAIOS 的所有资产（文档、配置、脚本、规则）必须使用开放格式（Markdown、YAML、JSON、标准 Python）。
不得锁定于某一 AI 工具或模型的私有格式。
更换 AI 模型或工具不应要求重建平台资产。
（源自 Principle #8 —— Tool Independence）

## Invariant 4：知识与自动化解耦

`20_KNOWLEDGE` 只存放经过验证的领域知识。
`40_AUTOMATION` 只存放工作流、脚本、Agent 定义。
知识不得包含自动化逻辑。
自动化的输出产物（索引、缓存、向量库）不得进入知识库。
（源自 Principle #4, #5）

## Invariant 5：重大架构调整必须留下 ADR

以下变更必须出具 ADR：
- 新增或删除一级目录
- 修改生命周期定义
- 修改本文件（Invariants）
- 修改 `Principles.md`
- 修改 Governance 流程
- 修改 Asset Lifecycle 定义

轻微变更（新增 Design Note、注册新 Capability、添加新 Script）无需 ADR，但应遵循 `architecture-governance.md` 中的 Impact Level 分级流程。

---

## 修改本文件的条件

修改 Architectural Invariants 属于 **Impact Level L4**（参见 `architecture-governance.md`），必须：
1. 出具 ADR，说明为什么需要修改以及修改后的影响
2. 说明修改后是否与现有系统兼容
3. 获得架构评审通过

---

> **关联文档**
> - `architecture-governance.md` — 治理流程与 Impact Levels
> - `paios-philosophy.md` — 第一性原理
> - `Principles.md` — 九大核心原则
> - `ADR-0002` — Automation Platform Freeze
