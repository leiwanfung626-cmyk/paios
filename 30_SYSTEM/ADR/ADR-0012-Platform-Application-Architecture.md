---
adr: "0012"
status: "Accepted"
date: "2026-07-10"
---

# ADR-0012: PAIOS 平台化 — Core + Applications 架构

## 背景

PAIOS v1.0 架构冻结后，系统已稳定运行。但在实际使用中，出现了一个新的需求方向：**成长伴生系统（Growth OS）**——以人生成长时间线为主轴的数据 + AI 系统。

这引出了一个架构性选择：Growth OS 应该直接塞进 PAIOS 目录，还是作为一个独立系统？如果独立，如何复用 PAIOS 已有的基础设施？

更深层的问题是：随着 Photo OS、Study OS、Health OS 等更多垂直场景自然涌现，PAIOS 的定位是否需要从"个人 AI 系统"升级为"AI 应用平台"？

## 问题

PAIOS 长期以来遵循"不因推测性价值增加结构"的原则（Necessity-Gated Architecture）。现在 Growth OS 是一个真实的、当下的需求，它应该：

1. **直接整合进 PAIOS**（继续扩展 PAIOS 目录）
2. **完全独立开发**（新建系统，不依赖 PAIOS）
3. **作为 PAIOS 平台上的独立应用**（PAIOS 提供通用能力，应用独立运行）

## 决策

**选择方案 3：PAIOS Core + Applications 架构。**

```
PAIOS (Platform)
  │
  ├── Core（通用基础设施）
  │     ├── Markdown 数据存储规范
  │     ├── AI Runtime / Provider 管理
  │     ├── Workflow（9 阶段流水线）
  │     ├── Automation（自动化引擎）
  │     ├── Registry（统一注册中心）
  │     ├── Git 版本管理
  │     └── 工程规范（ADR / Necessity Audit / Evidence Level）
  │
  ├── Applications（独立应用）
  │     ├── Growth OS（成长伴生系统）
  │     ├── Photo OS（照片管理系统）— 与 Growth OS 天然融合
  │     ├── Study OS（考研系统的自然演化）
  │     └── Future Apps...
  │
  └── SDK / Framework（待沉淀）
        ├── 通用数据模板
        ├── AI 分析 Pipeline
        ├── 报告生成器
        └── MCP / Embedding（未来）
```

### 各应用的独立性

- 每个 Application 有独立的目录、配置、数据存储
- 共享 PAIOS Core 的通用能力（AI 调用、自动化、版本管理）
- 应用之间可以互操作（如 Photo OS 为 Growth OS 提供照片数据）
- 不强制统一的目录结构——各应用按自身场景设计

### 通用能力的判断标准

只有**两个以上应用真正需要的**能力，才提升到 Core：
1. 通过证据验证（Evidence Level System）
2. 经过 Necessity Audit
3. 不因"未来可能用得上"而提前提升

## 为什么不选择其他方案

### 方案 1：直接整合进 PAIOS

**问题**：PAIOS 会变成越来越庞大的"超级仓库"。

```
PAIOS
 ├── 照片   ─── 单独的领域逻辑
 ├── 工作   ─── 单独的领域逻辑
 ├── 考研   ─── 单独的领域逻辑
 ├── 育儿   ─── 单独的领域逻辑
 ├── 健康   ─── 单独的领域逻辑
 ├── 股票   ─── 单独的领域逻辑
 └── ...
```

这种模式下：
- PAIOS 目录结构随应用增多而爆炸
- 各领域的关注点交叉污染
- 治理复杂度非线性增长
- 违背"Core 小而稳定"的原则

### 方案 2：完全独立开发

**问题**：重复建设已验证的基础设施。

Growth OS 需要完全重新实现：
- Markdown 数据存储规范
- AI 调用封装
- 自动化引擎
- 版本管理
- 配置管理

这等于把 PAIOS 已经验证的基础设施再做一遍——浪费且不可维护。

## 与现有架构原则的兼容性

| 原则 | 兼容性 | 说明 |
|------|--------|------|
| Necessity-Gated Architecture | ✅ | Growth OS 是真实需求，不是推测 |
| 不因推测性价值增加结构 | ✅ | 不预设完整生态，只先做第一个应用验证 |
| Evidence Level System | ✅ | Core 能力的提升需要应用验证证据 |
| Requirement Emergence | ✅ | 应用需求驱动 Core 能力演化 |
| 先跑通再优化 | ✅ | Growth OS 先跑通最小闭环 |

## 实施路径

### 当前阶段（Phase 1）：知识基准建立

- 建立年龄阶段性知识参考文档（如 REF-0010：0 岁早教）
- 这些文档属于 PAIOS 现有 Knowledge 层，不需要新架构

### 下一阶段（Phase 2）：第一个应用验证

- 当知识积累到足够程度，且出现实际使用场景时，创建 Growth OS 独立应用
- 从最小可用版本开始（如：记录模板 + 月度报告生成）
- 验证 AI 分析管线在实际场景中的有效性

### 未来阶段（Phase 3）：能力沉淀

- 当 Growth OS 运行稳定后，识别出真正通用的能力
- 将这些能力通过 ADR 流程提升到 PAIOS Core
- 当第二个应用自然出现时，复用这些能力

### 未来阶段（Phase 4）：生态形成

- 仅当有两个以上成熟应用，且互操作需求明确时
- 才考虑正式的 SDK / Framework / 应用间协议

## 风险与约束

| 风险 | 缓解措施 |
|------|---------|
| 过早设计生态蓝图 | Phase 1 只做知识积累，不建新系统 |
| Core 和应用边界模糊 | 通用能力判断标准：至少两个应用真实需要 |
| 应用间数据孤岛 | 通过标准化的数据模板和 Registry 统一 |
| 治理复杂度增加 | 每个应用独立治理，Core 治理保持当前节奏 |

## 结论

PAIOS 不变成一个"超级仓库"，也不放弃已有的基础设施。它进入平台化阶段——

**PAIOS Core 承载通用能力，Applications 承载垂直场景。Growth OS 是第一个验证者。**

这不是"重新设计系统"，而是 PAIOS 在真实需求驱动下的自然演进。

---

**Related**: `20_KNOWLEDGE/Concepts/Growth-OS-Life-Companion.md` | `20_KNOWLEDGE/References/Early-Education-0-Year.md` | `v1.0-Milestone.md`
