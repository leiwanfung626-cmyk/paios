# Documentation

> PAIOS Platform 的文档导航中心。
> 本文档树是**引用层（Reference Layer）**——所有原始文档保留在原位（`30_SYSTEM/`、`20_KNOWLEDGE/` 等），`docs/` 只提供按需分类的索引和快捷方式。

---

## Architecture

| Section | Source Location | Description |
|---------|----------------|-------------|
| **Vision** | `30_SYSTEM/Vision/` | 平台愿景与长期目标（00_Abstract ~ 09_System_Properties + 99_Appendix） |
| **Principles** | `30_SYSTEM/Principles.md` | 九项核心原则 + 需求涌现原则 + 架构冻结策略 |
| **Architecture Decisions** | `30_SYSTEM/ADR/ADR-INDEX.md` | 全部 18 个 ADR 索引（Foundation / Platform Evolution / Governance） |
| **Directory Architecture** | `30_SYSTEM/ADR/ADR-0003-Directory-Architecture.md` | 7 层目录结构定义 |
| **Multi-Instance Model** | `30_SYSTEM/ADR/ADR-0016-Multi-Instance-Architecture-Baseline.md` | 4 层多实例架构基线 |
| **Platform Purity** | `30_SYSTEM/ADR/ADR-0017-Platform-Purity-Physical-Separation.md` | Core/Workspace/Instance-State 三桶隔离 |
| **Role Model** | `30_SYSTEM/ADR/ADR-0018-Multi-Instance-Role-Model.md` | Developer/User 角色与单向数据流 |
| **Architecture Lifecycle** | `30_SYSTEM/Governance/Architecture-Lifecycle.md` | 端到端演进闭环 |
| **Design Notes** | `30_SYSTEM/Design_Notes/` | AI 能力架构、检索演进设计 |
| **Engineering** | `30_SYSTEM/Engineering/` | 证据等级、层完整性映射、必要性审计 |

→ [完整架构文档](architecture/README.md)

---

## Governance

| Section | Source Location | Description |
|---------|----------------|-------------|
| **Change Control** | `30_SYSTEM/Governance/Change-Control.md` | L1/L2/L3 变更分级 + 冻结策略 + Commit 纪律 |
| **Decision Traceability** | `30_SYSTEM/Governance/Decision-Traceability.md` | ADR 四字段证据链 + Reactive/Proactive ADR |
| **Operating Model** | `30_SYSTEM/Governance/Operating-Model.md` | 多实例角色分工与数据流方向 |
| **Pilot Gate** | `30_SYSTEM/Governance/Pilot-Gate.md` | 试点 Entry/Exit Criteria |
| **Rollout** | `30_SYSTEM/Governance/Rollout.md` | 全量推广前置条件与分批顺序 |
| **Architectural Invariants** | `30_SYSTEM/Governance/architectural-invariants.md` | 平台级架构不变量 |
| **Release Management** | `30_SYSTEM/Governance/Release/` | 发布清单、版本策略、分支策略 |

→ [完整治理文档](governance/README.md)

---

## Guides

| Guide | Source Location | Audience |
|-------|----------------|----------|
| **Quick Start** | `README.md` | 新用户 |
| **User Daily Operations** | `30_SYSTEM/SOP/SOP-2026-07-11-0001-User-Daily-Operations.md` | Case-02/03 User |
| **User Iron Rules (一页纸)** | `30_SYSTEM/SOP/SOP-2026-07-11-0002-User-Iron-Rules-One-Pager.md` | Case-02/03 User |
| **Contributing** | `CONTRIBUTING.md` | Maintainer / Contributor |
| **Release Flow** | `30_SYSTEM/SOP/SOP-2026-07-10-0001-Release-Flow.md` | Maintainer |
| **Pilot Launch Checklist** | `30_SYSTEM/SOP/SOP-2026-07-11-0003-Pilot-Launch-Checklist.md` | Maintainer |
| **Deployment** | `DEPLOYMENT.md` | Maintainer |
| **Sync Strategy** | `SYNC_STRATEGY.md` | Maintainer |
| **角色模型速览图** | `30_SYSTEM/SOP/User-Role-Model-Speed-View.html` | All Users |

→ [完整指南索引](guides/README.md)

---

## Decisions

| Section | Source Location | Description |
|---------|----------------|-------------|
| **ADR Index** | `30_SYSTEM/ADR/ADR-INDEX.md` | 全部架构决策索引（19 ADRs） |
| **Architecture Decisions** | `30_SYSTEM/ADR/` | ADR-0002 ~ ADR-0018 + ADR-9999 |
| **Evolution Evidence** | `30_SYSTEM/Evolution/Case-Studies/` | CASE-001（多实例首次并流）及复盘 |
| **Governance Retrospective** | `30_SYSTEM/Evolution/Governance-Retrospective-2026Q3.md` | Q3 治理回顾 |
| **Phase Blueprints** | `30_SYSTEM/Evolution/Phase-B-Core-Workspace-Split.md` | Phase B 蓝图 |
| **知识库决策** | `20_KNOWLEDGE/Platform/Decisions/` | 非架构级运营决策 |

→ [完整决策文档](decisions/README.md)

---

## Reference

| Section | Source Location | Description |
|---------|----------------|-------------|
| **Asset Class** | `30_SYSTEM/Specifications/Asset-Class.md` | 全平台内容分类轴 |
| **FIM v1 Spec** | `30_SYSTEM/Specifications/FIM-v1.md` | Federated Instance Manifest 协议 |
| **Evidence Level System** | `30_SYSTEM/Engineering/Evidence_Level_System.md` | 证据等级定义 |
| **Manifest** | `MANIFEST.json` | 平台版本清单 |
| **System Version** | `SYSTEM_VERSION.md` | 版本声明与冻结状态 |
| **CHANGELOG** | `CHANGELOG.md` | 版本变更历史 |
| **自动化脚本索引** | `40_AUTOMATION/README.md` | 自动化层概览 |
| **Registry** | `40_AUTOMATION/00_REGISTRY/` | 能力注册中心 |

→ [完整参考文档](reference/README.md)

---

## File Inventory

| Location | Count | Description |
|----------|-------|-------------|
| `30_SYSTEM/` | ~66 .md 文件 | 系统内核（ADR / Governance / SOP / Evolution / Engineering） |
| `20_KNOWLEDGE/` | ~35 .md 文件 | 知识库（Concepts / Methods / Decisions / References） |
| `40_AUTOMATION/` | ~20 .md 文件 | 自动化层 README + 文档 |
| Root | 8 .md 文件 | 项目级文档（README / CONTRIBUTING / CHANGELOG 等） |
| **Total** | **~115 .md 文件** | |

---

> **文档原则**：所有原始内容保留在生命周期层中它们应有的位置。`docs/` 不存储内容，只做索引和导航。这是 **Tool Independence Principle**（原则 #8）在文档领域的延伸——文档系统独立于任何单一阅读工具。
