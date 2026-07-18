---
adr: "0023"
status: "Accepted"
date: "2026-07-18"
accepted_date: "2026-07-18"
reviewed_by: Reasonix
evidence_level: "Emerging"
type: adr
depends_on: ADR-0022
related:
  - 30_SYSTEM/Governance/Architecture-Lifecycle.md
  - 30_SYSTEM/Evolution/Governance-Retrospective-2026Q3.md
  - 30_SYSTEM/Evolution/PAIOS-Retrospective-2026-07-10.md
  - 00_CAPTURE/inbox/20260718-110507-buddy-paios-positioning-consensus.md
promoted: true
promoted_to: 30_SYSTEM/ADR/ADR-0023-Review-Cadence.md
---
# ADR-0023 — PAIOS Review Cadence & Evolution Review

> **Status**: Proposed (draft, inbox staging)
> **Date**: 2026-07-18
> **Layer**: L0 Governance
> **Decider**: Evan (Architect)
> **Draft by**: Buddy (WorkBuddy) — Transport/记录层，非决策层

---

## Context

Evan 提出：PAIOS 应形成固定复盘节律（月度运行 / 季度架构 / 年度演化），
并沉淀统一的 **PAIOS Evolution Review** 模板（Origin / Evolution / Current Position /
Core Contributions / Boundaries / Future Direction）。目的不是"证明创新"，而是
保住长期系统最易丢失的东西：**为什么它变成现在这样，未来为什么应这样继续**。

### 仓库真实现状（先查后写，避免重复造轮子）

盘点后确认——**复盘在 PAIOS 里其实已经存在，但只有"事件驱动"，缺"时间驱动"**：

| 已有机制 | 类型 | 覆盖 | 缺口 |
|----------|------|------|------|
| `Governance/Architecture-Lifecycle.md` 的 **Retrospective 阶段** | 事件驱动 | 每轮架构升级闭环末端触发回顾（Accepted/Adjusted/Rejected/Deferred） | 只在"一轮架构演进跑完"时触发，不按日历 |
| `Evolution/Governance-Retrospective-2026Q3.md` | 准季度 | 治理规则成本/使用率评估 | 仅治理成本，非定位/演化；且仍 Pending 未填 |
| `Evolution/PAIOS-Retrospective-2026-07-10.md` | 一次性 | 某时点回顾 | 无固定节律，无统一模板 |
| `Metrics.md` / `Goals/Weekly.md` | 运行指标/周目标 | 运行层 | 无向上汇聚到定位层 |

**结论**：PAIOS 已有**事件驱动回顾**（跟着架构升级走），
缺的是**时间驱动节律**（跟着日历走）+ **面向"身份/定位"的统一模板**。
Evan 的提案正好补这一层，且**与现有 Architecture-Lifecycle 互补、不冲突**：
- 事件驱动（Lifecycle Retrospective）= 回答"这轮升级对不对"（横切一次演进）
- 时间驱动（本 ADR）= 回答"我还是不是我 / 方向对不对"（纵切定位与演化）

### 触发点（Need-Driven-Promotion 已满足）

不是前瞻设计——**模式已重复出现**：Q3 治理复盘 + 07-10 回顾 + 本次三轮 AI 定位复盘。
按 PAIOS 自己的 Need-Driven-Promotion 原则（实例中重复出现的模式 → 提炼为平台规范），
现在正是把它固化的时机。**本次三轮 AI 复盘本身，就是第一次事实上的"年度演化复盘"**。

---

## Decision

建立 **PAIOS 三级时间驱动复盘节律**，与事件驱动的 Architecture-Lifecycle 并存互补：

| 节律 | 名称 | 关注 | 产出 | 落盘 |
|------|------|------|------|------|
| **月度** | 运行复盘 (Operational Review) | 使用痛点 / 新需求 / Bug / 自动化机会 | 轻量条目，可并入 `Metrics.md` | 运行层 |
| **季度** | 架构复盘 (Architecture Review) | 定位是否漂移 / 是否需新 ADR / 重复模式 | 复用 `Governance-Retrospective` 模板 | `30_SYSTEM/Evolution/` |
| **年度** | 演化复盘 (Evolution Review) | PAIOS 是什么 / 核心贡献 / 下一阶段方向 | **Evolution Review 文档**（模板见附录） | `30_SYSTEM/Evolution/` 或 `80_HISTORY/` |

**核心锚点 = 年度演化复盘**：它是 PAIOS 的"身份基准"，其他两级向它汇聚。

### 配套决定

1. **采用统一 Evolution Review 模板**（见附录 A），晋升时落为 canonical 模板文件
   （建议 `30_SYSTEM/SOP/` 或 `30_SYSTEM/Governance/`），唯一权威、避免多版本。
2. **年度复盘固定回答三问**（定位防漂移）：是什么 / 不是什么 / 为什么存在。
3. **既有文件归位**：`Governance-Retrospective-2026Q3.md` 定性为"季度架构复盘"的首个实例；
   本次定位基线 v2.1 定性为"**年度演化复盘 2026**"的种子稿。
4. **克制上限**：月度≤1 页、季度复用现有模板、年度 1 份。防止复盘本身制造文档债。

---

## Rationale（Evan 提出的四作用，映射到治理价值）

1. **Evolution Memory（演化记忆）** — 保住"问题→尝试→副作用→抽象→架构"这条链，
   让未来的人（含未来的自己）看到结果也看到原因。
2. **Identity Drift 防漂移** — 长期 AI 系统最大风险是"不断加功能，最后不知道自己是什么"。
   年度三问强制回锚定位。
3. **Innovation Boundary 校验** — 每次复盘重检"哪些是已有技术/组合创新/真正新机制/只是实现方式"，
   避免低估（"只是文件夹整理"）和高估（"发明了 AI OS"）两个极端。
4. **Evolution Compass 方向盘** — 新增能力先过三问：是否增强治理？是否增强生命周期？
   还是只是加功能？（FIM=增强实例治理 ✅；Packet=增强协作沉淀 ✅；再做个聊天窗口 ❌）

---

## Consequences

**正向**
- 补上时间驱动这一层，与事件驱动形成完整复盘覆盖。
- 定位有周期性回锚机制，降低身份漂移风险（Phase-4 Stabilize 的核心诉求）。
- 复盘产出可追溯、可复用，成为"系统自我解释能力"的载体。

**成本/约束**
- 本 ADR 属治理层变更 → 须遵守 **Architecture-Lifecycle §6 元治理**（治理规则自身也受治理）
  与 **§7 交叉审查**（执行引擎 ≠ 审查引擎）。建议晋升前由 Reasonix 或其他引擎交叉审查。
- 需防"复盘通胀"：严格执行克制上限，否则违背系统自身的反过度设计原则。

**编号说明**
- 现有 ADR 已用到 0021；0022 为术语定位（inbox 草稿，未晋升）。本 ADR 顺延为 **0023**。
- 依赖：建议与 ADR-0022 一并晋升（同属定位/治理定型批次），或 0022 先行、0023 紧随。

---

## Alternatives Considered

1. **不做，沿用事件驱动回顾** — 否决：事件驱动只在架构升级时触发，无法周期性回锚定位；
   身份漂移风险不覆盖。
2. **只写模板不定节律** — 否决：模板无节律等于不会周期性发生，退化为一次性文档。
3. **新建独立复盘子系统** — 否决：过度设计，违反 Need-Driven-Promotion；应复用现有
   Lifecycle / Governance-Retrospective / Metrics 基础设施，只加最小的时间驱动层。

---

## 附录 A — PAIOS Evolution Review 模板（年度，canonical 候选）

```
# PAIOS Evolution Review — YYYY

1. Origin（起源）
   为什么产生 —— 最初的真实痛点

2. Evolution（演化）
   如何走到今天 —— 关键阶段与转折（附 ADR/CASE 锚点）

3. Current Position（当前定位）
   PAIOS 是什么 / 不是什么 / 为什么存在（三问必答）

4. Core Contributions（核心贡献）
   当前四大贡献 + 支撑体系（引用定位基线，不重写）

5. Boundaries（边界）
   明确不做什么 —— 防定位漂移

6. Future Direction（下一阶段方向）
   过 Evolution Compass 三问后的演化优先级
```

> **落地顺序（承接定位基线 v2.1 §落地顺序）**
> Inbox → ①定位基线✅ → ②ADR-0022 术语 → ③ADR-0023 复盘节律（本文件）
> → ④Vision/README 措辞收敛 → ⑤年度演化复盘 2026 定稿（以基线 v2.1 为种子）
