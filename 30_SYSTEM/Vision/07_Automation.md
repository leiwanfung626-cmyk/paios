# PAIOS 技术白皮书 v1.0 — 自动化体系

> **来源**：`40_AUTOMATION/` 目录结构 + `00_REGISTRY/`

## 7.1 自动化层结构

PAIOS 自动化引擎位于 `40_AUTOMATION/`，包含 11 个子系统：

```
40_AUTOMATION/
├── 00_REGISTRY/       # 服务注册中心（核心）
│   ├── agents.yaml
│   ├── capabilities.yaml
│   ├── providers.yaml
│   ├── scripts.yaml
│   └── workflows.yaml
├── 01_CAPABILITIES/   # 能力定义
├── 02_PROMPTS/        # 提示词库
│   ├── coder/
│   ├── planner/
│   ├── reviewer/
│   ├── system/
│   ├── teacher/
│   └── writer/
├── 03_AGENTS/         # Agent 定义
├── 04_MCP/            # MCP 接口
│   └── Reasonix/
├── 05_SCRIPTS/        # 自动化脚本
│   ├── Dashboard/
│   ├── Import/
│   ├── Knowledge/
│   ├── Maintenance/
│   └── Media/
├── 06_PROVIDERS/      # 提供商定义
├── 07_WORKFLOWS/      # 工作流定义
├── 08_TESTS/          # 测试
├── 09_LEGACY/         # 历史资产
│   ├── deprecated/
│   ├── original/      # DRS 时代的原始资产
│   ├── pending/
│   └── promoted/
└── 10_MANIFEST/       # 清单与状态
    ├── inventory.yaml
    ├── manifest.yaml
    └── migration_status.yaml
```

## 7.2 工具链标准化

| 工具 | 用途 | 状态 |
|------|------|------|
| **Python 3.10+** | 脚本运行时 | ✅ 就绪 |
| **Git** | 版本控制与跨设备同步 | ✅ 就绪 |
| **CLI** | 管理命令（doctor, validate, snapshot, upgrade） | ✅ 就绪 |
| **MCP** | Agent 接口协议 | ⚙️ 预留（Reasonix 目录已创建） |
| **YAML** | 配置格式统一 | ✅ 就绪 |
| **JSON** | Manifest 与状态 | ✅ 就绪 |

## 7.3 Registry First 原则

所有长期资产必须先注册到 Registry，再投入使用：

| Registry | 内容 | 当前状态 |
|----------|------|---------|
| `agents.yaml` | Agent 定义注册 | 框架就绪 |
| `capabilities.yaml` | 能力注册 | 框架就绪 |
| `providers.yaml` | AI 提供商注册 | 框架就绪 |
| `scripts.yaml` | 脚本注册（SCRIPT-0001~0004） | 3 pending, 1 registered |
| `workflows.yaml` | 工作流注册 | 框架就绪 |

**Registry 只反映现实状态**，不占位注册。

## 7.4 MCP / Agent 接口预留

`40_AUTOMATION/04_MCP/Reasonix/` 目录已创建，结构包含：

```
04_MCP/Reasonix/
├── Config/    # MCP 配置
├── Memory/    # MCP 记忆存储
└── Skills/    # MCP 技能注册
```

当前为框架预留状态，待 Agent 能力实质化后启用。

## 7.5 自动生成机制（预留）

### 当前可自动化的候选点

| 自动化点 | 当前方式 | 目标方式（Governance 2.0） |
|---------|---------|--------------------------|
| Impact Level 判定 | 人工判断 | 自动化规则校验 |
| Registry 更新 | 手动编辑 YAML | 脚本自动注册 |
| 知识索引 | 手动 grep | 自动构建索引 |
| 审查流程 | 人工 Review | PR Checklist 工具 |

### 晋升触发条件

与 Retrieve Capability 一致：**不预判需求，不提前引入复杂度。** 让真实工作驱动自动化晋升。

---

**关联文档**：[06_Governance.md](06_Governance.md) | [08_Evolution_Model.md](08_Evolution_Model.md) | `ADR-0006-Automation-Layer` | `40_AUTOMATION/`
