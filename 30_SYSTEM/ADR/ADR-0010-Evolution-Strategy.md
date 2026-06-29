# ADR-0010: 演化策略（Evolution Strategy）

## Status
Accepted

---

## Context
PAIOS 需要在不中断运行的前提下持续演化。历史资产（H 盘 DRS 时代的资产）需要系统化的处置流程。

---

## Decision
采用 **Need Driven Promotion（需求驱动晋升）** 策略：

**核心原则**：不预判需求，不提前引入复杂度。让真实工作驱动演进。

### 资产处置分类

| 类型 | 含义 | 处置方式 |
|------|------|---------|
| A. Philosophy | 设计哲学类 | Absorbed（吸收到新体系） |
| B. Architecture | 架构类 | Deferred（推迟，需要时晋级） |
| C. Capability | 能力类 | Deferred（推迟，已注册待激活） |
| D. Implementation | 实现类 | Retired（退役） |

### 晋升流程

```
Need → Discover → Evaluate → Refactor → Promote → Register
```

1. **Need** — 真实需求出现
2. **Discover** — 发现可复用的历史资产
3. **Evaluate** — 评估资产质量和适配性
4. **Refactor** — 重构为新体系格式
5. **Promote** — 晋升为正式资产
6. **Register** — 注册到 Registry

### 版本化

使用 `SYSTEM_VERSION.md` + `MANIFEST.json` 双记录：
- SYSTEM_VERSION 人类可读
- MANIFEST.json 机器可解析

---

## Rationale
- 避免过早优化和过度工程化（PAIOS 的前车之鉴）
- Migration Log 提供完整的处置追溯
- 6 步晋升流程确保每个晋升都经过审慎评估

---

## Consequences
### Positive
- 系统不会因为"更优雅"而重构
- 历史资产不会被丢弃，而是系统化处置

### Negative
- 初期能力可能不够丰富
- 部分资产长期处于 Deferred 状态

---

## Alternatives Considered
- **全量迁移** — 高迁移成本，无真实需求支撑
- **废弃所有历史资产** — 丢失有价值的经验
- **持续重构** — 导致"迁移瘫痪"，项目无法推进

---

## Related
- ADR-0008: Automation Layer
- ADR-9999: Legacy Retention Policy
- `Migration_Log.md`
- `retrieve-evolution.md`
