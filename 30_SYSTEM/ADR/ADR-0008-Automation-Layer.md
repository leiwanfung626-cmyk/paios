# ADR-0008: 自动化层设计（Automation Layer）

## Status
Accepted

> **2026-07-12 修正**：实际目录已扩展至 16 个子目录。
> 新增 `04_ADAPTERS`（适配器接口）、`10_TRACES`（跨引擎 Trace 中枢）、`11_ENGINES`（引擎运行时状态）、`12_SCHEDULER`（调度器）、`QuarkSync`（夸克同步配置）。
> 以下目录树已更新以反映当前结构。

---

## Context
自动化层（40_AUTOMATION）需要与知识层（20_KNOWLEDGE）解耦（Invariant #4），同时具备扩展能力以承载未来的自动化需求。

---

## Decision
自动化层采用 **Registry First 架构**，包含 16 个子目录：

```
40_AUTOMATION/
├── 00_REGISTRY/     # 注册中心（agents/capabilities/providers/scripts/workflows/adapters）
├── 01_CAPABILITIES/ # 能力定义
├── 02_PROMPTS/      # 提示词库（coder/planner/reviewer/system/teacher/writer）
├── 03_AGENTS/       # Agent 定义
├── 04_ADAPTERS/     # 引擎适配器（read_trace/export_context/probe） ⭐
├── 04_MCP/          # MCP 接口（Reasonix 预留）
├── 05_SCRIPTS/      # 脚本（fleet-push/classify_files/vision_query 等）
├── 06_PROVIDERS/    # 提供商定义
├── 07_WORKFLOWS/    # 工作流定义
├── 08_TESTS/        # 测试
├── 09_LEGACY/       # 历史资产（deprecated/original/pending/promoted）
├── 10_MANIFEST/     # 清单与状态
├── 10_TRACES/       # 跨引擎 Trace 中枢（handoff/artifact/schema） ⭐
├── 11_ENGINES/      # 引擎运行时状态 ⭐
├── 12_SCHEDULER/    # 引擎调度器（policy/rules/log） ⭐
└── QuarkSync/       # 夸克同步配置
```

核心规则：
1. **所有长期资产必须先注册再使用**
2. **自动化产出物（索引、缓存、向量库）不进入 20_KNOWLEDGE**
3. **Registry 只反映现实状态，不占位注册**

---

## Rationale
- Invariant #4（知识与自动化解耦）：20_KNOWLEDGE 只存放知识，40_AUTOMATION 只存放工作流
- Registry First 确保 AI 工具可发现所有可用能力
- 09_LEGACY 保留历史资产，遵循 Need Driven Promotion

---

## Consequences
### Positive
- 知识层与自动化层完全解耦，互不污染
- Registry 提供统一的能力发现入口
- Legacy 结构支持平滑迁移

### Negative
- 需要在 Registry 中维护资产状态，增加了管理成本
- 两个层之间的交互需要明确的接口定义

---

## Alternatives Considered
- **知识层与自动化层混合** — 违反 Invariant #4，知识库被运行时产物污染
- **无 Registry，按目录自动发现** — 目录结构不足以表达资产间的依赖关系
- **数据库驱动的注册中心** — 违反 Principle #3（工具无关），增加复杂度

---

## Related
- Invariant #4: Knowledge-Automation Decoupling
- ADR-0002: Automation Platform Freeze
- ADR-0003: Directory Architecture
- `40_AUTOMATION/`
