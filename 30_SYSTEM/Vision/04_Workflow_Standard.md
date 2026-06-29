# PAIOS 技术白皮书 v1.0 — 工作流标准

> **来源**：`paios-philosophy.md` + `Principles.md` 中的生命周期设计

## 4.1 九阶段工作流

PAIOS 定义完整的 9 阶段标准工作流，覆盖信息从进入系统到归档的全生命周期：

```
Input（输入）
  ↓
Capture（捕获进入 Inbox）
  ↓
Classify（分类定级）
  ↓
Process（处理/加工）
  ↓
Validate（验证）
  ↓
Store（存储到知识库）
  ↓
Route（路由到自动化）
  ↓
Evolve（演化）
  ↓
Archive（归档）
```

## 4.2 每阶段职责定义

| 阶段 | 入口 | 出口 | 自动触发点 |
|------|------|------|-----------|
| **Input** | 外部来源（对话、链接、文件、想法） | 原始内容 | 无（手动输入） |
| **Capture** | 原始内容 | `00_CAPTURE/Inbox.md` | 自动检测文件变化 |
| **Classify** | Inbox 条目 | 类型标注（Concept/Method/SOP/Decision/Model/Reference） | 元数据模板检测 |
| **Process** | 标注条目 | 处理完成内容 | AI 辅助处理脚本 |
| **Validate** | 处理结果 | 已验证知识 | 验证脚本（L0 自动） |
| **Store** | 已验证知识 | `20_KNOWLEDGE` 对应子目录 | 元数据写入触发 |
| **Route** | 知识条目 | `40_AUTOMATION`（如需自动化执行） | Registry 匹配触发 |
| **Evolve** | 使用数据 | 规则修订 / 最佳实践沉淀 | Migration Log 记录 |
| **Archive** | 不活跃资产（>90天无引用） | `90_ARCHIVE` | 生命周期检测 |

## 4.3 核心工作流原则

### 输入统一（Single Entry）
所有新内容先进入 `00_CAPTURE/Inbox.md`，不思考分类，不决定目录。

### 生命周期路由（Lifecycle Routing）
系统根据 Lifecycle 决定内容去向（Work / Knowledge / Automation / Archive），用户不决定目录。

### 流程记忆（Process Memory）
用户只记住流程（Capture → Route → Process），不记住目录路径。

### Inbox 使用规则
- Inbox 是**缓冲区（Buffer）**，不是仓库（Storage）
- 处理完成即清空（标记 `[x]`）
- 可以堆积，但生命周期不能跳过

## 4.4 自动触发点

当前定义但尚未自动化的触发点（预留 Governance 2.0）：

| 触发点 | 条件 | 预期动作 |
|--------|------|---------|
| 文件写入 Inbox | 检测到 Inbox.md 更新 | 自动提取条目 |
| 元数据标注完成 | 条目标记完整元数据 | 自动路由到对应目录 |
| 知识存储完成 | 写入 20_KNOWLEDGE | 自动更新索引 |
| Registry 匹配 | 新资产符合已注册能力 | 自动关联 |

---

**关联文档**：[03_Architecture.md](03_Architecture.md) | [05_Decision_Layer.md](05_Decision_Layer.md) | `Principles.md` | `ADR-0003-Workflow-Pipeline`
