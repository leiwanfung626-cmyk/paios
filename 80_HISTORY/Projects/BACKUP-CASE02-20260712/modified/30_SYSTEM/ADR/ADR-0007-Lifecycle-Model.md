# ADR-0007: 生命周期模型（Lifecycle Model）

## Status
Accepted

> 2026-07-11 更新：新增 `Experimental` 状态（v2），用于平台级实验验证阶段。
> 参见 ADR-0017 治理反馈。

---

## Context
系统需要统一管理所有资产从创建到退役的全过程。没有统一的生命周期模型会导致：
- 资产状态不明确（哪些是草稿、哪些是生效的）
- 冻结策略无法关联到具体资产
- AI 工具无法判断资产的可信度

---

## Decision
采用 8 状态生命周期模型（v2 — 新增 Experimental）：

```
Draft → Experimental → Reviewing → Approved → Active → Frozen → Deprecated → Archived
```

`Experimental` 位于 `Draft` 之后、`Reviewing` 之前，表示**已实现但尚未经多实例验证**的阶段。

### 状态定义

| 状态 | 含义 | 可否修改 | 可否引用 |
|------|------|----------|----------|
| **Draft** | 起草中，未正式采纳 | ✅ | ⚠️ 谨慎引用 |
| **Experimental** | 已实现，待多实例验证 | ✅ | ⚠️ 仅实验用途 |
| **Reviewing** | 正在评审 | ⚠️ 仅评审意见 | ⚠️ 谨慎引用 |
| **Approved** | 已通过评审，待实施 | ✅ 按评审意见修改 | ✅ |
| **Active** | 当前生效 | ✅ | ✅ |
| **Frozen** | 冻结，不允许修改 | ❌ | ✅ |
| **Deprecated** | 已废弃，建议用替代方案 | ❌ | ⚠️ 仅历史参考 |
| **Archived** | 归档，只读 | ❌ | ✅ 历史追溯 |

---

## Rationale
- 生命周期状态机**独立于审批权限**，为未来自动化预留接口
- 8 状态覆盖从创建到退役的完整过程，不留空白
- Freeze Policy 是 Lifecycle 中 `Frozen` 状态的实例化
- Governance 2.0 的自动化可以在不修改状态机的前提下对接

---

## Consequences
### Positive
- 所有资产状态清晰，可追溯
- Freeze Policy 可直接映射到 `Frozen` 状态

### Negative
- 状态流转需要人工维护初期的治理成本
- 需要培训使用者理解 8 状态的含义

---

## Alternatives Considered
- **3 状态简化模型**（草稿/生效/归档）— 缺少 Experimental/Frozen/Deprecated 状态，不利于长期治理
- **7 状态模型（无 Experimental）** — ADR 缺少实验验证阶段，提案直接从 Draft 跳 Reviewing，过早承诺
- **无生命周期** — 与 PAIOS 的治理设计矛盾

---

## Related
- Principle #2: Everything has exactly one formal location
- ADR-0003: Directory Architecture
- `architecture-governance.md`
