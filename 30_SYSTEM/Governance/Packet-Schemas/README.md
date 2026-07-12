# Packet Schemas — AI 通信包 Schema

> Packet 由 AI **自动生成**，人工只负责批准/否决，不负责搬运和格式化。
>
> Schema 使用 YAML 格式定义，供 AI 引擎在协作过程中自动生成结构化交接信息。

---

## 触发条件

| 场景 | 自动生成 Packet 类型 | 触发时机 |
|------|---------------------|----------|
| 架构讨论结束 | Decision Packet | 讨论达成结论时 |
| 需要开发实现 | Task Packet | Decision 批准后 |
| 实现完成需审查 | Review Packet | 代码/文档修改完成时 |
| 任务在引擎间流转 | Context Packet | 引擎交接时 |

## 路由规则

```
AI 讨论/开发
    │
    │（自动提取+生成）
    ▼
Packet（结构化成果）
    │
    │（进入 Inbox）
    ▼
Human Review（审批节点）
    │
    ├── Approved → 下一个 AI 引擎
    └── Rejected → 返回上一步
```

## 约束

- **AI 自动生成但不得自动修改核心文档**——所有平台文件修改须经 Human Review
- **人不搬运**——Packet 由 AI 自动生成，人只负责在 Inbox 中批准/否决
- **Packet 可审计**——每次交接有明确输入、输出和决策依据

---

## Schema 列表

| Packet | Schema 文件 | 说明 |
|--------|-------------|------|
| Task | [task.yaml](task.yaml) | 指派开发/修改任务 |
| Decision | [decision.yaml](decision.yaml) | 记录讨论结论和取舍 |
| Review | [review.yaml](review.yaml) | 发起审查请求 |
| Context | [context.yaml](context.yaml) | 任务流转上下文 |

> 当前协议版本：**1.0**
