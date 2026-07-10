---
ref_id: "REF-0009"
schema_version: 2
title: "OpenAI Codex 最佳实践 — 官方教程知识归档"
type: "reference"
lifecycle: "active"
created: "2026-07-06"
updated: "2026-07-08"
source: [douyin, openai-official-docs, web-search]
tags: [codex, openai, agent, agents-md, mcp, skills, automations, best-practices, prompt]
keywords: [Codex, AGENTS.md, config.toml, MCP, Skills, Automations, 推理等级, 多代理, worktree, 安全红线]
summary: "基于 OpenAI 官方 Codex Best Practices 整理的实战指南：把 Codex 当持续配置的队友，渐进路径 Prompt→AGENTS.md→config→MCP→Skills→Automations，含八大常见错误与安全红线。"
abstract: >
  源自抖音视频「如何把你的 Codex 用到极致」+ OpenAI 官方文档整理的 Codex 系统化使用指南。核心理念是将 Codex 视为需要
  持续配置和改进的队友，而非一次性助手。六大主题：结构化 Prompt（四要素+推理等级）、AGENTS.md 持久化指导（多级体系）、
  系统配置（config.toml + Sandbox/Approval 先紧后松）、测试与代码审查闭环、MCP 外部集成、Skills 封装、Automations 调度。
  另含多代理工作流（Git Worktrees 隔离、批量分发）、八大常见错误对照表、安装配置速查，以及信任分级与安全红线
  （绝不粘贴密钥/连接串/个人数据、强制 Code Review 门控）。
---

# OpenAI Codex 用到极致 — 官方最佳实践知识归档

> **来源**：抖音视频「OpenAI 官方教程｜如何把你的 Codex 用到极致」
> **链接**：https://v.douyin.com/7OPGXBs8ryk/
> **标签**：#每天学点ai #Codex #OpenAI #Agent #人工智能
> **归档日期**：2026-07-06
> **补充资料**：OpenAI 官方 Codex Best Practices 文档 + 2026 完整教程 + 知乎深度解析

---

## 一、核心理念

> **不要把 Codex 当成一次性的助手，而应当视其为一个需要持续配置和改进的队友。**

核心路径（渐进式六步）：

```
结构化 Prompt → AGENTS.md 持久化 → config.toml 标准化 → MCP 外部集成 → Skills 封装 → Automations 调度
```

---

## 二、六大主题详解

### 1. Prompt 编写与上下文管理

#### 结构化 Prompt 四要素

| 要素 | 说明 |
|------|------|
| **Goal（目标）** | 你想要修改或构建什么？ |
| **Context（上下文）** | 哪些文件、目录、文档、示例或错误相关？可用 `@` 引用文件 |
| **Constraints（约束）** | 需遵守的标准、架构要求、安全规则或编码规范 |
| **Done when（完成条件）** | 任务完成时应满足什么条件？如测试通过、bug 不再复现 |

#### Reasoning Level 选择

| 推理等级 | 适用场景 |
|----------|----------|
| Low | 边界清晰的快速任务 |
| Medium / High | 较复杂的代码变更或调试 |
| Extra High | 长链路、高推理需求的 agent 任务 |

#### 复杂任务先规划再执行

三种规划方式：
1. **Plan mode**：`/plan` 或 `Shift+Tab` 切换，Codex 先收集上下文、提出澄清问题，再制定方案
2. **让 Codex 采访你**：模糊想法 → 让 Codex 主动提问、挑战假设 → 转化为具体方案
3. **PLANS.md 模板**：适用于长期运行或多步骤工作

> ⚠️ **常见错误**：在多步骤复杂任务中跳过规划是最常见的错误，直接编码往往导致方向偏差和大量返工。

#### 语音输入加速

Codex App 支持语音听写（speech dictation），口述任务需求替代手动打字，对大量上下文场景尤其高效。

---

### 2. AGENTS.md：持久化指导

#### 什么是 AGENTS.md

给 agent 看的 README，自动加载到上下文中，是编码团队标准化 Codex 行为的最佳位置。

应覆盖内容：
- 仓库布局和重要目录
- 项目运行方式
- Build、test、lint 命令
- 工程规范和 PR 期望
- 约束和"不要做"规则
- "完成"的定义及验证方式

#### 多级 AGENTS.md 体系（就近优先）

| 层级 | 路径 | 用途 |
|------|------|------|
| 全局级 | `~/.codex/AGENTS.md` | 个人默认偏好 |
| 仓库级 | 项目根目录 `AGENTS.md` | 团队共享标准 |
| 子目录级 | 特定目录 `AGENTS.md` | 局部规则 |

#### 编写原则
- **保持简洁**：短而准确比冗长模糊有用得多
- **按需添加**：先写基础内容，只在发现重复性错误后才添加新规则
- **拆分引用**：文件过大时保持主文件精简，引用任务级 markdown（如 `code_review.md`、`architecture.md`）
- **回顾驱动**：Codex 犯同样错误两次时，让它做 retrospective 并更新 AGENTS.md

> ⚠️ **常见错误**：把本应写在 AGENTS.md 中的持久性规则反复写在 prompt 里，是最常见的反模式。

CLI 中用 `/init` 命令快速生成 starter AGENTS.md。

---

### 3. 系统配置

#### config.toml 配置体系

| 层级 | 路径 | 用途 |
|------|------|------|
| 个人默认 | `~/.codex/config.toml` | 个人级行为配置 |
| 仓库特定 | `.codex/config.toml` | 项目级行为配置 |
| 命令行覆盖 | CLI 参数 | 一次性场景 |

可配置项：model 选择、reasoning effort、sandbox mode、approval policy、profiles、MCP setup 等。

CLI、IDE 和 App **共享同一套配置层级**，任一端修改都影响其他端。

#### Sandbox 与 Approval 机制

| 控制旋钮 | 作用 |
|----------|------|
| **Approval mode** | 决定 Codex 何时需要请求许可才能执行命令 |
| **Sandbox mode** | 决定 Codex 能否在目录中读写，以及可以访问哪些文件 |

> 新手建议：**先紧后松**。保持默认严格权限，只在了解工作流、确认信任特定仓库后才逐步放宽。

---

### 4. 测试与代码审查

#### 闭环验证流程

```
编写/更新测试 → 运行测试套件 → 检查 lint/格式化/类型 → 确认行为一致 → 检查 diff 中的 bug/回归
```

> 关键前提：让 Codex 知道什么是"好"——来自 prompt 或 AGENTS.md 中的测试命令、lint 配置、代码风格期望。

#### /review 命令

支持多种审查模式：
- 对比 base branch 进行 PR 风格审查
- 审查未提交的变更
- 审查特定 commit
- 使用自定义审查指令

如团队有 `code_review.md` 并在 AGENTS.md 中引用，Codex 审查时也会遵循。

**GitHub Cloud 集成**：可设置 Codex 自动审查 PR。OpenAI 内部 Codex 审查了 100% 的 PR。可启用自动审查，也可通过 `@Codex` 触发。

---

### 5. MCP：外部工具集成

#### 什么是 MCP

Model Context Protocol，开放标准，将 Codex 连接到外部工具和系统。当所需上下文不在代码仓库中时，MCP 就是解决方案。

#### 何时使用 MCP
- 所需上下文在仓库之外（如 issue tracker、monitoring 系统）
- 数据频繁变化（如实时指标、日志）
- 希望 Codex 使用工具而非依赖粘贴的指令
- 需要跨用户、跨项目的可复用集成

#### 两种 MCP server 类型
- **STDIO**：标准输入/输出通信
- **Streamable HTTP**：支持 OAuth 认证

配置入口：
- Codex App：Settings → MCP servers
- CLI：`codex mcp add` 命令

> ⚠️ **不要一次性接入所有工具**。从 1-2 个明确能消除手动重复操作的工具开始，逐步扩展。

---

### 6. Skills：技能封装

#### 什么是 Skill

当工作流变得可重复，就不应继续依赖长 prompt。Skill 将指令（`SKILL.md`）、上下文和支持逻辑封装为可跨 CLI、IDE 和 App 一致调用的单元。

#### Skill 设计原则
- 每个 skill 聚焦于一个任务
- 从 2-3 个具体用例出发
- 定义清晰的输入和输出
- 描述要说明 skill 做什么、何时使用
- 包含用户实际会说的触发短语

#### 适用场景
- 日志分类（Log triage）
- Release notes 起草
- 按 checklist 进行 PR 审查
- 迁移规划（Migration planning）
- 遥测或事件摘要
- 标准调试流程

#### 存储位置
- **个人 skills**：`$HOME/.agents/skills/`
- **团队共享 skills**：仓库内 `.agents/skills/`

> 经验法则：如果你发现自己反复使用同一个 prompt，或反复纠正同一个工作流，它就应该成为一个 skill。

可用内置 `$skill-creator` skill 快速生成第一版。建议本地迭代稳定后再打包为 plugin 分享。

---

### 7. Automations：自动化调度

#### Skills vs Automations

> **Skills 定义方法，Automations 定义调度。**

工作流仍需大量人工干预时，先封装为 skill。只有当它足够可预测时，automation 才能发挥乘数效应。

#### 适用场景
- 汇总近期 commits
- 扫描潜在 bug
- 起草 release notes
- 检查 CI 失败
- 生成 standup 摘要
- 按计划运行重复性分析

> ⚠️ **先手动验证，再自动化**。过早自动化不可靠的任务只会放大错误。

Automation 还可用于**反思和维护**：审查近期 session、汇总重复性摩擦、改进 prompt 和工作流设置。

---

## 三、Session 管理与常用命令

### Session 的本质

不只是聊天记录，而是随时间累积上下文、决策和操作的**工作线程**。

### 常用 Slash 命令

| 命令 | 功能 |
|------|------|
| `/plan` | 切换到规划模式 |
| `/review` | 代码审查 |
| `/init` | 生成 starter AGENTS.md |
| `/experimental` | 切换实验性功能 |
| `/resume` | 恢复保存的会话 |
| `/fork` | 创建新线程并保留原始记录 |
| `/compact` | 压缩/总结较早的上下文 |
| `/agent` | 切换并行 agent 线程 |
| `/theme` | 选择语法高亮主题 |
| `/apps` | 在 Codex 中使用 ChatGPT apps |
| `/status` | 查看当前 session 状态 |

> **一任务一线程**：保持一个线程对应一个连贯的工作单元。只有当工作真正产生分支时才用 `/fork`。用单一线程管理整个项目会导致上下文膨胀，降低输出质量。

**Subagent 工作流**：将有限工作从主线程卸载，主 agent 聚焦核心问题，subagent 处理探索、测试或分类等辅助任务。

---

## 四、多代理工作流（2026 核心升级）

### Git Worktrees 隔离机制

创建新代理时 Codex 自动：
1. Clone Repository
2. 创建独立 Git Worktree（隔离副本）
3. 代理只能读写这个隔离副本
4. 任务完成后生成 Diff 供审查

→ 代理 A 修改 `auth.ts` 不影响代理 B 同时修改 `auth.ts`，两个版本并行存在，最后由你决定采用哪个。

### 批量任务分发

`spawn_agents_on_csv` 功能：从 CSV 文件批量创建子代理任务，自动为每行创建子代理、显示进度与预估完成时间。

### Codex Security

从 OpenAI 内部 Aardvark 计划演进，2026年3月上线首30天：
- 扫描超过 **120 万条 commits**
- 发现 **792 个严重漏洞**
- 识别 **10,561 个高风险漏洞**

---

## 五、八大常见错误（官方总结）

| # | 错误 | 正确做法 |
|---|------|----------|
| 1 | 在 prompt 中堆积持久性规则 | 迁移到 AGENTS.md 或 skill |
| 2 | 没告诉 agent 如何运行 build 和 test | 在 AGENTS.md 中写明命令 |
| 3 | 多步骤复杂任务跳过规划 | 先 `/plan` 再执行 |
| 4 | 不了解工作流就给完全系统权限 | 先紧后松，逐步放宽 |
| 5 | 同一批文件运行多个活跃线程，不用 git worktree | 用 worktree 隔离 |
| 6 | 工作流手动运行尚不可靠就转 automation | 先手动验证再自动化 |
| 7 | 把 Codex 当需要看管的工具 | 当作并行工作的队友 |
| 8 | 一个线程管理整个项目 | 一任务一线程 |

---

## 六、安装与配置速查

### 安装方式

```bash
# npm 安装（全平台）
npm install -g @openai/codex

# macOS Homebrew
brew install --cask codex

# 验证
codex --version
```

### API 密钥设置

```bash
export OPENAI_API_KEY="sk-proj-..."
```

### 配置中文回复（持久化）

```bash
mkdir -p ~/.codex && printf 'Always respond in Chinese-simplified\n' > ~/.codex/AGENTS.md
```

### Windows 用户

> ⚠️ Windows 原生环境处于实验阶段，**强烈建议通过 WSL 运行**，避免字符编码和路径依赖问题。

---

## 七、信任校准与安全红线

### 信任分级

| 信任度 | 场景 | 做法 |
|--------|------|------|
| **高信任** | 样板代码、单元测试、文档、不涉及业务逻辑的重构 | 简单审查即可 |
| **低信任** | 核心算法、身份验证、数据库查询、金融交易、>10行复杂函数 | 必须深度审查，视 AI 为初级工程师 |

### 绝对禁止

1. ❌ 绝不粘贴生产环境 API 密钥给 AI 代理
2. ❌ 绝不粘贴数据库连接字符串或密码
3. ❌ 绝不粘贴用户个人数据作为测试数据
4. ❌ 绝不跳过 AI 生成代码的 Code Review

### 强制安全门控

```
AI 修改 → 开发环境运行 → 单元测试（必须通过）
       → SAST 扫描（Snyk / Semgrep）
       → 依赖包授权检查
       → 人工 Code Review
       → 合并至主分支
```

---

## 八、参考链接

- [OpenAI Codex 官方文档](https://developers.openai.com/codex)
- [Codex Prompting Guide](https://developers.openai.com/codex/learn)
- [Codex Best Practices 官方视频](https://developers.openai.com/codex/learn/best-practices)
- [Model Context Protocol 规范](https://modelcontextprotocol.io)
- [Codex 配置参考](https://developers.openai.com/codex/docs/configuration)
- [Codex GitHub 官方 Repository](https://github.com/openai/codex)

---

*归档说明：抖音视频因平台限制无法直接提取字幕，本文档基于 OpenAI 官方 Codex Best Practices 文档及多篇权威教程整理，内容覆盖视频所述核心知识点。*
