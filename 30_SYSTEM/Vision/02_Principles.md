# PAIOS 技术白皮书 v1.0 — 设计原则

> **来源**：`30_SYSTEM/Principles.md`
> **架构状态**：Frozen | **版本**：1.0.0

## 九大核心原则

| # | 原则 | 含义 |
|---|------|------|
| 1 | **Directories express lifecycle, not content** | 目录表示生命周期阶段，不表示内容分类 |
| 2 | **Everything has exactly one formal location** | 每条知识有且仅有一个正式位置 |
| 3 | **The workspace is always temporary** | 工作区（10_WORK）永远是临时缓冲区 |
| 4 | **Knowledge must be validated before entering the knowledge base** | 知识必须经过验证才能进入 20_KNOWLEDGE |
| 5 | **Automation stores workflows, not knowledge** | 自动化层只存放工作流，不存放知识 |
| 6 | **Keep the top-level directory count low** | 顶层目录冻结为 7 个，不随意增加 |
| 7 | **Metadata is the primary classification system** | 元数据是主要分类手段，而非目录结构 |
| 8 | **Tool Independence** | 平台不依赖任何特定 AI 工具，所有资产使用开放格式（Markdown/YAML/JSON/Python） |
| 9 | **Bootstrap First** | 每次会话必须先加载平台治理信息（Principles → ADR → Registry → Manifest） |

## 工程实践原则

### 10. Requirement Emergence（需求涌现原则）

> **需求不是输入（Input），而是迭代的产物（Output）。**

本条原则是 PAIOS 在实际工程开发中总结出的设计原则，非外部理论引用。

#### 发现过程

在白皮书从 Markdown 到 Word 的交付过程中历经 3 轮迭代：

```text
需求：生成技术白皮书
  ↓
第一次交付：Markdown 内容（完整，但用户需要 Word）
  ↓
第二次交付：.docx 文件（生成了，但内容为空 — 脚本 bug）
  ↓
第三次交付：56KB 完整 .docx（262 段内容，70 张表格）
```

真正变化的不只是输出格式，而是需求定义本身。最初的需求是"映射文档结构"，在迭代中逐渐展开为审计、生成、转换、修复、验证等一系列真实需求。

#### 双循环模型

```
循环一：修正需求（核心循环）
模糊想法 → 第一次实现 → 看到结果 → 发现真正问题 → 重新定义需求 → 再次实现 → 真实需求逐渐收敛

循环二：修正实现（传统认知）
已知需求 → 方案设计 → 实现 → 验证 → Bug 修复 → 完成
```

#### 与 Need Driven Promotion 的关系

| 原则 | 关注点 | 回答的问题 |
|------|--------|-----------|
| **Need Driven Promotion** | 什么时候应该增加功能 | 功能演化时机 |
| **Requirement Emergence** | 需求是如何形成的 | 需求发现过程 |

两者共同构成 PAIOS 在需求管理上的核心工程经验。

#### 对系统设计的影响

1. **Decision Layer 的首要职责不是选择方案，而是帮助用户发现真正的需求**
2. **Feedback 的最大价值不是修改 Bug，而是不断修正 Problem Definition**
3. **Prototype 的用途不是验证方案，而是帮助需求收敛**

#### PAIOS 自身的验证

```text
想做知识库 → 需要统一 Prompt → 需要统一规则 → 需要 Workflow → 需要 Governance → 需要 Decision Layer
```

每一步都不是预先规划的，而是在前一步的产出上发现了更深层的真实需求。

**Status**: Validated by Engineering Practice

---

## Architecture Freeze 策略

当前架构已冻结，修改顶层目录结构需满足以下**至少两条**：

1. 连续使用 **3 个月**以上
2. **两个或以上**真实项目暴露同一结构问题
3. **清晰的收益**且可接受的迁移成本

## 用户心智模型

```
我不要问"放哪里"，
我只问"交给 PAIOS 了吗？"
```

## 四个统一

| 统一 | 含义 |
|------|------|
| 输入统一（Single Entry） | 所有新内容先进入 Inbox |
| 判断统一（Lifecycle Routing） | 生命周期决定去向，不是目录 |
| 登记统一（Registry First） | 长期资产进入 Registry |
| 治理统一（Governance） | 长期演化遵循 ADR 与 Freeze Policy |

## 三条用户约定

1. **输入统一** — 任何新输入先进入 `00_CAPTURE/Inbox.md`，不思考分类，不决定目录
2. **生命周期路由** — 系统根据 Lifecycle 决定内容去向，用户不决定目录
3. **流程记忆** — 用户只记住流程（Capture → Route → Process），不记住目录路径

## AI Tool Bootstrap 流程

```
Workspace: ${PAIOS_DRIVE}:/PAIOS
     ↓
Bootstrap（加载平台治理信息）
  ├── Principles    — 了解平台规则
  ├── ADR           — 了解架构约束
  ├── Registry      — 发现可用能力
  └── Manifest      — 确认平台版本
     ↓
Read only what the current task requires
     ↓
Start working
```

---

**关联文档**：[00_Abstract.md](00_Abstract.md) | [03_Architecture.md](03_Architecture.md) | `30_SYSTEM/Principles.md` | `paios-philosophy.md`
