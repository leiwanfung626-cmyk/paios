type: architecture_overview_packet

id: PAIOS-2026-0712-ARCH-OVERVIEW-001

title: "PAIOS Platform — 架构全景、多实例关系与 AI 引擎协作"

generated_at: 2026-07-12T14:00:00+08:00
generated_by: Case-02 Developer Instance (evan)
baseline: v1.1.0-pilot-baseline (ce72446)

---

## 一、平台概况

PAIOS (Personal AI Operating System) v1.0.1
状态: Architecture Frozen
核心哲学: 生命周期驱动 · 工具独立 · 证据驱动演进

### 七层目录模型

| 层 | 目录 | 功能 |
|----|------|------|
| L0 | 00_CAPTURE/ | 信息入口（Inbox） |
| L1 | 10_WORK/ | 活跃工作区（临时） |
| L2 | 20_KNOWLEDGE/ | 正式知识库（已验证） |
| L3 | 30_SYSTEM/ | 系统内核（治理、ADR、原则） |
| L4 | 40_AUTOMATION/ | 自动化引擎 |
| L5 | 50_DATA/ | 数据基础设施 |
| L6 | 60_HISTORY/ | 工程历史档案 |

生命周期流: Capture → Work → Knowledge → System/Automation → Data → Archive

---

## 二、多实例架构（四层模型）

依据 ADR-0016 Multi-Instance Architecture Baseline.

```
L1  Platform (PAIOS Core)        平台代码，开发者维护，git pull 更新
        ↓
L2  Instance (每用户一个 PAIOS)  部署单元，独立运行，用户资产留本地
        ↓
L3  Manifest (实例状态)          FIM 协议，实例主动声明状态
        ↓
L4  Fleet (聚合观察)             只读汇总，位于仓库外
```

Core 包含: ADR · SOP · Evolution · Registry · 40_AUTOMATION 脚本 · RELEASES · CHANGELOG · Specifications

---

## 三、三级角色模型

依据 ADR-0018 Multi-Instance Role Model.

| Case | 角色 | 使用者 | 机器 | 场景 | Core 权限 | 状态 |
|------|------|--------|------|------|-----------|------|
| Case-01 | Platform Maintainer | feng | 工作机 | 日常工作 | 读写 + **唯一合并入口** | 🟢 运行中 |
| Case-02 | Developer | evan | 个人机（本机） | 个人/照片/照片整理 | 写 feature 分支，不能合并 | 🟢 已同步 baseline |
| Case-03 | Pilot User | evan | 同机 | 考研复习 | 只读 Core，只写 Workspace | ⚪ 待接入 |

### 黄金纪律

> Workspace 可以每天变化；Platform 只能通过 Release 变化。
> Case-02/03 结构上无法污染平台 Core。

---

## 四、Fleet Manifest Exchange

依据 ADR-0013（Proposed）、ADR-0015（Proposed）、ADR-0017（Enforced）。

Fleet **不进入 Git**。通过独立交换通道同步。

### 目录结构

```
E:\FleetExchange\          <-- 共享交换区（Quark/Tailscale/LAN）
├── Case-01\
│   └── manifest.yaml      <-- Case-01 写入，其他实例读取
├── Case-02\
│   └── manifest.yaml      <-- Case-02 写入（本机职责）
└── Case-03\
    └── manifest.yaml      <-- 预留
```

### Case-02 每日推送

| 输出目标 | 路径 | 策略 |
|---------|------|------|
| 共享交换区 | E:\FleetExchange\Case-02\manifest.yaml | 始终覆盖 |
| 本地归档 | PAIOS/Fleet/cases/case-02-YYYYMMDD.yaml | 每日副本 |
| 本地最新 | PAIOS/Fleet/cases/case-02.yaml | 始终覆盖 |

触发方式: Windows Task Scheduler 每日定时 → 40_AUTOMATION\05_SCRIPTS\fleet-push-case-02.bat

---

## 五、AI 引擎协作模型

依据 ADR-0019 AI Engine Role Model.

### 核心原则

> Engine owns execution; PAIOS owns continuity.
> AI 引擎负责执行，PAIOS 负责连续性（Task/Handoff/Knowledge/Governance）。
> 所有引擎可替换，角色不变。

### 引擎清单

| 引擎 | 角色 | 运行方式 | 成本系数 | 适配器 | 适用场景 |
|------|------|---------|---------|--------|---------|
| Reasonix | 主编码引擎 | 本地 | 1.0 | ✅ active | 编码、Shell、Python、照片处理 |
| WorkBuddy | 主知识/日常引擎 | 本地 | 1.0 | ✅ active | 写作、知识沉淀、日常记录 |
| ChatGPT | 外部 API 引擎 | 云端 | 2.5 | ❌ 未实现 | 对话、推理、文档分析 |

### 调度策略

```
code_task           → Reasonix（首选）
writing_task        → WorkBuddy（首选）
knowledge_flow      → WorkBuddy（首选）
photo_organizer     → Reasonix（必须，依赖本地 GPU/库）
conversation        → WorkBuddy → ChatGPT（降级链）
default             → WorkBuddy
```

### 协作机制：四层交接

```
Engine 层    Reasonix / WorkBuddy / ChatGPT
                ↓  Adapter（read/write/export/import）
Adapter 层   适配器统一接口
                ↓  handoff.yaml
Task 层      10_WORK/{task_id}/ 标准交接文件
                ↓  知识验证与沉淀
Knowledge 层 20_KNOWLEDGE/ → ADR / SOP / 文档
```

---

## 六、当前治理焦点

### 已完成的治理闭环

```
CASE-001（第一次多实例并流，发现 4 个问题）
    ↓
ADR-0017（平台纯度 — Core/Workspace/Instance-State 三桶隔离）
    ↓
Phase B 蓝图（Core/Workspace 物理拆分）
    ↓
ADR-0018（角色模型 — Maintainer/Developer/Pilot User 三级）
    ↓
边界建立（Phase B Step 2，Commit 2）
    ↓
本包（架构全景归档）
```

### 待推进

- [ ] Phase B Stage 1 — Pilot（Case-01 单实例试点 14 天）
- [ ] Phase B Commit 3 — Git Cleanup（解决远端分叉）
- [ ] Phase B Commit 4 — Physical Separation（git rm --cached）
- [ ] Phase B Rollout — Case-02/03 统一升级
- [ ] Stage 1 完成条件：7 天无故障 + 首份 fleet.md 周报

---

## 七、关键文档索引

| 内容 | 路径 |
|------|------|
| 架构总览 | 30_SYSTEM/Vision/03_Architecture.md |
| 原则 | 30_SYSTEM/Principles.md |
| ADR 索引 | 30_SYSTEM/ADR/ADR-INDEX.md |
| 多实例架构 | 30_SYSTEM/ADR/ADR-0016-*.md |
| 平台纯度 | 30_SYSTEM/ADR/ADR-0017-*.md |
| 角色模型 | 30_SYSTEM/ADR/ADR-0018-*.md |
| AI 引擎角色 | 30_SYSTEM/ADR/ADR-0019-*.md |
| CASE-001 复盘 | 30_SYSTEM/Evolution/Case-Studies/CASE-001-Retrospective.md |
| Phase B 蓝图 | 30_SYSTEM/Evolution/Phase-B-Core-Workspace-Split.md |
| Fleet 案例 | Fleet/cases/README.md |
| 每日推送脚本 | 40_AUTOMATION/05_SCRIPTS/fleet-push-case-02.bat |
| FleetExchange | E:\FleetExchange\ |

---

## 八、关系总图

```
┌──────────────────────────────────────────────────────────┐
│                       PAIOS 平台                          │
│            (七层目录 · ADR 治理 · 生命周期驱动)             │
└───────────┬───────────┬───────────┬──────────────────────┘
            │           │           │
      ┌─────▼────┐ ┌───▼────┐ ┌───▼──────┐
      │ Case-01  │ │Case-02 │ │ Case-03  │
      │Maintainer│ │Developer│ │PilotUser │
      │  (feng)  │ │ (evan) │ │  (evan)  │
      │  🟢运行中 │ │ 🟢已同步│ │ ⚪待接入  │
      └─────┬────┘ └───┬────┘ └───┬──────┘
            │          │          │
            └──────────┼──────────┘
                       │
              ┌────────▼────────┐
              │  FleetExchange  │
              │ (Manifest 交换)  │
              │ Quark/Tailscale │
              └─────────────────┘

┌──────────────────────────────────────────────────────────┐
│                    AI 引擎层（可替换）                     │
│                                                          │
│   Reasonix         WorkBuddy          ChatGPT            │
│   主编码引擎        主知识引擎         外部 API 引擎        │
│   本地·零成本       本地·零成本         云端·成本 2.5       │
│   适配器: ✅ active  适配器: ✅ active   适配器: ❌ 未实现    │
│                                                          │
│   通过 handoff.yaml + Adapter + Scheduler 统一协作         │
│   引擎可插拔替换，角色不随引擎变化                          │
└──────────────────────────────────────────────────────────┘
```

---

end_of_packet
