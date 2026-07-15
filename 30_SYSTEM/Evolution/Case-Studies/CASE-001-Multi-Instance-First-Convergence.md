# CASE-001 — First Real Multi-Instance Convergence（第一次真实多实例并流）

> 类型：Architecture Evidence（架构证据）
> 来源：聊天记录收敛 + `git` 实测数据，非推测

## 元数据

- 时间：2026-07-11
- 触发版本：PAIOS v1.0.1
- 证据等级：**Validated**（三实例真实运行，数据可复现）
- 关联 ADR：ADR-0016（架构基线，提出 Phase B 触发条件）· ADR-0017（平台纯度与物理隔离，本 Case 直接支撑）· ADR-0018（多实例角色模型，本 Case 根因的结构性修复）
- **Evidence Commit**：`472e53d`（Phase B v2 设计冻结点）
- **Severity**：`Major`（Manifest 单路径冲突已真实发生；若将来出现真实数据丢失则升为 Critical）
- **配套文档**：[CASE-001 复盘（给 Case-02/03 的背景说明）](./CASE-001-Retrospective.md) —— 面向未参与讨论的实例，回答"为什么走到这一步 / 为什么分阶段修 / 你们该做什么"

---

## 背景（Context）

PAIOS v1.0.1 是第一次出现**三个真实实例同时运行并全部升级到同一 Core 版本**：

| Case | 场景 | 使用者 |
|------|------|--------|
| Case-01 | Work | user-a（本机 feng） |
| Case-02 | Personal | user-b（另一台机器 evan） |
| Case-03 | Study | user-c（同一台机器 evan） |

Developer（User1）首次按 SOP 收集三个 Manifest，意图生成首份 Fleet 周报。

---

## 观察（Observed）

三份 Manifest 实测（`git show` 只读提取，未冒险 merge）：

| 指标 | Case-01 | Case-02 | Case-03 | 汇总 |
|------|---------|---------|---------|------|
| Core Version | v1.0.1 | v1.0.1 | v1.0.1 | 100% 一致 |
| 活跃天数 | 8 | 9 | 9 | — |
| Git Commits | 21 | 25 | 27 | — |
| References | 11 | 11 | 16 | — |
| Automation | ✅ | ✅ | ✅ | 100% |
| Knowledge | ✅ | ✅ | ✅ | 100% |
| Growth | ✅ | ✅ | ✅ | 100% |
| Photo | ❌ | ✅ | ✅ | 2/3 |
| Review | ❌ | ❌ | ❌ | 0 |

**说明**：跨三种场景（工作 / 个人 / 考研），Automation / Knowledge / Growth 三个能力已成为稳定公共底座。这证明平台能力已经开始收敛出"人人一致的刚需层"。

---

## 新发现（Findings）

第一次真实运行（非理论）暴露四个问题：

### 1. Manifest 单路径冲突（已发生）

三个实例都写 `PAIOS-Usage/manifest.yaml` 同一路径。远端 `caf3033` 已用 Case-03 的 manifest **覆盖**了本机 Case-01。Case-02 靠手动改存 `Fleet/cases/` 才幸免。本机与远端合并必冲突。

> 这是 ADR-0013/0014 预判的"单路径冲突"第一次真实验证。

### 2. Workspace 被推进 Core（已发生）

远程实例把整个共享仓库当成了自己的 Workspace，推入：

- `10_WORK/photos_organizer/`（40+ py，约 5000 行）
- `20_KNOWLEDGE/References/Kaoyan-*`（考研知识库 5 科）
- `20_KNOWLEDGE/SOP/Photo-Organizer-SOP.md`
- `30_SYSTEM/photo/classification_policy.yaml`
- `90_ARCHIVE/openwrt_2f_reconfig/*`
- `Today.md` / `00_CAPTURE/Inbox.md` / `30_SYSTEM/Goals|Metrics|Principles`

违反 **ADR-0016**（Workspace 用户各自维护、不随 Core 同步）与 **ADR-0012**（平台/应用分离）。

### 3. Fleet 出现两个物理位置（边界未冻结）

- 本机设计：`F:\Fleet`（仓库外，正确）
- 另一台建：`F:\PAIOS\Fleet\cases`（仓库内，违反 ADR-0015"Fleet 不同步用户"）

说明 Fleet 的边界在首次并流时还没真正冻结。

### 4. 出现两套 Manifest 系统（Canonical 未统一）

- 本机：`40_AUTOMATION/05_SCRIPTS/collect_manifest.py`（SCRIPT-0009，canonical）
- 远程：`40_AUTOMATION/10_MANIFEST/`（inventory / manifest / migration_status）

同一职责两套实现，采集口径不一致。

---

## 结论（Validated）

此次运行**证明** ADR-0016 提出的"第二实例将暴露分发问题"已被真实数据验证。因此：

> **Phase B 正式进入可实施阶段——不是提前设计，而是真实需求驱动。**

这是一次 **Need-Driven Promotion**（需求驱动晋升），而非 Feature-Driven（功能驱动扩展）。

---

## 架构升级依据

本 Case 直接支撑：

- **Phase B**：Core / Workspace / Instance-State 物理拆分（ADR-0016 触发条件命中）
- **ADR-0017**：平台纯度原则（Platform Purity Principle）+ 物理隔离决策
- **Evidence-Driven Evolution**：PAIOS 治理方式从"设计驱动"转向"证据驱动"

---

## 决策（Decision）

建议形成正式 ADR（已落地为 **ADR-0017**）：

- 采用 **Platform Purity Principle** 作为文件归属的唯一判断标准：
  > 只问一句——"别人 pull 这个文件有价值吗？"有 → Core；没有 → Workspace。
- Core / Workspace / Instance-State 三桶物理隔离。
- `20_KNOWLEDGE/` **拆内容不拆目录**（Platform/ 留 Core，Personal/ 私有），而非整体 gitignore。
- `10_WORK/` 全部私有，但平台工具应迁入 `40_AUTOMATION`。
- Phase B **分阶段**：B1 逻辑隔离（先稳定分类与目录职责，git 暂允许存在，观察两周）→ B2 物理 `git rm --cached`。
- Manifest 流程升级为 **collect → publish → Fleet**（publish 是可扩展传输动作）。

---

## 后续验证指标（Validation Metrics）

Phase B 完成后继续观察若干版本，若以下四项**连续多个版本未再出现**，即认定 Phase B 验证完成：

- [ ] Manifest 冲突（单路径覆盖）
- [ ] Workspace 泄漏（用户内容进 Core）
- [ ] Fleet 回流（用户 pull 到 Fleet）
- [ ] Merge 冲突（因共享 Workspace 导致）

---

## 验证记录（Validation Log）

> 本 Case 不仅记录问题，也记录整个验证过程（Discovery → Decision → Implementation → Validation → Closure），与 Architecture Lifecycle 一致。下列为运行期验证节点，非新决策。

### Validation-01 — 2026-07-11

**问题（Question）**：是否应提前启动 Git Cleanup（Commit 3），以清理远端 `origin/master` 中的历史架构债务？

**证据（Evidence）**：
- `git fetch` 后 `origin/master` 仍停在 `caf3033`，与上次核对完全一致；`HEAD..origin/master` 的 8 个提交均为已知旧发散（Case-02/03 的 v1.0.1 升级流），**无新提交**
- 债务文件最后改动均来自已知历史提交：`10_WORK` / `20_KNOWLEDGE`（含考研正文）最后改动于 `caf3033`；`Today.md` / `PAIOS-Usage/manifest.yaml` 于 `1ddb28f`；仓库内 `Fleet/` 于 `a750af0`。tip 之后**无任何新增写入**
- **未观察到**任何"持续向远端写入 Workspace / 覆盖 Manifest"的活动
- **Hotfix 例外条件（持续污染）未触发**

**决策（Decision）**：维持原计划——继续 Pilot（Case-01），**不启动 Git Cleanup**，**不触发 Hotfix**。

**理由（Reason）**：远端债务为**历史遗留（frozen）**而非持续污染。现在清理会把"架构调整 + Git 收敛 + 历史清理"三件事混在一起，违反 Commit 纪律。Git Cleanup 的正确归属是 **Commit 3**（让 Git 同步已验证架构，而非决定架构）。

**意义（Significance）**：本次核实是 CASE-001 原则的一次真实运行——**用证据而非担心驱动决策**。它验证了"Pilot 前不启动 Git Cleanup"这一既有决策仍然成立，而非产生新决策，故作为 Validation 节点，不升级为新 CASE / 新 ADR。

---

## 决策影响（Decision Impact）

- **Created**：ADR-0017（Platform Purity & Physical Separation）· ADR-0018（Multi-Instance Role Model —— 本 Case 根因"三实例同权→互相污染"的结构性修复：重新定义角色使写 Core 能力只存在于 Case-01，而非加行为规则）
- **Triggered**：Phase B（Core / Workspace / Instance-State 物理隔离）
- **Introduced**：Platform Purity Principle（"别人 pull 这文件有价值吗？"）
- **Affected**：
  - `30_SYSTEM/ADR/ADR-INDEX.md`
  - `CHANGELOG.md`
  - `30_SYSTEM/Evolution/Phase-B-Core-Workspace-Split.md`（蓝图 v2）
  - `30_SYSTEM/Evolution/Case-Studies/README.md`（Case 公约）
- **Evidence Traceability**：任何"为什么有 ADR-0017 / 为什么开始 Phase B"的追问，都回溯到本 Case。

## 最大价值（Significance）

从 PAIOS 演进角度看，这次真正重要的**不是 Git 冲突本身**，而是架构治理方式的变化：

- **以前**：先设计，再等待未来验证。
- **现在**：真实运行 → 收集证据 → 提炼规律 → 升级架构。

这意味着 PAIOS 已从"以设计驱动为主"，逐步进入 **Evidence-Driven Evolution（证据驱动演进）** 阶段。

据此明确 PAIOS 的治理演进立场——以 **Evidence-Driven Evolution（证据驱动演进）** 为方法论：

> 架构可以基于原则进行前瞻设计，但是否成为正式平台能力，应由真实运行证据来验证。

这一表述**刻意不采用 "Evidence Before Architecture（证据先于架构）" 的绝对化版本**——因为 PAIOS 一贯允许基于原则的前瞻性设计：ADR-0014（升级机制）、ADR-0016（三层架构）、FIM 最初都是**预测性设计**，直到 CASE-001 才被真实验证。若坚持"无证据不能设计"，这些 ADR 根本不会存在。

因此正确关系应是：**设计可以走在证据之前，但正式成为平台能力必须经过真实运行验证。** 这与既有 **Need-Driven Promotion** 完全一致，也为未来每一次 Phase 升级提供统一依据。
