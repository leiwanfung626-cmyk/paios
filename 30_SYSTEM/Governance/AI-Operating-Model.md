---
title: "AI Operating Model — AI 舰队运行模型"
status: Active
created: 2026-07-12
supersedes: AI-Fleet-Governance.md（合并了多引擎任务继承 + AI 角色分工）
related:
  - ../ADR/ADR-0019-AI-Engine-Role-Model.md
  - ../ADR/ADR-0018-Multi-Instance-Role-Model.md
  - ../ADR/ADR-0017-Platform-Purity-Physical-Separation.md
  - ../Specifications/Asset-Class.md
  - Proposal-Template.md
  - Operating-Model.md
---

# AI Operating Model（AI 舰队运行模型）

> **PAIOS 治理体系的 AI 维度顶层文档。**
>
> 与 `Operating-Model.md`（Human Operating Model）平行——一个定义人如何协作，一个定义 AI 如何协作。
>
> 将两套独立发展的设计合并为统一模型：
>
> - **多引擎任务继承**（工作如何在引擎间连续不中断）
> - **AI 引擎角色分工**（每个引擎承担什么职责）
>
> 两者合并后，回答的是：**一个 Task 在 AI Fleet 中如何流动。**

---

## 1. 核心概念

### 1.1 什么是 AI Fleet？

AI Fleet 是 PAIOS 所有可用 AI 引擎的集合。每个引擎注册时需声明：

```
Engine Registry
    ├── Engine Identity（引擎身份：名称、版本、接口）
    ├── Engine Role（承担的角色）
    ├── Capability（能力清单）
    └── Access Scope（可访问的目录/文件范围）
```

### 1.2 三层结构

```
AI Operating Model
    ├── Layer 1: Static Role（静态角色定义）
    │   └── 谁负责什么
    ├── Layer 2: Task Routing（动态任务路由）
    │   └── 一个 Task 如何流动
    └── Layer 3: Structured Communication（结构化通信）
        └── AI 之间如何高效传递信息
```

---

## 2. Layer 1: 静态角色（Engine Role）

### 2.1 角色表

| 角色 | 职责 | 当前引擎 | 可替换 |
|------|------|----------|--------|
| **Architect** | 需求讨论、可行性分析、方案设计、Proposal 输出 | ChatGPT Web | Claude / Gemini |
| **Developer** | 编码、重构、ADR 修改、脚本开发、文档更新 | Reasonix | Claude Code / Codex CLI |
| **Executor** | 确定任务的执行落地：文件操作、数据处理、方案产出 | WorkBuddy | 自动脚本 / API |
| **Architecture Reviewer** | 架构一致性 Review、是否偏离 Proposal、过度设计检查 | ChatGPT Web | Claude / Gemini |
| **Code Reviewer** | 代码规范、安全审查、测试覆盖、重构建议 | Codex | 其他 Review 引擎 |
| **Auditor** | 第三方视角、独立审计、整体合理性、可维护性风险 | CloudCore | 其他审计引擎 |

### 2.2 核心原则

| 原则 | 含义 |
|------|------|
| **Engine may change. Role remains.** | 角色是平台定义，引擎是工具选择 |
| **AI 引擎不拥有平台权限，只拥有角色权限** | 不是"Reasonix 能改 PAIOS"，而是"Developer Role 有修改权限" |
| **AI 负责专业意见，人负责最终决策** | 任何 AI 的输出都须经 Case-01 Maintainer 批准才进入 Core |
| **工具独立（Principle #8）** | 更换引擎不应重构平台资产 |

### 2.3 职责边界

| 引擎 | 做 | 不做 |
|------|----|------|
| WorkBuddy | 执行确定的任务、文件操作、脚本运行 | 修改 PAIOS 架构、治理原则、Core 设计 |
| Reasonix | 架构设计、编码、Git、ADR 实现 | 独立决策——必须经 Architect Review |
| ChatGPT Web | 架构讨论、方案评审、风险识别 | 直接执行文件操作 |
| Codex | 代码审查、安全规范、测试建议 | 开发新功能 |
| CloudCore | 独立审查、整体评估 | 参与设计与开发 |

---

## 3. Layer 2: 动态任务路由（Task Routing）

### 3.1 标准任务流

```
WorkBuddy（Executor）
  日常执行 -> 产生新想法
        |
        v
ChatGPT（Architect）
  需求讨论 -> 可行性分析 -> 输出 Proposal
        |
        v
Reasonix（Developer）
  按 Proposal 实现 -> 编码/重构/ADR
        |
        v
ChatGPT（Architecture Reviewer）
  架构一致性 Review -> 是否偏离 Proposal
        |
    +---+---+
    |       |
  需要修改  通过
    |       |
返回 Dev    v
         Codex（Code Reviewer）
         代码审查 -> 测试建议
              |
              v
         CloudCore（Auditor）
         独立审计 -> 整体合理性
              |
              v
         Case-01 Maintainer
         最终决策 -> Merge / Reject / Rework
              |
              v
          发布 Release
```

### 3.2 三层 Review 体系

Review 按职责层级分为三层，分别由不同引擎承担：

| Review 类型 | 职责 | 承担引擎 | 时机 |
|-------------|------|----------|------|
| **Architecture Review** | 架构一致性、是否偏离 Proposal、过度设计检查 | ChatGPT Web | 开发完成后 |
| **Code Review** | 代码规范、安全审查、测试覆盖、重构建议 | Codex | 架构 Review 通过后 |
| **Independent Audit** | 第三方视角、整体合理性、可维护性风险 | CloudCore | 与 Code Review 并行 |

**原则**：Architecture Review 和 Code Review 可以并行或串行，但 Independent Audit 必须与开发引擎分离——不能自己审自己。

### 3.3 任务路由规则

| 步 | 路由 | 触发条件 |
|----|------|----------|
| 1 | Executor -> Architect | 执行中产生需架构决策的问题 |
| 2 | Architect -> Developer | Proposal 完成，方向确认 |
| 3 | Developer -> Architecture Reviewer | 实现完成，需验证架构一致性 |
| 4 | Architecture Reviewer -> Developer | Review 发现偏离 |
| 5 | Architecture Reviewer -> Code Reviewer | 架构验证通过 |
| 6 | Code Reviewer + Auditor | 代码审查 + 独立审计并行 |
| 7 | All -> Maintainer | 全部通过，需最终决策 |

### 3.4 终止条件（Termination Condition）

```
Maximum Review Iterations = 3
```

Architecture Review 最多可返回 Developer 修改 **3 次**。超过后自动进入：

```
        Maintainer Decision
        +---+---+---+
        |       |       |
      接受    延期    放弃
```

**目的**：防止 AI 在 Architect 和 Developer 之间无限循环。

### 3.5 上下文继承（Context Handover）

Task 在引擎间流转时，必须携带版本化的 Task Context Packet：

```
context_packet:
  version: 1.0                    # 版本号，支持向后演进
  task_id: "TASK-001"             # 任务唯一标识
  origin: "Case-01 x ChatGPT"     # 发起者：Human x Engine
  proposal: "proposals/xxx.md"    # 关联 Proposal 路径
  current_state: "discussion"     # 当前状态: discussion/development/review/audit
  artifacts: []                   # 已产生的文件/代码/文档清单
  decision_log: []                # 关键决策记录 [{time, who, what}]
  next_step: "..."                # 下一步应由谁做什么
```

**版本演进**：

| 版本 | 新增字段 | 说明 |
|------|----------|------|
| 1.0 | 当前 7 字段 | 初始版本 |
| 1.1（预留） | risk, evidence | 风险评估、证据引用 |
| 1.2（预留） | adr_references | 关联 ADR 索引 |

**兼容规则**：新版本引擎必须能读取旧版本 Context Packet；旧版本引擎遇到未知字段应跳过而非报错。

**原则**：每个引擎接收任务时，应能理解"前面发生了什么、我现在该做什么"，而无需重新发现。

---

## 4. Engine Registry（引擎注册表）

### 4.1 当前注册

| 引擎 | 角色 | 核心能力 | 职责边界 | 能力矩阵 |
|------|------|----------|----------|----------|
| WorkBuddy | Executor | 文件操作、脚本执行、文档生成 | 不修改架构和治理 | coding:N, review:N, execution:Y, image:N, reasoning:L |
| Reasonix | Developer | 编码、Git、ADR 修改、架构落地 | 不独立决策 | coding:Y, review:N, execution:Y, image:N, reasoning:H |
| ChatGPT Web | Architect / Architecture Reviewer | 方案设计、Review、风险识别 | 不直接执行文件操作 | coding:N, review:Y, execution:N, image:Y, reasoning:H |
| Codex | Code Reviewer | 代码审查、安全规范 | 不开发新功能 | coding:Y, review:Y, execution:N, image:N, reasoning:M |
| CloudCore | Auditor | 独立评估、风险发现 | 不参与设计与开发 | coding:N, review:Y, execution:N, image:N, reasoning:H |

**能力字段说明**：coding（编码能力）、review（审查能力）、execution（执行能力）、image（图像处理）、reasoning（推理强度 H/M/L）

### 4.2 新引擎加入流程

1. 确定角色映射（哪个 Role 适合此引擎）
2. 验证能力（是否能胜任该角色的职责）
3. 填写能力矩阵（coding / review / execution / image / reasoning）
4. 注册到 Engine Registry（更新本表）
5. 分配访问权限（遵循角色对应的权限边界）
6. 验证一次完整任务路由

---

## 5. Human x AI 矩阵

实际使用中，不同 Human 实例配合不同 AI 引擎完成工作：

| Human | AI 引擎 | 典型协作场景 |
|-------|---------|-------------|
| **Case-01 Maintainer** | ChatGPT (Architect) | 架构讨论、设计评审、治理决策 |
| | Reasonix (Developer) | Core 开发、ADR 实现、Release |
| | Codex (Code Reviewer) | 代码审查、安全审计 |
| **Case-02 Developer** | WorkBuddy (Executor) | 日常开发、实验、跨环境验证 |
| | ChatGPT (Architect) | 开发咨询、方案讨论 |
| **Case-03 Pilot User** | WorkBuddy (Executor) | 日常使用、资料整理 |
| | ChatGPT (Architect) | 问题反馈整理、体验改进建议 |

---

## 6. 各阶段输出物

| 阶段 | 角色 | 输出物 |
|------|------|--------|
| 需求讨论 | Architect | 讨论记录 |
| 方案确认 | Architect | **Proposal**（`Proposal-Template.md`） |
| 开发实现 | Developer | Code + ADR 修改 + 文档 |
| 架构 Review | Architecture Reviewer | Architecture Review Report |
| Code Review | Code Reviewer | Code Review Comments |
| 独立审计 | Auditor | Audit Report |
| 最终决策 | Maintainer | Merge / Reject / Rework |

---

## 7. 关键约束

- AI 引擎不得直接写入 Core 平台文件——所有修改须经 Maintainer Review
- Proposal 是进入开发的必要前置条件（防止"想到就做"）
- Architect 和 Architecture Reviewer 可以是同一引擎（如 ChatGPT 承担两个角色），但职责不同
- Auditor 必须与开发引擎不同——不能自己审自己
- 每个 Task 在引擎间流转时必须携带 Context Packet（§3.5）
- 新引擎加入须走注册流程（§4.2）
- **Maximum Review Iterations = 3**——Architecture Review 最多返回修改 3 次；超出后由 Maintainer 决策（接受 / 延期 / 放弃）

---

## 8. Layer 3: 结构化 AI 通信（Structured AI Communication）

### 8.1 问题

当前 AI 引擎间采用**人工中继**模式——ChatGPT 的讨论结果需人工复制给 Reasonix，几轮后 Token 膨胀、信息丢失、效率下降。

### 8.2 原则

> **AI 与 AI 的协作，应传递结构化成果（Proposal、Decision、Review、Context Packet），而不是完整聊天记录。**

### 8.3 Packet 协议

AI 之间传递四种标准 Packet（详见 `30_SYSTEM/Specifications/AI-Packets/`）：

| Packet | 用途 | 发送方 -> 接收方 |
|--------|------|-----------------|
| **Task Packet** | 指派具体开发/修改任务 | Architect -> Developer |
| **Decision Packet** | 记录讨论结论和取舍 | Architect -> 所有参与方 |
| **Review Packet** | 发起审查请求 | Developer -> Reviewer |
| **Context Packet** | 任务流转时携带的上下文 | 引擎间传递 |

### 8.4 文档流模型

AI 之间不直接聊天，而是通过文档交互：

```
ChatGPT（Architect）
    |  输出 Proposal.md
    v
Proposal.md（结构化任务）
    |  读取 + 执行
    v
Reasonix（Developer）
    |  输出 Review.md（如有审查需求）
    v
Review.md（结构化审查请求）
    |  读取 + 审查
    v
ChatGPT（Reviewer）
```

### 8.5 传递规则

| 可以传递 | 不建议传递 |
|----------|-----------|
| Task Packet | 30 轮聊天记录 |
| Decision Packet | 全部推理过程 |
| Review Packet | 全部历史上下文 |
| Context Packet | 整个聊天窗口 |
| Diff / Proposal | 未结构化的长篇讨论 |

---

## 9. 与 Human Role Model 的关系

```
                 Human Layer（ADR-0018）
  Case-01                Case-02              Case-03
 Maintainer             Developer            Pilot User
      |                     |                    |
      +---------------------+--------------------+
                            |
                 AI Fleet（本模型）
                            |
      +----------+----------+----------+----------+
      |          |          |          |          |
 ChatGPT    Reasonix   WorkBuddy    Codex   CloudCore
Architect   Developer   Executor   Reviewer  Auditor
```

两者正交叠加：Human 层决定"谁决策"，AI 层决定"谁执行/审查"。

---

> *本模型与 ADR-0019（AI Engine Role Model）和 ADR-0018（Human Multi-Instance Role Model）配套使用。*
