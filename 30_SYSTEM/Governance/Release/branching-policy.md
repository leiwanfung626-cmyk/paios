---
title: "Branching Policy — 分支策略"
status: Active
created: 2026-07-11
related:
  - release-checklist.md
  - version-policy.md
  - ../../ADR/ADR-INDEX.md
  - ../../Governance/Change-Control.md
---

# Branching Policy（分支策略）

> PAIOS 采用简约分支模型。当前为单操作员模式（Developer = Maintainer = 一人），
> 分支策略围绕"master 始终可发布"展开。

---

## 分支模型

```
master ───────●──────────●──────────●──────────► (releases)
               \        / \        /
feature/*       ●──●──●   ●──●──●
feature/cross-engine-runtime ●────●────●
```

### master（主分支——生产就绪）

- **唯一可发布的分支**。Master 始终处于生产就绪状态。
- 所有 Release Tag 仅从 master 打出。
- 禁止直接在 master 上开发——变更须经由 pilot 或 feature 分支。
- Pilot 期间 master 保持冻结，仅接受 Pilot 过闸后的合并。

### pilot（工程试运行分支）

- 命名：`pilot`（固定名称）
- 用途：**Engineering Pilot** 期间的全部开发在此进行
- 生命周期：从 master 分出 -> 每日 Commit -> Pilot Exit -> 合并回 master -> 删除
- **纪律**：
  - Commit - 每天结束前所有修改需提交
  - Push - Pilot 期间不推送到 origin
  - Merge to master - 仅 Pilot Exit 后合并
  - 每天结束前 pilot 分支必须能独立运行（不可留下半成品代码）
- 适用阶段：L3 架构变更后的 Engineering Pilot 阶段

### feature/*（功能分支）

- 命名：`feature/<short-description>`（如 `feature/cross-engine-runtime`）
- 用途：新功能开发、架构变更、治理修订
- 生命周期：从 master 分出 → 开发 → PR → 合并回 master → 删除
- L2 及以上变更（见 [Change Control](../Change-Control.md)）必须使用 feature 分支

### hotfix/*（热修复分支，可选）

- 命名：`hotfix/<short-description>`
- 用途：生产环境紧急修复
- 生命周期：从 master 分出 → 修复 → 直接合并回 master + 打 PATCH tag
- 热修复后应补 ADR（如需要）并记录在 CHANGELOG

### release/*（发布分支，可选）

- 命名：`release/vX.Y.Z`
- 用途：版本发布的最后准备阶段（版本冻结、文档完善）
- 生命周期：从 master 分出 → 最终检查 → 合并回 master + 打 tag
- 只有在需要多轮 RC 测试时才使用

---

## 提交纪律

所有提交遵循 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

### Type

| Type | 用途 | 版本影响 |
|------|------|----------|
| `feat` | 新功能 | MINOR |
| `fix` | 修复 | PATCH |
| `docs` | 文档 | PATCH |
| `refactor` | 重构（不改变行为） | PATCH |
| `chore` | 日常维护 | PATCH |
| `governance` | 治理规则 | PATCH |
| `release` | 版本发布 | — |

### Scope 示例

| Scope | 说明 |
|-------|------|
| `(fim)` | Federated Instance Manifest |
| `(governance)` | 治理规则 |
| `(case-01)` | 特定实例 |
| `(adr)` | ADR 相关 |
| `(docs)` | 文档 |

### 架构变更强制要求

- 架构相关 commit 必须标注关联 ADR：`ADR-0017`
- L2 及以上变更必须标注审查引擎：`Reviewed-by: <engine-name>`
- 架构变更 commit 与 git cleanup（merge）commit **严格分离**
- Git History 四段展开：Architecture → Governance → Git Cleanup → Physical Separation

> 详见 [Change Control §4](../Change-Control.md)

---

## 版本标签

```
vMAJOR.MINOR.PATCH
```

- 所有 Release 必须在 master 上打 tag
- Tag 必须是 annotated tag：`git tag -a vX.Y.Z -m "vX.Y.Z"`
- 推送 tag：`git push origin vX.Y.Z`

---

> 关联：[Version Policy](version-policy.md) | [Release Checklist](release-checklist.md) | [Change Control](../Change-Control.md) | [Release Flow SOP](../SOP/SOP-2026-07-10-0001-Release-Flow.md)
