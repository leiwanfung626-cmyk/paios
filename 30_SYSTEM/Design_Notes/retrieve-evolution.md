---
title: Retrieve Capability Evolution
status: accepted
related_capability: retrieve
related_adr:
  - ADR-0002
implementation: pending
decision_trigger:
  - Markdown 检索已无法满足效率需求
  - 出现真实的跨文档语义检索需求
created: 2026-06-29
---

# Retrieve Capability Evolution

## 1. 背景（Background）

PAIOS 在迁移 H 盘旧系统时，发现了一个完整的禁毒宣传 RAG 原型（`40_AUTOMATION/09_LEGACY/original/rag_prototype.py`），包含 FAISS 向量索引 + DeepSeek API 生成流程。与此同时，`30_SYSTEM/Config/rag.yaml` 已存在框架配置，`00_REGISTRY/scripts.yaml` 已登记三个 RAG 相关脚本（`SCRIPT-0001`~`0003`，状态 `pending`）。

这促使重新审视一个问题：**PAIOS 与 RAG 的关系是什么？**

## 2. 设计决策（Decision）

### 核心定位

**PAIOS 不是 RAG 系统，而是可以承载 RAG 的平台（RAG-ready Platform）。**

### Retrieve 作为单一 Capability 分级演进

Retrieve 始终是**一个** Capability，其实现随知识规模自然升级：

| Level | 实现 | 适用场景 |
|-------|------|----------|
| **L0** | Markdown 搜索（grep / 全文搜索） | 几十篇知识，直接搜索即可 |
| **L0.5** | **Embedding Ready** — Metadata Contract | 所有知识条目统一元数据（ID、schema_version、summary/abstract、tags、keywords），不生成向量。Schema First，为未来 L3 无缝升级做准备，零运行时成本。 |
| **L1** | Metadata 检索（按 YAML 元数据筛选） | 百级规模，需要按类型/标签/时间过滤 |
| **L2** | BM25 全文检索 | 数百篇，关键词匹配已不够精确 |
| **L3** | Vector RAG（嵌入 + 向量库） | 千级规模，需要语义检索 |
| **L4** | Hybrid Search（向量 + 关键词融合） | 万级规模，精度与召回兼顾 |

### Index 是 Runtime Artifact

向量索引、倒排索引等是知识的**运行产物**，不是知识本身：
- 可以随时重新生成
- 不应长期维护
- 不应进入 `20_KNOWLEDGE`
- 不纳入版本管理

## 3. 触发条件（Decision Trigger）

以下条件满足**任一**时，启动 Retrieve 晋升流程：

1. **Markdown 检索已无法满足效率需求** — 知识量导致检索明显变慢、频繁漏检
2. **出现真实的跨文档语义检索需求** — 例如"根据过去所有禁毒工作总结回答问题"这类需要聚合多个文档语义的任务

晋升流程：Need → Discover → Evaluate → Refactor → Promote → Register

## 4. 暂不实施（Deferred）

当前明确不做的五件事：

| 事项 | 原因 |
|------|------|
| ❌ 迁移 Legacy RAG 原型 | 无真实需求，20_KNOWLEDGE 尚未形成知识资产 |
| ❌ 建立向量索引 | 无数据可索引，Index 是 Runtime Artifact |
| ❌ 在 Registry 注册 Retrieve Capability | Registry 只反映现实状态，不占位注册 |
| ❌ 维护 `rag.yaml` 实现细节 | 无晋升不维护实现配置，保持框架态 |
| ❌ 为技术先进性提前引入复杂度 | 不预判需求，让真实工作驱动演进 |

## 5. 未来实现（Implementation Guide）

当第一次因真实需求晋升 Retrieve 时，推荐结构：

```
40_AUTOMATION/
└── 01_CAPABILITIES/
    └── retrieve/
        ├── capability.md
        ├── metadata.yaml
        ├── implementations/
        │   ├── markdown_search.py   ← L0
        │   ├── bm25.py              ← L2（视需求跳过 L1）
        │   ├── vector_rag.py        ← L3
        │   └── hybrid.py            ← L4
        └── tests/
```

### 可复用资产

现有 Legacy 原型（`40_AUTOMATION/09_LEGACY/original/rag_prototype.py`）中的以下模块可参考：
- `chunk_text()` — 文档分块逻辑
- `retrieve()` — 向量检索流程
- `call_llm()` — LLM 生成调用

### 设计依据引用

晋升 Retrieve 时，本文档作为设计依据，无需重新讨论分级演进、Index 定位等已确定的决策。

---

> **关联文档**
> - ADR-0002: Automation Platform Freeze
> - `40_AUTOMATION/09_LEGACY/original/rag_prototype.py`
> - `30_SYSTEM/Config/rag.yaml`
