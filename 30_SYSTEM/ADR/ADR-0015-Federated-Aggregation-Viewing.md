---
adr: "0015"
status: "Proposed"
date: "2026-07-10"
evidence_level: "Emerging"
---

# ADR-0015: 联邦式聚合与查看（Federated Aggregation & Viewing）— 三级架构 + 权限边界

## 背景

ADR-0013 定义了 **FIM（联邦式实例清单协议）**——每个实例声明自己的身份、场景与状态。
ADR-0014 定义了 **Upgrade Mechanism**——版本如何发布、实例如何自我声明 `core_version`。

本 ADR 补上最后一块：**多实例状态如何汇总、谁可查看、在哪里查看**。它是整个 FIM 生态的收口层，也是"产品真实使用情况可观测"的唯一通道。

## 核心原则（最重要的一条）

> **PAIOS 不收集用户数据，只收集用户主动共享的实例状态（Instance State）。**

这一条决定后面所有设计都简单：离开用户电脑的**只有一个文件** `manifest.yaml`。
Knowledge / Photo / Daily Log / 项目内容**全部留本地**，永不离开。

---

## 三级架构

```
┌─────────────────────────────┐
│ User A（工作）              │
│ Workspace                   │
│ manifest.yaml               │
└────────────┬────────────────┘
             │（用户主动共享 manifest）
┌────────────▼────────────────┐
│ User B（个人）              │
│ Workspace                   │
│ manifest.yaml               │
└────────────┬────────────────┘
             │
┌────────────▼────────────────┐
│ User C（考研）              │
│ Workspace                   │
│ manifest.yaml               │
└────────────┬────────────────┘
             │
             │（仅 manifest.yaml 离开本机）
             ▼
┌─────────────────────────────┐
│ Fleet（聚合层）             │
│ aggregate.py                │
│ Dashboard                   │
│ Weekly Report               │
└─────────────────────────────┘
```

**唯一离开用户电脑的文件：`manifest.yaml`。**
没有：Knowledge、Photo、Daily Log、项目内容。全部留本地。

---

## 职责边界与 Fleet 归属

基于"PAIOS 不收集用户数据，只收集主动共享的实例状态"，各组件归属与同步范围如下：

| 组件 | 属于谁 | 是否同步给用户 |
|------|--------|----------------|
| **Core** | 平台（Developer 维护） | ✅ 是（`git pull`） |
| **Workspace** | 用户 | ❌ 否（各自维护，不入库） |
| **PAIOS-Usage（Manifest）** | 用户生成 | ✅ 仅 Manifest 回传给 Developer |
| **Release（Notes + Notice）** | 平台 | ✅ 所有用户同步（随 Core 仓库分发） |
| **Fleet（manifests / reports / aggregate.py）** | Developer 运营 | ❌ 不同步给用户 |

**Fleet 物理位置**：`F:\Fleet`，**独立于 `F:\PAIOS` Core 仓库**。用户实例没有这个目录，也不会 `pull` 它。这让"用户 `git pull` 升级"不会把 `fleet.md` 反向同步回用户——Fleet 是产品运营资产，不是用户实例的一部分。

**Manifest 单向流（铁律）**：User → Developer。开发者拉取 manifest 后生成 Fleet 周报，**绝不反向推回用户**。用户关心的是自己的 Self Dashboard，不是 Fleet Dashboard。

---

## 收集方式（不是上传数据库）

每周（或每天）在用户本机执行：

```bash
python 40_AUTOMATION/05_SCRIPTS/collect_manifest.py
```

生成：

```
PAIOS-Usage/
    manifest.yaml
```

目标 manifest（manifest_version: 1）示例：

```yaml
manifest_version: 1

instance:
  id: case-01          # 语义 ID（取自 profile.yaml）

profile:
  primary: work        # work / personal / study

usage:
  active_days: 19      # 近 N 天活跃天数

assets:
  references: 22       # 知识资产计数（示例）

features:
  photo: false         # 是否启用照片能力
  automation: true     # 是否启用自动化
```

> `usage` / `assets` / `features` 为 v1 富 schema；当前 `collect_manifest.py` 仅输出基础字段，扩展见 Phase B。

---

## 汇总方式（三种模式）

### 模式一：Git（推荐）

**传输通道**（用户 → 开发者，单向）：
- 用户升级后，`collect_manifest.py` 生成 `PAIOS-Usage/manifests/case-XX.yaml`（按 `instance.id` 命名，避免共享仓库同名覆盖）
- 用户 `git commit` 仅 `PAIOS-Usage/` → `git push` 到 Core 仓库
- 开发者 `git pull` Core 仓库 → 取得三个 manifest → 复制到 **`F:\Fleet\manifests\`**

**聚合位置**（开发者私有，用户不 pull）：
```
F:\Fleet\
    manifests/
        case-01.yaml
        case-02.yaml
        case-03.yaml
    reports/
        fleet-2026-W28.md
```
- Aggregator：读取 `F:\Fleet\manifests/` 即可
- **无需服务器。Fleet 不在 Core 仓库内，用户永远不会拉到它。**

### 模式二：共享网盘（Quark 等）
```
Fleet/
    manifests/
```
- 每人覆盖自己的 `case-XX.yaml`
- Aggregator：扫描整个目录
- 适合不熟 git 的用户。

### 模式三：HTTP API（远期）
- 目前完全没必要。
- 触发条件：实例规模增长，中心化服务带来明显收益时再评估（Phase C）。

---

## 查看者模型

| 角色 | 能查看 | 不能查看 |
|------|--------|----------|
| **用户本人** | 自己的 Self Dashboard、自己的 Manifest | 其他用户的数据 |
| **其他用户** | 默认什么都看不到（除非主动共享） | 对方的使用情况、知识内容 |
| **开发者（Evan）** | 三个实例的 Manifest、Fleet Dashboard、聚合统计 | 用户知识正文、照片、笔记、项目内容 |
| **Aggregator** | 只读取 Manifest 协议 | 不读取 Workspace 中任何文件 |

---

## 在哪里查看（不做网页，生成 HTML）

**不建 Web 服务。直接生成 HTML 文件，浏览器打开即 Dashboard。**

```
F:\Fleet\
    dashboard/
        index.html
```

以后可升级为动态服务，但 v1 阶段静态 HTML 足够。

### Self Dashboard（用户看自己）
```
PAIOS Usage
────────────────────
本周
  活跃：6 天
  Knowledge：+12
  Automation：42 次
```

### Fleet Dashboard（开发者看聚合）
```
Fleet
  实例：3
  Work：1  Study：1  Personal：1
  平均活跃：5.7 天
  Automation：67%
  Photo：33%
```
> 无任何正文，用户间互不可见。

### Developer Dashboard / Fleet Health（最重要）
```
Fleet Health
  Manifest：✔ 3/3
  Version：1.0.1  3/3
  Upgrade：0
  Schema：v1  3/3
  Errors：0
```
> 若某实例 Manifest 仍是旧版 → 开发者立刻知道"需要提醒升级"。直接回答 ADR-0014 原则一的"谁没升级"。

---

## Dashboard 形态（首页 + 钻取）

**首页**
```
PAIOS Fleet
────────────────────
实例          3
在线          3
────────────────────
Work      ████
Personal  ████
Study     ████
────────────────────
Automation  67%
Knowledge   100%
Photo       33%
────────────────────
Version  1.0.1  3/3
────────────────────
```

**点击 Case-01 钻取**
```
Case-01
  Profile    Work
  Active Days  21
  Knowledge    35
  Automation   On
  Version      1.0.1
```
> 没有知识内容。只有状态。

---

## 实施阶段（Need-Driven，不提前建）

- **Phase A（本次）**：固化原则为 ADR-0015；定义 manifest v1 富 schema、三种汇总模式、三级查看、权限边界表。
- **Phase B（触发：第二 / 第三真实实例 manifest 出现）**：
  - 实现 `aggregate.py`：读取 `Fleet/manifests/*.yaml` → 聚合
  - 生成 Self / Fleet / Developer 三套 HTML Dashboard
  - `collect_manifest.py` 扩展为输出 `usage` / `assets` / `features`
  - 选定汇总模式（默认 Git，备选 Quark）
- **Phase C（远期）**：HTTP API 模式（若实例规模需要中心服务）。

> 当前仅 Case-01 一个实例真实运行，Phase B 的实际代码**暂不产生**——单实例下 Aggregator 只能聚合出"1 个"，无验证价值。这与 ADR-0013/0014 的推迟策略一致。

---

## 与现有架构的兼容性

| 原则 | 兼容 | 说明 |
|------|------|------|
| ADR-0013 FIM | ✅ | 本 ADR 消费 FIM 的 manifest，定义其下游使用 |
| ADR-0014 Upgrade | ✅ | Developer Dashboard 的 `Version 3/3 / Upgrade 0` 直接回答"谁没升级" |
| Necessity-Gated | ✅ | 实现推迟到真实多实例数据出现，不预建平台 |
| 用户拥有 Workspace | ✅ | 离开本机的只有 manifest；权限边界表明确 Aggregator 不读 Workspace |
| 先跑通再优化 | ✅ | Phase A 文档化原则，Phase B 再落地代码 |

---

## 风险与约束

| 风险 | 缓解 |
|------|------|
| 过度收集（误把 Knowledge/Photo 推上 Fleet） | 铁律：Aggregator 只解析 manifest 协议字段；脚本不改即无法读到内容 |
| 用户误 `git push` 整个 Workspace 或 Fleet 回传用户 | ① 用户 push 范围限定为 `PAIOS-Usage/`（manifest + profile），Workspace 不入库；② Fleet 物理位于 `F:\Fleet`（独立目录），不在用户 pull 范围内，杜绝回推 |
| Dashboard 范围蔓延（想看正文） | 权限边界表写死：Developer 也看不到知识正文 |
| 过早建中心服务 | 模式三（HTTP API）明确推迟到 Phase C |
| 单实例下建 Aggregator 无意义 | Phase B 触发条件绑定"第二实例出现" |

---

## 结论

PAIOS 的可观测性不是"监控系统"，而是"**用户主动共享的状态快照**"。三级架构（User Workspace → Fleet 聚合 → 分级 Dashboard）+ 权限边界（用户只看自己、开发者只看状态、Aggregator 只读协议）共同保证了：**既能了解产品真实使用情况，又不打破用户对本地数据的控制权。** 这条原则与 PAIOS 的设计理念完全一致——用户拥有自己的 Workspace，开发者只观察实例状态，不拥有用户内容。

---

**Related**: `ADR-0013-Federated-Instance-Manifest.md` | `ADR-0014-Upgrade-Mechanism.md` | `ADR-0016-Multi-Instance-Architecture-Baseline.md` | `40_AUTOMATION/05_SCRIPTS/collect_manifest.py` | `PAIOS-Usage/manifest.yaml` | `RELEASES/1.0.1.md` | `30_SYSTEM/Evolution/Multi-Instance-Roadmap.md`
