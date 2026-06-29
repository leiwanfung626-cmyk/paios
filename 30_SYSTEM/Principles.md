# PAIOS Platform — Principles

> **Architecture**: Frozen
> **Version**: 1.0.0

## Nine Core Principles

1. **Directories express lifecycle, not content.**
2. **Everything has exactly one formal location.**
3. **The workspace is always temporary.**
4. **Knowledge must be validated before entering the knowledge base.**
5. **Automation stores workflows, not knowledge.**
6. **Keep the top-level directory count low** (frozen at 7).
7. **Metadata is the primary classification system.**
8. **Tool Independence Principle.**
   PAIOS is the platform, not a configuration for any single AI tool.
   AI tools (Codex, Claude, ChatGPT, Gemini, etc.) are **clients** of the
   platform, not the platform itself.  All platform assets use open,
   portable formats (Markdown, YAML, Python, JSON).  Changing an AI tool
   must not require rebuilding platform assets.
9. **Bootstrap First Principle.**
   AI tools must load platform governance information (Principles, ADR,
   Registry, Manifest) before performing tasks.  Assets (Knowledge,
   Projects, Archives) are loaded on-demand based on the current task,
   not pre-scanned.  All AI tools follow the same bootstrap convention
   to preserve tool independence.

### Requirement Emergence Principle (需求涌现原则)

> **Requirements are not input — they are output of iteration.**

In complex knowledge work, user requirements typically do not exist
fully-formed at the start of a task.  What exists initially is a
direction, a dissatisfaction, or a vague goal.  The real requirement
gradually emerges through cycles of feedback, validation, and iteration.

PAIOS does not treat requirements as fixed input.  Instead, it treats
requirement convergence as a primary goal of the workflow — supporting
not just solution iteration, but also the ongoing clarification and
redefinition of the problem itself.

#### Dual-loop model

```
Loop 1 — Requirement refinement (the critical loop):
   Vague idea → First implementation → See result →
   Discover real problem → Redefine requirement → Re-implement →
   Real need gradually converges

Loop 2 — Implementation refinement (traditional view):
   Known requirement → Design → Implement → Verify →
   Fix bugs → Done
```

Many projects fail not because the implementation is poor, but because
they have been optimizing a problem that was never well-defined.

#### Relation to Need Driven Promotion

| Principle | Focus | Answers |
|-----------|-------|---------|
| Need Driven Promotion | When to add features | Feature timing |
| Requirement Emergence | How requirements form | Need discovery |

#### System design implications

1. The primary duty of the Decision Layer is not to choose among
   solutions — it is to help the user discover their real need.
2. The greatest value of Feedback is not bug-fixing — it is
   continuously correcting the problem definition.
3. The purpose of a Prototype is not to validate a solution —
   it is to help the requirement converge.

**Status**: Validated by Engineering Practice (PAIOS Platform v1.0.0)

## Architecture Freeze

This architecture is frozen per the Architecture Freeze Policy:
- 3+ months of continuous use, OR
- Two or more projects exposing the same structural issue, OR
- Clear benefit with acceptable migration cost

## How to Use — 操作指南

### 三条用户约定

1. **输入统一（Single Entry）** — 任何新输入先进入 `00_CAPTURE/Inbox.md`，不思考分类，不决定目录。
2. **生命周期路由（Lifecycle Routing）** — 系统根据 Lifecycle 决定内容去向（Work / Knowledge / Automation / Archive），用户不决定目录。
3. **流程记忆（Process Memory）** — 用户只记住流程（Capture → Route → Process），不记住目录路径。

### 核心心智模型

```
我不要问"放哪里"，
我只问"交给 PAIOS 了吗？"
```

### 四个统一

| 统一 | 含义 |
|------|------|
| 输入统一（Single Entry） | 所有新内容先进入 Inbox |
| 判断统一（Lifecycle Routing） | 生命周期决定去向，不是目录 |
| 登记统一（Registry First） | 长期资产进入 Registry |
| 治理统一（Governance） | 长期演化遵循 ADR 与 Freeze Policy |

### Inbox 使用规则

- Inbox 是缓冲区（Buffer），不是仓库（Storage）
- 处理完成即清空（标记 `[x]`）
- 可以堆积，但生命周期不能跳过

### AI Tool Guidance — AI 工具使用规范

#### 启动流程

```
Workspace: F:\PAIOS
     ↓
Bootstrap (加载平台治理信息)
  ├── Principles    — 了解平台规则
  ├── ADR           — 了解架构约束
  ├── Registry      — 发现可用能力
  └── Manifest      — 确认平台版本
     ↓
Read only what the current task requires
     ↓
Start working
```

#### 关键约定

- **Bootstrap 是加载治理信息，不是扫描全系统。**
  Knowledge、Projects、Archive 等业务内容应根据当前任务按需加载，
  不作为 Bootstrap 的一部分。
- 每次新会话的第一步：读取 Principles + ADR + Registry + Manifest。
- 不同 AI 工具（Codex、Claude Code、ChatGPT、Gemini CLI）遵循相同的启动流程。
