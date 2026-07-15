# Contributing to PAIOS Platform

> 感谢你关注 PAIOS！PAIOS 是一个多实例 Personal AI Operating System。
> 在参与之前，请先了解本项目的角色模型和协作方式。

---

## 1. 角色模型（Role Model）

PAIOS 定义了两种角色（详见 [Operating Model](30_SYSTEM/Governance/Operating-Model.md)）：

| 角色 | 对 Core 权限 | 职责 |
|------|-------------|------|
| **Platform Maintainer**（Case-01） | 读写全权 | 开发平台、架构演进、发布 Release、聚合 Fleet、决策 CASE |
| **Platform User**（Case-02/03） | 只读（`git pull`） | 使用平台、写 Workspace、反馈问题、publish Manifest |

**如果你是 User：**
- 对 Core 仓库 **只执行 `git pull`**，不 push、不 merge、不改平台文件
- 日常工作在 `10_WORK/` 等自有目录进行
- 通过 Issue / Feedback 提交改进建议
- Manifest 状态通过 out-of-band 方式回传给 Maintainer

**如果你是 Maintainer：**
- 你是 Core 仓库的唯一写入口
- 所有平台变更必须走完整的 Governance 流程

---

## 2. 如何报告问题（Issues / Feedback）

任何人都可以提出问题或改进建议。

1. 在 GitHub Issues 中创建 Issue
2. 使用以下标签：
   - `bug` — 平台行为异常
   - `enhancement` — 功能建议
   - `question` — 使用问题
   - `observation` — 观察记录（低严重度）
3. 对于 User：问题描述应关注**使用体验**，而非直接给出方案
4. Maintainer 评估后决定是否进入 [CASE 流程](30_SYSTEM/Evolution/Case-Studies/README.md)

---

## 3. 架构变更流程

PAIOS 采用**证据驱动演进（Evidence-Driven Evolution）**。所有架构变更须遵循：

```
Evidence → Case → ADR → Blueprint → Freeze → Boundary → Pilot → Rollout → Validate
```

详见 [Architecture Lifecycle](30_SYSTEM/Governance/Architecture-Lifecycle.md)

### 变更分级（Change Control）

| 级别 | 范围 | 流程 |
|------|------|------|
| **L3 Architecture** | Core/Workspace 拆分、Registry 重构 | 完整 Lifecycle |
| **L2 Behavior** | 工作流调整、SOP 修订 | 精简 Lifecycle |
| **L1 Content** | 知识库增删、日常文档 | 直接操作 |

详见 [Change Control](30_SYSTEM/Governance/Change-Control.md)

### ADR 编写规范

- ADR 存放在 `30_SYSTEM/ADR/ADR-NNNN-Title.md`
- 必须包含四字段证据链：**Evidence / Implements / Frozen By / Supersedes**
- Reactive ADR（基于已有证据）和 Proactive ADR（前瞻设计）有不同要求
- 详见 [Decision Traceability](30_SYSTEM/Governance/Decision-Traceability.md)

---

## 4. Commit Message 规范

PAIOS 使用 **Conventional Commits** 格式：

```
<type>(<scope>): <description>

[optional body]
[optional footer: ADR-XXXX / Reviewed-by: <engine>]
```

### Type 列表

| Type | 用途 |
|------|------|
| `feat` | 新功能（触发 MINOR 版本） |
| `fix` | 修复（触发 PATCH 版本） |
| `docs` | 文档变更（README、知识库等） |
| `refactor` | 重构（不改变外部行为） |
| `chore` | 日常维护（gitignore、配置等） |
| `governance` | 治理规则变更 |
| `release` | 版本发布 |

### Scope 示例

- `(fim)` — Federated Instance Manifest
- `(governance)` — 治理规则
- `(case-01)` — 特定实例
- `(adr)` — ADR 相关

### 架构变更强制要求

- 架构相关 commit 必须标注关联 ADR：`ADR-0017`
- L2 及以上变更必须标注审查引擎：`Reviewed-by: reasonix`
- 架构变更 commit 与 `git cleanup` commit **严格分离**
- 详见 [Change Control §4](30_SYSTEM/Governance/Change-Control.md)

---

## 5. 分支策略（Branch Strategy）

| 分支 | 用途 | 说明 |
|------|------|------|
| `master` | 主分支——始终可发布 | 所有 Release 从 master 打 tag |
| `feature/*` | 功能开发分支 | 完成后 PR 到 master |
| `release/*` | Release 准备分支（可选） | 版本冻结、最后检查 |

- master 分支应始终保持**可发布状态**
- 功能开发在 feature 分支进行
- 与架构基线（Architecture Freeze）冲突的修改必须走 ADR

---

## 6. 发布流程（Release Process）

1. 更新 `CHANGELOG.md`（按 Keep a Changelog 格式）
2. 更新 `SYSTEM_VERSION.md`
3. 创建 Release Tag：`vMAJOR.MINOR.PATCH`
4. 生成 `RELEASES/vX.Y.Z.md` Release Notes
5. 推送至 GitHub
6. User 执行 `git pull` 获取更新

详见 [Release Flow SOP](30_SYSTEM/SOP/SOP-2026-07-10-0001-Release-Flow.md)

### Release Notes 模板

Release Notes 存放在 `RELEASES/` 目录，必须包含：
- 版本号与发布日期
- 变更分类（Features / Fixes / 用户须知）
- 兼容性说明（Core / Manifest / Workspace / Migration）
- 用户操作指引

---

## 7. 平台纯度规则（Platform Purity）

Core 仓库只包含**平台能力定义**。以下内容不进入 Core：

- `10_WORK/` — 项目工作区
- `20_KNOWLEDGE/Personal/` — 个人知识
- `00_CAPTURE/` — 日常收集
- `90_ARCHIVE/` — 历史归档
- `Today.md` — 日更新
- `Fleet/` — 实例状态（在 Core 仓库外）

详见 [ADR-0017: Platform Purity](30_SYSTEM/ADR/ADR-0017-Platform-Purity-Physical-Separation.md)

---

## 8. 代码风格

### Python

- 遵循 PEP 8
- 脚本存放在 `40_AUTOMATION/05_SCRIPTS/`
- 新脚本建议添加类型注解（type hints）
- 使用 `pathlib` 而非 `os.path`
- 使用 `argparse` 提供命令行接口

### Markdown

- 遵循项目现有格式
- 使用 ATX 标题（`#`），不混用 Setext
- 代码块标注语言
- 项目内部链接使用相对路径

### Shell

- 脚本存放在 `scripts/` 或 `40_AUTOMATION/05_SCRIPTS/`
- `.bat` 文件使用 **GBK** 编码（Windows 兼容）
- 为脚本添加 `set -e`（bash）或等效保护

---

## 9. 测试

- 测试目录：暂为 `40_AUTOMATION/08_TESTS/`
- 新功能脚本应包含基本的功能测试
- Python 测试建议使用 `pytest`

---

## 10. Code Review

- 所有 PR 需经 Review 后方可合并到 master
- L2 及以上变更在 commit message 中标注 `Reviewed-by: <engine>`
- 架构变更需交叉审查

---

## 参考文档

| 文档 | 说明 |
|------|------|
| [README.md](README.md) | 项目概览 |
| [Principles](30_SYSTEM/Principles.md) | 九项核心原则 |
| [ADR Index](30_SYSTEM/ADR/ADR-INDEX.md) | 架构决策索引 |
| [Architecture Lifecycle](30_SYSTEM/Governance/Architecture-Lifecycle.md) | 治理闭环 |
| [Operating Model](30_SYSTEM/Governance/Operating-Model.md) | 多实例角色与数据流 |
| [Change Control](30_SYSTEM/Governance/Change-Control.md) | 变更分级与纪律 |
| [CHANGELOG](CHANGELOG.md) | 版本变更历史 |
| [System Version](SYSTEM_VERSION.md) | 版本声明 |

---

*PAIOS — 工具独立，治理驱动。*
