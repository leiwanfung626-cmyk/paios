---
type: models
topic: "来源约束机制对比 — NotebookLM vs PAIOS"
lifecycle: active
id: "KB-2026-07-02-0001"
created: "2026-07-02"
updated: "2026-07-02"
source: "REF-0002 NotebookLM + PAIOS Principles"
tags: [models, source-constraint, verification, comparison]
attributes:
  comparison_axis: [来源约束, 工具观, 流水线, 可追溯, 多模态, 强制机制, 范围, 进化]
  verdict: "PAIOS 在治理/决策/进化更强；NotebookLM 在多模态/引用精度/预处理摩擦更优"
extensions:
  related_refs: ["REF-0002", "REF-0001"]
  related_principles: ["#4 知识验证", "#8 工具独立"]
---

# 来源约束机制对比模型

## 核心问题

两个系统都在解决同一个问题：**如何确保知识可信？** 但路径不同。

## 对比框架

| 维度 | NotebookLM | PAIOS | 相通/差异 |
|------|-----------|-------|----------|
| 来源约束 | 引擎层技术拦截：数据不够不回答 | 治理层制度约束：Principle #4 + evidence_chain | 相通（方向一致），差异（执行层） |
| 工具观 | 组合使用，各擅其长 | 工具独立，所有 AI 都是客户端 | 相通 |
| 流水线 | 来源 → 转录稿 → 大模型整理 | Inbox → 分类 → 验证 → 知识库 | 相通（结构同构） |
| 可追溯 | claim 级内联引用（段落级） | frontmatter evidence_chain（文件级） | 相通，PAIOS 粒度更粗 |
| 多模态 | 原生支持音频/视频/PDF/网页 | 文本/Markdown 为主 | 差异（PAIOS 短板） |
| 强制机制 | 技术强制（产品级） | 原则+ADR（治理级） | 差异 |
| 范围 | 来源整理器（单一环节） | 决策操作系统（全生命周期） | 差异（PAIOS 更大） |
| 进化 | 无演化机制 | 反馈闭环 + L5 进化层 | 差异（PAIOS 独有） |

## 判定逻辑

```
NotebookLM = 好用的环节（source → structured text）
PAIOS      = 完整的系统（capture → route → process → validate → store → evolve）

两者不是替代关系，是环节与系统的关系。
NotebookLM 可以成为 PAIOS 流水线中的预处理工具。
```

## 适用场景

- **选 NotebookLM**：需要快速把音频/视频/长报告变成可追问的结构化文本
- **选 PAIOS**：需要长期管理知识生命周期、做决策记录、持续演化

## 结论

PAIOS 在治理、决策、进化三个维度是 NotebookLM 完全不具备的。但 NotebookLM 在多模态输入、claim 级引用、低摩擦预处理三方面的设计值得 PAIOS 学习。详见 DEC-2026-07-02-0001。
