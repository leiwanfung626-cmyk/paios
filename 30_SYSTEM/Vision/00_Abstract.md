# PAIOS 技术白皮书 v1.0 — 摘要

> **基于 PAIOS Platform v1.0.0 实际工程导出**
> 架构状态：**Frozen**
> 生成日期：2026-06-29

## PAIOS 定义

**PAIOS** = **Personal AI Operating System** — 一套让任何 AI 都能基于用户的知识、规则和反馈，持续做出更符合用户长期利益的决策的个人智能基础设施。

## 系统目标

| 目标 | 说明 |
|------|------|
| **知识管理** | 从无序输入到结构化知识库的全生命周期管理 |
| **AI 辅助决策** | 通过 ADR + Decision Protocol 约束 AI 的推理方式 |
| **工作流执行** | 从 Capture 到 Archive 的 9 阶段工作流 |
| **系统演化** | 通过 Migration Log + Evolution Model 持续改进 |

## 核心能力

1. **统一入口** — 所有输入先进入 `00_CAPTURE/Inbox.md`，不思考分类
2. **生命周期路由** — 生命周期决定内容去向，不是目录
3. **治理体系** — ADR + Impact Levels + Freeze Policy 三权分立
4. **工具无关** — 所有 AI 工具都是客户端，平台使用开放格式（Markdown/YAML/JSON/Python）

## 与传统系统差异

| 维度 | 传统系统 | PAIOS |
|------|---------|-------|
| 定位 | 笔记软件 / RAG / 聊天机器人 | 决策操作系统 |
| 知识组织 | 手动分类到目录 | 生命周期自动路由 |
| 决策记录 | 无 | ADR + Decision Log |
| 演化机制 | 手动迁移 | Migration + Evolution Model |
| 模型依赖 | 绑定特定模型 | 工具无关，开放格式 |

> **标准定位句**：PAIOS is a Personal AI Operating System designed for structured knowledge management, AI-assisted decision making, workflow execution, and system evolution.

---

**关联文档**：[01_Background.md](01_Background.md) | [02_Principles.md](02_Principles.md) | [03_Architecture.md](03_Architecture.md) | `README.md`
