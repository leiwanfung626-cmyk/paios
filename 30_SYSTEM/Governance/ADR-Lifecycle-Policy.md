---
title: "ADR Lifecycle Policy — ADR 生命周期治理规则"
status: Active
created: 2026-07-12
supersedes: direct ADR rewriting practices before v1.0.1
related:
  - ADR-INDEX.md
  - 80_HISTORY/PACKETS/PAIOS-2026-0712-ADR-GOVERNANCE-001.md
---

# ADR Lifecycle Policy

## 核心原则

1. **事实不可修改。** ADR 是历史决策证据，不是活文档。过去发生的事实不能被删除或覆盖。
2. **决策可以演进。** 架构发生变化时，通过新增 ADR 来表达新决策，而非修改旧 ADR。
3. **状态必须透明。** 每个 ADR 必须有明确的生命周期状态，AI 工具启动时先读状态。

## ADR 生命周期状态

```
Proposed ──→ Accepted ──→ Implemented ──→ Deprecated
                │                              │
                └──────→ Superseded ────────────┘
                                              │
                                              └──→ Archived
```

| 状态 | 含义 |
|------|------|
| **Proposed** | 提出但未正式采用 |
| **Accepted** | 当前有效的架构决策 |
| **Implemented** | 已落地实现 |
| **Superseded** | 被新 ADR 替代，但历史有效 |
| **Deprecated** | 不再推荐使用 |
| **Archived** | 仅保留历史记录 |

## 三种变更场景

### 场景一：文档落后于实现

> 问：ADR 描述只是落后于当前实现，架构本身没变？

**处理**：在 ADR 顶部添加修正注释（注明日期），保留原正文作为历史背景。**状态保持 Accepted。**

*例：ADR-0003 七层→十层模型——不是架构推翻，是文档演进。*

### 场景二：设计被替代

> 问：原设计被新设计完全替代？

**处理**：旧 ADR 标记 **Superseded**（注明 `superseded_by: ADR-XXXX`），创建新 ADR。

*例：50_RUNTIME 独立层 → 40_AUTOMATION/11_ENGINES + 12_SCHEDULER。*

### 场景三：决策被证明错误

> 问：历史决策被证明错误？

**处理**：旧 ADR 标记 **Deprecated**，增加 Correction 说明，保留错误背景供未来参考。

## 禁止行为

- ❌ 为了简洁直接删除旧 ADR
- ❌ 为了符合现状修改历史决策原因
- ❌ 忽略 ADR 演进链，跳跃式变更

## AI 工具行为规范

### 读取 ADR 时

1. 先读 **Status** — 决定是否信任该决策
2. 检查 **Superseded** 关系 — 如果被替代，跳到新 ADR
3. 理解 **Decision Context** — 为什么当初这么做
4. 避免重新提出已被解决的问题

### 提议变更时

1. 判断是否影响架构（目录结构、核心原则、接口约定）
2. 如果影响架构 → 提出新 ADR
3. 不能直接修改 Frozen 原则（须经完整 Architecture Lifecycle）

## 引用

- 本 Policy 的交接上下文见 `80_HISTORY/PACKETS/PAIOS-2026-0712-ADR-GOVERNANCE-001.md`
- ADR 完整索引见 `30_SYSTEM/ADR/ADR-INDEX.md`
