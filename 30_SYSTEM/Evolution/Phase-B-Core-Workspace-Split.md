# Phase B — Core / Workspace / Instance-State 物理拆分（设计蓝图 v2）

> 状态：**Approved-with-refinements（蓝图已采纳，执行按 Step2 建立边界 → Pilot Gate → Step3 Git Cleanup → Step4 物理隔离）**
> 决策依据：**ADR-0017（Platform Purity & Physical Separation，Accepted）**
> 证据来源：**CASE-001-Multi-Instance-First-Convergence（Validated）**
> 触发：ADR-0016 Phase B 触发条件命中（第二实例暴露分发痛点，git 实测）
> 治理规范：本阶段遵循 **Governance 层**（`Architecture-Lifecycle` / `Decision-Traceability` / `Pilot-Gate` / `Rollout` / `Change-Control`），Asset Class 引用 `Specifications/Asset-Class.md`；蓝图只引用、不内联实现。

---

## 0. 现状诊断（git 实测事实，见 CASE-001）

2026-07-11，本地 (`6f09441`) 与远端 (`caf3033`) 分叉，远端多 9 提交 / 89 文件 / +11943 行，暴露四个真实缺陷：

1. **Manifest 单路径冲突**：`PAIOS-Usage/manifest.yaml` 被 case-03 覆盖
2. **Workspace 泄漏进 Core**：`10_WORK/photos_organizer`、`20_KNOWLEDGE/References/Kaoyan-*`、`Today.md`、`30_SYSTEM/Goals|Metrics` 等进共享仓库
3. **Fleet 双位置**：仓库外 `F:\Fleet` vs 仓库内 `F:\PAIOS\Fleet\cases`
4. **两套 Manifest 系统**：`collect_manifest.py` vs `40_AUTOMATION/10_MANIFEST/`

> 校准：三实例目前均由 Evan 在两台机器操作，暂无第三方隐私风险；但架构正确性必须修。

---

## 1. 目标架构（Platform Purity Principle 驱动）

核心判断标准（ADR-0017 D0，已升级为"是否定义平台能力"）：
> **"这个文件是在定义平台能力，还是仅仅记录平台使用？"**
> - 定义平台能力 → Core
> - 仅记录使用 → Workspace

### 1.1 资产类别（Asset Class）— 引用 `Specifications/Asset-Class.md`

Platform Purity Principle（ADR-0017 D0）只回答"进 Core 还是 Workspace"。内容**如何分类、未来如何扩展**，由独立的 **`30_SYSTEM/Specifications/Asset-Class.md`** 定义可扩展分类轴 `Platform / Shared / Personal / Imported`——它不隶属于 `20_KNOWLEDGE`，而是跨目录、跨桶的统一分类标准（同样适用于 `10_WORK/`、`Fleet/` 等）。

- 当前 Phase B 只落地 **Platform** 与 **Personal** 两类边界（`20_KNOWLEDGE/Platform/` 共享、`/Personal/` 私有）；**Shared / Imported** 预留分类位。
- 扩展规则：新增类别只在分类轴加一行，不改动 Principle、不新增"Registry X"式特例。
- 判定顺序：先问 Platform Purity（是不是平台能力 → Core / Workspace），再问 Asset Class（归属哪一类 → 目录组织）。详见规范文档。

### Core（tracked，所有实例 git pull 共享）

```
PAIOS Core 仓库
├─ 30_SYSTEM/
│   ├─ ADR/              平台决策（含 FIM 四件套 + ADR-0017）
│   ├─ SOP/              发布/采集等平台 SOP
│   ├─ Evolution/        路线图 / 复盘 / Case-Studies（方法论，非个人状态）
│   ├─ Patterns/         ⭐ 新增：平台模式库
│   └─ Registry/         ⭐ 新增：统一注册表（未来 Plugin/Tool/Agent 复用同一结构）
│        ├─ capabilities/   能力注册表
│        ├─ providers/      Provider 注册表
│        ├─ workflow/       工作流注册表
│        └─ schema/         注册表 schema（版本化）
├─ 40_AUTOMATION/        ⭐ 平台工具统一入口（installer/deploy/automation 脚本迁此）
│   └─ 05_SCRIPTS/collect_manifest.py  ← 唯一 canonical manifest 生成器
├─ RELEASES/             发布说明 + 升级通知 + 回执
├─ Specifications/       FIM-v1 等协议规范
├─ CHANGELOG / SYSTEM_VERSION / MANIFEST.json / README / DEPLOYMENT / SYNC_STRATEGY
└─ scripts/ / .githooks/ / .gitignore
```

### Workspace（每机私有，gitignored，绝不进 Core）

```
Workspace（本地私有）
├─ 10_WORK/                       ⭐ 全部私有（平台工具已迁出至 40_AUTOMATION）
├─ 20_KNOWLEDGE/
│   ├─ Platform/    ⭐ 保留共享（Growth OS / PAIOS / Architecture / Patterns / ADR 引用 / Capability / Workflow）
│   └─ Personal/    ⭐ 私有（考研 / OpenWrt / 照片 / 个人资料）
├─ 00_CAPTURE/  /  30_SYSTEM/Goals|Metrics|Principles|photo/
├─ 90_ARCHIVE/<项目>/
├─ Today.md  /  PAIOS-Usage/(本机)  /  QuarkSync/
```

### Instance-State（单向流向 Developer，不回推）

```
collect_manifest.py  →  publish  →  F:\Fleet\incoming\case-XX.yaml
                                    （未来 publish 可接 git/http/api/usb/email）
```

---

## 2. 决策采纳表（ADR-0017，源自用户评审）

| 项 | 用户裁定 | 落地 |
|----|---------|------|
| Core / Workspace 拆分 | ✅ 立即开始 | ADR-0017 D1 |
| Fleet 仓库外 | ✅ 同意 | `F:\Fleet`，删仓库内 `Fleet/cases/` |
| Manifest 单向汇总 | ✅ 同意 | Instance-State 桶 |
| Canonical Manifest 唯一 | ✅ 同意 | 删 `40_AUTOMATION/10_MANIFEST/` |
| 10_WORK 全部私有 | ✅ 同意 | 前提：平台工具迁 `40_AUTOMATION` |
| 20_KNOWLEDGE 全部私有 | ❌ 不采纳 | **拆内容不拆目录**：Platform/ 共享，Personal/ 私有 |
| git rm --cached 一次性 | ⚠️ 延后 | 改为 Step2 建立边界(Governance) → Pilot Gate → Step4 物理隔离(git rm --cached)，分类稳定且 Pilot 过闸后 |
| Platform Purity Principle | ✅ 作为核心判断 | ADR-0017 D0 |

---

## 3. `.gitignore` 修订（union 两边 + Phase B 排除）

```gitignore
# ===== 既有 =====
*.docx *.pdf *.zip *.exe
.reasonix/ .workbuddy/ .codebuddy/
00_CAPTURE/Downloads/ 70_TMP/ 50_DATA/ 50_IMPORT/
__pycache__/ .venv/ .DS_Store .env

# ===== 远程已有的 photos_organizer 数据规则（保留） =====
10_WORK/photos_organizer/database/ 10_WORK/photos_organizer/models/
10_WORK/photos_organizer/inputs/ 10_WORK/photos_organizer/outputs/
10_WORK/photos_organizer/face_index/face_index.db
10_WORK/photos_organizer/face_index/faiss_index.bin
10_WORK/photos_organizer/face_index/*.npy
10_WORK/photos_organizer/face_index/{faces,export,retrieval}/  *.log
10_WORK/photos_organizer/scripts/*.log *.txt

# ===== Phase B：Workspace 永不进 Core（ADR-0017 Platform Purity） =====
10_WORK/
20_KNOWLEDGE/Personal/
00_CAPTURE/
30_SYSTEM/Goals/ 30_SYSTEM/Metrics.md 30_SYSTEM/Principles.md 30_SYSTEM/photo/
90_ARCHIVE/
Today.md
PAIOS-Usage/
QuarkSync/

# ===== Phase B：Fleet 仅 Developer 仓库外（ADR-0015/0017） =====
Fleet/

# ===== 环境自管理 =====
reasonix.toml
```

> 关键修正（vs v1 蓝图）：**不再整体 `gitignore 20_KNOWLEDGE/`**，改为仅 `20_KNOWLEDGE/Personal/`，保留 `Platform/` 共享。

---

## 4. 执行步骤（分阶段；命令为"提议"，待各自启动令）

> **关键命名纪律**：本蓝图刻意区分两类动作——
> - **Establish Boundaries（Governance）**：只明确职责、调整目录、新建结构、更新 Registry/SOP、写 `.gitignore`。**不拆任何物理文件**。
> - **Physical Separation**：只有 `git rm --cached` 才叫物理隔离。
> 前期所有"逻辑隔离"命名统一改为"建立边界"，避免 Git History 被误读成"已开始拆分"。

### Commit 节奏（Git History 一眼可读）

| Commit | 类型 | 提交信息 | 实质 |
|--------|------|----------|------|
| **1** | Architecture | `docs(architecture): introduce evidence-driven governance and Phase B blueprint`（已落地 `472e53d`，未 push） | 设计冻结 |
| **2** | Governance | `refactor(governance): establish Core/Workspace boundaries` | 建立边界（不拆物理） |
| **3** | Git Cleanup | `chore(git): merge remote after boundary prep` | 解决分叉 / 冲突 |
| **4** | Physical Separation | `refactor(core): physical separation via git rm --cached` | 真正物理隔离 |

### Step 2 — Establish Boundaries（Governance，不物理拆分）

1. **本地备份锚点**：`git tag pre-phaseb-backup HEAD`
2. **确立目录职责**：本机创建 `20_KNOWLEDGE/Platform/` 与 `20_KNOWLEDGE/Personal/`，将个人知识移入 Personal/；将 `10_WORK/` 中平台工具迁出至 `40_AUTOMATION/`。
3. **写入新 `.gitignore`**（第 3 节）。
4. **收敛 Manifest**：标记 `40_AUTOMATION/10_MANIFEST/` 为废弃（Step 4 删除）。
5. **Fleet 子结构初始化**：`F:\Fleet\{incoming,history,reports,stats,dashboards\}`；将现有三份 manifest 移入 `incoming/`。
   - **版本自声明**：Manifest 自带 `manifest_version`（当前 `1`，由 `collect_manifest.py` 输出），Fleet **不解析兼容逻辑**、只按声明版本归档；`collect_manifest.py` 升级时 bump 该字段并保留旧版读取。Fleet 不负责"猜"版本。
   - 可选：`incoming/v1/ v2/` 按 schema 版本分桶，便于 Developer 做版本化聚合。
6. **更新 Registry / SOP**：`scripts.yaml` 标注 `collect_manifest.py` 为 canonical；SOP 增补 `publish` 语义。
7. **commit（不 push）**：`refactor(governance): establish Core/Workspace boundaries`。
8. **观察两周**：期间继续真实使用，记录是否仍有分类歧义。

### Pilot Gate（试点门槛，Step 2 之后、Step 4 之前）

Step 2 完成后**不要立即让三实例全部切换**，先过试点门槛。Pilot Gate 已抽离为独立规范：**`30_SYSTEM/Governance/Pilot-Gate.md`**（Entry / Exit Criteria + 单实例试点模式），过闸后的分批推广见 **`30_SYSTEM/Governance/Rollout.md`**。

本 Phase 的关键参数（供规范引用）：
- **Pilot = Case-01（Developer）**：三实例分饰 Developer / Personal / Study，Case-01 天然即 Pilot，无需额外搭环境。
- **Pilot 期间验证信号**：`collect_manifest.py` 正常生成 manifest（含 `manifest_version`）；`publish` 正常流入 `F:\Fleet\incoming\`；`F:\Fleet` 子结构工作正常；`scripts.yaml` Registry 读取正常；`upgrade` 路径无碍。
- **Pilot Exit（全部满足才 Rollout）**：连续 14 天无中断 · 0 Critical · 0 Data Loss · Merge Normal · Manifest Stable。
- **过闸后 Rollout**：Case-02（Personal）、Case-03（Study）一起升级到新边界。

### Step 3 — Git Cleanup（解决分叉，与边界实施分离）

1. **merge 远端**（取回合法 Core 增补）：`git merge origin/master`，冲突仅在 `PAIOS-Usage/manifest.yaml`——因 Case-01 manifest 已存 `F:\Fleet\manifests\case-01.yaml`，以"不写回本机"方式解决。
2. 确认无 Workspace 内容被误写回本机 `PAIOS-Usage`（执行时二次确认）。
3. `git commit` + `git push origin master`。

### Step 4 — Physical Separation（Pilot 过闸后执行）

1. 对 Workspace 内容 `git rm --cached --quiet <path>...`（**保留磁盘文件**）：`10_WORK/`、`20_KNOWLEDGE/Personal/`、`00_CAPTURE/`（除 Downloads）、`30_SYSTEM/Goals|Metrics|Principles|photo/`、`90_ARCHIVE/`、`Today.md`、`PAIOS-Usage/`、`QuarkSync/`、`Fleet/`（仓库内）。
2. 删除废弃的 `40_AUTOMATION/10_MANIFEST/`。
3. `git commit` + `git push origin master`。

---

## 5. 风险与回滚

- **回滚锚点**：`pre-phaseb-backup` tag。
- **数据零丢失**：所有 `git rm --cached` 仅取消跟踪，磁盘文件原样保留。
- **manifest 不丢**：三份已落 `F:\Fleet\incoming\`，与仓库解耦。
- **主要风险**：`git merge` 误把 case-03 manifest 写回本机 PAIOS-Usage——以"不写回"策略规避，执行时二次确认。

---

## 6. 验证

**B1 完成**：分类边界清晰、Fleet 子结构就位、gitignore 写入、三实例 manifest 在 `F:\Fleet\incoming\`。
**B2 完成**（且连续多版本无以下现象，详见 CASE-001）：
- [ ] `git ls-files` 不再含 Workspace 内容（`10_WORK/`、`20_KNOWLEDGE/Personal/`、`PAIOS-Usage/`、`Fleet/`、`Today.md`）
- [ ] `git ls-files` 仍含 `30_SYSTEM/ADR/`、`30_SYSTEM/Evolution/Case-Studies/`、`40_AUTOMATION/05_SCRIPTS/collect_manifest.py`、`20_KNOWLEDGE/Platform/`
- [ ] 另一台机器 `git pull` 后不再收到你的 Workspace / Fleet
- [ ] Manifest 冲突 / Workspace 泄漏 / Fleet 回流 / Merge 冲突 连续多版本未出现

---

## 7. 一句话

Phase B 不是"加功能"，是**把第一次并流暴露的架构违约修掉**——用 Platform Purity Principle 一条标准替代繁琐分类，先逻辑稳定、再物理隔离，让 Core 回到"只有平台"、Workspace 回到"每机私有"、Instance-State 回到"单向流动"。

## 8. 治理闭环（Architecture Lifecycle）

本蓝图的 Commit 纪律（Architecture→Governance→Git Cleanup→Physical Separation）只是"一次升级的 Git History 形状"。真正可复用的是**整轮架构演进的闭环**——已抽离为平台级 **Governance 层**，本 Phase 只引用、不内联：

- `30_SYSTEM/Governance/Architecture-Lifecycle.md` — 端到端节奏（横切）
- `30_SYSTEM/Governance/Decision-Traceability.md` — ADR 四字段 + Reactive/Proactive + Commit 引用
- `30_SYSTEM/Governance/Pilot-Gate.md` — 试点 Entry/Exit
- `30_SYSTEM/Governance/Rollout.md` — 全量推广
- `30_SYSTEM/Governance/Change-Control.md` — 变更分级 + 冻结 + 证据门禁
- `30_SYSTEM/Specifications/Asset-Class.md` — 全平台内容分类轴
- Phase C / D 全部复用同一套，不复制。

```
Case ──► ADR ──► Blueprint ──► Freeze ──► Boundary(Governance)
  ▲                                                          │
  │                                                          ▼
  └──── Validate ◄── Rollout(Physical Sep) ◄── Pilot(Exit) ◄──┘
```

- 任何 L3（Architecture）级变更都走完整闭环。
- **证据门禁（Reactive / Proactive）**：Reactive ADR 必须有证据支撑；Proactive ADR 必须明确验证条件，并在真实运行后完成验证或修订（见 `Decision-Traceability.md` §4）。
- Pilot 不可跳过：设计冻结后，至少单实例跑通 Exit Criteria 再过闸。
