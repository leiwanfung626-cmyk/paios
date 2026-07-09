---
title: Evidence Level System
status: validated-by-engineering-practice
category: engineering-discovery
layer: L2
layer_status: active
first_observed: 2026-06-29
validated_by: PAIOS Platform v1.0.0 — Requirement Emergence principle documentation process
related_adr:
  - ADR-0009 (Governance Model — document status conventions)
related_engineering:
  - Requirement_Emergence.md
created: 2026-06-29
---

# PAIOS Evidence Level System — 统一证据等级体系

> **PAIOS Original Engineering Finding**
>
> 传统文档状态（Draft → Proposed → Accepted → Deprecated）只能表达"有没有被采纳"，
> 无法表达"这个认识有多可靠"。
>
> PAIOS 在实际工程中发现：文档的价值不仅取决于它是否被采纳，
> 更取决于它背后的认识是**推导而来**还是**在实践中反复验证而来**。
>
> 由此产生了这套证据等级体系。

---

## Status

**Validated by Engineering Practice**

本条原则本身即采用其所定义的证据等级体系标记。

---

## 1. 问题

传统文档状态体系（如 ADR 常见的 Proposed → Accepted → Deprecated）存在一个根本缺陷：

> **Accepted 并不代表经过长期实践验证。**

它无法区分以下两种情况：

| 情况 | 状态 | 问题 |
|------|------|------|
| 一个设计在架构评审中通过，但从未在真实场景中运行过 | Accepted | 状态正确，但用户不知道它未被实战检验 |
| 一个原则在多个项目中反复被验证，但未经过正式评审流程 | 无状态 | 没有状态能表达"已验证" |

PAIOS 需要一套能表达**证据强度**的状态体系，而不仅仅是**采纳状态**。

---

## 2. 五级证据等级

```
Evidence Level 0: Observed（观察到）
    │  一次观察记录，可作为线索，不应单独作为决策依据
    │  Example: "我发现每次需求都会变"
    │  Tag: observed
    │
    ▼
Evidence Level 1: Validated by Engineering Practice（经工程实践验证）
    │  经过多个真实项目或多次迭代验证，有可重复的案例
    │  Example: Requirement Emergence（在白皮书迭代中反复出现）
    │  Tag: validated-by-engineering-practice
    │
    ▼
Evidence Level 2: Institutionalized（制度化）
    │  已写入 Principles / Standards / Governance，成为系统规范
    │  Example: 九大核心原则、Tool Independence
    │  Tag: institutionalized
    │
    ▼
Evidence Level 3: Standardized（标准化）
    │  已成为系统默认行为，无需额外决策即可自动执行
    │  Example: Bootstrap First（每次会话自动加载 Principles + ADR + Registry + Manifest）
    │  Tag: standardized
    │
    ▼
Evidence Level -1: Deprecated（已废弃）
    不再适用，有替代方案
    Tag: deprecated
```

### 晋级条件

| 等级 | 从何而来 | 需要什么证据 |
|------|---------|------------|
| **Observed** | 一次开发中的观察记录 | 至少有 1 个具体案例 |
| **Validated by Engineering Practice** | 多个项目或多次迭代中的重复验证 | 至少 2 个独立案例或 3+ 次迭代 |
| **Institutionalized** | 正式写入规范文档 | 经过评审（ADR 或架构 Review） |
| **Standardized** | 成为系统默认行为 | 已实现为默认行为且经过验证 |
| **Deprecated** | 被替代或不再适用 | 有替代方案文档 |

---

## 3. 元数据 Schema

任何原则、发现、规范都应包含以下证据元数据：

```yaml
---
# 必填
status: <evidence-level-tag>        # 五级之一

# 按等级可选
first_observed: <date>              # Observed 或更高：首次观察日期
validated_by: <context>             # Validated+：在什么项目/迭代中验证的
related_adr:                        # Institutionalized+：关联的 ADR
  - ADR-XXXX
related_engineering:                # 关联的工程发现
  - Engineering_Finding.md
standardized_in: <system-behavior>  # Standardized：已标准化的系统行为
superseded_by: <document-ref>       # Deprecated：被什么替代
---
```

---

## 4. PAIOS 现有文档的证据等级映射

| 文档 | 当前状态 | 证据等级 | 说明 |
|------|---------|---------|------|
| `Principles.md`（9条） | 无状态字段 | **institutionalized** | 已写入规范，使用时无需额外决策 |
| `paios-philosophy.md` | accepted | **institutionalized** | 核心愿景，已制度化 |
| `architecture-governance.md` | baseline | **institutionalized** | Governance 框架已生效 |
| `architectural-invariants.md` | active | **institutionalized** | 不可违反的系统约束 |
| ADR-0002 ~ ADR-0011, ADR-9999 | Active/Accepted | **validated-by-engineering-practice** | 已采纳但尚未经长期实战检验 |
| `Design_Notes/ai-capability-architecture.md` | accepted | **observed** | 设计笔记，理论上通过但未多项目验证 |
| `Design_Notes/retrieve-evolution.md` | accepted | **observed** | 设计笔记，待真实需求触发验证 |
| `Engineering/Requirement_Emergence.md` | validated-by-engineering-practice | **validated-by-engineering-practice** | 已通过 PAIOS 自身开发循环验证 |
| `Engineering/Evidence_Level_System.md` | validated-by-engineering-practice | **validated-by-engineering-practice** | 本文档 — 自指有效（self-validating） |

### 映射说明

证据等级与实际业务状态（Active / Frozen / Deprecated）是正交维度：

```
                  Evidence Level
                  Low ──────────────────→ High
                  Observed    Validated    Institutionalized    Standardized
业务状态  Active       ✅ ok       ✅ ok           ✅ ok              ✅ ok
         Frozen       ⚠️ rare      ✅ ok           ✅ ok              ✅ ok
         Deprecated   N/A         N/A            ❌ 矛盾            ❌ 矛盾
```

Frozen 的业务状态可以与高证据等级共存（如 Architecture Freeze —— 架构冻结不代表它没有被验证过）。

---

## 5. 与传统状态体系的兼容

这套体系不替代 ADR 的业务状态（Proposed / Accepted / Deprecated），而是补充：

| 维度 | 传统状态 | 证据等级 |
|------|---------|---------|
| **回答的问题** | 这个文档是否被采纳？ | 这个认识有多可靠？ |
| **适用范围** | ADR 为主 | 所有文档类型 |
| **变化频率** | 随决策变化 | 随实践积累变化（慢） |
| **谁来决定** | 架构评审 | 工程实践验证 |

两者在 frontmatter 中并存：

```yaml
---
status: accepted           # 传统业务状态
evidence: validated-by-engineering-practice  # 证据等级
---
```

---

## 6. 证据等级的工程意义

### 6.1 区分知识来源

PAIOS 的文档知识来源可以分为三类，每种对应不同的初始证据等级：

| 来源 | 说明 | 初始证据等级 |
|------|------|------------|
| **External Knowledge** | 来自公开标准、论文、最佳实践 | observed（需在 PAIOS 环境中验证后才能升级） |
| **Architectural Decisions** | 开发过程中主动做出的架构决策（ADR） | observed（评审通过后仍为 observed，需实战验证） |
| **Engineering Findings** | 长期实践中逐步提炼并经过验证的工程规律 | validated-by-engineering-practice（起点即更高） |

### 6.2 设计决策的参考权重

当需要做设计决策时，证据等级帮助判断参考权重：

- 参考 **institutionalized** 或 **standardized** 的原则：必须遵守
- 参考 **validated-by-engineering-practice** 的发现：强烈建议采纳
- 参考 **observed** 的设计笔记：参考价值，需结合实际情况判断

### 6.3 适用场景

这套体系适用于 PAIOS 中的所有持久文档：

- Principles
- ADR
- Design Notes
- Engineering Findings
- Governance documents
- Vision / Philosophy

Runtime 文件（Inbox、Today.md、TMP 文件）不受此体系约束。

---

## 7. 案例：Requirement Emergence 的证据等级分析

| 字段 | 值 |
|------|-----|
| **文档** | `Engineering/Requirement_Emergence.md` |
| **证据等级** | validated-by-engineering-practice |
| **首次观察** | 2026-06-29（白皮书迭代过程中发现） |
| **验证案例 1** | 白皮书 Markdown → docx 的三轮迭代 |
| **验证案例 2** | PAIOS 自身演化路径（知识库 → Prompt → 规则 → Workflow → Governance → Decision Layer） |
| **关联原则** | Need Driven Promotion |
| **当前晋级目标** | institutionalized（需在另一个独立项目中再次验证） |

---

## Related

- `Engineering/Requirement_Emergence.md` — 第一个使用证据等级标注的工程发现
- `Principles.md` — 核心原则（evidence: institutionalized）
- `ADR-0009-Governance-Model.md` — Governance 框架，定义了文档状态约定
