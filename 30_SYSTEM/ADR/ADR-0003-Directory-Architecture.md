# ADR-0003: 七层目录架构

## Status
Accepted

---

## Context
PAIOS 需要一套表达知识生命周期的目录结构，而非传统的按主题分类的目录。传统笔记软件按主题分类导致用户需要思考"放哪里"，增加了认知负担。

同时，系统需要一个清晰的目录路由规则，让 AI 工具和用户都能理解每层目录的职责。

---

## Decision
采用 7 层目录架构，外加 2 个辅助目录：

```
${PAIOS_DRIVE}:/PAIOS/
├── 00_CAPTURE/     # 信息入口（Inbox）
├── 10_WORK/        # 工作区（临时）
├── 20_KNOWLEDGE/   # 知识库（已验证）
├── 30_SYSTEM/      # 系统内核
├── 40_AUTOMATION/  # 自动化引擎
├── 50_DATA/        # 数据基础设施
├── 60_EXTERNAL/    # 外部引用
├── 70_TMP/         # 运行时临时文件
└── 90_ARCHIVE/     # 历史归档
```

数字前缀表达生命周期阶段：00 捕获 → 10 工作 → 20 知识 → 30 系统 → 40 自动化 → 50 数据 → 60 外部 → 90 归档。

---

## Rationale
- 目录表达生命周期而非内容分类（Principle #1）
- 每层职责明确，路由规则清晰（Capture → Work → Knowledge → System → Automation → Archive）
- 数字前缀自动排序，无需维护索引
- 用户只记住流程（Capture → Route → Process），不记住目录路径

---

## Consequences
### Positive
- 用户不再需要思考"放哪里"，生命周期自动路由
- 隐藏层（50_DATA、70_TMP）保护运行时数据不被误提交

### Negative
- 初期需要适应非传统目录思维
- 前 3 层（00/10/20）暂为空目录，需要内容填充

---

## Alternatives Considered
- **按主题分类**（传统的笔记软件方式）— 违反 Principle #1，增加分类压力
- **按文件类型分类** — 混合生命周期与类型，路由规则不清晰
- **单层扁平结构** — 无生命周期表达，无法支撑系统演化

---

## Related
- Principle #1: Directories express lifecycle, not content
- Principle #6: Keep the top-level directory count low
- `paios-philosophy.md`
