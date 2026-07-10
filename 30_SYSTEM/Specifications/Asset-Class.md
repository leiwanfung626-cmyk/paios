---
title: "Asset Class — 资产类别规范"
status: Active
created: 2026-07-11
related:
  - ../ADR/ADR-0017-Platform-Purity-Physical-Separation.md
  - ../Evolution/Phase-B-Core-Workspace-Split.md
  - ../Governance/Architecture-Lifecycle.md
---

# Asset Class（资产类别规范）

> 定义 PAIOS 全平台的**内容分类轴**。
> 它不隶属于某个目录（如 `20_KNOWLEDGE`），而是跨目录、跨桶的统一分类标准。
> 适用对象：Core 内的知识、Workspace 内的资产、Fleet 内的共享产物——凡 PAIOS 管理的内容都可被分类。

---

## 1. 为什么独立成规范

Phase B 早期把 `Platform / Personal` 写死在 `20_KNOWLEDGE/` 章节里。但分类需求不只出现在 Knowledge：

- `10_WORK/` 也有 Platform（平台工具）与 Personal（个人项目）之分
- `Fleet/` 也有 Platform（聚合脚本产物）与 Shared（跨实例汇总）之分
- 未来还会出现 Imported（论文 / RFC / Vendor Docs / 开源文档）

→ 若把分类规则绑死在某个目录，每处都要重写。独立成 `Specifications/Asset-Class.md` 后，**全平台引用同一份规则**，新增类别零成本。

---

## 2. 分类轴（可扩展）

| Asset Class | 定义 | 典型落点 | 未来扩展 |
|-------------|------|----------|----------|
| **Platform** | 平台能力 / 方法论（ADR / Patterns / Architecture / Capability / Workflow / 平台工具） | Core 共享 | — |
| **Shared** | 跨实例可复用但非平台能力（公共引用、共享知识库） | 视纯度归 Core 或 Workspace | 独立子类 |
| **Personal** | 个人资产 / 状态 / 项目 / 笔记 | Workspace 私有 | — |
| **Imported** | 外部引入、非平台定义（论文 / RFC / Vendor Docs / 开源文档） | Workspace（除非被平台显式引用） | Knowledge / External |

> **目录是 Asset Class 的实现，不是分类本身。** 当前 Phase B 只落地 Platform 与 Personal 两类边界；Shared / Imported 预留分类位。

---

## 3. 与 Platform Purity Principle 的关系

Asset Class 只回答"**怎么分小类**"，不回答"**进 Core 还是 Workspace**"。后者由 `ADR-0017 D0` 的 Platform Purity Principle 判定：

> **"这个文件是在定义平台能力，还是仅仅记录平台使用？"**

判定顺序：
1. 先问 Platform Purity：**是不是平台能力？**
   - 是 → Core
   - 否 → Workspace
2. 再问 Asset Class：**在它归属的桶内，属于哪一类？**（用于目录组织、共享策略、未来扩展）

两者正交、互补：Purity 管"桶"，Asset Class 管"类"。

---

## 4. 扩展规则

- 新增类别：**只在 §2 分类轴加一行**，不改动 Platform Purity Principle、不新增"Registry X"式特例。
- 任何目录要引入分类，引用本规范，不自带分类逻辑。

---

## 5. 复用规则

- `20_KNOWLEDGE/`、`10_WORK/`、`Fleet/` 等凡涉及分类，一律引用本规范。
- 本规范与 `ADR-0017`（Purity 判定）、Governance 层配套。
