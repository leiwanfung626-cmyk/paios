# ADR-9999: 历史资产处置策略（Legacy Retention Policy）

## Status
Accepted

---

## Context
PAIOS 前身 DRS 在 H 盘遗留了大量资产（脚本、规则、原型、文档）。这些资产需要在 PAIOS 体系下被妥善处置，不能简单丢弃（丢失经验价值），也不能全量迁移（高成本无回报）。

---

## Decision
建立 **A/B/C/D 四类资产分类模型**，按类型决定处置方式：

| 类型 | 定义 | 处置 | 示例 |
|------|------|------|------|
| **A. Philosophy** | 设计哲学、原则类 | **Absorbed** — 吸收到新体系对应文档 | DRS 概念、规则索引 |
| **B. Architecture** | 架构设计、算法类 | **Deferred** — 保留概念，Need Driven Promotion | RAG 原型、VUBG 评分 |
| **C. Capability** | 能力实现、管道类 | **Deferred** — 注册待激活，需求时晋级 | Douyin Pipeline |
| **D. Implementation** | 具体实现代码类 | **Retired** — 退役，不迁移 | kb_add.py、kb_status.py |

### 资产处置流程

```
发现 Legacy 资产
    ↓
分类（A/B/C/D）
    ↓
A类 ──→ 吸收到对应文档，标记 Absorbed
B类 ──→ 记录到 Migration Log，标记 Deferred
C类 ──→ 注册到 Registry（状态: pending），标记 Deferred
D类 ──→ 记录退役原因，标记 Retired
    ↓
更新 Migration Log
```

### Deferred 资产的晋升条件

与 Retrieve Capability 一致的 Need Driven Promotion：
- **B 类**（架构）：出现无法在当前体系实现的需求
- **C 类**（能力）：出现真实的使用场景

---

## Rationale
- 吸取"迁移瘫痪"教训：不让历史资产成为前进的障碍
- A/B/C/D 分类简单清晰，任何审查者都能快速判定
- Deferred 不等于废弃，保留晋升路径

---

## Consequences
### Positive
- 历史资产得到系统化处理，不会变成"垃圾堆"
- Migration Log 提供完整处置追溯

### Negative
- 部分资产长期处于 Deferred 状态，需要定期审视
- Retired 资产可能包含可复用的代码片段（从 Migration Log 可查）

---

## Alternatives Considered
- **全量迁移** — 无真实需求支撑的高成本操作
- **全部删除** — 丢失 DRS 时代的经验价值
- **保留原样不处置** — 历史资产持续"腐烂"，无法引用

---

## Related
- ADR-0010: Evolution Strategy
- `Migration_Log.md`
- `40_AUTOMATION/09_LEGACY/`
