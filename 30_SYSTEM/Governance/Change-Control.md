---
title: "Change Control — 变更控制"
status: Active
created: 2026-07-11
related:
  - Architecture-Lifecycle.md
  - Decision-Traceability.md
  - Pilot-Gate.md
  - Rollout.md
---

# Change Control（变更控制）

> 管"什么级别的变更需要走什么流程"。
> 与 `Architecture-Lifecycle.md`（节奏）、`Decision-Traceability.md`（证据链）配套，三者构成 PAIOS 治理骨架。

---

## 1. 变更分级

| 级别 | 例子 | 流程 |
|------|------|------|
| **L3 Architecture** | Core / Workspace 拆分、Registry 重构、生命周期调整 | 完整 Lifecycle（Evidence→Case→ADR→Blueprint→Freeze→Boundary→Pilot→Rollout→Validate） |
| **L2 Behavior** | 工作流调整、SOP 修订、工具行为变更 | 精简 Lifecycle（Evidence→ADR→Blueprint→Freeze→Rollout→Validate），可省略 Pilot |
| **L1 Content** | 知识库增删、日常文档 | 直接操作，无需 ADR（重大争议除外） |

---

## 2. 冻结策略（Freeze Policy）

- **设计冻结（Freeze）**：只提交文档，不碰物理文件。冻结后若需改，回到 Blueprint 修订、重新 Freeze，不带着未定设计执行。
- **架构冻结（ADR-0016 基线）**：已冻结的架构基线（如 4 层模型）非经新 ADR 不可改。
- **发布冻结**：`SYSTEM_VERSION.md` 记录的版本状态，release 期间锁定。

---

## 3. 证据门禁（Evidence Gate）

- **Reactive ADR**：必须有 Evidence（CASE / 实测）支撑，否则不进 ADR。
- **Proactive ADR**：必须明确验证条件，并在真实运行后完成验证或修订（见 `Decision-Traceability.md` §4）。
- **禁止"先大改再补证据"**：架构变更以证据为起点，不以设想为起点（Proactive 例外，但须自带验证条件）。

---

## 4. Commit 纪律（Commit Discipline）

- 架构变更 commit 与 git cleanup（merge）commit **严格分离**。
- Rollout 在 Git History 上展开为四段：Architecture / Governance / Git Cleanup / Physical Separation（见 `Rollout.md` §3）。
- "建立边界（Establish Boundaries）" ≠ "物理拆分（Physical Separation）"；前者只调目录 / Registry / `.gitignore`，后者才 `git rm --cached`。
- 架构相关 commit message 必带 `ADR-XXXX`（见 `Decision-Traceability.md` §3）。

---

## 5. 复用规则

- 任何 L3 变更必须走完整 Lifecycle + 本规范。
- 本规范是 Governance 层的"入口守门员"：判定变更级别 → 决定走哪条流程。
