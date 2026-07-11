---
title: "ADR-0018 — Multi-Instance Role Model (Developer / User) & One-Way Flow"
status: Accepted
evidence_level: Validated
date: 2026-07-11
related:
  - ADR-0017-Platform-Purity-Physical-Separation.md
  - ../Governance/Operating-Model.md
  - ../SOP/SOP-2026-07-11-0001-User-Daily-Operations.md
  - ../SOP/SOP-2026-07-10-0001-Release-Flow.md
  - ../Evolution/Case-Studies/CASE-001-Multi-Instance-First-Convergence.md
  - Architecture-Lifecycle.md
---

# ADR-0018 — Multi-Instance Role Model & One-Way Flow

## Decision Traceability（决策可追溯性）

> 本 ADR 遵循 `30_SYSTEM/Governance/Decision-Traceability.md` 四字段规范。

- **Evidence**: CASE-001 (Multi-Instance First Convergence, Validated) —— 根因：三实例均以 Developer 身份操作，互相污染
- **Implements**: Architecture Lifecycle（Role / Owner 模型）+ 扩展 ADR-0017（Platform Purity 的"谁能动 Core"补充）
- **Frozen By**: c49cd54 (design freeze, unpushed)
- **Supersedes**: `SOP-2026-07-10-0001-Release-Flow.md` 第 ② ③ 步「User 推送 PAIOS-Usage/ 至 Core 仓库」的用户 push 机制（改为 out-of-band publish → Fleet）

> 类型：**Reactive ADR**——由 CASE-001 暴露的真实根因（三实例同权 → 互相污染）触发，非前瞻预判。

## Summary（摘要）

CASE-001 暴露的四个缺陷（Manifest 单路径冲突 / Workspace 泄漏 / Fleet 双位置 / 两套 Manifest）只是表象。根因是：**三个实例全部以 Developer 身份运行**——都能改平台文件、都能 push Core、都能 merge。对称的能力导致对称的污染。

本 ADR 的决策不是"告诉 Case-02/03 不要 push"（一条行为规则，压力下必破），而是**重新定义角色，让污染能力从结构上不存在**：

- **Case-01 = Platform Maintainer（Developer）**：Core 的唯一写入口。
- **Case-02 = Platform User（Personal）** / **Case-03 = Platform User（Study）**：只使用平台、只反馈，永不写 Core。

配套建立**单向数据流**与**平台受保护文件清单**，使多实例协作形成清晰、可持续的治理模式。

## Context（背景）

CASE-001（§新发现）记录三个实例把共享仓库当成自己的 Workspace 互推，根因不是"某人手滑"，而是**架构没有区分角色**：每台机器都拥有完整的 Developer 能力（改 ADR、改 Registry、push Core、merge 远端）。只要能力存在，污染就只是时间问题。

真正的修复是**消除能力的不对称来源**——让写 Core 的能力只存在于 Case-01。这与 ADR-0017（内容分离：Core/Workspace/Instance-State）正交互补：

- ADR-0017 解决**"什么内容进 Core"**（Purity 判定）
- 本 ADR 解决**"谁能写 Core"**（Role 判定）

两者共同构成"平台不被污染"的双重保险。

## Decision（决策）

### D0 — 角色模型（Role Model）

| Case | 角色 | 平台权限 | 职责 |
|------|------|----------|------|
| Case-01 | **Platform Maintainer（Developer）** | 读写 Core 全权 | 平台开发、架构、发布、聚合 Fleet、决策 CASE |
| Case-02 | **Platform User（Personal）** | 只读 Core，写 Workspace | 使用平台、反馈问题、提交 Manifest |
| Case-03 | **Platform User（Study）** | 只读 Core，写 Workspace | 使用平台、反馈问题、提交 Manifest |

> **核心转变**：Case-02/03 从"平台开发者"归位为"平台使用者"。它们不再拥有改 Core 的能力，因此不会因一次日常操作把 Workspace 内容带回 Core。

### D1 — 单向数据流（One-Way Flow）

```
                Core
                  │  (git pull，只读)
                  ▼
         Case-01（Developer / Maintainer）
                  │
           发布 Release（Tag vX.Y.Z）
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
Case-02（User）         Case-03（User）
      │  (日常写 Workspace)     │  (日常写 Workspace)
      │                       │
      └───────────┬───────────┘
                  │  publish Manifest（out-of-band）
                  ▼
             F:\Fleet\incoming\
                  │
             Developer Review（聚合 / 统计）
```

- **User 永远不直接修改 Core，永不 push Core，永不 merge 远端。**
- Manifest 通过 **out-of-band publish**（collect_manifest → publish → `F:\Fleet\incoming`）回流，不经 Core 仓库（见 D6）。

### D2 — 平台受保护文件（Platform Protected Files，User 只读）

以下文件/目录**只有 Developer（Case-01）可改**；Case-02/03 视作只读，禁止编辑、禁止 push：

- `30_SYSTEM/`（ADR / Architecture / Governance / Lifecycle / Registry / Principles）
- `40_AUTOMATION/`（Scripts / Capabilities / Registry / Installer / Upgrade）
- `RELEASES/`
- `CHANGELOG.md` · `SYSTEM_VERSION.md` · `MANIFEST.json` · `README.md`
- 根级平台文件：`reasonix.toml` · `DEPLOYMENT.md` · `SYNC_STRATEGY.md` · `PAIOS_Technical_Standard_v1.0.docx` 等

### D3 — 用户自有文件（User-Owned，永远属于 User）

以下**永远属于实例本人**，Developer 不碰、不共享、不入库：

- `10_WORK/`（项目、照片整理脚本、个人工具）
- `20_KNOWLEDGE/Personal/`（考研 / OpenWrt / 个人资料）
- `Today.md` · `00_CAPTURE/` · `90_ARCHIVE/`（本机）
- `Archive` · `Projects` · `Photos` 等用户资产目录

### D4 — 黄金纪律（Golden Rule）

> **Workspace 可以每天变化；Platform 只能通过 Release 变化。**

这句话是本次 Phase B 最值得固化的一条。它意味着：

- 日常工作（写知识、做项目、拍照、考研）**不会污染平台**——因为 Workspace 与 Core 在权限上已隔离。
- 平台升级**都有版本、有验证、有回滚**——因为 Platform 的唯一写入口是 Developer 的 Release。
- Case-02/03 **永远不会因为一次日常操作，把 Workspace 内容带回 Core**——因为写 Core 的能力不存在。

### D5 — 平台改进通道（Improvement Channel）

User 若想到平台改进：

1. **记录**（Issue / Feedback / Observation），**不自主改**。
2. **发给 Developer**（Case-01）。
3. Developer 决定是否进入 **CASE → ADR → Blueprint → Release**。
4. User 在下一轮 **Release** 中 `git pull` 获得能力。

User **不得**直接改：ADR / Automation / Registry / Architecture / Lifecycle。

### D6 — 取代"用户 push Core"机制

现有 `SOP-2026-07-10-0001-Release-Flow.md` 第 ② ③ 步描述「User `git push` 自己的 `PAIOS-Usage/` 到 Core 仓库」——该机制本身是污染向量（用户 push 即拥有写 Core 能力），**被本 ADR 取代**：

- Manifest 不再经由 Core 仓库回流，改为 **out-of-band publish → `F:\Fleet\incoming\`**（USB / 复制 / API / 邮件均可，语义先确立）。
- User 对 Core 仓库只有 `git pull`（读），没有 `git push`（写）。
- Release-Flow SOP 已加修订注记（见该文件顶部「修订 (2026-07-11, ADR-0018)」）。

## Consequences（后果）

**正面**

- 污染从结构上消除：写 Core 的能力只存在于 Case-01，Case-02/03 无能力即无事故。
- 角色清晰：Owner 明确（Lifecycle Gate Owner 表落地），多实例协作可持续。
- 与 ADR-0017 双重保险：内容分离（Purity）+ 角色分离（Role）。

**负面 / 成本**

- Case-02/03 不能自助改平台（**这是设计意图，不是缺陷**）——任何平台改动须经 Developer 的 Release。
- 要求 Developer 对反馈响应及时，否则 User 改进意愿受阻。
- Manifest 回流需 out-of-band 通道（当前靠复制/USB；Phase C 可上 HTTP API，但职责边界不变）。

## Validation（验证）

Role Model 在 Pilot（Case-01）与 Rollout（Case-02/03）下应持续满足：

- [ ] 0 次 User `git push` Core（User 仅有 pull 权限）
- [ ] 0 Workspace 泄漏（User 内容进 Core）
- [ ] 0 Manifest 冲突（out-of-band publish，按 `instance.id` 命名）
- [ ] 0 Fleet 回流（Fleet 不回推 User）
- [ ] 0 用户自行改 ADR / Registry / Architecture

> 上述指标与 CASE-001 的 Validation Metrics 对齐；Role Model 是其结构性根因修复。

## Related（关联）

- `ADR-0017`（平台纯度，内容维度）· `../Governance/Operating-Model.md`（角色模型规范）· `../SOP/SOP-2026-07-11-0001-User-Daily-Operations.md`（User 日常 SOP）· `../SOP/SOP-2026-07-10-0001-Release-Flow.md`（已修订，移除用户 push Core）· `../Evolution/Case-Studies/CASE-001-Multi-Instance-First-Convergence.md`（证据源）
