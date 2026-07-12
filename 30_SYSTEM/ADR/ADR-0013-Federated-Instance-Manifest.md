---
adr: "0013"
status: "Proposed"
date: "2026-07-10"
evidence_level: "Emerging"
---

# ADR-0013: PAIOS Fleet — 联邦式实例清单（Federated Instance Manifest, FIM）

## 背景

PAIOS 已从单用户个人系统，演进到**多实例部署**阶段。当前已有 3 个实例在真实使用，且代表三种完全不同的场景：

| 实例 | 核心场景 | 使用目标 |
|------|----------|----------|
| A | 白天日常工作 | 提高工作效率 |
| B | 晚上整理个人档案、兴趣 | 个人知识管理 |
| C | 考研复习 | 学习辅助 |

这带来一个产品运营（Product Analytics）问题：**如何在完全不扰乱各实例正常使用的前提下，让开发者了解 PAIOS 的整体使用情况？**

这个问题的正确表述不是"汇总三个用户的产出"，而是"**汇总三个实例的状态（Instance State）**"。两者是截然不同的设计方向：
- 汇总产出 → 上传内容、中央分析 → 隐私边界模糊、中央变重、Schema 失控、用户为统计调整行为
- 汇总状态 → 只读元数据、实例自治 → 隐私安全、聚合轻量、非侵入

## 问题

需要为 PAIOS 多实例生态找到一个**极轻量的连接方式**，满足：

1. **不扰乱各自使用** — 各实例照常用 PAIOS，聚合层零侵入
2. **知道整体使用情况** — 开发者能看到健康度、功能采用率、演进趋势
3. **长期可演进** — 未来 Growth OS / Photo OS 等应用也能用同一机制，aggregator 不必修改
4. **符合 PAIOS 原则** — 实例自治、非侵入、需求驱动、Markdown-native

## 决策

**采用 Federated Instance Manifest（FIM，联邦式实例清单）机制。**

每个 PAIOS 实例由一个脚本**自动读取现有结构**生成 `manifest.yaml`（用户零行为改变），aggregator **主动拉取（pull）** 各 manifest 并合并为 Fleet Dashboard。内容永远留本地，只流转元数据。

```
PAIOS 实例（用户 A / B / C）
    │  正常运行，内容留本地
    │
    └── collect_manifest.py（只读现有状态）
            │
            ▼
        manifest.yaml（仅状态，无正文）
            │  push 或 aggregator 主动拉取
            ▼
    Fleet Aggregator（只理解 Manifest 协议）
            │
            ▼
    Fleet Dashboard（健康度 / 采用率 / 趋势 / 场景分布）
```

### 设计原则（9 条，来自架构评审）

| # | 原则 | 说明 |
|---|------|------|
| 1 | **Observe, Don't Own** | manifest 由脚本读现有结构生成，不新增数据库 / API / 同步协议 / 登录 |
| 2 | **Pull > Push** | aggregator 需要时主动读取，用户可离线、无事件总线、无实时同步、无一致性问题 |
| 3 | **Manifest = 能力声明** | 除计数外增加 `features`（photo/vision/embedding/face_search 等 enabled），Capability > Count |
| 4 | **Evidence 绑定对象** | 列出 `ADR-0012: Proposed` 而非统计 `proposed: 2`，保持可追溯 |
| 5 | **Project 用 UUID** | `id: KY-2026`，名字只是展示，聚合靠 ID 区分同名项目 |
| 6 | **Manifest 版本化** | 首行 `manifest_version: 1`，aggregator `switch(version)` 保证向后兼容 |
| 7 | **Aggregator 不知 PAIOS** | 只理解 Manifest 协议；Growth OS / Photo OS 也输出 Manifest，aggregator 零修改 |
| 8 | **Snapshot 非 History** | manifest 永远是快照；历史由 aggregator 按日期保存（fleet/20260710...），用户不负责历史 |
| 9 | **Instance 而非 Usage** | 命名为 FIM——描述整个实例（能力/健康/版本/使用/Evidence/Projects），Usage 只是子集 |

## Manifest v1 Schema

```yaml
manifest_version: 1

instance:
  id: "case-01"               # 优先取自 PAIOS-Usage/profile.yaml 语义 ID；缺省回退 UUID（持久化于 instance-id.txt）
  version: "v1.0.0"           # 读 SYSTEM_VERSION.md
  profile:                    # 场景画像，决定 Dashboard 如何归类
    primary: work             # work | personal | study
    secondary:                # 列表，可多个子场景
      - office
      - community-service
  owner: "user-a"             # 取自 profile.yaml owner.alias
  privacy: share              # 取自 profile.yaml privacy.manifest（share | private）

usage:                        # 第一层：系统活跃度（Health）
  last_active: 2026-07-10
  active_days_30d: 11
  git_commits_total: 16

features:                     # 第二层：功能采用（Capability，非计数）
  capture: true
  knowledge: true
  automation: true
  git: true
  photo: false
  growth: false
  review: false

assets:                       # 第三层：资产增长（趋势，Aggregator 只画曲线）
  references: 10
  concepts: 3
  decisions: 3
  models: 2
  methods: 2
  sops: 2
  projects: 2

projects:                     # 每个项目带 ID，聚合靠 ID
  - id: KY-2026
    name: Kaoyan-2026
    status: active
  - id: SN-2026
    name: Safety-Net
    status: active

evidence:                     # Evidence 绑定对象，不统计数量
  - object: ADR-0012
    level: Accepted
  - object: ADR-0013
    level: Proposed

feedback:                     # 第四层：问题反馈（产品迭代最该看的）
  pain_points:
    - "OCR 太慢"
    - "不知道资料放哪里"
```

**无任何正文内容**——只有状态、计数、标题、日期。

## 场景化聚合（Scenario-First）

Dashboard **首先按场景归类，而非按用户罗列**。原因是：未来工作用户可能 15 人、学习用户 30 人，真正该关心的是"哪一种场景最成功"。

```
PAIOS Fleet
  工作效率（1）  █████████
  个人知识（1）  ████████
  学习成长（1）  ██████████
```

每个场景有**独立 KPI**，而非统一统计 Reference：

| 场景 | 核心 KPI |
|------|----------|
| 工作（A） | 每日 Capture 数、完成任务数、知识沉淀、Automation 使用率 |
| 个人（B） | 照片整理数、日记数、兴趣知识、Memory 增长 |
| 学习（C） | 学习天数、学习时长、计划完成率、模拟考试、知识卡片 |

Fleet Dashboard 应输出：

```
==================  PAIOS Fleet  ==================
实例数 ............ 3
本周活跃 .......... 3

---- 工作实例 ----
  工作天数 .... 5
  Capture .... 43
  日报 ...... 5

---- 个人实例 ----
  照片整理 .. 120
  新增知识 .. 18
  日记 ...... 7

---- 考研实例 ----
  学习天数 .. 6
  计划完成率  91%
  知识卡片 .. 35

---- 系统功能采用率 ----
  Capture .... 100%
  Knowledge .. 100%
  Automation . 67%
  Photo ...... 33%
  Review ..... 33%
==================================================
```

## Reference Cases（官方验证案例）

3 个实例不止是"用户"，应作为**官方验证案例**，验证三个应用方向是否成立：

| Case | 定位 | 验证目标 |
|------|------|----------|
| Case-01 | 工作助手 | 工作流是否成立 |
| Case-02 | 个人知识库 | 长期积累是否成立 |
| Case-03 | 考研助手 | 学习闭环是否成立 |

验证核心问题（而非资产数量）：

| 问题 | A | B | C |
|------|---|---|---|
| 是否每天打开 PAIOS？ | ✅ | ✅ | ✅ |
| 是否形成固定工作流？ | ✅ | ✅ | ✅ |
| 是否持续沉淀知识？ | ✅ | ✅ | ✅ |
| 哪个模块最常用？ | Capture/Work | Photos/Knowledge | Study/Review |
| 最大阻碍？ | 录入成本 | 分类效率 | 学习坚持 |

## MVP 实施路径

最小可行，不建复杂 Dashboard：

1. **`collect_manifest.py`**：遍历 `20_KNOWLEDGE/*` 计数、`git log` 取 commits/active days、读 `10_WORK/Active` 取项目 → 输出 `30_SYSTEM/PAIOS-Usage/manifest.yaml`
2. **`fleet/aggregate.py`**：读所有 `manifests/*.yaml` → 合并成 `fleet-YYYY-Www.md` 周报
3. 先在当前单实例跑通验证脚本正确性，再扩展到多实例

## 与现有架构原则的兼容性

| 原则 | 兼容性 | 说明 |
|------|--------|------|
| Necessity-Gated Architecture | ✅ | 不加数据库/中心仓库，只读取与合并 |
| Observe, Don't Own | ✅ | 只读现有状态，不改变用户工作流 |
| ADR-0012 Core + Applications | ✅ | FIM 是跨实例协议层，不属任何单一应用 |
| Evidence Level System | ✅ | evidence 字段绑定对象，可追溯到具体 ADR |
| 先跑通再优化 | ✅ | MVP 两脚本即可验证，不预建平台 |

## 风险与约束

| 风险 | 缓解 |
|------|------|
| Manifest schema 演化不兼容 | `manifest_version` 字段 + aggregator `switch(version)` |
| Aggregator 耦合到具体业务 | Aggregator 只解析 Manifest 协议，不理解 PAIOS/Growth/Photo |
| 隐私边界模糊 | 仅元数据流转，内容永不出本机；用户可退出统计 |
| 场景画像不准 | `profile` 由实例本地配置声明，可手动修正 |

## 结论

PAIOS Fleet 的职责**不是收集用户的数据，而是帮助开发者了解每个 PAIOS 实例的健康度、功能采用率和演进趋势**。

FIM 机制首次为 PAIOS 多实例生态提供了极轻量的连接方式：实例自治、非侵入、联邦聚合、可退出、可扩展——并已具备成为 **PAIOS 多实例通信协议**（而不仅是统计方案）的潜力。

---

**Related**: `ADR-0012-Platform-Application-Architecture.md` | `20_KNOWLEDGE/Concepts/Growth-OS-Life-Companion.md` | `PAIOS-2Week-Review-2026-07-10.html` | `ADR-0014-Upgrade-Mechanism.md` | `ADR-0015-Federated-Aggregation-Viewing.md` | `ADR-0016-Multi-Instance-Architecture-Baseline.md`

> **定位确认（ADR-0016）**：FIM 描述的是 **Instance State**（含 Version / Schema / Health / Profile / Capability / Evidence / Usage），不是单纯的"Usage"。Usage 只是其中一维。
