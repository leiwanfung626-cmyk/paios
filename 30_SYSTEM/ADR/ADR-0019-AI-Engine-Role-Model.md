---
title: "ADR-0019 — AI Engine Role Model (AI Fleet Governance)"
status: Accepted
evidence_level: Established
date: 2026-07-12
related:
  - ADR-0018-Multi-Instance-Role-Model.md
  - ADR-0017-Platform-Purity-Physical-Separation.md
  - ../Governance/Operating-Model.md
  - ../Principles.md
  - ../SOP/SOP-2026-07-10-0001-Release-Flow.md
  - ../Governance/AI-Operating-Model.md
  - ../Specifications/AI-Packets/README.md
---

# ADR-0019 — AI Engine Role Model（AI 引擎角色模型）

## Decision Traceability（决策可追溯性）

> 本 ADR 遵循 `30_SYSTEM/Governance/Decision-Traceability.md` 四字段规范。

- **Evidence**: 多 AI 引擎协作实践（WorkBuddy / Reasonix / ChatGPT Web / Codex / CloudCore 已在实际运行中自然形成分工）
- **Implements**: 扩展 ADR-0018（人的多实例治理）到 AI 引擎治理；落实 Principle #8（Tool Independence）
- **Frozen By**: —
- **Supersedes**: —

> 类型：**Proactive ADR**——基于多引擎协作实践提炼的治理原则，非由 CASE 触发。

---

## Summary（摘要）

PAIOS 长期同时使用多个 AI 引擎（WorkBuddy、Reasonix、ChatGPT Web、Codex、CloudCore），它们在实际工作中已自然形成分工。本 ADR 将这种分工正式化为**AI 引擎角色模型**，使引擎可替换但角色不变，落实 Tool Independence 原则（原则 #8）。

**核心原则**：
- **AI Engine 不拥有平台权限，只拥有角色权限**
- **Engine may change. Role remains.**
- **AI 负责专业意见，人（Case-01 Maintainer）负责最终决策**
- **结构化 AI 通信**：AI 与 AI 的协作应传递结构化成果（Proposal、Decision、Review、Context Packet），而不是完整聊天记录

---

## Context（背景）

PAIOS 日常使用多个 AI 引擎：

| 引擎 | 当前实际职责 |
|------|-------------|
| WorkBuddy | 具体任务执行：照片整理、文件操作、脚本运行、方案落地 |
| Reasonix | PAIOS 架构设计、编码、重构、工程实现、Git 操作 |
| ChatGPT Web | 架构讨论、方案评审、风险识别、治理建议 |
| Codex | 代码审查、安全规范、测试建议 |
| CloudCore | 独立第三方审计、整体合理性评估 |

它们在实际运行中已形成自然分工，但没有正式的职责定义和协作流程。这导致：
- 职责边界模糊（谁该做什么不清晰）
- 缺少审查环节（实现后没有系统性 Review）
- 工具锁定风险（一旦换引擎，职责需重新分配）

---

## Decision（决策）

### D0 — AI 引擎角色模型

| 角色 | 职责 | 当前引擎 | 可替换 |
|------|------|----------|--------|
| **Architect（架构顾问）** | 需求讨论、可行性分析、方案设计、Proposal 输出 | ChatGPT Web | Claude/Gemini 等 |
| **Developer（开发实现）** | 编码、重构、ADR 修改、脚本开发、文档更新 | Reasonix | Claude Code/Codex CLI 等 |
| **Executor（执行者）** | 确定任务的执行落地：文件操作、数据处理、方案产出 | WorkBuddy | 自动脚本/API 等 |
| **Code Reviewer（代码审查）** | 代码规范、安全审查、测试覆盖、重构建议 | Codex | 其他 Review 引擎 |
| **Auditor（独立审计）** | 第三方视角、整体合理性、可维护性风险 | CloudCore | 其他审计引擎 |

### D1 — 核心原则

**原则一：角色不绑定引擎**

```
Engine may change. Role remains.
```

Reasonix 可以替换为 Claude Code，但 Developer 角色不变。WorkBuddy 可以替换为自动脚本，但 Executor 角色不变。角色是平台定义，引擎是工具选择。

**原则二：AI 引擎不拥有平台权限**

不是"Reasonix 可以修改 PAIOS"，而是"Developer Role 拥有修改权限"。如果未来换成 Gemini，只要它承担 Developer 角色，就自动继承该角色的职责边界。

**原则三：AI 负责专业意见，人负责最终决策**

无论 ChatGPT、Reasonix、Codex 还是 CloudCore，都可以提出建议、实现功能、发现问题，但只有 Case-01 Maintainer 决定是否接受、是否进入 Core、何时发布版本。

### D2 — AI Fleet 协作流程

```
                    日常工作
                        │
                        ▼
                WorkBuddy（Executor）
      照片整理 | 活动方案 | 办公事务 | 资料整理
                        │
          ──────────────┼────────────────
                        │
             新想法出现
                        │
                        ▼
           ChatGPT（Architect）
       需求讨论 | 可行性分析 | 方案设计
                        │
        是否值得进入 PAIOS？
                        │
             ┌──────────┴──────────┐
             │                     │
            否                    是
             │                     │
       保留为笔记              形成 Proposal
                                   │
                                   ▼
                  Reasonix（Developer）
        编码 | 重构 | ADR 修改 | 脚本开发 | 文档
                                   │
                                   ▼
                  ChatGPT（Reviewer）
       架构一致性 | 过度设计检查 | 治理合规
                                   │
                      ┌─────────────┴─────────────┐
                      │                           │
                     需要修改                     通过
                      │                           │
                 返回 Reasonix              进入审查阶段
                                   │
                     ┌─────────────┴─────────────┐
                     ▼                           ▼
            Codex（Code Reviewer）     CloudCore（Auditor）
          代码规范 | 安全 | 测试        第三方视角 | 可维护性
                     └─────────────┬─────────────┘
                                   │
                                   ▼
                      Case-01 Maintainer
                   最终决定是否进入 Core
                                   │
                                   ▼
                           发布 Release
                                   │
                                   ▼
                    Case-02 Developer 验证
                    Case-03 Pilot User 使用反馈
```

### D3 — 各阶段输出物

| 阶段 | 参与角色 | 输出物 |
|------|----------|--------|
| 需求讨论 | ChatGPT (Architect) | Discussion Notes |
| 方案确认 | ChatGPT (Architect) | **Proposal**（1 页提案） |
| 开发实现 | Reasonix (Developer) | Code + ADR + 文档 |
| 架构 Review | ChatGPT (Reviewer) | Review Report |
| Code Review | Codex (Code Reviewer) | Code Review Comments |
| 独立审计 | CloudCore (Auditor) | Audit Report |
| 最终决策 | Case-01 Maintainer | Merge / Reject |

### D4 — Proposal 提案格式

每个进入开发阶段的需求，必须先形成 Proposal：

```
# Proposal: [标题]

## 背景
为什么需要这个功能/变更？

## 方案
有哪些方案？为什么选择这个？

## 影响
影响哪些模块？需要修改哪些 ADR？

## 风险
有什么风险？如何缓解？

## 完成标准
怎样算做完？
```

Proposal 由 ChatGPT（Architect 角色）输出，Reasonix（Developer 角色）按此实现，ChatGPT（Reviewer 角色）验证是否偏离。

---

## Consequences（后果）

**正面**

- AI 引擎可替换，不受工具锁定
- 职责边界清晰，减少协作冲突
- 每个环节都有 Review，降低质量风险
- 与 ADR-0018 人的角色模型正交叠加，形成完整治理

**负面 / 成本**

- 增加 Proposal 环节，节奏略慢（**这是设计意图**——防止"想到就做"）
- 需要维护各引擎的职责边界文档
- 新引擎加入时需要重新映射角色

---

## Validation（验证）

- [ ] 5 个角色（Architect / Developer / Executor / Reviewer / Auditor）职责定义明确
- [ ] 至少 1 次完整流程走通：Proposal → Dev → Review → Audit → Merge
- [ ] 引擎可替换验证：至少一个角色成功替换为不同引擎
- [ ] 无 AI 引擎直接写入 Core 平台文件的事故（必须经 Maintainer）

---

## Related（关联）

- `ADR-0018`（人的多实例角色模型）· `../Principles.md`（原则 #8：Tool Independence）· `../Governance/Operating-Model.md`（运营模型）· `../SOP/SOP-2026-07-10-0001-Release-Flow.md`（发布流程）
