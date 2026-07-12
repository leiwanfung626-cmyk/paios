# PAIOS 技术白皮书 v1.0 — 附录

## A. 术语表

| 术语 | 定义 |
|------|------|
| **PAIOS** | Personal AI Operating System |
| **DRS** | Decision Replica System（前身，原 Digital Replica System） |
| **ADR** | Architecture Decision Record — 架构决策记录 |
| **Inbox** | `00_CAPTURE/Inbox.md` — 统一输入缓冲区 |
| **Bootstrap** | 会话启动读取 AI_STARTUP.md → Principles → ADR-INDEX；数据放置规则由工作区配置全局强制执行 |
| **Invariant** | 不可违反的系统约束 |
| **Impact Level** | 变更影响等级（L0-L4） |
| **Registry** | `40_AUTOMATION/00_REGISTRY/` — 资产注册中心 |
| **Lifecycle** | 资产生命周期状态机（Draft → Reviewing → Approved → Active → Frozen → Deprecated → Archived） |
| **Freeze Policy** | 冻结期行为约束，当前 90 天 |
| **Memory Engine** | 记忆引擎 — 管理长期知识与检索 |
| **Decision Engine** | 决策引擎 — 管理决策协议与 ADR |
| **Learning Engine** | 学习引擎 — 管理复盘与规则修订 |
| **Need Driven Promotion** | 需求驱动晋升 — 不预判需求，不提前引入复杂度 |
| **Tool Independence** | 工具无关原则 — 所有 AI 工具都是客户端 |

## B. Metadata Schema

> 来源：`30_SYSTEM/Config/metadata.yaml`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 唯一标识 |
| `type` | string | ✅ | 资产类型（concepts/methods/sop/decisions/models/references） |
| `lifecycle` | string | ✅ | 生命周期状态 |
| `version` | string | ✅ | 版本号（semver） |
| `tags` | string[] | ✅ | 标签（至少 1 个） |
| `created` | datetime | ✅ | 创建时间 |
| `updated` | datetime | ✅ | 最后更新时间 |
| `related_adr` | string[] | 可选 | 关联 ADR 编号 |
| `schema_version` | string | ✅ | Schema 版本 |
| `summary` | string | ✅ | 摘要（用于 L3 Embedding 的 Chunk 0） |
| `verification.status` | string | 可选 | 验证状态 |

### Reference 模板（最成熟）

```yaml
ref_id: REF-XXXX
schema_version: "1.0"
type: paper / tool / article / book / video / code
title: ""
summary: ""
abstract: ""    # Chunk 0 for vector indexing
tags: []
verification:
  status: unverified / verified / peer_reviewed
  date: null
confidence: 0.0  # 0.0 ~ 1.0
maintenance:
  review_date: null
  next_review: null
```

## C. 生命周期模型

### 7 状态生命周期

```
Draft → Reviewing → Approved → Active → Frozen → Deprecated → Archived
```

### 状态矩阵

| 状态 | 含义 | 可否修改 | 可否引用 |
|------|------|----------|----------|
| **Draft** | 起草中，未正式采纳 | ✅ | ⚠️ 谨慎引用 |
| **Reviewing** | 正在评审 | ⚠️ 仅评审意见 | ⚠️ 谨慎引用 |
| **Approved** | 已通过评审，待实施 | ✅ 按评审意见修改 | ✅ |
| **Active** | 当前生效 | ✅ | ✅ |
| **Frozen** | 冻结，不允许修改 | ❌ | ✅ |
| **Deprecated** | 已废弃，建议用替代方案 | ❌ | ⚠️ 仅历史参考 |
| **Archived** | 归档，只读 | ❌ | ✅ 历史追溯 |

## D. 目录说明

| 目录 | 角色 | 生命周期阶段 | 同步方式 |
|------|------|-------------|---------|
| 00_CAPTURE | 信息入口 | Capture | Git（同步但清空） |
| 10_WORK | 工作区 | Process | Git（文档）+ 同步盘（大文件） |
| 20_KNOWLEDGE | 知识库 | Validate → Store | Git |
| 30_SYSTEM | 系统内核 | Governance | Git |
| 40_AUTOMATION | 自动化层 | Route | Git |
| 50_DATA | 数据基础设施 | Runtime | ❌ 不同步 |
| 60_EXTERNAL | 外部引用 | Reference | 独立管理，不入主仓库 |
| 70_TMP | 临时文件 | Runtime | ❌ 不同步 |
| 90_ARCHIVE | 历史归档 | Archive | Git（文本）+ 云盘（附件） |

## E. 当前系统健康状态

| 指标 | 分数 | 说明 |
|------|------|------|
| Doctor Health Score | **94/100** | 系统健康度 |
| Validate Status | **97/100（0 errors）** | 完整性校验 |
| Principles | ✅ 9 条 | 全部就绪 |
| ADR | ✅ 2 条（+8 条新增） | ADR-0002 ~ ADR-0009 + ADR-9999 |
| Registry | ✅ 5 YAMLs | 全部可读 |
| Templates | ✅ 6 套 | 覆盖全部知识类型 |

## F. 关联文档索引

| 文档 | 位置 |
|------|------|
| PAIOS 哲学 | `30_SYSTEM/Vision/paios-philosophy.md` |
| 九大原则 | `30_SYSTEM/Principles.md` |
| 架构治理 | `30_SYSTEM/Governance/architecture-governance.md` |
| 架构不变量 | `30_SYSTEM/Governance/architectural-invariants.md` |
| AI 能力架构 | `30_SYSTEM/Design_Notes/ai-capability-architecture.md` |
| Retrieve 演化 | `30_SYSTEM/Design_Notes/retrieve-evolution.md` |
| 迁移日志 | `30_SYSTEM/Evolution/Migration_Log.md` |
| Governance 回顾 | `30_SYSTEM/Evolution/Governance-Retrospective-2026Q3.md` |
| ADR 索引 | `30_SYSTEM/ADR/ADR-INDEX.md` |
| 系统版本 | `SYSTEM_VERSION.md` |
| 变更日志 | `CHANGELOG.md` |
| 部署指南 | `DEPLOYMENT.md` |
| 同步策略 | `SYNC_STRATEGY.md` |
| 平台 Manifest | `MANIFEST.json` |

---

*PAIOS 技术白皮书 v1.0 完 · 2026-06-29*
