# Phase B — Core / Workspace / Instance-State 物理拆分方案

> 状态：Draft（待审阅，未执行）
> 触发：ADR-0016 Phase B 触发条件已命中——"第二个真实实例暴露分发痛点"
> 依据：ADR-0012（平台/应用分离）· ADR-0013（FIM）· ADR-0014（升级三层）· ADR-0015（聚合与权限）· ADR-0016（架构基线冻结）

---

## 0. 现状诊断（已用 `git` 验证的事实）

2026-07-11 实测，本地 (`HEAD=6f09441`) 与远端 (`origin/master=caf3033`) 分叉：

- 本地仅比 merge-base (`f9edc9f`) 多 1 个提交：`6f09441`（Case-01 manifest 重生成）
- 远端比 merge-base 多 **9 个提交 / 89 文件 / +11943 行**，关键内容：

| 远程推入的内容 | 性质 | 判定 |
|------|------|------|
| `10_WORK/photos_organizer/`（40+ py，~5000 行） | 用户项目代码 | ❌ Workspace 泄漏进 Core |
| `20_KNOWLEDGE/References/Kaoyan-*`（5 科+手册） | 用户知识正文 | ❌ Workspace 泄漏进 Core |
| `20_KNOWLEDGE/SOP/Photo-Organizer-SOP.md` | 用户 SOP | ❌ Workspace 泄漏进 Core |
| `30_SYSTEM/photo/classification_policy.yaml` | 用户配置 | ❌ Workspace 泄漏进 Core |
| `90_ARCHIVE/openwrt_2f_reconfig/*` | 用户归档项目 | ❌ Workspace 泄漏进 Core |
| `Today.md` / `00_CAPTURE/Inbox.md` / `30_SYSTEM/Goals/*` / `30_SYSTEM/Metrics.md` | 用户日更状态 | ❌ 每机私有，不应共享 |
| `Fleet/cases/case-02.yaml` + `Fleet/cases/README.md` | 在仓库内的 Fleet | ❌ 违反 ADR-0015"Fleet 不同步用户" |
| `40_AUTOMATION/10_MANIFEST/`（inventory/manifest/migration_status） | **另一套** manifest 系统 | ❌ 与 SCRIPT-0009 `collect_manifest.py` 撞车 |
| `.gitignore`（+.env、+photos_organizer 数据规则） | 合理扩展 | ✅ 应保留并合并 |
| `30_SYSTEM/Evolution/PAIOS-Retrospective-2026-07-10.md` | 方法论复盘 | ✅ 属 Core，应保留 |
| `RELEASES/upgrade-receipt-v1.0.1.md`（注意多了 `-v1.0.1` 重名文件） | 回执副本 | ⚠️ 文件名重复，需归并 |
| `QuarkSync/` | 同步辅助 | ⚠️ 待定（见 D3） |
| `PAIOS-Usage/manifest.yaml`（= case-03）覆盖了本地 case-01 | 单路径冲突 | ❌ 已发生，正是预判的痛点 |

**核心结论**：多实例模型在第一次并流就破了——因为远程实例把共享仓库当成了自己的 Workspace。这违反 ADR-0016"Workspace 用户各自维护、不随 Core 同步"与 ADR-0015"唯一离机文件是 manifest.yaml"。

> 校准：三实例目前均由 Evan 在两台机器上操作（本机 Case-01/work + 另一台 Case-02/personal、Case-03/study）。所以暂无第三方隐私泄露风险，但**架构正确性必须现在修**，否则真实第三方接入时会炸。

---

## 1. 目标架构（三桶模型）

```
PAIOS Core 仓库（tracked, 所有实例 git pull 同步）
├─ 30_SYSTEM/ADR/          平台决策（含 FIM 四件套）
├─ 30_SYSTEM/SOP/          发布/采集等平台 SOP
├─ 30_SYSTEM/Evolution/    路线图/复盘（方法论，非个人状态）
├─ 40_AUTOMATION/05_SCRIPTS/collect_manifest.py  ← 唯一 canonical manifest 生成器
├─ RELEASES/               发布说明 + 升级通知 + 回执
├─ CHANGELOG / SYSTEM_VERSION / MANIFEST.json / README / DEPLOYMENT / SYNC_STRATEGY
└─ scripts/ / .githooks/ / .gitignore

Workspace（每机私有，gitignored，绝不进 Core）
├─ 10_WORK/  (含 photos_organizer 等用户项目)
├─ 20_KNOWLEDGE/  (含 Kaoyan-* 等用户知识正文)
├─ 00_CAPTURE/  /  30_SYSTEM/Goals|Metrics|Principles|photo/
├─ 90_ARCHIVE/<项目>/  /  Today.md  /  PAIOS-Usage/(本机)
└─ QuarkSync/ (待定)

Instance-State（单向流向 Developer，不回推）
└─ 每份 manifest 以 case-XX.yaml 命名，归集到 Developer 的 F:\Fleet\manifests\
   （未来：独立 paios-fleet 仓库 / 分支，见 D3）
```

---

## 2. 需你拍板的四个决策点（D1–D4）

| # | 决策 | 我的建议 | 影响 |
|---|------|---------|------|
| **D1** | 远程推入的 Workspace 内容（photos_organizer / Kaoyan KB / openwrt 等）怎么处理 | `git rm --cached` 取消跟踪、**保留本地文件**、不再共享；历史记录仍在，未来 pull 不污染 | 决定 Core 仓库"瘦身"到什么程度 |
| **D2** | 两套 manifest 系统收敛到哪个 | 保留 `collect_manifest.py`（SCRIPT-0009），**删除**远程的 `40_AUTOMATION/10_MANIFEST/` | 消除撞车，统一采集口径 |
| **D3** | manifest 回流通道（现在三实例都是你机器） | 现阶段维持 `F:\Fleet\manifests\case-XX.yaml` 拷贝；**真实第三方接入时**再建独立 `paios-fleet` 仓库 | 决定是否需要新仓库 |
| **D4** | Fleet 位置 | **仅** `F:\Fleet`（仓库外）；**删除**仓库内 `Fleet/cases/` | 消除"用户 pull 回 fleet"隐患 |

---

## 3. `.gitignore` 修订（union 两边 + 新增 Phase B 排除）

```gitignore
# ===== 既有（保持不变） =====
*.docx  *.pdf  *.zip  *.exe
.reasonix/  .workbuddy/  .codebuddy/
00_CAPTURE/Downloads/  70_TMP/  50_DATA/  50_IMPORT/
__pycache__/  .venv/  .DS_Store  .env

# ===== 远程已有的 photos_organizer 数据规则（保留） =====
10_WORK/photos_organizer/database/  10_WORK/photos_organizer/models/
10_WORK/photos_organizer/inputs/    10_WORK/photos_organizer/outputs/
10_WORK/photos_organizer/face_index/face_index.db
10_WORK/photos_organizer/face_index/faiss_index.bin
10_WORK/photos_organizer/face_index/*.npy
10_WORK/photos_organizer/face_index/faces/  export/  retrieval/
10_WORK/photos_organizer/face_index/*.log
10_WORK/photos_organizer/scripts/*.log  *.txt

# ===== Phase B 新增：Workspace 永不进 Core（ADR-0016） =====
10_WORK/
20_KNOWLEDGE/
00_CAPTURE/
30_SYSTEM/Goals/  30_SYSTEM/Metrics.md  30_SYSTEM/Principles.md  30_SYSTEM/photo/
90_ARCHIVE/
Today.md
PAIOS-Usage/
QuarkSync/

# ===== Phase B 新增：Fleet 仅 Developer 仓库外（ADR-0015） =====
Fleet/

# ===== 环境自管理，不跟踪 =====
reasonix.toml
```

> 注：若 `20_KNOWLEDGE/` 整体 gitignore，原 base 里共享的方法论引用（如 REF-0010 Growth OS）也会变本地私有。若你希望**部分**平台知识仍共享，改为逐文件白名单（`!20_KNOWLEDGE/Concepts/Growth-OS-*.md`）。这事归 D1 一并定。

---

## 4. 执行步骤（分阶段，全部命令为"提议"，待你批准）

### B1 — 立即修复（解当前分叉 + 消除破绽）

1. **本地先备份**：`git tag pre-phaseb-backup HEAD`（可逆锚点）
2. **合并远端**（取回合法 Core 增补）：
   `git merge origin/master` → 预期冲突仅在 `PAIOS-Usage/manifest.yaml`（case-01 vs case-03）。
   解决：因 Case-01 manifest 已安全存于 `F:\Fleet\manifests\case-01.yaml`，直接以"删跟踪"方式处理（见第 4 步），**不要**把 case-03 写回本机 PAIOS-Usage。
3. **应用 D1**：对远程泄漏的 Workspace 内容 `git rm --cached --quiet <path>...`（保留磁盘文件），包括：
   `10_WORK/photos_organizer`、`20_KNOWLEDGE/References/Kaoyan-*`、`20_KNOWLEDGE/SOP/Photo-Organizer-SOP.md`、`30_SYSTEM/photo/`、`90_ARCHIVE/openwrt_2f_reconfig`、`Today.md`、`00_CAPTURE/Inbox.md`、`30_SYSTEM/Goals/*`、`30_SYSTEM/Metrics.md`、`30_SYSTEM/Principles.md`、`PAIOS-Usage/manifest.yaml`、`PAIOS-Usage/profile.yaml`、`PAIOS-Usage/feature-photo`、`PAIOS-Usage/instance-id.txt`。
4. **应用 D2**：`git rm -r --cached 40_AUTOMATION/10_MANIFEST`（保留本地备查，或彻底删）。
5. **应用 D4**：`git rm -r Fleet`（仓库内 Fleet 全删；`F:\Fleet` 不受影响，因已被 gitignore）。
6. **应用 D3 现阶段**：无需新仓库；确认 `F:\Fleet\manifests/{case-01,02,03}.yaml` 三份齐备（已齐）。
7. **写入新 `.gitignore`**（第 3 节内容），提交：`feat(phase-b): Core/Workspace split — untrack workspace, remove in-repo Fleet, converge manifest`。
8. **归并回执重名**：删除 `RELEASES/upgrade-receipt-v1.0.1.md`，保留 `upgrade-receipt-1.0.1.md`。
9. **push**：`git push origin master`。

### B2 —  deferred（真实第三方接入时再做）

- 建独立 `paios-fleet` 仓库 / `manifests` 分支，实例只 push `case-XX.yaml`。
- 物理 Core/Workspace 目录拆分（Core 成独立可分发包，Workspace 完全脱离 git）。
- `collect_manifest.py` 增加自检 + `minimum_core` 提示（ADR-0014 Phase B daemon 部分）。

---

## 5. 风险与回滚

- **回滚锚点**：`pre-phaseb-backup` tag，随时 `git reset --hard pre-phaseb-backup` 回到分叉前。
- **数据零丢失**：所有 `git rm --cached` 仅取消跟踪，**磁盘文件原样保留**，用户 Workspace 内容不丢。
- **manifest 不丢**：三份已落 `F:\Fleet\manifests\`，与仓库解耦。
- **主要风险**：`git merge` 若处理不当可能误把 case-03 manifest 写回本机 PAIOS-Usage——已用"删跟踪"策略规避，执行时需二次确认。

---

## 6. 验证（B1 完成后）

- [ ] `git ls-files` 不再含 `10_WORK/`、`20_KNOWLEDGE/`、`PAIOS-Usage/`、`Fleet/`、`Today.md`
- [ ] `git ls-files` 仍含 `30_SYSTEM/ADR/`、`RELEASES/`、`40_AUTOMATION/05_SCRIPTS/collect_manifest.py`
- [ ] 三实例 manifest 在 `F:\Fleet\manifests/` 齐备
- [ ] 另一台机器 `git pull` 后不再收到你的 Workspace / Fleet
- [ ] `collect_manifest.py` 仍能在本机生成 manifest 到 `PAIOS-Usage/`（本地私有，不进仓库）

---

## 7. 一句话

Phase B 不是"加功能"，是**把第一次并流暴露的架构违约修掉**——让 Core 回到"只有平台"，Workspace 回到"每机私有"，Instance-State 回到"单向流动"。修完，多实例模型才真正站得住。
