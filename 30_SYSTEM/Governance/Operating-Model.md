---
title: "Operating Model — 多实例角色与数据流模型（v2 — 三级模型）"
status: Active
created: 2026-07-11
updated: 2026-07-12
related:
  - ../ADR/ADR-0018-Multi-Instance-Role-Model.md
  - ../ADR/ADR-0017-Platform-Purity-Physical-Separation.md
  - ../Specifications/Asset-Class.md
  - ../SOP/SOP-2026-07-11-0001-User-Daily-Operations.md
  - Architecture-Lifecycle.md
---

# Operating Model（多实例角色与数据流模型）

> 本文件定义 PAIOS 多实例协作的**角色分工**与**数据流方向**。
> 它不重复 `ADR-0017`（内容分离）与 `Asset-Class`（分类轴），而是补上**"谁能动什么"**这一维。
>
> 三者关系：
> - `ADR-0017`：什么内容进 Core（Purity 判定）
> - `Asset-Class.md`：内容怎么分小类（Platform/Shared/Personal/Imported）
> - **本文件**：谁能写 Core（Role 判定）——与上面两者正交、互补
>
> **v2 更新（2026-07-12）**：角色模型从两级的 Maintainer/User 升级为三级的 Maintainer/Developer/Pilot User。

---

## 1. 角色表（Role Table）

| Case | 角色 | Core 权限 | 日常动作 | 不可逆动作 |
|------|------|-----------|----------|------------|
| **Case-01** | Maintainer | **读写 + 合并** | 架构设计、治理、Review、Release、ADR、聚合 Fleet、决策 CASE | 改 ADR / 发布 Release / push Core / 合并 PR |
| **Case-02** | Developer & Primary Integration Environment | **可写（Feature Branch）但不能合并到主线** | 新功能开发、跨环境集成验证、实验、提 Proposal | 直接 merge Core（禁止——必须经 Case-01 Review + Integration Validation） |
| **Case-03** | Pilot User | **只读 Core，写 Workspace** | 安装、升级、使用、反馈、Issue、提交 Manifest | 修改平台文件（禁止） |

> **一句话**：Core 的唯一合并入口是 Case-01（Maintainer），Case-02 通过 Proposal 提交变更，Case-03 只使用和反馈。

---

## 2. 数据流（Data Flow）

```
                Core（平台能力）
                  │  git pull
                  ▼
         Case-01（Platform Maintainer）
                  │
           发布 Release（Tag vX.Y.Z + Release Notes）
                  │
      ┌───────────┴────────────────────┐
      ▼                                ▼
Case-02（Platform Developer）    Case-03（Pilot User）
      │                                │
  开发 Feature Branch              git pull 升级
      │  新功能实验                   使用平台
      │  跨环境验证                   反馈 / Issue
      │  提交 Proposal                提交 Manifest
      │                                │
      └───────────┬────────────────────┘
                  │
                  ▼
          Proposal Pool
                  │
         Case-01 Review
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
   Approved              Rejected
      │                       │
      ▼                       ▼
 进入 Release            记录为 Observation
      │
      ▼
   New Release → git pull → 所有实例
```

**原则**

- **Case-02 可以开发任何内容**，但不得直接修改 Core 主线
- 所有希望进入平台的能力，必须经过 **Proposal → Review → Promote → Release** 流程
- **Case-03 永远不修改系统**——其反馈通过 Issue 通道进入 Proposal Pool
- Manifest 通过 **out-of-band publish** 回流到 `F:\Fleet\incoming\`

---

## 3. 平台受保护文件（Platform Protected Files）

只有 Maintainer（Case-01）可改；Case-02/03 视作**只读**：

| 受保护对象 | 说明 | Case-02 例外 |
|------------|------|-------------|
| `30_SYSTEM/` | ADR / Governance / Lifecycle / Principles / Evolution | 可读，不可写 |
| `40_AUTOMATION/` | Scripts / Registry / Installer / SOP | 可读，不可写 |
| `RELEASES/` | 版本发布记录 | 可读，不可写 |
| `CHANGELOG.md` · `SYSTEM_VERSION.md` · `MANIFEST.json` · `README.md` | 平台元信息 | 可读，不可写 |
| `reasonix.toml` · `DEPLOYMENT.md` · `SYNC_STRATEGY.md` | 根级平台文件 | 可读，不可写 |

---

## 4. 实例自有文件（Instance-Owned）

以下**永远属于实例本人**，各实例独立管理，不入 Core 仓库：

| 自有对象 | 说明 |
|----------|------|
| `10_WORK/` | 项目、脚本、个人工具 |
| `20_KNOWLEDGE/Personal/` | 个人知识、学习资料 |
| `00_CAPTURE/` · `90_ARCHIVE/` | 日常收集与归档 |
| `Today.md` | 每日记录 |
| `Fleet/incoming/`（Case-01 侧） | 实例 Manifest 收集 |

---

## 5. 黄金纪律（Golden Rule）

> **Workspace 可以每天变化；Platform 只能通过 Release 变化。**

- 日常工作（写知识、做项目）不会污染平台——Workspace 与 Core 已隔离
- 平台升级有版本、有验证、有回滚——Maintainer 的 Release 是唯一入口
- Case-02 可以大胆实验——在 Feature Branch 上，失败了也不污染 Core
- Case-03 不会因日常操作把内容带回 Core——写 Core 的能力不存在

---

## 6. 平台改进通道（Improvement Channel）

### Case-02（Developer）

1. 在 Feature Branch 上开发和测试
2. 验证完成后提交 **Proposal**（含变更说明、验证结果、关联 ADR）
3. Case-01 Review
   - Approved → 进入 Release 流程
   - Rejected → 记录为 Observation，留存备用
4. 不直接合并到 Core 主线

### Case-03（Pilot User）

1. 记录 Issue / Feedback / Observation
2. 发给 Maintainer（Case-01）
3. Case-01 评估是否进入 Proposal Pool
4. 在下一轮 Release 中 `git pull` 获得能力

---

## 7. Maintainer 职责转变

Maintainer 不是"天天改平台"，而是"**维护平台**"——类似 Linux Kernel：

- 日常：Review Proposal、响应 Issue、聚合 Fleet、维护 Release
- 周期性：阶段性新功能开发（通过 Release 发布）
- 治理：CASE → ADR → Blueprint → Freeze → Release
- 核心能力：**Review** 和 **决策**，而非仅开发

---

## 8. 复用规则

- 本文件与 `ADR-0018`（决策层）、`SOP-2026-07-11-0001-User-Daily-Operations.md`（User 日常）、`SOP-2026-07-10-0001-Release-Flow.md`（发布流程）配套。
- Role 模型的变更（如新增 Case-04/05）须走 Architecture Lifecycle，不得随手改。
- 本文件自身也是平台资产，遵循元治理原则（见 `Architecture-Lifecycle.md` §6）。
