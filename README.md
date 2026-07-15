# PAIOS Platform

> **Personal AI Operating System** — 一个人工智能操作系统，伴随用户成长。

| | |
|---|---|
| Version | v1.0.1 |
| Status | Architecture Frozen |
| License | MIT |

---

## Overview

PAIOS 是一个以**生命周期驱动**的个人 AI 操作系统。它将知识工作从"文件管理"升级为"流程治理"：输入统一进入 Inbox，系统根据生命周期自动路由到工作区、知识库、自动化引擎或归档。

PAIOS 不是任何单一 AI 工具的配置——它是独立于工具的**平台**。所有资产使用开放格式（Markdown、YAML、Python、JSON），任何 AI 工具（Codex、Claude、ChatGPT、Gemini 等）都可以作为客户端接入。

---

## Documentation

PAIOS 拥有 ~115 个 Markdown 文档分布在系统的各个生命周期层中。
`docs/` 目录提供了**按需求分类的导航索引**，不重复存储内容：

| Section | Description |
|---------|-------------|
| [Architecture](docs/architecture/) | 愿景、原则、ADR、架构演进、设计笔记 |
| [Governance](docs/governance/) | 变更控制、决策追溯、发布管理 |
| [Guides](docs/guides/) | 面向 User 和 Maintainer 的操作指南 |
| [Decisions](docs/decisions/) | 全部 ADR 索引 + 演化证据 |
| [Reference](docs/reference/) | 规格说明、版本声明、自动化参考 |

> 所有原始文档保留在 `30_SYSTEM/`、`20_KNOWLEDGE/` 等生命周期层中。
> `docs/` 是引用层（Reference Layer），不是存储层。

---

## Architecture

### Layer Model

| Layer | Directory | Description |
|-------|-----------|-------------|
| **Capture** | `00_CAPTURE/` | 信息统一入口——所有新输入先进入 Inbox |
| **Work** | `10_WORK/` | 活跃工作区——进行中的项目、处理中任务 |
| **Knowledge** | `20_KNOWLEDGE/` | 正式知识库——经过验证的知识资产 |
| **System** | `30_SYSTEM/` | 系统内核——治理、ADR、原则、演进证据 |
| **Automation** | `40_AUTOMATION/` | 自动化引擎——脚本、Agent、Registry、Prompts |
| **Data** | `50_DATA/` | 数据基础设施 |
| **History** | `60_HISTORY/` | 工程历史档案（Engineering Journal + 版本历史） |
| **Archive** | `90_ARCHIVE/` | 历史归档 |

### Multi-Instance Model

PAIOS 支持多实例部署（ADR-0016~0018）：

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Case-01    │     │  Case-02    │     │  Case-03    │
│  Platform   │     │  Platform   │     │  Platform   │
│  Maintainer │     │  User       │     │  User       │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
                    ┌──────────────┐
                    │   Fleet/    │
                    │  (Federation)│
                    └──────────────┘
```

- **Maintainer**：对 Core 仓库有写权限，负责发布和治理
- **User**：只读 Core，写自己的 Workspace，通过 Manifest 单向回传状态

---

## Core Principles

1. **目录表达生命周期，不表达内容**
2. **每件事物有且仅有一个正式位置**
3. **工作区始终是临时的**
4. **知识必须经过验证才能进入知识库**
5. **自动化存储工作流，不存储知识**
6. **顶层目录数量保持最少**（冻结为 7 个）
7. **元数据是主要分类系统**
8. **工具独立**：PAIOS 是平台，AI 工具是客户端
9. **Bootstrap First**：AI 工具必须先加载平台治理信息

> 详见 [Principles](30_SYSTEM/Principles.md)

---

## Governance Framework

PAIOS 拥有一套完整的治理体系，记录在 `30_SYSTEM/Governance/` 中：

| Area | Description |
|------|-------------|
| **ADR** | Architecture Decision Records — 架构决策记录（Foundation / Platform Evolution / Governance 三层） |
| **Architecture Lifecycle** | Evidence → Case → ADR → Blueprint → Freeze → Boundary → Pilot → Rollout → Validate |
| **Change Control** | L1/L2/L3 变更分级 + 冻结策略 + 证据门禁 |
| **Decision Traceability** | ADR 四字段（Evidence / Implements / Frozen By / Supersedes）+ 双向追溯 |
| **Pilot Gate** | 试点 Entry/Exit Criteria |
| **Operating Model** | 多实例角色与数据流模型 |
| **Release Management** | 发布清单、版本策略、分支策略（`Governance/Release/`） |

> 详见 [ADR Index](30_SYSTEM/ADR/ADR-INDEX.md) | [Governance](30_SYSTEM/Governance/) | [Documentation](docs/)

---

## Quick Start

```bash
# 1. Clone 仓库
git clone git@github.com:leiwanfung626-cmyk/paios.git

# 2. 查看文档导航
cd docs/

# 3. 设置计算机身份（脚本自动配置 PAIOS_DRIVE 等环境）
bash scripts/setup-computer.sh

# 4. 创建 Inbox 并开始使用
echo "- [ ] 我的第一条输入" > 00_CAPTURE/Inbox.md
```

### Roles

- **如果你是 Maintainer**：对 Core 有写入权限，按 Release SOP 进行发布
- **如果你是 User**：只读 Core 仓库，将 Manifest 回传到 Fleet 目录

> 详见 [Operating Model](30_SYSTEM/Governance/Operating-Model.md) | [User SOP](30_SYSTEM/SOP/SOP-2026-07-11-0001-User-Daily-Operations.md)

---

## Versioning

PAIOS 遵循语义化版本（SemVer）：`MAJOR.MINOR.PATCH`

- **MAJOR**：架构冻结级变更（需经 Architecture Lifecycle）
- **MINOR**：平台能力新增（ADR → Release）
- **PATCH**：修复、文档、非破坏性功能

当前版本：**v1.0.1** — Multi-Instance Architecture Baseline（架构冻结）

> 详见 [SYSTEM_VERSION](SYSTEM_VERSION.md) | [CHANGELOG](CHANGELOG.md) | [Version Policy](30_SYSTEM/Governance/Release/version-policy.md)

---

## Project Layout

```
PAIOS/
├── 00_CAPTURE/          # 信息入口（Inbox）
├── 10_WORK/             # 活跃工作区
├── 20_KNOWLEDGE/        # 正式知识库
├── 30_SYSTEM/           # 系统内核
│   ├── ADR/             # 架构决策记录
│   ├── Governance/      # 治理规范
│   ├── Principles.md    # 九项核心原则
│   ├── SOP/             # 标准操作流程
│   └── Evolution/       # 演进证据与 Case Studies
├── 40_AUTOMATION/       # 自动化脚本与 AI 配置
│   ├── 00_REGISTRY/     # 能力注册中心
│   ├── 05_SCRIPTS/      # 自动化脚本
│   └── ...
├── 50_DATA/             # 数据基础设施
├── 60_HISTORY/          # 工程历史档案
│   └── JOURNAL/         # 工程日志（Engineering Journal）
├── 90_ARCHIVE/          # 历史归档
├── CHANGELOG.md         # 变更日志
├── CONTRIBUTING.md      # 贡献指南
├── LICENSE              # MIT 许可证
├── SYSTEM_VERSION.md    # 版本声明
├── pyproject.toml       # Python 项目配置
├── docs/                # 文档导航索引
├── scripts/             # 系统管理脚本
```

---

## Automation Scripts

`40_AUTOMATION/05_SCRIPTS/` 包含平台自动化脚本：

| Script | Description |
|--------|-------------|
| `collect_manifest.py` | 只读收集实例状态，生成 manifest.yaml |
| `classify_files.py` | 文件自动分类 |
| `vision_query.py` | 视觉模型查询工具 |
| `check_vision_payload.py` | 视觉载荷检查 |
| `douyin.bat` / `douyin.sh` | 抖音转写辅助脚本 |

---

## Contributing

PAIOS 有多实例角色模型，参与前请阅读：

- [Operating Model](30_SYSTEM/Governance/Operating-Model.md) — 角色与数据流
- [CONTRIBUTING.md](CONTRIBUTING.md) — 贡献指南
- 所有架构变更须遵循 [Architecture Lifecycle](30_SYSTEM/Governance/Architecture-Lifecycle.md)

---

## License

MIT License © 2026 PAIOS Platform Contributors. 详见 [LICENSE](LICENSE)。

---

## Acknowledgments

Built with the assistance of AI tools (Codex, Claude, ChatGPT, Gemini).
PAIOS is the platform — AI tools are the clients.
