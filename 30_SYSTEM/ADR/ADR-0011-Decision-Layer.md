# ADR-0011: 决策层结构（Decision Layer）

## Status
Accepted

---

## Context
PAIOS 的核心关注点是决策而非知识存储。传统系统优先优化"存了什么"，PAIOS 优先优化"怎样做决定"。需要正式定义决策层的结构和职责。

---

## Decision
决策层由五个组件组成：

```
┌─────────────────────────────────────┐
│         Intent Analyzer              │  ← 理解用户意图
├─────────────────────────────────────┤
│         Strategy Planner             │  ← 规划执行策略
├─────────────────────────────────────┤
│         Decision Engine              │  ← 执行决策（ADR + Protocol）
├─────────────────────────────────────┤
│         Verification Engine          │  ← 验证决策结果
├─────────────────────────────────────┤
│         Learning Engine              │  ← 复盘优化
└─────────────────────────────────────┘
```

### 决策工具

| 工具 | 用途 | 结构程度 |
|------|------|---------|
| **ADR**（架构决策记录） | 正式、不可逆的重大决策 | 高（7字段模板） |
| **Decision Protocol**（决策协议） | 约束 AI 的推理方式 | 中 |
| **Decision Template**（决策模板） | 标准化决策输入 | 中 |
| **Decision Log**（日常决策日志） | 轻量级日常决策 | 低 |

### 决策层级映射

| 系统层级 | ADR 对应 | Impact Level |
|---------|---------|-------------|
| Philosophy | ADR-（未分配） | L4 |
| Architecture | ADR-0003~0021 | L3 |
| Behavior | ADR-0002（Freeze） | L2 |
| Configuration | 无需 ADR | L1 |
| Documentation | 无需 ADR | L0 |

---

## Rationale
- Principle #4（Knowledge as Code）在决策层的延伸：决策即代码，可版本化、可追溯
- 五个组件构成完整闭环：理解 → 规划 → 执行 → 验证 → 学习
- ADR 层级与 Impact Levels 一一对应，治理体系一致

---

## Consequences
### Positive
- 每次决策都有记录、可追溯、可复用
- 决策过程标准化，AI 工具可参与决策流程

### Negative
- 决策流程增加了执行前置时间
- 需要维护 ADR 和 Decision Log 的更新

---

## Alternatives Considered
- **无独立决策层** — 决策逻辑散落在各处，不可追溯
- **纯人工决策** — 无法利用 AI 的推理能力
- **纯 AI 决策** — 缺乏 Human in Control 机制

---

## Related
- ADR-0009: Governance Model
- ADR-0007: Lifecycle Model
- `paios-philosophy.md`（第③节 AI 能力来源）
- `05_Decision_Layer.md`
