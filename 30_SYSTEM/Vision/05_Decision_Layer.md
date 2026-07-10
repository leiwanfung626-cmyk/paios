# PAIOS 技术白皮书 v1.0 — 决策层

> **来源**：`paios-philosophy.md` 第③节 + `ai-capability-architecture.md`

## 5.1 决策层定义

> **决策先于执行，是系统控制中心。**

PAIOS 的核心关注点不是"存储知识"，而是"做出更好的决策"。传统系统优先优化知识存储；PAIOS 优先优化决策质量。

## 5.2 决策层结构

```
┌─────────────────────────────────────┐
│         Intent Analyzer              │  ← 理解用户意图
├─────────────────────────────────────┤
│         Strategy Planner             │  ← 规划执行策略
├─────────────────────────────────────┤
│         Decision Engine              │  ← 执行决策（ADR + Protocol）
├─────────────────────────────────────┤
│         Verification Engine          │  ← 验证决策结果
├─────────────────────────────────────┤
│         Learning Engine              │  ← 复盘优化
└─────────────────────────────────────┘
```

### Intent Analyzer（意图分析器）
- 解析用户输入的真实意图
- 区分"存储型"和"决策型"请求
- 确定所需的知识层和决策层级别

### Strategy Planner（策略规划器）
- 基于意图制定执行策略
- 匹配 Registry 中可用的 Capability
- 选择适当的工作流路径

### Decision Engine（决策引擎）
- 加载相关的 ADR 和 Decision Protocol
- 应用决策模板进行结构化判断
- 输出可追溯的决策记录

### Verification Engine（验证引擎）
- 验证决策结果是否满足原意图
- 检查是否符合 Invariants 和 Principles
- 记录验证结果供 Learning Engine 使用

### Learning Engine（学习引擎）
- 收集决策结果和反馈数据
- 识别模式和改进机会
- 更新 Decision Protocol 和决策模板

## 5.3 决策层级

| 决策类型 | 工具 | 影响范围 |
|---------|------|---------|
| **战略决策**（L4） | ADR + 重大评审 | Philosophy、Principles、Invariants |
| **架构决策**（L3） | ADR | 目录结构、生命周期、Engine |
| **行为决策**（L2） | Review | Workflow、Agent、Prompt |
| **配置决策**（L1） | Review | 元数据、Registry、配置 |
| **日常决策**（L0） | 无 | 文档、注释 |

## 5.4 决策记录体系

| 记录类型 | 用途 | 结构程度 | 示例 |
|---------|------|---------|------|
| **ADR** | 正式、不可逆的重大决策 | 高度结构化 | ADR-0002~ADR-0009 |
| **Decision Log** | 轻量级日常决策 | 模板化 | 20_KNOWLEDGE/Decisions/ |
| **Decision Template** | 决策输入标准化 | 结构化模板 | 20_KNOWLEDGE/Decisions/_template.md |

## 5.5 DRS → PAIOS 决策演化

| DRS 概念 | PAIOS 架构位置 | 状态 |
|----------|---------------|------|
| 人格画像 | → Decision Profile（决策偏好） | 重构 |
| 思维模型 | → Decision Engine / Workflow Engine | 保留并升级 |
| 价值观 | → Operating Principles（`paios-philosophy.md`） | 保留并升级 |
| 经验知识 | → 20_KNOWLEDGE + Memory Engine | 保留并升级 |
| 行为习惯 | → Decision Preferences（长期主义/风险控制/ROI优先） | 重构 |
| 情感模拟 | → ❌ 不纳入核心架构 | 移除 |
| 意识复制 | → ❌ 不纳入核心架构 | 移除 |

---

**关联文档**：[04_Workflow_Standard.md](04_Workflow_Standard.md) | [06_Governance.md](06_Governance.md) | `paios-philosophy.md` | `ADR-0009-Decision-Layer`
