# Story Candidate: AI Communication Layer

> **状态**：Candidate（设计探索，未激活）
> **触发条件**：需要真实跨引擎协作摩擦证据
> **关联**：`30_SYSTEM/Governance/AI-Communication-Protocol.md` · `30_SYSTEM/Governance/Packet-Schemas/`

---

## 概念

AI 引擎间不通过人工转发聊天记录协作，而是通过自动生成的结构化 Packet 通信。

## 当前状态

2026-07-12 实时运行测试验证了以下方向正确：

- ✅ 人可继续复制原始 AI 输出（不改变工作流）
- ✅ AI 应自动理解上下文并提取结构化信息
- ✅ Human 只负责批准关键变化
- ⏳ 等待真实协作摩擦证据

## 为什么暂未激活

遵循 Need Driven Promotion。目前有设计需求和理论价值，但尚未积累足够的生产痛点证据。需要观察到以下现象之一才能触发 Promotion：

1. 第 5 轮后 AI 丢失初始目标
2. 上下文膨胀导致 Token 超限
3. 需要反复解释已确定的决策
4. AI 产生决策不一致

## 设计原型

现有设计文档（design exploration 级别）：

| 文档 | 说明 |
|------|------|
| `AI-Communication-Protocol.md` | 通信协议规范 |
| `Packet-Schemas/task.yaml` | 任务指派 Schema |
| `Packet-Schemas/decision.yaml` | 决策记录 Schema |
| `Packet-Schemas/review.yaml` | 审查请求 Schema |
| `Packet-Schemas/context.yaml` | 上下文交接 Schema |

---

> 本候选不构成平台能力，仅作为未来 ADR 的前置探索记录。
