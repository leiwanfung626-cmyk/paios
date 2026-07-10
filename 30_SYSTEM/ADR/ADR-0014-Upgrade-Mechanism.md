---
adr: "0014"
status: "Proposed"
date: "2026-07-10"
evidence_level: "Emerging"
---

# ADR-0014: PAIOS 升级机制（Upgrade Mechanism）— Core / Workspace / Upgrade 三层

## 背景

PAIOS Core 已从单用户个人系统演进到**多实例部署**阶段（当前 3 个 Reference Cases：Case-01 工作 / Case-02 个人 / Case-03 考研）。一旦交付给他人，每一次架构调整都不再只是"改代码"，而是"**产品发布**"。

当前没有升级机制：版本只记录在 `SYSTEM_VERSION.md`（v1.0.0）与 `CHANGELOG.md`，**实例不会声明自己的版本**，开发者靠"发微信通知"维持。几个月内就会失忆：谁升级了？升到哪版？谁没升？

## 问题

需要为 PAIOS 多实例生态定义一条**平台级升级原则**，满足：

1. 不靠人工通知用户，而是实例自我声明版本
2. 升级不破坏用户数据（Workspace 永不被覆盖）
3. 非强制、可退出：开发者发布 → 实例发现 → 用户决定
4. 任何目录结构变化都通过可重复执行（idempotent）的 Migration 完成
5. 符合现有治理：`SYSTEM_VERSION.md` 已声明"顶层结构冻结"，结构性变更需满足触发条件

## 决策

建立 **Core / Workspace / Upgrade 三层 + 版本化发布（Versioned Release）** 机制。

### 原则一：通知实例，不通知用户

每个 PAIOS 实例在 manifest（或 `.version`）中声明自己的 `core_version` 与 `manifest_version`。Aggregator（未来的 Fleet Dashboard）读取所有 manifest，直接回答：

> 哪些实例已升级 / 哪些停留在旧版 / 哪些需要迁移

开发者无需记住"通知了哪三个用户"。

### 原则二：版本化发布（Release Mechanism）

```
PAIOS/
├── CHANGELOG.md          # 持续记录版本线
└── RELEASES/
    ├── 1.0.1.md          # 每份发布：新增 / 影响 / 需要用户做 / 兼容性 / 迁移
    ├── 1.0.2.md
    └── 1.1.0.md
```

实例通过对比自身 `core_version` 与最新 Release 判断是否需要升级。

### 原则三：Upgrade Required（非强制提示）

Release 可声明 `minimum_core`。Aggregator 发现某实例 `core_version < minimum_core` 时，标记为 **Upgrade Available**——只是提示，绝不自动强制。PAIOS 不是 SaaS，是每个用户自己的实例。

### 原则四：Core / Workspace / Upgrade 职责分离

```
PAIOS
├── Core        平台代码（开发者维护，git pull 更新）
├── Workspace   用户资产（用户维护，升级永不被覆盖）
└── Upgrade     迁移脚本（把旧 Workspace 平滑适配新结构）
```

- **Core 演进**：发布版本、修 Bug、加能力
- **Workspace 归属用户**：知识、照片、项目、配置永远属于用户
- **Upgrade 负责结构适配**：新增配置文件 / 目录 / 注册项，全部通过 idempotent Migration

### 原则五：所有升级写成 Migration

```
migrations/
  001_add_profile.py     # 1.0.0 → 1.0.1：若 PAIOS-Usage/profile.yaml 不存在则复制模板
  002_register_*.py      # 未来 1.0.2
```

升级时按顺序执行所有未应用的 migration。用户无需手动复制文件。

### 原则六：绝不 zip 重发覆盖

禁止"发压缩包 → 覆盖 → 担心覆盖用户数据"模式。**Workspace 一行不被动。**

## 分阶段实施（Need-Driven，不一次性重构成平台）

与 `SYSTEM_VERSION.md` 的"架构冻结"策略一致——顶层结构变更需满足触发条件，故物理拆分分阶段：

- **Phase A（本次 v1.0.1，立即执行）**：建立版本化发布范式。bump 1.0.0→1.0.1；写 `CHANGELOG.md` + `RELEASES/1.0.1.md`；给三个用户发**统一升级通知**（手动，可验证，非自动）；manifest 经 `get_version()` 自动反映 `core_version`。**不做物理拆分**。
- **Phase B（触发条件：第二个真实实例跑通并暴露分发痛点）**：引入 Core/Workspace 物理分离 + `migrations/` + `migrate.py` + 每实例 `.version` 文件。届时 Phase A 的"手动通知"退场，由 Aggregator 版本检测接管。

## 与现有架构的兼容性

| 原则 | 兼容 | 说明 |
|------|------|------|
| Necessity-Gated | ✅ | 物理拆分推迟到真实痛点出现，不预建平台 |
| SYSTEM_VERSION 冻结策略 | ✅ | Core/Workspace 拆分属顶层结构变更，受冻结策略门控，Phase B 需满足触发条件 |
| ADR-0013 FIM | ✅ | 本机制依赖 FIM 的 manifest 携带 `core_version`，Aggregator 读版本答"谁没升级" |
| 先跑通再优化 | ✅ | Phase A 用手动通知验证发布范式，Phase B 再自动化 |

## 风险与约束

| 风险 | 缓解 |
|------|------|
| 早期过度工程（立即做 Core/Workspace 拆分） | 分阶段；当前仅 Case-01 真实运行，拆分本身需迁移，自相矛盾 |
| 用户数据被升级覆盖 | 铁律：Workspace 永不被 Core 升级覆盖；所有结构变更走 Migration |
| 版本语义混乱 | `core_version`（平台）与 `manifest_version`（FIM 协议）分离，互不干扰 |
| 强制升级引发抵触 | Upgrade Required 仅提示，用户自主决定 |

## 结论

PAIOS 的升级机制核心不是"推送"，而是"**声明 + 发现 + 自选**"。本次 v1.0.1 先用手动统一通知验证发布范式；当实例数增长到真正需要自动化分发时，Core/Workspace/Upgrade 三层 + Migration 自然接管。这条原则比任何 Dashboard 都更决定平台的持续演进能力。

---

**Related**: `ADR-0013-Federated-Instance-Manifest.md` | `ADR-0015-Federated-Aggregation-Viewing.md` | `ADR-0016-Multi-Instance-Architecture-Baseline.md` | `SYSTEM_VERSION.md` | `CHANGELOG.md` | `RELEASES/1.0.1.md` | `RELEASES/upgrade-notice-1.0.1.md`
