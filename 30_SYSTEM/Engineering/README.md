# Engineering Discoveries — 工程发现

> **定位**：记录 PAIOS 在开发过程中总结出的原创工程发现。
>
> 这些发现不是外部理论的引用，不是在架构评审中做出的决策，
> 而是在长期实践中逐步提炼并经过验证的工程规律。

---

## 知识来源分类

PAIOS 的知识来源现在可以区分为三类：

| 来源 | 说明 | 存储位置 |
|------|------|---------|
| **External Knowledge** | 来自公开标准、论文、最佳实践等外部资料 | 20_KNOWLEDGE/References |
| **Architectural Decisions** | 开发过程中主动做出的架构决策 | 30_SYSTEM/ADR/ |
| **Engineering Findings** | 在长期实践中逐步提炼并经过验证的工程规律 | 30_SYSTEM/Engineering/ |

## 文档索引

| 文档 | 证据等级 | 层 | 描述 |
|------|---------|-----|------|
| [Requirement_Emergence.md](Requirement_Emergence.md) | validated-by-engineering-practice | L2 | 需求不是输入，是迭代的产物 |
| [Evidence_Level_System.md](Evidence_Level_System.md) | validated-by-engineering-practice | L2 | PAIOS 文档统一证据等级体系 |
| [Layer_Integrity_Map.md](Layer_Integrity_Map.md) | observed | L1 | 系统层级完整性审计与污染检测 |

## 与 ADR 的区别

| 维度 | ADR | Engineering Finding |
|------|-----|-------------------|
| **记录什么** | "我们决定这么做" | "我们为什么会发现这件事" |
| **来源** | 架构评审 | 实际开发 |
| **证据** | 评审通过 | 实践验证 |
| **范围** | 单一决策 | 跨项目规律 |

## 文档元数据规范

Engineering 目录下的所有文档应包含以下字段：

```yaml
---
title: <文档标题>
status: <evidence-level-tag>       # observed | validated-by-engineering-practice | institutionalized | standardized | deprecated
category: engineering-discovery
first_observed: <date>             # 首次观察日期
validated_by: <context>            # 验证上下文
related_adr:                       # 关联 ADR
  - ADR-XXXX
related_engineering:               # 关联工程发现
  - Other_Finding.md
created: <date>
---
```

## Candidates（候选工程发现）

`_candidates/` 目录用于存放待验证的工程发现假设。
Candidate 文档不得作为 Principles、Standards 或 ADR 的依据引用，除非已完成工程验证并正式晋升。

| 文档 | 证据等级 | 层 | 描述 |
|------|---------|-----|------|
| [_candidates/Stability_Discipline.md](_candidates/Stability_Discipline.md) | observed | L3 (candidate) | 在没有新证据之前，不因新想法修改系统 |
| [_candidates/Necessity_Gated_Architecture.md](_candidates/Necessity_Gated_Architecture.md) | observed (high confidence) | L3 (candidate) | 结构准入控制系统，扩展需可验证需求触发 |
