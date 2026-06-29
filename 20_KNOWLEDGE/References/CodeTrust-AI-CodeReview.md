---
ref_id: REF-0001
schema_version: 2
title: "CodeTrust — AI 代码缺陷检测工具"
type: tool
lifecycle: active
created: 2026-06-29
updated: 2026-06-29
source:
  - douyin
  - official-doc
tags:
  - ai
  - code-review
  - hallucination
  - open-source
  - typescript
keywords:
  - 幻影导入
  - 死逻辑
  - 过度防御
  - 确定性检测
  - AST
  - npm
summary: >
  使用确定性规则引擎检测 AI 生成代码中的幻觉。
abstract: >
  CodeTrust 是一个开源 AI Code Review 工具，
  通过将代码解析为 AST 并应用 29 条确定性规则，
  检测 AI 生成代码中的幻影导入、死逻辑分支和过度防御等问题，
  覆盖安全、逻辑、结构、覆盖、样式五个维度，
  最终输出 0-100 可信度评分。
  当前支持 TypeScript/JavaScript。
related: []
verification:
  status: partial
  scope:
    - installation
    - cli
    - ci-cd
  last_verified: 2026-06-29
  evidence_chain:
    - douyin-url
    - downloaded-video
    - whisper-transcript
    - manual-summary
    - official-npm-page (libraries.io)
    - nodejs-not-installed (无法本地运行)
confidence: medium
maintenance:
  owner: wanfung
  review_cycle_days: 180
  last_review: 2026-06-29
  next_review: 2026-12-26
---

# CodeTrust — AI 代码缺陷检测工具

> **信息来源**: 抖音视频 + npm 官方页面 (v0.3.2)
> **视频链接**: https://v.douyin.com/PQo7QHCKLzs/
> **npm 包名**: `@gulu9527/code-trust` (v0.3.2, 2026-04-04)
> **GitHub**: https://github.com/GuLu9527/CodeTrust
> **仓库地址**: `npm install @gulu9527/code-trust@0.3.2`
> **转写文件**: `00_CAPTURE/Downloads/CodeTrust_douyin_transcription_2026-06-29.txt`
> **验证状态**: ⚠️ 以下内容来自视频 + 官方 npm 页面，环境缺少 Node.js 无法本地运行
> **标签**: #AI代码审查 #开源工具 #CodeTrust #确定性检测 #TypeScript

---

## 为什么 AI 代码会产生幻觉？

大语言模型根据统计概率生成代码，它会输出"看起来合理"的 token 序列，但**不会真正验证**：

- 导入的模块是否存在
- 条件分支是否可达
- 防御检查是否必要

因此可能产生**语法正确但语义错误**的代码。CodeTrust 的目标就是发现这些"看着合理，实际跑不通"的模式。

---

## 检测流程

```
AI 生成代码
      │
      ▼
  Parser（AST 解析）
      │
      ▼
  29 条确定性规则引擎
      │
      ▼
  5 个维度加权评分
      │
      ▼
  0-100 Trust Score
      │
      ▼
  人工决定是否合并
```

---

## 三类幻觉检测

| 幻觉类型 | 检测方式 | 原理 |
|---------|---------|------|
| **幻影导入** | 模块解析验证 | AI 编造不存在的模块路径 → CodeTrust 检查该模块在项目中是否真实存在 |
| **死逻辑分支** | 条件恒定性分析 | 条件永远为真（如 `if (2 > 1)`）或重复条件导致第二个分支永远不可达 |
| **过度防御** | 嵌套防御检查 | 连续的 `if (x != null)` 嵌套，代码不报错但变成一团"健壶" |

---

## 29 条规则 × 5 维度

每条规则命中后按权重扣分，最终得分是**算法计算**结果，而非 AI 主观判断。基于惩罚递减模型，同类问题多次命中时惩罚递减（×0.7），避免单一规则类别主导评分。

| 维度 | 权重 | 检测内容 | 规则示例 |
|------|------|---------|---------|
| **安全** | 30% | 硬编码密钥、注入风险 | `security/hardcoded-secret`, `security/eval-usage`, `security/sql-injection` |
| **逻辑** | 25% | 幻觉检测：死分支、幻影导入 | `logic/phantom-import`, `logic/missing-await`, `logic/dead-branch`, `logic/unnecessary-try-catch` |
| **结构** | 20% | 复杂度、函数长度、嵌套深度 | 圈复杂度、认知复杂度、参数数量 |
| **覆盖** | 15% | 测试文件覆盖 | 检测缺失对应测试文件 |
| **样式** | 10% | 命名一致性 | camelCase / snake_case 混用检测 |

> 规则共 **29 条**（23 条逻辑 + 5 条安全），每项有唯一 Rule ID，例如 `logic/phantom-import`。

### 评分模型

基于惩罚递减模型：

| 严重级别 | 基础扣分 | 重复衰减因子 |
|---------|---------|------------|
| high | 15 | ×0.7/次 |
| medium | 8 | ×0.7/次 |
| low | 3 | ×0.7/次 |
| info | 0 | — |

例如：3 个 high 问题扣分 = 15 + 10.5 + 7.35 = **32.85**（而非 45）

每个问题通过 SHA256 内容哈希指纹标识（规则 ID + 文件路径 + 代码片段），确保结果在不同行偏移下保持稳定。

### 评分区间

- **90+** — 高信任，放心合并
- **70-90** — 建议人工看一眼
- **50-70** — 需要修改
- **<50** — 不可信，不应合并

> 注意：规则引擎可能漏检（False Negative）或误报（False Positive），但不会像 LLM 一样"幻想"一个不存在的问题。规则需要持续维护以降低漏报率。

---

## 集成方式（官方文档，环境缺少 Node.js 无法本地验证）

**npm 包名**: `@gulu9527/code-trust`（支持 `codetrust` 和 `code-trust` 两个命令）

```bash
npm install -g @gulu9527/code-trust
```

| 命令 | 说明 | 适用场景 |
|------|------|---------|
| `codetrust init` | 生成 `.codetrust.yml` 配置 | 首次使用 |
| `codetrust scan --staged` | 扫描 git 暂存文件 | 个人开发 |
| `codetrust scan --diff origin/main` | 扫描与主分支差异 | CI/CD |
| `codetrust scan --staged --min-score 70` | 低于 70 分返回退出码 1 | CI/CD 门禁 |
| `codetrust fix src/ --apply` | 自动修复安全问题 | 一键清理 |
| `codetrust hook install` | 安装 pre-commit hook | 团队协作 |
| `codetrust rules list` | 列出全部 29 条规则 | 规则了解 |

### CI/CD (GitHub Action)

```yaml
- uses: GuLu9527/CodeTrust@main
  with:
    min-score: 70
```

### 自动修复

```bash
# 预览修复（dry-run，默认）
codetrust fix src/

# 应用修复
codetrust fix src/ --apply

# 仅修复特定规则
codetrust fix src/ --apply --rule logic/type-coercion
```

可自动修复的规则：`no-debugger`、`unused-import`、`type-coercion`、`unused-variables`

### 语言支持

- ✅ **TypeScript** 5.x — 基于 `@typescript-eslint/typescript-estree` AST 解析
- ✅ **JavaScript** — 同一解析器
- ❌ **Python** — 不支持（AST 解析器为 TS 专属）
- ❌ **Go / Java / Rust** — 不支持

> 官方信息确认：CodeTrust 当前**仅支持 TypeScript/JavaScript**。Python 等语言不在当前路线图中。

---

## 未来路线图（npm 官方信息）

1. **MCP Server** — 官方路线图中提及
2. **多语言支持** — ⚠️ 官方信息**未确认** Python/Go/Java/Rust 支持。视频中提到的 TreeSitter 方案不在当前官方文档中
3. **VS Code 扩展** — 未在官方页面提及
4. **团队仪表盘** — 未在官方页面提及

> 截至 v0.3.2 (2026-04-04)，CodeTrust 仅支持 TypeScript 和 JavaScript。视频中提到的多语言支持可能为远期规划，不应视为已验证信息。

---

## 核心原则

- ✅ **完全本地运行** — 代码不上传任何服务器
- ✅ **确定性** — 同一段代码永远得同样的分
- ❌ **非 AI 审查** — 不使用另一个 AI 来审核 AI 代码
- ⚠️ **仍需人工判断** — 规则无法覆盖所有场景，低分代码应人工审查

---

## 部署建议（2026-06-29 决策）

**当前定位**: 按需调用的专业工具（On-Demand Tool），不是系统常驻组件。

**不部署为基础设施的理由**：
- PAIOS 当前核心是知识管理，不是代码质量管控
- 无持续 TypeScript/JavaScript 开发任务
- 过早集成增加维护成本，收益有限
- 遵循 Need Driven Promotion 原则

**环境依赖**（已验证）：
- ❌ **Node.js 未安装** — CodeTrust 依赖 Node.js 20+ 运行，当前系统无 Node.js 运行时
- ❌ **仅支持 TypeScript/JavaScript** — AST 解析器为 `@typescript-eslint/typescript-estree`，不支持 Python 或其他语言
- 两项条件均不满足，CodeTrust 无法在当前环境运行

**触发部署的条件**（满足任一即可）：
1. 安装 Node.js 20+ 运行时
2. 开始大量开发 TypeScript/JavaScript（如 PAIOS Web UI）
3. 建立 CI/CD 流水线，需要 PR 自动检查

**当前状态**：保持为知识参考（REF-0001），不注册到 Automation Registry，不安装。
