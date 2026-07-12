# Changelog

All notable changes to PAIOS Platform are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/),
and PAIOS follows [Semantic Versioning](https://semver.org/lang/zh-CN/).

---

## [Unreleased]

### Added

- `docs/` 文档导航目录（architecture / governance / guides / decisions / reference）
- `CONTRIBUTING.md` 贡献指南（10 节：角色模型、ADR 流程、Commit 规范、分支策略等）
- `LICENSE`（MIT）
- `pyproject.toml`（项目元数据 + pytest 配置）
- `40_AUTOMATION/08_TESTS/` 测试基础设施（smoke test × 3）
- `30_SYSTEM/Governance/Release/` 发布管理规范：
  - `release-checklist.md` 发布前逐项检查清单
  - `version-policy.md` 语义化版本规则
  - `branching-policy.md` 分支策略与命名规范
- `.gitignore` 补充 `.pytest_cache/` 忽略规则

### Changed

- **README.md**：从 539 字节扩展为完整项目文档（架构、多实例模型、治理框架、快速开始、版本说明）
- **CHANGELOG.md**：按 Keep a Changelog 格式重构（Added / Changed / Fixed 分类）

---

## [1.0.1] — 2026-07-10

### Added

#### Federated Instance Manifest & Upgrade Mechanism (2026-07-10)

- ADR-0013: Federated Instance Manifest (FIM) — 多实例状态汇总协议
- ADR-0014: Upgrade Mechanism — Core/Workspace/Upgrade 三层 + 版本化发布
- ADR-0015: Federated Aggregation & Viewing — 三级架构 + 汇总模式
- ADR-0016: Multi-Instance Architecture Baseline — 4 层模型（Platform→Instance→Manifest→Fleet）
- `collect_manifest.py`（SCRIPT-0009）：只读收集实例状态，生成 manifest.yaml
- `PAIOS-Usage/profile.yaml`：实例身份声明（场景画像）

#### Architecture Evidence & Evolution (2026-07-11)

- `30_SYSTEM/Evolution/Case-Studies/` 架构证据目录
- CASE-001-Multi-Instance-First-Convergence.md（Validated 级首次多实例并流证据）
- ADR-0017: Platform Purity & Physical Separation（三桶隔离 + 判断标准）
- Phase-B-Core-Workspace-Split.md v2（Core/Workspace 拆分蓝图）
- 治理方法论升级：**Evidence-Driven Evolution**（证据驱动演进）

#### Architecture Lifecycle (2026-07-11)

- `30_SYSTEM/Governance/Architecture-Lifecycle.md`：平台级架构生命周期（Evidence→Case→ADR→Blueprint→Freeze→Boundary→Pilot→Rollout→Validate）
- **Asset Class 抽象**：`30_SYSTEM/Specifications/Asset-Class.md`（Platform/Shared/Personal/Imported）
- **Pilot Gate**：Entry/Exit Criteria（14 天 / 0 Critical / 0 Data Loss / Merge Normal / Manifest Stable）
- Phase B v2 引入 `manifest_version` 自声明（Fleet 不猜版本）

#### Governance Layer Extraction (2026-07-11)

- `Architecture-Lifecycle.md`：端到端演进闭环
- `Decision-Traceability.md`：ADR 四字段 + Reactive/Proactive 区分
- `Pilot-Gate.md`：试点 Entry/Exit Criteria + 单实例试点模式
- `Rollout.md`：全量推广前置条件 + 分批顺序 + Git History 四段
- `Change-Control.md`：L1/L2/L3 变更分级 + 冻结策略 + 证据门禁 + Commit 纪律
- Phase B 蓝图改为引用式（引用 Governance 层与 Asset-Class 规范）

#### Architecture Lifecycle v1.0 冻结 (2026-07-11)

- `lifecycle_version: 1.0` 版本字段
- Gate Owner 列（Evidence/Case/ADR/Blueprint/Freeze/Rollout/Validate 等）
- Evidence Severity 四级（Critical / Major / Minor / Observation）
- Retrospective Outcome 四选一（Accepted / Adjusted / Rejected / Deferred）
- 双向 Traceability（CASE ↔ ADR ↔ Blueprint ↔ Commit）
- 元治理原则（Meta-Governance）：Lifecycle 修改须遵循 Lifecycle

#### Multi-Instance Role Model (2026-07-11)

- ADR-0018: Multi-Instance Role Model（Developer/User）& One-Way Flow（Accepted, Validated, Reactive）
- `30_SYSTEM/Governance/Operating-Model.md`：多实例角色与数据流模型
- `30_SYSTEM/SOP/SOP-2026-07-11-0001-User-Daily-Operations.md`：用户侧日常 SOP
- `30_SYSTEM/SOP/SOP-2026-07-11-0002-User-Iron-Rules-One-Pager.md`：开机提醒式铁律一页纸
- `30_SYSTEM/SOP/User-Role-Model-Speed-View.html`：角色模型速览信息图
- `30_SYSTEM/SOP/User-Boot-Reminder.cmd`：开机提醒启动器
- `RELEASES/RELEASE-NOTES-TEMPLATE.md`：Release Notes 模板（含用户须知段）

#### Pilot & Release Infrastructure (2026-07-11)

- `30_SYSTEM/SOP/SOP-2026-07-11-0003-Pilot-Launch-Checklist.md`：Pilot 启动清单
- `RELEASES` 发行目录（RELEASE-NOTES-TEMPLATE.md、upgrade-receipt 等）
- `F:\Fleet\`：Developer 运营目录（manifests/ + reports/）
- `30_SYSTEM/SOP/SOP-2026-07-10-0001-Release-Flow.md`：标准发布 SOP
- `60_REFERENCE_CASES/`：官方验证案例目录（Case-01~03）
- `30_SYSTEM/Specifications/FIM-v1.md`：FIM v1 平台级协议正式定义

#### CASE-001 复盘 (2026-07-11)

- `30_SYSTEM/Evolution/Case-Studies/CASE-001-Retrospective.md`：面向 Case-02/03 的背景说明

### Changed

- **ADR-INDEX.md**：按 Foundation / Platform Evolution / Governance 三组重组，新增 Layer 列
- **Phase B v2 再精炼**：引入 Asset Class 抽象替代写死的 Platform/Personal；Registry 统一；Fleet 版本改为 Manifest 自声明
- **ADR-0017 D0 升级**：Platform Purity 判断标准从"别人 pull 有价值吗"提升为"是否在定义平台能力"
- **SOP-2026-07-10-0001-Release-Flow.md**（ADR-0018 修订）：移除「User git push PAIOS-Usage/ 至 Core 仓库」— 改由 out-of-band publish → `F:\Fleet\incoming\`
- **30_SYSTEM/Governance/Pilot-Gate.md**：§6 增加配套清单指针
- 架构审计：标记 ADR-0001 不存在（历史遗漏），清理全系统引用

### Fixed

- **manifest version**：manifest.yaml 版本从 v1.0.0 纠正为 v1.0.1
- **Claw/ 游离目录**：已删除

---

## [1.0.0] — 2026-06-29

### Added

- PAIOS Platform v1.0.0 初始化
- 7 层目录结构部署于 E:\PAIOS（00_CAPTURE / 10_WORK / 20_KNOWLEDGE / 30_SYSTEM / 40_AUTOMATION / 50_DATA / 90_ARCHIVE）
- `30_SYSTEM/`：9 项核心原则、ADR（2 个）、Config、Goals、Evolution
- `40_AUTOMATION/`：Registry、Capabilities、Prompts、Agents、MCP、Scripts、Legacy、Manifest
- `20_KNOWLEDGE/`：Concepts、Methods、SOP、Decisions、Models、References
- `00_CAPTURE/`：Inbox.md 统一入口
- 运营工具：Doctor（94/100）、Validate（97/100）、Snapshot、Upgrade
- 治理基线：Automation Platform Freeze（ADR-0002）
- 原则 #8：Tool Independence（AI 工具是客户，PAIOS 是平台）
- 原则 #9：Bootstrap First（AI 工具必须加载平台治理信息）

---

## Version History

| Version | Date | Summary |
|---------|------|---------|
| **1.0.1** | 2026-07-10 | Multi-Instance Architecture Baseline + Governance Layer + Release Management |
| **1.0.0** | 2026-06-29 | Initial Production Platform Baseline |
