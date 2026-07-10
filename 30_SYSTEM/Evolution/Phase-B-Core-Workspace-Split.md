# Phase B — Core / Workspace / Instance-State 物理拆分（设计蓝图 v2）

> 状态：**Approved-with-refinements（蓝图已采纳，执行按 B1→B2 分阶段）**
> 决策依据：**ADR-0017（Platform Purity & Physical Separation，Accepted）**
> 证据来源：**CASE-001-Multi-Instance-First-Convergence（Validated）**
> 触发：ADR-0016 Phase B 触发条件命中（第二实例暴露分发痛点，git 实测）

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

核心判断标准（ADR-0017 D0）：
> **"别人 pull 这个文件有价值吗？"** 有 → Core；没有 → Workspace。

### Core（tracked，所有实例 git pull 共享）

```
PAIOS Core 仓库
├─ 30_SYSTEM/
│   ├─ ADR/              平台决策（含 FIM 四件套 + ADR-0017）
│   ├─ SOP/              发布/采集等平台 SOP
│   ├─ Evolution/        路线图 / 复盘 / Case-Studies（方法论，非个人状态）
│   ├─ Patterns/         ⭐ 新增：平台模式库
│   ├─ Capability-Registry/   ⭐ 新增：能力注册表
│   └─ Workflow-Registry/      ⭐ 新增：工作流注册表
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
| git rm --cached 一次性 | ⚠️ 延后 | 改为 B1 逻辑 → B2 物理（分类稳定后） |
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

## 4. 执行步骤（分阶段，命令为"提议"，待 B1 启动令）

### Phase B1 — 逻辑隔离（先稳定分类，git 暂允许 Workspace 存在）

1. **本地备份锚点**：`git tag pre-phaseb-backup HEAD`
2. **merge 远端**（取回合法 Core 增补）：`git merge origin/master`，冲突仅在 `PAIOS-Usage/manifest.yaml`——因 Case-01 manifest 已存 `F:\Fleet\manifests\case-01.yaml`，以"不写回本机"方式解决。
3. **确立目录职责**：本机创建 `20_KNOWLEDGE/Platform/` 与 `20_KNOWLEDGE/Personal/`，将个人知识移入 Personal/；将 `10_WORK/` 中平台工具迁出至 `40_AUTOMATION/`。
4. **写入新 `.gitignore`**（第 3 节）。
5. **收敛 Manifest**：标记 `40_AUTOMATION/10_MANIFEST/` 为废弃（B2 删除）。
6. **Fleet 子结构初始化**：`F:\Fleet\{incoming,history,reports,stats,dashboards\}`；将现有三份 manifest 移入 `incoming/`。
7. **commit（不 push）**：`chore(phase-b-b1): establish Core/Workspace classification & Fleet sub-structure`。
8. **观察两周**：期间继续真实使用，记录是否仍有分类歧义。

### Phase B2 — 物理隔离（B1 分类稳定后执行）

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
