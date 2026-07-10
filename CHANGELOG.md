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
