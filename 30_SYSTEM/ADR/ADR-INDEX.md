# Architecture Decision Record Index

## Foundation Layer（基础架构）

| ADR | Status | Date | Title |
|-----|--------|------|-------|
| ADR-0002 | Active | 2026-06-29 | Automation Platform Freeze |
| ADR-0003 | Accepted | 2026-06-29 | Directory Architecture (10-Layer 00-90) |
| ADR-0004 | Accepted | 2026-06-29 | Knowledge Layer Design |
| ADR-0005 | Accepted | 2026-06-29 | Workflow Pipeline |
| ADR-0006 | Accepted | 2026-06-29 | Metadata Standard |
| ADR-0007 | Accepted | 2026-06-29 | Lifecycle Model |
| ADR-0008 | Accepted | 2026-06-29 | Automation Layer |
| ADR-0009 | Accepted | 2026-06-29 | Governance Model |
| ADR-0010 | Accepted | 2026-06-29 | Evolution Strategy |
| ADR-0011 | Accepted | 2026-06-29 | Decision Layer |

## Platform Evolution（平台演进 — 多实例架构）

| ADR | Status | Date | Title | Layer | Story |
|-----|--------|------|-------|-------|-------|
| ADR-0012 | Accepted | 2026-07-10 | Platform-Application Architecture (Core + Applications) | L1 Platform | [Story-001](../Evolution/Stories/001-为什么PAIOS不是第二大脑.md) |
| ADR-0016 | Accepted | 2026-07-10 | Multi-Instance Architecture Baseline (4-layer model) | L1–L4 | [Story-005](../Evolution/Stories/005-为什么不用直接Merge.md) |
| ADR-0017 | Accepted | 2026-07-11 | Platform Purity & Physical Separation (Core/Workspace/Instance-State) | L1–L4 | [Story-002](../Evolution/Stories/002-Platform-Purity-是如何诞生的.md) |
| ADR-0018 | Accepted | 2026-07-11 | Multi-Instance Role Model (Maintainer/Developer/Pilot User) & One-Way Flow | L1–L4 | [Story-003](../Evolution/Stories/003-CASE-001-改变了什么.md) |
| ADR-0019 | Accepted | 2026-07-12 | AI Engine Role Model (AI Fleet Governance) | L0 Governance | — |
| ADR-0014 | Proposed | 2026-07-10 | Upgrade Mechanism (Core/Workspace/Upgrade) | L1 Platform | — |
| ADR-0013 | Proposed | 2026-07-10 | Federated Instance Manifest (FIM — Instance State) | L3 Manifest | — |
| ADR-0015 | Proposed | 2026-07-10 | Federated Aggregation & Viewing | L4 Fleet | — |

## Governance（治理）

| ADR | Status | Date | Title |
|-----|--------|------|-------|
| ADR-0022 | Accepted | 2026-07-18 | Terminology and Positioning（术语与定位） |
| ADR-0023 | Accepted | 2026-07-18 | Review Cadence & Evolution Review（复盘节律） |
| ADR-9999 | Accepted | 2026-06-29 | Legacy Retention Policy |

## Experimental / Historical（实验性 / 已吸收）

| ADR | Status | Date | Title | Note |
|-----|--------|------|-------|------|
| ADR-0020 | Experimental | 2026-07-11 | Cross-Engine Trace & Work Context Inheritance | 原 ADR-0017（冲突编号）。四层 Trace 架构实验，50_RUNTIME 合并至 40_AUTOMATION 后已吸收 |
| ADR-0021 | Experimental | 2026-07-11 | Engine Scheduling & Runtime Management | 原 ADR-0018（冲突编号）。Engine Scheduler 实验，内容已移至 40_AUTOMATION/11_ENGINES/ + 12_SCHEDULER/ |

## Architecture Evidence（架构证据 / Case Studies）

> 真实演化证据，非会议纪要。详见 `30_SYSTEM/Evolution/Case-Studies/README.md`。

| Case | Date | Title | 证据等级 | 关联 ADR | Story |
|------|------|-------|----------|----------|-------|
| CASE-001 | 2026-07-11 | First Real Multi-Instance Convergence | Validated | ADR-0017 | [Story-003](../Evolution/Stories/003-CASE-001-改变了什么.md) |

> **注意（2026-07-09 维护）**：ADR-0001（Core API Freeze）从未实际创建——git 历史中无该文件记录，`Necessity_Impact_Audit.md` 已注明"不含 ADR-0001"。本索引原将其列为 Active 属历史遗漏，已移除该行。其余文档中对 ADR-0001 的引用已于 2026-07-09 统一清理（`99_Appendix.md`、`06_Governance.md`、`05_Decision_Layer.md`、`ADR-0003-Directory-Architecture.md` 及同源的 `CHANGELOG.md`、`Evidence_Level_System.md` 引用）。
