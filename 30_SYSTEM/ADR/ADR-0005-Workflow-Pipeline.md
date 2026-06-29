# ADR-0005: 工作流管道（Workflow Pipeline）

## Status
Accepted

---

## Context
PAIOS 需要一套标准工作流来管理信息从进入系统到归档的全生命周期。缺乏标准化流程会导致：
- 知识沉淀不一致
- AI 工具无法预测内容的处理阶段
- 系统演化缺乏基准

---

## Decision
定义 9 阶段标准工作流：

```
Input → Capture → Classify → Process → Validate → Store → Route → Evolve → Archive
```

每个阶段有明确的：入口、出口、职责定义、自动触发点（预留）。

### 各阶段概要

| 阶段 | 核心动作 | 关联目录 |
|------|---------|---------|
| Input | 接收外部来源 | 外部 |
| Capture | 写入 Inbox | 00_CAPTURE |
| Classify | 类型标注 | 00_CAPTURE |
| Process | 内容加工 | 10_WORK |
| Validate | 验证通过 | 10_WORK |
| Store | 写入知识库 | 20_KNOWLEDGE |
| Route | 路由到自动化 | 40_AUTOMATION |
| Evolve | 规则优化 | 30_SYSTEM/Evolution |
| Archive | 归档历史 | 90_ARCHIVE |

---

## Rationale
- 工作流与 7 层目录架构一一对应，路由规则清晰
- 9 阶段覆盖从输入到归档的完整链路，不留空白
- 预留自动触发点，为 Governance 2.0 的自动化做准备
- 用户只需记住"Capture → Route → Process"三个核心动作

---

## Consequences
### Positive
- AI 工具可基于工作流阶段感知内容成熟度
- 自动路由路径清晰

### Negative
- 初期需手动执行各阶段流转
- 完整走完 9 阶段有一定认知负担

---

## Alternatives Considered
- **3 阶段简化流程**（输入→处理→归档）— 缺少验证和演化阶段，不利于长期质量
- **无固定流程** — 与 PAIOS 的核心设计哲学矛盾

---

## Related
- ADR-0003: 七层目录架构
- Principle #1: Directories express lifecycle
- `04_Workflow_Standard.md`
