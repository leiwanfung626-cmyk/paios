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
