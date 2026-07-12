---
title: "Version Policy — 语义化版本规则"
status: Active
created: 2026-07-11
related:
  - release-checklist.md
  - branching-policy.md
  - ../../../SYSTEM_VERSION.md
  - ../../ADR/ADR-INDEX.md
---

# Version Policy（语义化版本规则）

PAIOS 遵循 [Semantic Versioning 2.0.0](https://semver.org/lang/zh-CN/)：

```
MAJOR.MINOR.PATCH
```

---

## 版本号递增规则

| 级别 | 触发条件 | 示例 |
|------|----------|------|
| **MAJOR** | 架构冻结级变更——顶层目录结构调整、Core 层接口不兼容 | `1.0.0` → `2.0.0` |
| **MINOR** | 平台能力新增——新 ADR 经完整 Lifecycle、新系统层文档 | `1.0.0` → `1.1.0` |
| **PATCH** | 修复、文档更新、非破坏性功能新增 | `1.0.0` → `1.0.1` |

## PAIOS 特殊规则

### 架构冻结规则

顶层目录结构（当前冻结为 00-90 十层模型）仅在以下条件满足 **至少两项** 时方可修改：

1. 连续使用 3 个月以上
2. 两个或以上真实项目暴露同一结构问题
3. 明显收益且可接受的迁移成本

> 见 `SYSTEM_VERSION.md` 与 `30_SYSTEM/Principles.md` § Architecture Freeze

### Pre-release 与 Build Metadata

| 后缀 | 含义 | 示例 | 稳定性 |
|------|------|------|--------|
| `-alpha.N` | 内部开发版，可能不完整 | `1.1.0-alpha.1` | 不稳定 |
| `-beta.N` | 外部测试版，功能完整 | `1.1.0-beta.1` | 较稳定 |
| `-rc.N` | 发布候选 | `1.1.0-rc.1` | 接近发布 |
| 无后缀 | 正式发布 | `1.1.0` | 稳定 |

PAIOS 日常开发不使用 pre-release 后缀——Master 分支始终可发布。
Pre-release 仅在需要多轮 Pilot 测试时使用。

### 版本声明位置

版本号必须在以下文件中保持一致：

| 文件 | 路径 |
|------|------|
| SYSTEM_VERSION.md | 根目录 |
| MANIFEST.json | 根目录 |
| pyproject.toml | 根目录 |
| CHANGELOG.md | 每次发布的版本头 |
| Release Notes | `RELEASES/vX.Y.Z.md` |

---

## 版本兼容性

| 组件 | 兼容性承诺 |
|------|-----------|
| **Core**（`30_SYSTEM/`、`40_AUTOMATION/`、根级配置） | PATCH 级别兼容 |
| **Manifest**（`FIM`、`profile`） | MAJOR 版本内向前兼容 |
| **Workspace**（`10_WORK/`、`20_KNOWLEDGE/Personal/`） | 不受平台版本影响——Workspace 永远是用户自有内容 |
| **Migration** | MAJOR 发布必须提供迁移指南 |

---

> 关联：[Release Checklist](release-checklist.md) | [Branching Policy](branching-policy.md) | [Release Flow SOP](../SOP/SOP-2026-07-10-0001-Release-Flow.md)
