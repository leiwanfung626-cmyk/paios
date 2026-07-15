---
title: "ADR-0017 — Platform Purity & Physical Separation of Core / Workspace / Instance-State"
status: Accepted
evidence_level: Validated
date: 2026-07-11
related:
  - ADR-0012-Platform-Application-Architecture.md
  - ADR-0013-Federated-Instance-Manifest.md
  - ADR-0014-Upgrade-Mechanism.md
  - ADR-0015-Federated-Aggregation-Viewing.md
  - ADR-0016-Multi-Instance-Architecture-Baseline.md
  - ../Evolution/Case-Studies/CASE-001-Multi-Instance-First-Convergence.md
  - ../Evolution/Phase-B-Core-Workspace-Split.md
---

# ADR-0017 — Platform Purity & Physical Separation

## Decision Traceability（决策可追溯性）

> 本 ADR 遵循 `30_SYSTEM/Governance/Decision-Traceability.md` 四字段规范。

- **Evidence**: CASE-001 (Multi-Instance First Convergence, Validated)
- **Implements**: Phase B Blueprint v2
- **Frozen By**: 472e53d (design freeze, unpushed)
- **Supersedes**: ADR-0016 §Phase B draft

> 类型：**Reactive ADR**——由真实运行证据（CASE-001）触发，非前瞻预判。前瞻型（Proactive）ADR 须自带验证条件并在真实运行后完成验证或修订（见 `Decision-Traceability.md` §4）。

## Summary（摘要）

首次真实多实例并流（CASE-001）提供了 **Validated** 级证据，证明 ADR-0016 提出的 Phase B 触发条件已命中。本 ADR 据此正式决策：将 PAIOS 的仓库内容按 **Platform Purity Principle（平台纯度原则）** 拆为三桶——**Core / Workspace / Instance-State**，并分阶段（B1 逻辑隔离 → B2 物理隔离）落地。

## Context（背景）

CASE-001（2026-07-11）记录：三个实例（work / personal / study）全部升级至 v1.0.1 并首次并流，实测暴露四个真实缺陷：

1. `PAIOS-Usage/manifest.yaml` 单路径冲突（远端被覆盖）
2. 用户 Workspace（`10_WORK/photos_organizer`、`20_KNOWLEDGE/References/Kaoyan-*`、`Today.md` 等）被推入共享 Core 仓库
3. Fleet 出现仓库内 / 仓库外两个位置
4. 两套 Manifest 系统（`collect_manifest.py` vs `40_AUTOMATION/10_MANIFEST/`）撞车

这些不是理论风险，是 `git` 实测事实。据此，Phase B 从"未来可能"转为"现在必须"。

## Decision（决策）

### D0 — Platform Purity Principle（核心判断标准，v2 升级）

> **Core 仅保存"定义平台能力"的内容，不保存任何仅记录平台使用、用户资产、用户状态、项目内容或个人知识。**
>
> 判断一个文件归属，只问一句（**两层级**）：
> **"这个文件是在定义平台能力，还是仅仅记录平台使用？"**
> - **定义平台能力** → 进 Core
> - **仅记录平台使用** → 进 Workspace

**为什么从"别人 pull 有价值吗"升级到"是否定义平台能力"**：前者偏**共享视角**（有价值 ≠ 是平台），会出现"Growth 思考 / 文章"别人 pull 有价值、却不是平台能力的灰色地带；后者直接问**架构边界**（是不是平台能力），长期更稳定、更纯。

| 文件 | 别人 pull 有价值？ | 定义平台能力？ | 归属 |
|------|:---:|:---:|------|
| ADR | ✅ | ✅ | Core |
| Capability / Workflow | ✅ | ✅ | Core |
| Patterns / Architecture | ✅ | ✅ | Core |
| Growth 思考 / 文章 | ✅ | ❌ | **Workspace**（仅记录使用） |
| 考研笔记 | ❌ | ❌ | Workspace |
| Today / 日更状态 | ❌ | ❌ | Workspace |

→ 判断**先问"是不是平台能力"**；不是，直接归 Workspace。这样 Platform Purity 更纯。

### D1 — 三桶物理隔离

| 桶 | 内容 | 同步策略 |
|----|------|----------|
| **Core** | 平台能力：Architecture / ADR / Patterns / **Registry/**（capabilities·providers·workflow·schema）/ Scripts / Installer / Upgrade / Release / Evolution / Governance / Manifest Schema | 所有实例 `git pull` 共享 |
| **Workspace** | 用户资产：项目、个人知识、照片、日更状态、PAIOS-Usage（本机） | 每机私有，`gitignore`，**绝不进 Core** |
| **Instance-State** | 各 `case-XX.yaml`（Manifest） | **单向**流向 Developer 的 `F:\Fleet\manifests\`，**不回推**用户 |

### D2 — 20_KNOWLEDGE：拆内容，不拆目录

`20_KNOWLEDGE/` 含两类性质不同的东西：
- **Platform**（Growth OS / PAIOS / Architecture / Patterns / ADR 引用 / Capability / Workflow）→ 属 Core，**保留共享**
- **Personal**（考研 / OpenWrt / 照片 / 个人资料）→ 属 Workspace，**私有**

→ 目录内部分 `Platform/` 与 `Personal/`，仅 `Personal/` 进入 `.gitignore`。**不整体 gitignore `20_KNOWLEDGE/`。**

### D3 — 10_WORK：全部私有，但平台工具迁出

`10_WORK/` 整体私有（`gitignore`）。**前提**：平台工具（installer / deployment / automation 脚本）不再放 `10_WORK`，统一迁入 `40_AUTOMATION`。这样 `10_WORK` 才能干净地全私有。

### D4 — Fleet：仓库外 + 子结构

仅保留 `F:\Fleet`（仓库外）。删除仓库内 `Fleet/cases/`。`F:\Fleet` 内部标准化子目录：

```
F:\Fleet\
├─ incoming/    各实例 publish 进来的 case-XX.yaml（原始）
├─ history/     按日期归档的历史快照（如 2026-07-11/）
├─ reports/     人工/自动生成的周报（fleet-weekly.md）
├─ stats/       聚合统计缓存
└─ dashboards/  HTML Dashboard（Phase B 后）
```

> **Manifest 版本自声明**：Manifest 自带 `manifest_version`（当前 `1`，由 `collect_manifest.py` 输出）。Fleet **不解析兼容逻辑**——只按声明版本归档/分流；`collect_manifest.py` 升级时 bump 该字段并保留旧版读取兼容。Developer 聚合以 Manifest 自声明版本为准，不靠 Fleet 猜。

### D5 — Manifest：collect → publish → Fleet

将"直接 copy"升级为显式 **publish** 动作：

```
collect_manifest.py  →  publish  →  F:\Fleet\incoming\case-XX.yaml
```

`publish` 是可扩展传输抽象，未来可接 git / http / api / usb / email，不必现在实现，但语义上先确立。

### D6 — Canonical Manifest 唯一

保留 `collect_manifest.py`（SCRIPT-0009）为唯一 canonical 生成器；删去远程的 `40_AUTOMATION/10_MANIFEST/`（撞车系统）。

### D7 — 分阶段落地（关键修正）

**不一次性 `git rm --cached`**；且**建立边界 ≠ 物理拆分**。原因：当前仅三实例、分类边界尚在稳定，过早物理隔离会反复折腾；且"逻辑隔离"命名易被误读为"已开始拆分"。

执行节奏（详见 `../Evolution/Phase-B-Core-Workspace-Split.md`）：

- **Step 2 — Establish Boundaries（Governance）**：只明确职责、调整目录、新建结构、更新 Registry/SOP、写 `.gitignore`。**不拆任何物理文件**。提交信息 `refactor(governance): establish Core/Workspace boundaries`。
- **Pilot Gate**：Step 2 后先用 Case-01（Developer 角色）单实例试点约两周，验证 manifest/Fleet/publish/registry/upgrade 全部正常，再过闸推广 Case-02/03。
- **Step 3 — Git Cleanup**：单独提交解决远端分叉（`chore(git): merge remote`），与边界实施分离。
- **Step 4 — Physical Separation**：Pilot 过闸、分类稳定后，才 `git rm --cached` 取消跟踪（磁盘保留），提交信息 `refactor(core): physical separation via git rm --cached`。

## Consequences（后果）

**正面**
- Core 回到"只有平台"，多实例模型真正站得住。
- Platform Purity Principle 提供可复用的文件归属判断，降低未来分类争论。
- 分阶段降低返工风险，符合 Need-Driven。

**负面 / 成本**
- B1 期间仓库仍含 Workspace 内容，存在短暂不一致（可接受，因当前三实例均 Evan 操作，无第三方隐私风险）。
- 需将既有平台工具从 `10_WORK` 迁至 `40_AUTOMATION`（一次性整理成本）。
- 远程 `caf3033` 与本地分叉需先 merge 再执行 B1；merge 须避免把 case-03 manifest 写回本机 PAIOS-Usage（Case-01 manifest 已安全存 `F:\Fleet\manifests\case-01.yaml`）。

## Validation（验证）

Phase B 完成后，连续多版本观察以下指标不再出现，即认定验证完成（详见 CASE-001）：
- Manifest 冲突（单路径覆盖）
- Workspace 泄漏（用户内容进 Core）
- Fleet 回流（用户 pull 到 Fleet）
- 因共享 Workspace 导致的 Merge 冲突

## Related

- `ADR-0012-Platform-Application-Architecture.md` · `ADR-0013-Federated-Instance-Manifest.md` · `ADR-0014-Upgrade-Mechanism.md` · `ADR-0015-Federated-Aggregation-Viewing.md` · `ADR-0016-Multi-Instance-Architecture-Baseline.md`
- `../Evolution/Case-Studies/CASE-001-Multi-Instance-First-Convergence.md`（本 ADR 的证据源）
- `../Evolution/Phase-B-Core-Workspace-Split.md`（执行蓝图，已按本 ADR 修正为 B1/B2 分阶段）
