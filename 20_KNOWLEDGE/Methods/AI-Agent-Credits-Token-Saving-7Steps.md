---
id: "KB-2026-07-06-0001"
schema_version: 2
title: "AI Agent 积分/Token 节省 7 步实战法"
type: "method"
lifecycle: "active"
created: "2026-07-06"
updated: "2026-07-06"
source: [REF-0007, douyin, web-search]
tags: [method, cost-optimization, workbuddy, token, agent-mode, context, automation]
keywords: [积分节省, 模式选择, 强弱模型, 上下文, 目录结构, 验收, 自动化检查]
summary: "从老顽童周老师视频提炼的可操作方法论：用对模式、强弱分工、控范围、定结构、管对话、查自动化、严验收。公式：积分=倍率×上下文×反复次数。"
abstract: >
  一套用于日常使用 AI Agent（WorkBuddy/Codex/Cursor 等）时控制积分与 Token 消耗的实战方法。
  源自 REF-0007（老顽童周老师抖音视频），经 WebSearch 独立来源交叉验证（high 置信度）。
  核心公式：积分消耗 = 模型倍率 × 上下文长度 × 任务反复次数。
  全部动作收敛为三件事：别用贵模型干便宜活、别让 AI 读无用上下文或背太久、别因前面没想清楚反复返工。
  该方法可直接映射到 PAIOS 的每日使用与系统治理（模式分层、上下文外置、自动化巡检、验收机制）。
related: ["REF-0007", "REF-0005", "SOP-2026-07-02-0001"]
verification:
  status: "verified"
  scope: ["方法步骤与独立教程一致", "模式消耗差异有多来源确认", "CodeGraph 插件真实存在"]
  last_verified: "2026-07-06"
  evidence_chain: ["REF-0007", "WebSearch Toutiao 系列", "GitHub codegraph-ai/CodeGraph"]
confidence: "high"
maintenance:
  owner: "Evan / PAIOS"
  review_cycle_days: 180
  last_review: "2026-07-06"
  next_review: "2026-12-31"
---

# AI Agent 积分/Token 节省 7 步实战法

> 提炼自 REF-0007 | 验证状态：high（多独立来源确认）

## 心法公式

```
积分消耗 = 模型倍率 × 上下文长度 × 任务反复次数
```

三步收敛：
1. **别用贵模型干便宜活** → 强弱模型分工
2. **别让 AI 读无用上下文 / 背太久** → 控制范围 + 管理对话
3. **别因前面没想清楚反复返工** → 选对模式 + 先规划

## 执行清单（7 步）

| # | 步骤 | 关键动作 | 反模式（禁止） |
|---|------|---------|---------------|
| 1 | **选对模式** | 纯咨询→Ask；理思路→Plan；真干活→Craft | 不管什么任务都开 Craft |
| 2 | **强弱分工** | 强模型定架构/计划，弱模型执行，Codex/人工复核 | 全用强模型或 Auto 一把梭 |
| 3 | **控制范围** | 文件放干净目录再指定给 AI；用 CodeGraph 减检索耗 | 把混乱文件夹（副本/截图/过期）直接丢给 AI |
| 4 | **定义目录** | 长期项目把目录结构写进规则/项目说明，每次强制读取 | 指望 AI 自己记住文件在哪 |
| 5 | **管理对话** | 阶段性让 AI 总结并关闭对话，下次续上 | 一个对话无限加任务、越聊越长 |
| 6 | **巡检自动化** | 自动化定期升级合并；半夜跑、早晨查 | 设完定时任务就一劳永逸 |
| 7 | **严格验收** | 四步法：偏离？编造？漏限制？超范围？ | AI 做完就当完成 |

## 四步验收法（Step 7 细化）

1. 是否**偏离**目标或场景？
2. 是否**编造**数据或信息？
3. 是否**漏掉**你给的重要限制？
4. 是否**超出范围**做事？

发现缺约束 → 立即加规则；但规则别写太复杂，否则 AI 变畏缩。

## 与 PAIOS 的映射

| 步骤 | PAIOS 落点 |
|------|-----------|
| 1 模式 | 原生 ask/plan/craft |
| 2 强弱 | 模型路由 |
| 3 范围 | L1-L4 目录分层 + 干净工作区 |
| 4 目录 | workspace memory 强制读取 + 规则文件 |
| 5 对话 | 上下文外置（memory），不依赖单对话 |
| 6 自动化 | automations 系统 + 定期复盘 |
| 7 验收 | SOP 质量检查（evidence_chain / 置信度 / ⚠️） |

## 使用建议

- 新手先固化 **Step 1（模式）** 和 **Step 5（对话管理）**——性价比最高，立竿见影。
- 模型价格与强弱会变，别死记数字；关注的是"让花出去的 Token 提高你的能力"。
