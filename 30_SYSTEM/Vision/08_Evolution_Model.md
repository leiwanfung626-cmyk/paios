# PAIOS 技术白皮书 v1.0 — 演化模型

> **来源**：`Migration_Log.md` + `retrieve-evolution.md`

## 8.1 DRS → PAIOS 演化路径

PAIOS 前身为 **DRS（Digital Replica System → Decision Replica System）**，经历了根本性转变：

| 维度 | DRS（2025） | PAIOS（2026） |
|------|------------|--------------|
| 核心问题 | 怎样创造一个像我的 AI？ | 怎样让任何 AI 都能利用我的知识和规则？ |
| 实现方法 | 训练私有模型，复制人格 | 管理 Context，沉淀决策 |
| 稀缺认知 | 稀缺的是模型 | 稀缺的是上下文（Context） |
| 核心理念 | 改变模型本身 | 改变模型看到的世界 |

> **改变模型看到的世界，而不是改变模型本身。**

## 8.2 历史资产处置（Migration Log）

本地系统已完成对 H 盘旧系统的全面审计与处置（2026-06-29）：

### 处置分类

| 类型 | 含义 | 处置方式 |
|------|------|---------|
| **A. Philosophy** | 设计哲学类资产 | Absorbed（吸收到新体系） |
| **B. Architecture** | 架构类资产 | Deferred（推迟，真实需求时晋级） |
| **C. Capability** | 能力类资产 | Deferred（推迟，已注册待激活） |
| **D. Implementation** | 实现类资产 | Retired（退役） |

### 已处置资产清单

| 资产 | 类型 | 处置 | 原因 |
|------|------|------|------|
| DRS（Digital Replica System 概念） | A | ✅ Absorbed | 已吸收至 `paios-philosophy.md` |
| 27条规则索引（`规则索引.md`） | A | ✅ Absorbed | 已由 Principles.md + Governance 取代 |
| VUBG Scoring（`workbuddy_rules.md:142-160`） | B | ⏳ Deferred | 保留概念（优先级分析），真实调度需求时晋级 |
| RAG Prototype（`rag_prototype.py`） | B | ⏳ Deferred | 保留概念（知识检索），知识规模触发时晋级 |
| Douyin Pipeline（`douyin_full_pipeline.py`） | C | ⏳ Deferred | 保留为 Workflow 候选，已注册 SCRIPT-0004 |
| `kb_add.py` | D | ❌ Retired | 绑定旧 H 盘路径，功能由 20_KNOWLEDGE 架构覆盖 |
| `kb_status.py` | D | ❌ Retired | 绑定旧 RAG 索引路径，当前 PAIOS 无对应需求 |
| `archive_workbuddy.py` | D | ❌ Retired | WorkBuddy 已由 PAIOS 取代 |

**核心原则**：Assets are promoted when real need arises（Need Driven Promotion），not pre-migrated.

## 8.3 Retrieve Capability 分级演进

Retrieve 作为单一 Capability，其实现随知识规模自然升级：

| Level | 实现 | 适用场景 | 触发条件 |
|-------|------|----------|---------|
| **L0** | Markdown 搜索（grep / 全文搜索） | 几十篇知识，直接搜索即可 | 默认 |
| **L0.5** | **Embedding Ready** — Metadata Contract | 所有知识条目统一元数据，零运行时成本 | Schema First |
| **L1** | Metadata 检索（按 YAML 元数据筛选） | 百级规模，需要按类型/标签/时间过滤 | 效率需求 |
| **L2** | BM25 全文检索 | 数百篇，关键词匹配已不够精确 | 效率需求 |
| **L3** | Vector RAG（嵌入 + 向量库） | 千级规模，需要语义检索 | 语义检索需求 |
| **L4** | Hybrid Search（向量 + 关键词融合） | 万级规模，精度与召回兼顾 | 精度需求 |

### 晋升触发条件

以下条件满足**任一**时，启动 Retrieve 晋升流程：

1. **Markdown 检索已无法满足效率需求** — 知识量导致检索明显变慢、频繁漏检
2. **出现真实的跨文档语义检索需求** — 需要聚合多个文档语义的任务

晋升流程：**Need → Discover → Evaluate → Refactor → Promote → Register**

### Index 是 Runtime Artifact

向量索引、倒排索引等是知识的**运行产物**，不是知识本身：
- 可以随时重新生成
- 不应长期维护
- **不应进入 `20_KNOWLEDGE`**
- 不纳入版本管理

## 8.4 版本演化

| 版本 | 日期 | 内容 |
|------|------|------|
| v1.0.0 | 2026-06-28T14:33:16Z | 平台初始化，7层架构部署 |
| v1.0.0 (+1d) | 2026-06-29 | 首个 Operations Cycle，Legacy 审计完成，Doctor 94/100 |

## 8.5 系统重构策略

- **不可因为"更优雅"而重构** — 重构必须有真实驱动力
- **Need Driven Promotion** — 需求驱动晋升，而非预先迁移
- **90 天 Freeze Policy** — 防止过度重构和迁移瘫痪
- **Migration Log** — 每次处置都有记录，可追溯

---

**关联文档**：[07_Automation.md](07_Automation.md) | [09_System_Properties.md](09_System_Properties.md) | `retrieve-evolution.md` | `Migration_Log.md` | `ADR-0008-Evolution-Strategy`
