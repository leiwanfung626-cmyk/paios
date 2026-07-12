# AI Packets — 结构化 AI 通信协议

> AI 与 AI 的协作，应传递结构化成果（Proposal、Decision、Review、Context Packet），而不是完整聊天记录。
>
> 本目录定义 PAIOS AI Fleet 中引擎间通信的标准化 Packet 格式。

---

## Packet 类型

| Packet | 用途 | 发送方 → 接收方 |
|--------|------|-----------------|
| [Task Packet](TASK.md) | 指派具体开发/修改任务 | Architect → Developer |
| [Decision Packet](DECISION.md) | 记录讨论结论和取舍 | Architect → 所有参与方 |
| [Review Packet](REVIEW.md) | 发起审查请求 | Developer → Reviewer |
| [Context Packet](CONTEXT.md) | 任务在引擎间流转时携带的上下文 | 所有引擎间传递 |

---

## 核心原则

> **Structured AI Communication Principle**
>
> AI 与 AI 的协作，应传递结构化成果（Proposal、Decision、Review、Context Packet），而不是完整聊天记录。

### 可以传递 vs 不建议传递

| 可以传递 | 不建议传递 |
|----------|-----------|
| Task Packet | 30 轮聊天记录 |
| Decision Packet | 全部推理过程 |
| Review Packet | 全部历史上下文 |
| Context Packet | 整个聊天窗口 |
| Diff / Proposal | 未结构化的长篇讨论 |

### 文档流模型

AI 之间不直接聊天，而是通过文档交互：

```
ChatGPT（Architect）
    ↓ 输出 Proposal.md
Proposal.md
    ↓ 读取
Reasonix（Developer）
    ↓ 输出 Review.md
Review.md
    ↓ 读取
ChatGPT（Reviewer）
```

---

## 版本

当前协议版本：**1.0**
