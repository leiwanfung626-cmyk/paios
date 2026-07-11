---
title: "Operating Model — 多实例角色与数据流模型"
status: Active
created: 2026-07-11
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

---

## 1. 角色表（Role Table）

| Case | 角色 | 对 Core 的权限 | 日常动作 | 不可逆动作 |
|------|------|----------------|----------|------------|
| **Case-01** | Platform Maintainer（Developer） | **读写全权** | 开发平台、架构、发布、聚合 Fleet、决策 CASE | 改 ADR / 发布 Release / push Core |
| **Case-02** | Platform User（Personal） | **只读（git pull）** | 写 Workspace、用平台、反馈、publish Manifest | 无（不碰 Core） |
| **Case-03** | Platform User（Study） | **只读（git pull）** | 写 Workspace、用平台、反馈、publish Manifest | 无（不碰 Core） |

> 一句话：**Core 的唯一写入口是 Case-01（Developer）。** Case-02/03 是平台使用者，不是平台开发者。

---

## 2. 单向数据流（One-Way Flow）

```
                Core（平台能力）
                  │  git pull（只读）
                  ▼
         Case-01（Developer / Maintainer）
                  │
            发布 Release（Tag vX.Y.Z + Release Notes）
                  │
      ┌───────────┴────────────┐
      ▼                        ▼
 Case-02（User）          Case-03（User）
      │ 写 Workspace            │ 写 Workspace
      │ （10_WORK / 20_KNOWLEDGE/Personal / Today.md）
      │                        │
      └───────────┬────────────┘
                  │  collect_manifest → publish（out-of-band）
                  ▼
             F:\Fleet\incoming\case-XX.yaml
                  │
             Developer Review（聚合 / 统计 / 决策下一轮 CASE）
```

**原则**

- User → Core：**无**（永不 push、永不 merge、永不改平台文件）
- Core → User：Release 经 `git pull` 下发
- User → Developer：Manifest（状态）+ Issue/Feedback（改进建议），均 out-of-band
- Developer → Fleet：聚合结果，不回推 User

---

## 3. 平台受保护文件（Platform Protected Files · User 只读）

只有 Developer（Case-01）可改；Case-02/03 视作**只读**，禁止编辑、禁止 push：

| 受保护对象 | 说明 |
|------------|------|
| `30_SYSTEM/` | ADR / Architecture / Governance / Lifecycle / Registry / Principles / Evolution |
| `40_AUTOMATION/` | Scripts / Capabilities / Registry / Installer / Upgrade / SOP |
| `RELEASES/` | 版本发布记录 |
| `CHANGELOG.md` · `SYSTEM_VERSION.md` · `MANIFEST.json` · `README.md` | 平台元信息 |
| `reasonix.toml` · `DEPLOYMENT.md` · `SYNC_STRATEGY.md` · `PAIOS_Technical_Standard_v1.0.docx` | 根级平台文件 |

---

## 4. 用户自有文件（User-Owned · 永远属于 User）

Developer 不碰、不共享、不入库：

| 自有对象 | 说明 |
|----------|------|
| `10_WORK/` | 项目、照片整理脚本、个人工具 |
| `20_KNOWLEDGE/Personal/` | 考研 / OpenWrt / 个人资料 |
| `Today.md` · `00_CAPTURE/` · `90_ARCHIVE/`（本机） | 日更 / 收集 / 归档 |
| `Archive` · `Projects` · `Photos` | 用户资产目录 |

---

## 5. 黄金纪律（Golden Rule）

> **Workspace 可以每天变化；Platform 只能通过 Release 变化。**

- 日常工作（写知识、做项目、拍照、考研）不会污染平台——Workspace 与 Core 在权限上已隔离。
- 平台升级都有版本、有验证、有回滚——Platform 的唯一写入口是 Developer 的 Release。
- Case-02/03 永远不会因为一次日常操作，把 Workspace 内容带回 Core——因为写 Core 的能力不存在。

---

## 6. 平台改进通道（Improvement Channel）

```
User 想到改进
   │  记录 Issue / Feedback / Observation
   ▼
发给 Developer（Case-01）
   │  Developer 评估
   ▼
是否进入 CASE？
   ├─ 是 → CASE → ADR → Blueprint → Release → User git pull 获得
   └─ 否 → 记录为 Observation，留待后续
```

User **不得**直接改：ADR / Automation / Registry / Architecture / Lifecycle。

---

## 7. Developer 职责转变（Maintainer，非天天改）

Developer 以后不是"天天改平台"，而是"**维护平台**"——类似 Linux Kernel：

- 应用天天变，Kernel 很少变。
- Developer 维护平台稳定 + 响应 User 反馈 + 周期性 Release。
- 平台改动走完整 Architecture Lifecycle（Evidence→Case→ADR→Blueprint→Freeze→Boundary→Pilot→Rollout→Validate）。

---

## 8. 复用规则

- 本文件与 `ADR-0018`（决策层）、`SOP-2026-07-11-0001-User-Daily-Operations.md`（User 日常）、Governance 层（`Architecture-Lifecycle` / `Pilot-Gate` / `Rollout` / `Change-Control`）配套。
- 任何"用户能否改 X"的疑问，先查 §3 受保护清单，再查 Asset-Class（属哪类），最后查 ADR-0017（进 Core 还是 Workspace）。
- Role 模型的变更（如新增 Case-04）须走 Architecture Lifecycle，不得随手改本文件——本文件自身也是平台资产，遵循元治理原则（见 `Architecture-Lifecycle.md` §6）。
