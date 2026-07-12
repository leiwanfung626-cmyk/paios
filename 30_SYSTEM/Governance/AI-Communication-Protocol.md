---
title: "AI Communication Protocol — AI 通信协议"
status: Active
created: 2026-07-12
related:
  - AI-Operating-Model.md
  - Packet-Schemas/README.md
  - ../ADR/ADR-0019-AI-Engine-Role-Model.md
  - ../../00_CAPTURE/Inbox.md
---

# AI Communication Protocol（AI 通信协议）

> **AI 自动生成结构化 Packet，人工只负责批准/否决。**
>
> 不是让人学会填写 Packet，而是让 AI 在协作过程中自动生成结构化交接信息。

---

## 1. 设计原则

### 原则一：AI 自动生成，人工不搬运

AI 完成讨论或开发后，**自动提取关键信息生成 Packet**。人不负责复制粘贴、格式化、整理——只负责在 Inbox 中审批。

### 原则二：AI 生成但不得自动 Apply

AI 可以生成 Packet、提出修改建议，但**不得自动修改核心文档**。所有平台文件修改须经 Human Review 后才能 Apply。

### 原则三：人和 AI 的分工

```
AI → 整理 / 生成 / 路由
人 → 批准 / 否决（在 Inbox 中完成）
```

---

## 2. 自动生成触发条件

| 场景 | 自动生成 | 触发时机 |
|------|----------|----------|
| 架构讨论结束 | Decision Packet | 讨论达成结论时 |
| 需要开发实现 | Task Packet | Decision 批准后 |
| 实现完成需审查 | Review Packet | 代码/文档修改完成时 |
| 任务在引擎间流转 | Context Packet | 引擎交接时 |

---

## 3. 完整流程

```
AI-1（ChatGPT）
    │  讨论 → 自动生成 Decision Packet
    ▼
Inbox（Human Review）
    │  批准 / 否决
    ▼
AI-1（ChatGPT）
    │  自动生成 Task Packet
    ▼
Inbox（Human Review）
    │  批准
    ▼
AI-2（Reasonix）
    │  按 Task Packet 实现
    │  自动生成 Review Packet
    ▼
Inbox（Human Review）
    │  批准
    ▼
AI-3（Codex / CloudCore）
    │  Review → 自动生成 Audit Report
    ▼
Inbox（Human Review）
    │  批准
    ▼
Human（Case-01 Maintainer）
    │  最终决策 → Release
```

---

## 4. Packet 路由规则

1. AI 生成 Packet 后写入 `00_CAPTURE/Inbox.md`（或指定目录）
2. Human 在 Inbox 中查看并批准/否决
3. 批准后的 Packet 进入下一环节
4. 否决的 Packet 附带原因返回上一步

---

## 5. 约束

- AI 自动生成 Packet 但**不得自动修改核心文档**
- 所有平台文件修改须经 Human Review
- Packet 可审计——每次交接有明确输入、输出和决策依据
- Schema 定义见 [Packet-Schemas/](Packet-Schemas/README.md)

---

## 6. 与现有模型的关系

| 层 | 职责 | 对应文档 |
|----|------|----------|
| Layer 1: Static Role | 谁负责什么 | AI-Operating-Model §2 |
| Layer 2: Task Routing | 任务如何流动 | AI-Operating-Model §3 |
| **Layer 3: Communication** | **AI 之间如何高效通信** | **本协议 + AI-Operating-Model §8** |
| Approval Gate | 人如何审批 | 本协议 §3 |

> **AI 负责交流格式化，System 负责保存上下文，Human 负责最终授权。**
