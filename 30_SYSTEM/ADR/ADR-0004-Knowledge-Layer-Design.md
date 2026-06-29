# ADR-0004: 知识层设计（20_KNOWLEDGE）

## Status
Accepted

---

## Context
知识库是 PAIOS 的核心资产层，需要结构化分类以支持高效检索和 AI 理解。同时必须保持灵活性，不因分类方式限制知识的表达。

---

## Decision
知识库分为 6 个领域，每个领域使用统一模板 + 元数据：

| 领域 | 内容 | 模板复杂度 |
|------|------|-----------|
| **Concepts**（概念） | 领域概念、定义、原理 | 基础 |
| **Methods**（方法） | 可复用的方法流程 | 基础 |
| **SOP**（标准流程） | 标准操作流程 | 基础 |
| **Decisions**（决策） | 决策记录与经验 | 基础 |
| **Models**（模型） | 思维模型、分析框架 | 基础 |
| **References**（参考资料） | 外部资料、工具、论文 | 最成熟（29字段） |

每个领域包含：
- `README.md` — 领域说明
- `_index.md` — 索引
- `_template.md` — 标准化模板

---

## Rationale
- Principle #7（Metadata is primary classification）：目录只作为粗粒度分类，元数据作为精粒度分类
- Reference 模板设计为 L3 Embedding-ready（abstract 作为 Chunk 0）
- 统一模板确保 AI 工具可理解每条知识的结构
- 6 个领域覆盖常见知识类型，不过多也不过少

---

## Consequences
### Positive
- 知识条目不依赖目录深度，元数据可无限扩展
- 新知识类型可通过新增元数据字段支持，无需调整目录

### Negative
- 对元数据质量有较高要求（填写不完整会影响检索）
- 初期知识条目较少，看起来"空"

---

## Alternatives Considered
- **单目录扁平存储** — 检索困难，无分类维度
- **按来源分类**（网页/书籍/对话）— 混合了分类和来源，不符合 Principle #7
- **深度嵌套目录** — 违反 Principle #1，给用户增加分类压力

---

## Related
- Principle #4: Knowledge must be validated before entering the knowledge base
- Principle #7: Metadata is the primary classification system
- `20_KNOWLEDGE/`
- `retrieve-evolution.md`（L0.5 Embedding Ready）
