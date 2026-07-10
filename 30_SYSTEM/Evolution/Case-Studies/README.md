# Case Studies — Architecture Evidence（架构证据）

> 位置：`30_SYSTEM/Evolution/Case-Studies/`
> 定位：**真实演化证据**，不是会议纪要，不是聊天记录。

## 为什么单独建目录

PAIOS 的演进方式已经转变（详见 CASE-001）：

- 以前：先设计，再等待未来验证。
- 现在：**真实运行 → 收集证据 → 提炼规律 → 升级架构**。

聊天记录是思考过程，散落其中会丢失。每一次"真实运行暴露了足够证据、足以推动架构升级"的事件，都应固化成一个 **Case**，沉淀为可复用的架构证据。

## 与 ADR 的关系

```
真实运行  ──产生证据──►  Case Study（本目录）
                             │  提供 Validated 级证据
                             ▼
                        ADR（决策层）
                             │  据此冻结/升级架构
                             ▼
                      Phase 执行（Evolution/ 下的方案）
```

- **Case = 证据**（发生了什么、观察到什么、验证了什么）
- **ADR = 决策**（基于证据，我们决定怎么做）
- 一个 ADR 可由多个 Case 支撑；一个 Case 可触发多个 ADR。

## 何时创建

✅ 满足以下任一条即可立 Case：
- 多实例真实运行首次暴露某类架构痛点（如冲突、泄漏、撞车）
- 某平台原则被真实场景**验证**或**证伪**
- 一个 Phase 完成并产出可复用的演化规律

❌ 不要为以下建 Case：
- 纯讨论 / 假设 / 未发生的设计
- 单实例的日常使用（那是 Usage，不是 Evolution）
- 会议纪要（那是过程，不是证据）

## 命名

`CASE-NNN-kebab-case-title.md`，编号三位递增（CASE-001, CASE-002, ...）。

## 固定结构（写 Case 时照抄）

```
# CASE-NNN — <标题>

## 元数据
- 时间：YYYY-MM-DD
- 触发版本：PAIOS vX.Y.Z
- 证据等级：Validated / Emerging / Proposed
- 关联 ADR：（如有）

## 背景（Context）
为什么这件事值得记——当时处于什么阶段。

## 观察（Observed）
真实运行得到的客观数据（带数字，可验证）。

## 新发现（Findings）
第一次真实出现的问题 / 规律。

## 结论（Validated）
此次运行证明了什么（或证伪了什么）。

## 架构升级依据
本 Case 支撑了哪条 ADR / 哪个 Phase。

## 决策（Decision）
建议形成的正式决策（通常指向某 ADR）。

## 后续验证指标（Validation Metrics）
升级完成后继续观察什么，证明修复有效。

## 最大价值（Significance）
这次对 PAIOS 演进方法论本身的意义。
```

## 范例

- `CASE-001-Multi-Instance-First-Convergence.md` — 第一次真实多实例并流，触发 ADR-0017（平台纯度与物理隔离）
- `CASE-002-Photo-System-Evolution.md` —（预留，待真实证据）
