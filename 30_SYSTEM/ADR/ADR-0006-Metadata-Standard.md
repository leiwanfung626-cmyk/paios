# ADR-0006: 元数据标准（Metadata Standard）

## Status
Accepted

---

## Context
PAIOS 依赖元数据作为主要分类手段（Principle #7）。如果没有统一的元数据标准，不同知识条目的元数据格式不一致，AI 工具无法可靠地解析和检索。

---

## Decision
定义统一的 Metadata Schema，包含以下核心字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 唯一标识 |
| `type` | string | ✅ | 资产类型 |
| `lifecycle` | string | ✅ | 生命周期状态 |
| `version` | string | ✅ | 版本号 |
| `tags` | string[] | ✅ | 标签（至少 1 个） |
| `created` | datetime | ✅ | 创建时间 |
| `updated` | datetime | ✅ | 更新时间 |
| `related_adr` | string[] | 可选 | 关联 ADR |

Reference 类型扩展附加字段（最成熟的模板）：
- `ref_id`, `schema_version`, `summary`, `abstract`（Chunk 0）
- `verification.status`, `confidence`, `maintenance`

元数据存储方式：Markdown frontmatter（YAML 格式），与内容同文件。

---

## Rationale
- Frontmatter YAML 与 Markdown 结合，人类可读、机器可解析
- Principle #7 要求元数据为主要分类手段，Schema 必须标准化
- Reference 模板设计为 L3 Embedding-ready，abstract 字段作为向量索引的 Chunk 0
- 统一 Schema 确保 AI 工具可可靠解析

---

## Consequences
### Positive
- 所有知识条目结构一致，AI 可可靠解析
- 升级到 L3 Vector RAG 时无需重建数据模型

### Negative
- 创建条目时需要填写元数据，增加了创建成本
- 元数据字段的完整性和一致性需要维护

---

## Alternatives Considered
- **无元数据，纯目录分类** — 违反 Principle #7，检索能力受限
- **数据库存储元数据** — 增加系统复杂度，违反 Principle #3（工具无关）
- **JSON 元数据文件分离** — 维护两份文件的同步成本高

---

## Related
- Principle #7: Metadata is the primary classification system
- ADR-0004: Knowledge Layer Design
- `retrieve-evolution.md`（L0.5 Embedding Ready）
- `30_SYSTEM/Config/metadata.yaml`
