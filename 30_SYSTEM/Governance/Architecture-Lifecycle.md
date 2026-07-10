---
title: "Architecture Lifecycle — 平台级架构生命周期"
status: Active
created: 2026-07-11
related:
  - architecture-governance.md
  - ../ADR/ADR-0017-Platform-Purity-Physical-Separation.md
  - ../Evolution/Phase-B-Core-Workspace-Split.md
  - ../Evolution/Case-Studies/README.md
---

# Architecture Lifecycle（平台级架构生命周期）

> 本文档从 **Phase B v2** 的 Commit 纪律中升华而来。
>
> Phase B 把"Commit"变成了治理对象（Architecture → Governance → Git Cleanup → Physical Separation）。
> 但那只是"一次升级的 Git History 形状"。真正可复用的是**整轮架构演进的闭环节奏**——
> 它不只服务 Phase B，**Phase C / D / … 全部复用同一套生命周期**。

---

## 1. 它解决什么问题

以前 PAIOS 的演进是：先画大图 → 等未来验证。证据散落聊天记录，难以复用。
现在 PAIOS 的演进是：真实运行 → 暴露证据 → 固化 Case → 决策 ADR → 冻结蓝图 → 建边界 → 试点 → 推广 → 再验证。

**Architecture Lifecycle 把这条路径抽成平台级规范**，让每一轮重大升级都套同一个模板，而不是每次重新发明流程。

---

## 2. 生命周期（闭环）

```
        ┌───────────────────────────────────────────────────────┐
        │                                                       │
        ▼                                                       │
  ┌──────────┐                                                  │
  │ Evidence │  真实运行暴露的客观事实（带数字，可验证）            │
  └────┬─────┘                                                  │
       ▼                                                        │
  ┌──────────┐                                                  │
  │  Case    │  固化成 CASE-NNN（架构证据，非会议纪要）           │
  └────┬─────┘                                                  │
       ▼                                                        │
  ┌──────────┐                                                  │
  │   ADR    │  基于证据决策（Accepted / Rejected）              │
  └────┬─────┘                                                  │
       ▼                                                        │
  ┌──────────┐                                                  │
  │ Blueprint│  可实施的架构蓝图（分阶段、有命令纪律）            │
  └────┬─────┘                                                  │
       ▼                                                        │
  ┌──────────┐                                                  │
  │  Freeze  │  设计冻结：仅文档，不碰物理文件                   │
  └────┬─────┘                                                  │
       ▼                                                        │
  ┌──────────┐                                                  │
  │ Boundary │  Establish Boundaries（Governance）：明确职责 /  │
  │ (Gov)    │  调目录 / 写 .gitignore / 更新 Registry，不拆物理 │
  └────┬─────┘                                                  │
       ▼                                                        │
  ┌──────────┐                                                  │
  │  Pilot   │  单实例试点（如 Case-01 / Developer），跑 Exit   │
  │          │  Criteria 全部满足才过闸                         │
  └────┬─────┘                                                  │
       ▼                                                        │
  ┌──────────┐   Rollout 内部展开为 Git History 四段：          │
  │ Rollout  │   Architecture → Governance → Git Cleanup →      │
  │          │   Physical Separation（git rm --cached）         │
  └────┬─────┘                                                  │
       ▼                                                        │
  ┌──────────┐                                                  │
  │ Validate │  连续多版本观察：缺陷不再复现 → 验证完成           │
  └────┬─────┘                                                  │
       │                                                        │
       └──────────────► 沉淀为新 Case ──► 触发下一轮 ADR ──┐
                                                    （回到 Evidence）
```

### 各阶段职责与门槛（Gate）

| 阶段 | 输入 | 动作 | 输出 | 进入下一阶段的门槛（Gate） |
|------|------|------|------|----------------------------|
| **Evidence** | 真实运行 | 观察、记录客观事实 | 带数字的事实 | 足够显著，值得固化 |
| **Case** | Evidence | 写 CASE-NNN（固定结构 + Decision Impact） | 架构证据 | 通过"是否验证/证伪某原则"判定 |
| **ADR** | Case | 决策（含 D0/D1…），记录证据等级 | 冻结的决策 | status = Accepted |
| **Blueprint** | ADR | 写可实施蓝图（分阶段、命令纪律） | 设计文档 | 覆盖对应 Phase 触发条件 |
| **Freeze** | Blueprint | 仅提交文档，不碰物理 | 设计冻结 commit | 评审通过 |
| **Boundary** | Freeze | Establish Boundaries（不物理拆分） | 目录/Registry/.gitignore 就位 | 备份锚点 + Rollback Ready |
| **Pilot** | Boundary | 单实例跑新边界 | 试点信号 | **Exit Criteria 全满足** |
| **Rollout** | Pilot 过闸 | 展开为 Git History 四段 + 物理隔离 | 多实例升级 | 所有实例升级完成 |
| **Validate** | Rollout | 连续观察 | 验证结论 | 缺陷连续多版本未复现 |
| **（闭环）** | Validate | 沉淀新 Case | 下一轮 Evidence | — |

---

## 3. 与现有治理文档的关系

- `architecture-governance.md`（Governance 1.0）：定义 **单资产的 Impact Levels + Asset Lifecycle（Draft→Active→Frozen→Archived）**——管"一个东西怎么变状态"。
- 本文档（Architecture Lifecycle）：定义 **一轮架构演进的端到端节奏**——管"一次升级怎么走完闭环"，跨资产、跨时间。
- 两者互补：Governance 1.0 是纵切（单资产状态机），Lifecycle 是横切（跨资产演进流）。

### 3.1 Governance 子层（本 Lifecycle 的配套规范）

本 Lifecycle 已从 Phase B 抽离为**独立治理层**，以下文件共同构成 PAIOS 治理骨架，任何 Phase 复用、不复制：

| 文件 | 职责 |
|------|------|
| `Architecture-Lifecycle.md`（本文件） | 一轮架构演进的端到端节奏（横切） |
| `Decision-Traceability.md` | 决策证据链：ADR 四字段 + Blueprint 反向引用 + Commit 引用 + Reactive/Proactive |
| `Pilot-Gate.md` | 试点门槛：Entry / Exit Criteria，单实例试点模式 |
| `Rollout.md` | 全量推广：前置条件 + 分批顺序 + Git History 四段展开 |
| `Change-Control.md` | 变更控制：分级 + 冻结策略 + 证据门禁 + Commit 纪律 |
| `../Specifications/Asset-Class.md` | 全平台内容分类轴（Platform / Shared / Personal / Imported） |

> 各 Phase（B / C / D …）只**引用**这些规范，不内联实现；规范本身独立演进。

---

## 4. 复用规则

- **任何 L3（Architecture）级变更**都走完整 Lifecycle。
- **L2（Behavior）级变更**可走精简版（Evidence→ADR→Blueprint→Freeze→Rollout→Validate），省略 Pilot。
- **证据门禁（Reactive / Proactive）**：Reactive ADR 必须有证据支撑；Proactive ADR 必须明确验证条件，并在真实运行后完成验证或修订（详见 `Decision-Traceability.md` §4）。不否定前瞻设计，但前瞻决策须自带验证条件。
- **Pilot 不可跳过**：设计冻结后，至少单实例跑通 Exit Criteria 再过闸。
- **Commit 是治理对象**：Rollout 阶段在 Git History 上展开为四段（Architecture / Governance / Git Cleanup / Physical Separation），使历史一眼可读、便于审计。

---

## 5. 一句话

Architecture Lifecycle 是 PAIOS 的"演进操作系统"——把每一次重大升级从一次性设计，变成可重复、可追溯、可审计的闭环。
