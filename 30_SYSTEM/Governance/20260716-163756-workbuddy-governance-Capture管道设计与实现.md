---
metadata:
  source: workbuddy
  type: governance
  created: 2026-07-16T16:37:56
  project: paios-core
  keywords: ['捕获', '管道', '治理']
  related: []
  status: captured
  promoted: true
  promoted_to: 30_SYSTEM/governance/20260716-163756-workbuddy-governance-Capture管道设计与实现.md
---
# Capture管道设计与实现

# PAIOS Capture Pipeline 设计与实现（ADR）

- 状态：ACCEPTED（bootstrap）
- 日期：2026-07-16
- 阶段：Phase-4 STABILIZE / Day-2
- 来源包：PAIOS-2026-0716-CAPTURE-PIPELINE-EXECUTION-001

## 1. 背景与问题

PAIOS-PORTABLE 进入 Phase-4 多 AI 协同阶段，持续产生 Pocket/Packet、ADR 草案、
架构分析、技术方案、项目文档、研究资料、决策记录。原有问题：

1. AI 生成物来源分散（ChatGPT / WorkBuddy / 豆包 / 千问 / 元宝）
2. 文件生命周期不可追踪
3. 临时内容易污染知识库（20_KNOWLEDGE / 30_SYSTEM）
4. 多实例同步存在边界风险
5. 缺少统一入口治理机制

核心理念：**所有输入统一 Capture，所有知识必须经过治理晋升。**

## 2. 架构审查发现（与现有布局的冲突）

执行包目标架构与 `D:\PAIOS-PORTABLE\Core` 现状存在三处冲突，已裁决：

- **F1 编号碰撞**：执行包将处理中间层定为 `10_INBOX_PROCESSING`，但 `10_WORK`
  已占用 `10_`（含 Active/Done/Review/Waiting 等 GTD 工作层）。裁决：处理层
  **重新编号为 `15_INBOX_PROCESSING`**，语义上夹在 10_WORK 与 20_KNOWLEDGE 之间，
  符合"捕获→处理→知识"的流向。
- **F2 冗余层**：执行包新增 `50_PROJECTS`，但 `10_WORK` 本就承担项目交付物。
  裁决：**不新建 `50_PROJECTS`**，项目统一归 `10_WORK`，避免项目归属分裂。
- **F3 跨系统例外**：执行包"禁止 AI 直写 20/30/40"规则适用于**便携 Core 系统内部**。
  禁毒类敏感工作数据按双盘协同规则归 **G 盘**（`G:\workspace\...2026年禁毒简报\`），
  属另一系统，不在本管道治理范围（见第 6 节）。

现状 `00_CAPTURE` 下已有 `Daily / Downloads / Images / Imported / Voice` 及 `Inbox.md`，
它们作为"原始快速捕获桶"保留，与新增的 `inbox / attachments / incoming` 并存——
原始桶是原始素材入口，`inbox` 是**结构化 AI 产出**入口，二者不冲突。

## 3. 决策

| 项 | 决策 |
|----|------|
| 唯一入口 | `00_CAPTURE/inbox`（结构化 AI 产出）；原始素材仍可用 Daily/Images/Voice |
| 禁止直写 | AI 日常产出禁止直写 20_KNOWLEDGE / 30_SYSTEM / 40_AUTOMATION |
| 唯一晋升通道 | `classify_capture.py` 是唯一被允许写入上述层的机制 |
| 处理层 | `15_INBOX_PROCESSING/{classified,needs_review,failed}` |
| 项目层 | 复用 `10_WORK`，不新建 `50_PROJECTS` |
| 禁毒例外 | 走 G 盘双盘协同，不进便携 Core 管道 |

## 4. 目标结构（调和后）

```
00_CAPTURE/
├── inbox/          # 结构化 AI 产出唯一入口（Stage-1）
├── attachments/    # 附件（图片/文档）落点
├── incoming/       # 外部流入待认领
├── Daily/ Images/ Voice/ Downloads/ Imported/   # 原始快速捕获桶（保留）
└── Inbox.md        # 统一索引

15_INBOX_PROCESSING/   # Stage-2/3 中间层
├── classified/        # 已晋升记录 + PROMOTE_LOG.md
├── needs_review/      # 类型不明 / 待人工确认
└── failed/            # 无元数据 / 解析失败

10_WORK/          # 项目与活跃工作（复用，含 Projects）
20_KNOWLEDGE/     # 长期知识：architecture/research/tech/lessons
30_SYSTEM/        # 系统自身：ADR/governance/registry/bootstrap/packets
40_AUTOMATION/    # 自动化：pipeline/classifier/scripts（capture.py 在此）
90_ARCHIVE/       # 历史归档
```

## 5. 工作流（Stage 1-4）

**Stage-1 Capture**：AI 产出 → `00_CAPTURE/inbox`，命名
`YYYYMMDD-HHMMSS-source-type-title.md`。

**Stage-2 Metadata Extraction**：自动写入 YAML 头
`source / type / created / project / keywords / related / status / promoted`。

**Stage-3 Promotion**：`classify_capture.py` 读元数据，按 `type` 路由：
- governance/adr/decision/packet → 30_SYSTEM
- architecture/research/tech/lessons → 20_KNOWLEDGE
- project/doc → 10_WORK
- 不明 → 15_INBOX_PROCESSING/needs_review
- 无元数据 → 15_INBOX_PROCESSING/failed
晋升时改写 `promoted: true` + `promoted_to`，并记 `classified/PROMOTE_LOG.md`。

**Stage-4 Archive**：显式标记 `archive` 或超龄内容 → 90_ARCHIVE。

## 6. 禁毒例外（双盘协同）

禁毒宣传稿等敏感工作数据**不进入便携 Core 管道**，生成即直达 G 盘
`G:\workspace\01_Projects\工作记录\2026\2026年禁毒简报\`。此例外与
`00_CAPTURE/Inbox.md` 第43行既有约定一致（"0703 禁毒文件未走 Inbox 流程，
按双盘协同规则直接路由到 G 盘"）。便携 Core 的 Capture Pipeline 仅治理
非敏感、可携带的 AI 协同产出。

## 7. 工具

- `40_AUTOMATION/05_SCRIPTS/capture.py`：Stage-1+2，生成命名文件 + 元数据。
- `40_AUTOMATION/05_SCRIPTS/classify_capture.py`：Stage-3，晋升路由
  （默认 `--dry-run`，`--apply` 实际移动）。

## 8. Bootstrap 说明

本设计文档本身是管道的"第 0 个样本"：经 `capture.py` 落入 `00_CAPTURE/inbox`，
再经 `classify_capture.py --apply` 晋升至 `30_SYSTEM/governance/`。此 bootstrap
例外（直接落地治理文档）仅在管道尚未存在时允许，此后所有写入必须走管道。

## 9. 后续

- 将 `classify_capture.py` 接入定时任务（每日 --apply 一次）。
- 在 WorkBuddy 约定中固化：生成物默认走 capture.py。
- 多实例（PAIOS-PORTABLE-001 等）同步时仅同步已晋升层，inbox/processing 不跨实例。

