---
adr: "0016"
status: "Accepted"
date: "2026-07-10"
evidence_level: "Verified"
---

# ADR-0016: PAIOS 多实例架构基线（4 层模型 + 冻结项）

## 背景

本次对话（2026-07-10）的主题经历了**三次升级**：

1. Growth OS 是否应该作为 PAIOS 的一个分支？
2. PAIOS Core + Applications 如何演进？
3. PAIOS 从"一个人的系统"走向"多个实例的平台"。

真正的成果**不是某个单一机制（FIM / Aggregator）**，而是**第一次建立了 PAIOS 的多实例架构**。这是一次阶段转换：从"如何设计"转向"三个真实用户已经在用了，如何升级、兼容、观察、持续演进"。

本 ADR 把这次讨论收敛为一份**可冻结的架构基线**，让后续工作有统一的坐标，不再反复调整方向。

---

## 决策一：4 层架构模型

```
L1  Platform (PAIOS Core)       平台代码，开发者维护，git pull 更新
        │
        ▼
L2  Instance (每个用户一个 PAIOS)   部署单元，独立运行
        │
        ▼
L3  Manifest (实例状态)           FIM 协议，实例主动声明
        │
        ▼
L4  Fleet (聚合观察)              只读汇总，非侵入
```

各层对应关系：

| 层 | 含义 | 覆盖 ADR |
|----|------|----------|
| L1 Platform | PAIOS Core（平台代码） | ADR-0012（Core+Applications）、ADR-0014（Upgrade） |
| L2 Instance | 每个用户一个 PAIOS（独立部署） | ADR-0012、Instance 独立性（本 ADR 冻结③） |
| L3 Manifest | 实例状态声明（FIM 协议） | ADR-0013（FIM = Instance State） |
| L4 Fleet | 只读聚合观察层 | ADR-0015（Aggregation & Viewing） |

> 本 ADR **冻结架构形态与边界**；具体机制（FIM / Upgrade / Aggregation）的实现成熟度仍按各自 ADR 的 Proposed 状态在 Phase B 落地。

---

## 决策二：冻结项（Accepted，不宜再反复调整）

### ① PAIOS 不再只是个人系统
以前：`PAIOS`（单用户）。
现在：
```
PAIOS Core
    ├── Case-01（工作）
    ├── Case-02（个人）
    └── Case-03（考研）
```
**平台已经出现。** 这一点正式确立为架构基线。

### ② Core 与 Workspace 分离（比 FIM 更基础）
```
Core        平台代码（开发者维护，git pull 更新）
Workspace   用户资产（用户维护，升级永不被覆盖）
```
以后所有升级都围绕这条边界。**建议直接冻结——以后不会再改。**

### ③ Instance 独立
已经形成共识：每个人的知识、照片、项目**全部留本地**。
这一点**以后不要再讨论**。

### ④ FIM = Instance State（原则已成熟）
原则集：**Snapshot / Pull / Observe / Zero Intrusion**。
已足够，冻结。

---

## 决策三：重新定位——FIM 是 Instance State，不是 Usage

FIM 协议内容不仅含 Usage，还含：

`Version` / `Schema` / `Health` / `Profile` / `Capability` / `Evidence` / `Usage`

Usage 只是其中一个维度。后续文档与代码**统一使用"Instance State"定位**（ADR-0013 已采用此定位，本 ADR再次确认）。

---

## 决策四：设计纪律——不让架构领先数据

真实用户只有 **3 个**。Dashboard / Fleet / Capability / Validator 等机制均正确，但**实现时机由真实数据触发**，不允许架构领先于数据。这是 PAIOS 一贯的 Need-Driven / Necessity-Gated 原则。

---

## 路线图（摘要，详见 `30_SYSTEM/Evolution/Multi-Instance-Roadmap.md`）

| Stage | 内容 | 状态 |
|-------|------|------|
| Stage0 | 单实例 | ✅ 已完成 |
| Stage1 | 三个实例（Core / Workspace / Upgrade / Manifest） | ★ 当前 |
| Stage2 | Fleet MVP（aggregate.py → fleet.md → 版本统计 → Profile 统计） | ⏳ |
| Stage3 | Fleet Dashboard（HTML / 趋势 / Health / Adoption） | ⏳ |
| Stage4 | PAIOS Platform（Photo OS / Growth OS / Study OS 统一 Manifest） | ⏳ |

### 优先级

| 优先级 | 事项 | 是否立即 | 原因 |
|--------|------|----------|------|
| P0 | 冻结 Core / Workspace / FIM 三层架构 | ✅ | 后续工作基础，不宜反复调整 |
| P0 | 三个实例升级到同一 Core 版本（1.0.1） | ✅ | 建立统一版本基线 |
| P0 | 补齐 profile.yaml（Case-01 work / Case-02 personal / Case-03 study） | ✅ | 场景信息无法自动推导，是聚合关键 |
| P0 | 在三个真实实例运行 collect_manifest.py 并生成 Manifest | ✅ | 首次跨实例验证 FIM 设计是否成立 |
| P0 | 人工汇总三个 Manifest → 输出 fleet.md 周报 | ✅ | 用真实数据验证聚合需求，避免过早开发 Dashboard |
| P1 | Manifest Validator | ⏳ | 保证 Schema/版本一致性，降低维护成本 |
| P1 | aggregate.py 自动生成 Markdown/HTML 周报 | ⏳ | 人工汇总开始重复时再自动化 |
| P1 | Release / Migration 机制完善 | ⏳ | 版本迭代频率增加时再完善 |
| P2 | Fleet Dashboard / 趋势 / Capability Adoption | ⏳ | 至少 5–10 个真实实例后 |
| P3 | 统一应用生态（Photo/Growth/Study OS） | ⏳ | 应用成熟后再统一接入 FIM |

---

## 结论

这次工作的意义**不是设计一个新功能**，而是为 PAIOS 建立一套"**多实例持续演进机制**"：

> 实例自治 · 平台统一 · 升级可控 · 观察轻量 · 聚合非侵入

就此收敛设计，先把**三个真实实例**跑通完整闭环（升级 → Manifest → 人工聚合 → 周报），再根据真实使用数据决定下一步，而不是继续扩展架构。

---

**Related**: `ADR-0012-Platform-Application-Architecture.md` | `ADR-0013-Federated-Instance-Manifest.md` | `ADR-0014-Upgrade-Mechanism.md` | `ADR-0015-Federated-Aggregation-Viewing.md` | `30_SYSTEM/Evolution/Multi-Instance-Roadmap.md` | `RELEASES/upgrade-notice-1.0.1.md`
