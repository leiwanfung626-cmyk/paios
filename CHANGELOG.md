# Changelog

## v1.0.1 (2026-07-10)

### Federated Instance Manifest + Upgrade Mechanism

- ADR-0013: Federated Instance Manifest (FIM) — 多实例状态汇总协议
- ADR-0014: Upgrade Mechanism — Core/Workspace/Upgrade 三层 + 版本化发布
- ADR-0015: Federated Aggregation & Viewing — 三级架构 + 汇总模式（Git/Quark/API）+ 权限边界（设计原则，未实现）
- ADR-0016: Multi-Instance Architecture Baseline — 4 层模型（Platform→Instance→Manifest→Fleet）+ 冻结项（Core/Workspace 分离、Instance 独立、FIM=Instance State）；status=Accepted（架构基线冻结）
- 新增 collect_manifest.py（SCRIPT-0009）：只读现有结构生成 manifest.yaml
- 新增 PAIOS-Usage/profile.yaml：实例身份声明（场景画像）
- 非破坏性功能新增；不影响现有使用方式，不修改知识库

### Architecture Evidence & Phase B Blueprint (2026-07-11)

- **新增 `30_SYSTEM/Evolution/Case-Studies/`**：架构证据目录（README 定义 Case 公约）
- **CASE-001-Multi-Instance-First-Convergence.md**：第一次真实多实例并流证据（Validated 级），支撑 Phase B 触发
- **ADR-0017**：Platform Purity & Physical Separation（Accepted，Validated）—— Core/Workspace/Instance-State 三桶隔离 + Platform Purity Principle 判断标准
- **Phase-B-Core-Workspace-Split.md v2**：按 ADR-0017 + 用户评审修正（20_KNOWLEDGE 拆内容不拆目录、10_WORK 全私有、Fleet 子结构、Manifest collect→publish、B1 逻辑→B2 物理分阶段）
- 治理原则升级：确立 **Evidence-Driven Evolution（证据驱动演进）** 为治理方法论；将原先拟定的 "Evidence Before Architecture" 修正为更温和的表述——架构可基于原则进行前瞻设计，但是否成为正式平台能力须由真实运行证据验证（与 Need-Driven Promotion 一致，不否定前瞻性设计）
- 治理节奏细化（同批 refine）：Commit 2 更名 `refactor(governance): establish Core/Workspace boundaries`（建立边界，非拆分）；新增 **Pilot Gate**（Case-01 单实例试点两周、验证 5 信号过闸后再 Rollout Case-02/03）；CASE 固定增 **Decision Impact** 章节（证据链 Traceability）；蓝图 Step2/3/4 对应 Git History 四段 Architecture→Governance→Git Cleanup→Physical Separation

### Architecture Lifecycle & Blueprint Refinement (2026-07-11)

- **新增 `30_SYSTEM/Governance/Architecture-Lifecycle.md`**：从 Phase B v2 的 Commit 纪律升华出的**平台级架构生命周期**（Evidence→Case→ADR→Blueprint→Freeze→Boundary→Pilot→Rollout→Validate 闭环），Phase C/D 全部复用；明确与 Governance 1.0（Asset Lifecycle）的纵切/横切互补关系
- **Phase B v2 再精炼**：引入 **Asset Class（资产类别）** 抽象（Platform/Shared/Personal/Imported，零成本扩展）替代写死的 Platform/Personal；Registry 统一为 `Registry/`（capabilities/providers/workflow/schema），未来 Plugin/Tool/Agent 复用同一结构；Fleet 版本改为 **Manifest 自声明 `manifest_version`**（Fleet 不猜）；Pilot Gate 增 **Entry/Exit Criteria**（14 天 / 0 Critical / 0 Data Loss / Merge Normal / Manifest Stable）
- **ADR-0017 D0 升级**：Platform Purity Principle 判断标准从"别人 pull 有价值吗"提升为"**是否在定义平台能力**"（两层级判断 + 归属表），更符合架构边界、长期更稳定

### Governance Layer Extraction & Specifications (2026-07-11)

用户终评 Phase B 已进入**可实施蓝图（Implementation Blueprint）**阶段（架构思想 10/10、治理模型 10/10、工程可实施性 9.7/10），提出三点长期可维护性增强，全部落地：

- **Governance 抽离为独立层**：从 Phase B 蓝图内联内容中抽出平台级治理规范，置于 `30_SYSTEM/Governance/`，任何 Phase（B / C / D …）只引用、不复制：
  - `Architecture-Lifecycle.md`：端到端演进闭环（Evidence→Case→ADR→Blueprint→Freeze→Boundary→Pilot→Rollout→Validate），Phase C/D 复用
  - `Decision-Traceability.md`：ADR 强制四字段（Evidence / Implements / Frozen By / Supersedes）+ Blueprint 反向引用 + Commit 引用；制度化 **Reactive vs Proactive ADR** 区分（取代"Evidence 必须在 ADR 之前"的绝对表述）
  - `Pilot-Gate.md`：试点 Entry / Exit Criteria + 单实例试点模式
  - `Rollout.md`：全量推广前置条件 + 分批顺序 + Git History 四段展开
  - `Change-Control.md`：变更分级（L1 / L2 / L3）+ 冻结策略 + 证据门禁 + Commit 纪律
- **Asset Class 独立成规范**：`30_SYSTEM/Specifications/Asset-Class.md` 定义全平台内容分类轴（Platform / Shared / Personal / Imported），不隶属于 `20_KNOWLEDGE`，同样适用 `10_WORK/`、`Fleet/`；目录只是分类的实现。
- **Phase B 蓝图改为引用式**：§1.1 / §4 Pilot Gate / §8 治理闭环均改为引用 Governance 层与 Asset-Class 规范，不再内联实现。
- **ADR-0017 增加 Decision Traceability 四字段块**（Evidence: CASE-001 / Implements: Phase B Blueprint v2 / Frozen By: 472e53d / Supersedes: ADR-0016 §Phase B draft）+ 标注为 Reactive ADR。

### Architecture Lifecycle v1.0 冻结 (2026-07-11)

用户终评 Architecture Lifecycle 为"PAIOS 至今最重要治理文档"，给予架构思想 10/10、可复用性 10/10、长期治理成熟度 9.8/10，**建议冻结（后续修改须走新 CASE→ADR→新版本 Lifecycle，不得随手改）**。本轮为冻结前的最后一轮结构增强，仅落实用户点名 6 项，不引入 Canary/Sandbox/Release Ring 等新概念：

- **`lifecycle_version: 1.0`**：文件头增加版本字段；Blueprint 未来通过 `lifecycle:` 声明所遵循版本，避免混用。
- **Gate Owner 列**：各阶段 Gate 表新增 Owner 列（Evidence/Case=任何操作员；ADR/Blueprint/Freeze/Retrospective=Architect；Boundary/Pilot=Developer；Rollout/Validate=Maintainer+Fleet）；单操作员现状下由 Evan 兼任，字段为多人协同预留。
- **Evidence Severity**：新增四级严重度（Critical / Major / Minor / Observation），用于决定流程可跳过范围；CASE-001 的 Manifest 冲突判为 **Major**。
- **Retrospective Outcome**：回顾结论固定四选一（Accepted / Adjusted / Rejected / Deferred），CASE-002 将携带 `Outcome` 字段。
- **双向 Traceability**：`Decision-Traceability.md` 新增 §1.5 **CASE 追溯字段**（Evidence Commit / Triggered ADR / Severity），CASE-001 已补 `Evidence Commit: 472e53d`；闭环图改为 commit ↔ Blueprint ↔ ADR ↔ CASE 双向反查。
- **元治理原则（Meta-Governance）**：文档末 §6 新增——"Lifecycle 本身也是平台资产，任何修改都应遵循本 Lifecycle"，确立自洽的元治理基础；v1.0 当前冻结，待新 CASE 触发才升级。

### Release Flow & Fleet Separation (2026-07-10)

- 新增 `30_SYSTEM/SOP/SOP-2026-07-10-0001-Release-Flow.md`：v1.0.1 标准发布 SOP（5 步 + 职责边界表 + Manifest 单向流）
- 新增 `RELEASES/upgrade-receipt-1.0.1.md`：升级回执，跟踪三用户升级 / 回传状态
- 新增 `F:\Fleet\`（独立于 Core 仓库的 Developer 运营目录：`manifests/` + `reports/`）
- 明确职责边界：Core 同步用户 / Workspace 不碰 / Manifest 单向回传 / Fleet 不回推用户（写入 ADR-0015 + SOP）

### Architecture Review Fixes (2026-07-10)

- **ADR-INDEX.md**：按 Foundation / Platform Evolution / Governance 三组重新组织，新增 Layer 列标识 4 层归属
- **30_SYSTEM/Specifications/FIM-v1.md**：正式定义 FIM v1 为平台级协议（字段/类型/版本兼容性/实现契约）
- **60_REFERENCE_CASES/**：建立官方验证案例目录（Case-01~03），含 Stage 1 完成条件
- **RELEASES/1.0.1.md**：增加 Compatibility 字段（Core / Manifest / Workspace / Migration）
- **SYSTEM_VERSION.md**：版本总结强调"项目→可发布软件"的转变
- **empty dirs**：`40_AUTOMATION/02_PROMPTS/*/` 增加 README 标记 Reserved；删除 Claw/ 游离目录
- **manifest version fix**：manifest.yaml 版本不一致修复（v1.0.0 → v1.0.1）

## v1.0.0 (2026-06-29)

### Initial Production Platform Baseline

- PAIOS Platform v1.0.0 initialized
- 7-layer directory structure deployed on E:\PAIOS
- 30_SYSTEM: Principles (9), ADR (2), Config, Goals, Evolution
- 40_AUTOMATION: Registry, Capabilities, Prompts, Agents, MCP, Scripts, Legacy, Manifest
- 20_KNOWLEDGE: Concepts, Methods, SOP, Decisions, Models, References
- 00_CAPTURE: Inbox.md unified entry
- Operations: Doctor (94/100), Validate (97/100), Snapshot, Upgrade
- Governance: Automation Platform Freeze (ADR-0002)
- Tool Independence: Principle #8, Bootstrap First: Principle #9
