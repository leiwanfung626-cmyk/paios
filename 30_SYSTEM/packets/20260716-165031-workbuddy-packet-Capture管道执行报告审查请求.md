---
metadata:
  source: workbuddy
  type: packet
  created: 2026-07-16T16:50:31
  project: paios-core
  keywords: ['捕获', '管道', '执行报告', '审查']
  related: []
  status: captured
  promoted: true
  promoted_to: 30_SYSTEM/packets/20260716-165031-workbuddy-packet-Capture管道执行报告审查请求.md
---
# Capture管道执行报告审查请求

# PAIOS Capture Pipeline 执行报告与审查请求

## 1. 任务摘要

| 项 | 内容 |
|----|------|
| 来源包 | PAIOS-2026-0716-CAPTURE-PIPELINE-EXECUTION-001 |
| 执行引擎 | Reasonix WorkBuddy |
| 当前状态 | READY_FOR_REVIEW（执行完成，待其他 AI 审查） |
| 阶段 | Phase-4 STABILIZE / Day-2 |

执行范围：作为 Architecture Reviewer & Implementation Planner，
对 Capture Pipeline 进行需求审查、架构冲突裁决、目录骨架搭建、
管道脚本实现、设计 ADR 撰写与验证闭环。

---

## 2. 来源包逐项回应

### 2.1 Task Context

**原文问题**：
> AI生成物来源分散、文件生命周期不可追踪、临时内容易污染知识库、多实例同步存在边界风险、缺少统一入口治理机制

**执行反馈**：已全部覆盖。Capture Pipeline 定义了统一入口（00_CAPTURE/inbox）、元数据生命周期（status: captured→processing→promoted）、治理机制（禁止直写 20/30/40）、晋升路由表。

### 2.2 Core Decision

**原文原则**：
> 所有输入统一 Capture。所有知识必须经过治理晋升。

**执行反馈**：已采纳并落地。但补充一项**禁毒例外**（见 3.3）。

### 2.3 Target Architecture

**原文目标结构**：
```
00_CAPTURE/     10_INBOX_PROCESSING/    20_KNOWLEDGE/
30_SYSTEM/      40_AUTOMATION/          50_PROJECTS/    90_ARCHIVE/
```

**架构审查发现 3 处冲突，已全部裁决**：

| 冲突 | 诊断 | 裁决 |
|------|------|------|
| F1 编号碰撞 | `10_INBOX_PROCESSING` 与现有 `10_WORK` 冲突 | → `15_INBOX_PROCESSING`（夹在 10_WORK 与 20_KNOWLEDGE 之间） |
| F2 冗余层 | `50_PROJECTS` 与 `10_WORK` 职责重叠 | → 不新建，复用 `10_WORK` |
| F3 跨系统例外 | 禁毒数据归 G 盘，不应进入便携 Core 管道 | → 明文排除，走双盘协同 |

**调和后实际结构**：
```
00_CAPTURE/
├── inbox/         ← 结构化 AI 产出唯一入口
├── attachments/   ← 附件
├── incoming/      ← 外部流入
├── Daily/Images/Voice/Downloads/Imported/ ← 原始桶（保留）

15_INBOX_PROCESSING/
├── classified/   + PROMOTE_LOG.md
├── needs_review/
└── failed/

10_WORK/        ← 项目与活跃工作（复用，含 Projects）
20_KNOWLEDGE/   ← 长期知识
30_SYSTEM/      ← 系统文件 + pockets
40_AUTOMATION/  ← 管道脚本
90_ARCHIVE/     ← 归档
```

### 2.4 Required Workflow

**原文**：Stage-1 Capture + Stage-2 Metadata Extraction（命名 YYYYMMDD-HHMMSS-source-type-title.md）

**执行反馈**：已实现 Stage-1 至 Stage-3，且端到端验证通过。

```
Stage-1  capture.py → 00_CAPTURE/inbox/
Stage-2  capture.py 自动写 YAML 元数据头
Stage-3  classify_capture.py --apply → 路由到 20/30/40/10/15
```

Stage-4（归档至 90_ARCHIVE）未实现，留待 Phase-5。

---

## 3. 交付物清单

### 3.1 目录骨架
- `00_CAPTURE/{inbox,attachments,incoming}` — 3 个新目录
- `15_INBOX_PROCESSING/{classified,needs_review,failed}` — 3 个处理层子目录

### 3.2 管道脚本
- `40_AUTOMATION/05_SCRIPTS/capture.py` — Stage-1+2：
  - 按 `YYYYMMDD-HHMMSS-source-type-title.md` 命名落入 inbox
  - 自动生成 YAML 元数据（source/type/created/project/keywords/related/status）
  - 支持 `--body-file`、`--stdin`、`--attach`、`--dry-run`
- `40_AUTOMATION/05_SCRIPTS/classify_capture.py` — Stage-3：
  - 按 type 路由：governance/adr/decision/packet→30_SYSTEM, architecture/research/tech→20_KNOWLEDGE, project/doc→10_WORK
  - 晋升时改写 `promoted: true` + `promoted_to`，记录 `classified/PROMOTE_LOG.md`
  - 无元数据→failed，类型不明→needs_review
  - 默认 `--dry-run`，`--apply` 实际晋升

### 3.3 设计 ADR
- `30_SYSTEM/governance/20260716-163756-workbuddy-governance-Capture管道设计与实现.md`
- 含：架构审查记录、决策列表、调和后结构图、Stage 1-4 工作流、禁毒例外条款
- 端到端验证：经 capture.py 捕获 → classify_capture.py --apply 晋升

### 3.4 治理文档更新
- `00_CAPTURE/Inbox.md` — 新增 Capture Pipeline 入口说明 + 禁毒例外条款
- `.workbuddy/memory/MEMORY.md` — 固化 Capture Pipeline 约定

### 3.5 禁毒例外
禁毒宣传稿等敏感工作数据**不进便携 Core 管道**，生成即直达 G 盘
`G:\workspace\01_Projects\工作记录\2026\2026年禁毒简报\`。
与 `Inbox.md` 第43行既约定一致。

---

## 4. 待审查事项

以下决策和未决问题需要其他 AI 审查确认要求：

### ❓ Q1：处理层编号改为 `15_INBOX_PROCESSING`

执行包原案为 `10_INBOX_PROCESSING`，但 `10_WORK` 已占用 `10_` 槽。
裁决：改为 `15_`（夹在 10 与 20 之间）。请确认此编号调整是否可接受。
有无其他候选编号方案？

### ❓ Q2：不建 `50_PROJECTS`，复用 `10_WORK`

执行包原案新增 `50_PROJECTS`。裁决：职责与现有 `10_WORK` 重叠，
不新建以避免项目归属分裂。请确认。

### ❓ Q3：禁毒例外范围

已将禁毒类数据从 Capture Pipeline 范围中排除。需确认：
- 仅禁毒相关，还是所有 G 盘工作数据？
- 是否存在其他敏感数据类型也应排除？

### ❓ Q4：未实现的 Stage-4 Archive

归档（90_ARCHIVE）的晋升规则尚未实现。当前建议：显式标记 `archive`
或超龄 90 天的内容由人工/定时任务移入。建议在 Phase-5 实现自动化归档。

### ❓ Q5：每日自动晋升

`classify_capture.py` 目前需手动 `--apply`。是否需要我将其接入
WorkBuddy 定时任务（每日一次）？

---

## 5. 验收标准

- [x] `00_CAPTURE/{inbox,attachments,incoming}` 已创建
- [x] `15_INBOX_PROCESSING/{classified,needs_review,failed}` 已创建
- [x] `capture.py` 已实现并验证（支持 --body-file/--stdin/--attach/--auto）
- [x] `classify_capture.py` 已实现并验证（支持 --apply/--source/--dry-run）
- [x] 设计 ADR 端到端走通：capture→promote→30_SYSTEM/governance
- [x] `Inbox.md` 已更新 Capture Pipeline 入口规则
- [x] 记忆已固化到 MEMORY.md
- [x] 禁毒例外已明文排除（走 G 盘）
- [x] 编号冲突（F1）已裁决调和
- [x] 冗余层（F2）已裁决不建

---

## 6. 可追溯性

相关资源：

- Source: `PAIOS-2026-0716-CAPTURE-PIPELINE-EXECUTION-001`
- ADR: `30_SYSTEM/governance/20260716-163756-workbuddy-governance-Capture管道设计与实现.md`
- Scripts: `40_AUTOMATION/05_SCRIPTS/capture.py`, `classify_capture.py`
- Capture Inbox: `00_CAPTURE/inbox/`
- Processing: `15_INBOX_PROCESSING/`
- Inbox Rule: `00_CAPTURE/Inbox.md`
- Memory: `.workbuddy/memory/MEMORY.md`
- Daily: `.workbuddy/memory/2026-07-16.md`

---

## Final State

```yaml
packet_status: READY_FOR_REVIEW
resolution: EXECUTED_PENDING_REVIEW
executor: Reasonix_WorkBuddy
executor_role: Architecture_Reviewer_Implementation_Planner
target_reviewers:
  - ChatGPT
  - 豆包
  - 千问
  - 元宝
default_reviewer: Reasonix_WorkBuddy  # 回执确认
open_questions: 5  # Q1-Q5
follow_up:
  - Q1-Q5 reviewer decisions
  - Stage-4 Archive (Phase-5)
  - Daily promotion automation (if approved)
```

