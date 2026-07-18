---
adr: "0022"
status: "Accepted"
date: "2026-07-18"
accepted_date: "2026-07-18"
reviewed_by: Reasonix
evidence_level: "Emerging"
type: adr
related:
  - 30_SYSTEM/ADR/ADR-0009-Governance-Model.md
  - 30_SYSTEM/Vision/00_Abstract.md
  - README.md
  - 00_CAPTURE/inbox/20260718-110507-buddy-paios-positioning-consensus.md
promoted: true
promoted_to: 30_SYSTEM/ADR/ADR-0022-Terminology-and-Positioning.md
---
# ADR-0022 — PAIOS Terminology and Positioning（术语与定位）

> **状态说明**：本 ADR 由 Evan 于 2026-07-18 口述决策批准内容，以 inbox 草稿形式暂存。须经 Capture Pipeline 晋升（`classify_capture.py --apply`）后正式写入 `30_SYSTEM/ADR/` 并成为 Accepted。
> **编号说明**：原拟用 ADR-0018，但 `30_SYSTEM/ADR/ADR-0018` 已被「Multi-Instance Role Model & One-Way Flow」占用，故顺延至 **ADR-0022**。

## Context（背景）

PAIOS 历经「愿景探索期（v0.x）」到「架构成熟期（v1.x）」：

- 早期对外语言为 **"Personal AI Operating System"**（愿景 / 品牌层）。
- 架构成熟后，治理层、生命周期、平台-实例解耦、FIM 等机制使系统更接近 **"Governance-driven Personal AI Architecture"**（技术定义层）。

当前仓库同时存在两套语言（如 `README.md` L3/L15 与 `30_SYSTEM/Vision/00_Abstract.md` L9/L31/L37 仍自称 Personal AI Operating System，而技术讨论已用 architecture）。**这不是错误，而是版本演化遗留（Terminology Evolution Residue）。**

在架构冻结 / 定位稳定阶段，最重要的是**统一内部语义**，而非扩大外部表达。

## Decision（决策）

确立 PAIOS 双层术语与定位体系：

1. **PAIOS 名称保留** — `PAIOS` 即 `Personal AI Operating System`，作为项目名 / 愿景 / 长期目标。
2. **OS 作为愿景概念（Brand Layer）** — 不删除、不否定早期愿景；OS 是隐喻与长期方向，不是"已实现的完整操作系统"的技术声称。
3. **Architecture 作为技术定义（Architecture Layer）** — 所有技术文档、论文、开源介绍统一使用：
   - EN: *PAIOS is a governance-driven architecture for building personal AI operating systems.*
   - ZH: *PAIOS 是一种面向个人 AI 操作系统构建的治理驱动架构。*
   - 禁止技术文本中出现 "PAIOS is a Personal AI Operating System"（声称已实现完整 OS）。
4. **对外技术文本统一使用 Architecture 表述** — README / Vision 技术段 / Architecture Overview / 开源简介均遵循本 ADR。

### Dual-Layer Definition

```
Brand Layer（保留）
  PAIOS
  Personal AI Operating System
  → 项目名称 / 愿景 / 长期目标

Architecture Layer（统一）
  PAIOS is a governance-driven architecture
  for personal AI operating systems.
  → 所有技术文档 / 论文 / 开源介绍
```

### Terminology Evolution Record（术语演化记录）

| 时期 | 定义 | 性质 |
|------|------|------|
| v0.x | Personal AI Operating System | 探索概念（愿景阶段） |
| v1.x | Governance-driven Personal AI Architecture | 架构定义（成熟阶段） |

> 该表应进入 `30_SYSTEM/Vision/` 或 `ARCHITECTURE.md`，体现演化成熟度，而非否定旧历史。

## Rationale（理由）

- 完全删除 OS 会削弱 PAIOS 品牌含义；完全保留 OS 作技术声称会引审稿 / 开源争议（scheduler / kernel / resource mgmt？）。
- 分层后：愿景与实现解耦，历史连续，对外严谨。
- 符合 PAIOS 已有治理体系（ADR 作为一等公民、Decision Traceability）。

## Consequences（影响）

### Positive
- 内部语义统一，README / Vision / ADR / 开源共享同一语言体系。
- 消除"成熟架构却用早期探索语言描述自己"的错位。

### Negative / 注意
- Vision 文档保留 OS 愿景词，需配套 Architecture Overview 说明隐喻关系，避免读者混淆。
- 需一次性 README 技术段改写（仅 2 处，不碰 Vision 愿景词）。

## Alternatives Considered
- **全局替换删除 OS**：损失品牌含义，且破坏历史连续性 → 否决。
- **维持现状两套语言并存**：语义漂移，冻结期不允许 → 否决。

## Related
- `ADR-0009` Governance Model（本 ADR 是其术语层落地）
- `00_CAPTURE/inbox/20260718-110507-buddy-paios-positioning-consensus.md`（定位基线 v2，含创新证据矩阵）
- `README.md`、`30_SYSTEM/Vision/00_Abstract.md`（待按本 ADR 更新）

## 落地顺序（Evan 指定）

```
Inbox（本草稿 + 定位基线）
  ↓
① 定位基线确认（Baseline v1.0 Accepted）
  ↓
② Terminology ADR（本 ADR，晋升后 Accepted）
  ↓
③ 更新 Vision（补 Architecture Overview + Terminology Evolution Record）
  ↓
④ 更新 README（技术段 2 处改 Architecture）
  ↓
⑤ 生成公开简介（最后一步，当前不做）
```
