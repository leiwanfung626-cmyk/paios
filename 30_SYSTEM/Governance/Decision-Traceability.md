---
title: "Decision Traceability — 决策可追溯性"
status: Active
created: 2026-07-11
related:
  - Architecture-Lifecycle.md
  - Pilot-Gate.md
  - Rollout.md
  - Change-Control.md
  - ../ADR/ADR-0017-Platform-Purity-Physical-Separation.md
  - ../Evolution/Case-Studies/README.md
---

# Decision Traceability（决策可追溯性）

> 治理体系的"证据链"。没有它，Architecture Lifecycle 只是一张流程图；
> 有了它，每一次架构变更都能从"代码里的 commit"一路反查到"真实运行的证据"。

---

## 1. 强制四字段（所有 ADR 必须有）

每个 ADR 在正文顶部（frontmatter 之后、Summary 之前）固定声明四个字段：

| 字段 | 含义 | 取值 |
|------|------|------|
| **Evidence** | 支撑本决策的证据来源 | `CASE-NNN` / 实测 / 文档；Reactive 必填 |
| **Implements** | 本 ADR 落实了哪个蓝图 / 原则 | `Phase B Blueprint` / `ADR-0012` / … |
| **Frozen By** | 设计冻结的 commit（未 push 也算） | commit hash（如 `472e53d`） |
| **Supersedes** | 被本 ADR 取代 / 修正的文档 | `ADR-0016 Phase B draft` / `—` |

**示例（ADR-0017）**：

```
Evidence:   CASE-001 (Multi-Instance First Convergence, Validated)
Implements: Phase B Blueprint v2
Frozen By:  472e53d (design freeze, unpushed)
Supersedes: ADR-0016 §Phase B draft
```

---

## 2. 反向引用（所有 Blueprint 必须有）

每个 Blueprint 在头部固定声明它 **Implements** 哪个 ADR：

```
Implements: ADR-0017 (Platform Purity & Physical Separation)
```

这样 ADR → Blueprint 双向可追。

---

## 3. Commit 引用（所有相关 commit 必须带）

涉及架构变更的 commit message 引用 `ADR-XXXX` 与 `CASE-XXX`：

```
docs(architecture): introduce evidence-driven governance and Phase B blueprint (ADR-0017, CASE-001)
refactor(governance): establish Core/Workspace boundaries (ADR-0017)
```

Git History 因此天然成为"决策索引"。

---

## 4. Reactive vs Proactive ADR

| 类型 | 触发 | 证据要求 | 例子 |
|------|------|----------|------|
| **Reactive** | 真实运行暴露问题 | **必须有 Evidence 支撑**（CASE / 实测） | ADR-0017 ← CASE-001 |
| **Proactive** | 前瞻预判未来风险 | **必须明确验证条件**，并在真实运行后完成验证或修订 | ADR-0016（预判第二实例，后被 CASE-001 验证） |

> **规则**：Reactive ADR 必须有证据支撑；Proactive ADR 必须明确验证条件，并在真实运行后完成验证或修订。
>
> 这条取代原先"Evidence 必须在 ADR 之前"的绝对表述——它不否定 PAIOS 的前瞻设计能力，只是要求前瞻决策自带"如何被证伪 / 验证"的说明。

---

## 5. 闭环（Traceability Loop）

```
CASE-NNN (Evidence)
   │  validated
   ▼
ADR-XXXX (Evidence / Implements / Frozen By / Supersedes)
   │  implemented by
   ▼
Blueprint (Implements: ADR-XXXX)
   │  frozen by
   ▼
commit hash (ref: ADR-XXXX, CASE-NNN)
   │
   └──────────── 反查链：commit → Blueprint → ADR → CASE ────────────┘
```

任意一端（commit / CASE / ADR / Blueprint）都能沿链追到另一端。

---

## 6. 复用规则

- **所有 L3（Architecture）级 ADR**：四字段必填，缺失则评审不通过。
- **Blueprint / SOP / Specification**：头部 `Implements` 必填。
- **架构相关 commit**：message 必带 `ADR-XXXX`（必要时 `CASE-XXX`）。
- 本规范与 `Architecture-Lifecycle.md` 配套：Lifecycle 管"节奏"，Traceability 管"证据链"。
