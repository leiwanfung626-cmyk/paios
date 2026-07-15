# ADR-0017: 跨引擎工作上下文继承标准（Cross-Engine Work Context Inheritance）

## Status
Experimental

> 2026-07-11: 从 Accepted 降级为 Experimental。50_RUNTIME 是新增平台层，需验证后方可成为 Core。

---

## Context

PAIOS 由多个 AI 引擎/工具协同驱动：Reasonix、Codex、WorkBuddy、ChatGPT、Claude 等，未来还会增加。

核心问题：

1. **工具可以换，工作不能丢** — 一个引擎开始的工作，另一个引擎要能无缝继续，不重新解释上下文
2. **痕迹孤岛** — 每个引擎的 session/对话历史存在私有目录，彼此不可见
3. **工作流断裂** — 跨引擎切换时上下文丢失，需要人工重述进度
4. **Platform > Tool** — PAIOS 不应依赖任何一个 AI 引擎

---

## Architecture Principle

**Engine owns execution; PAIOS owns continuity.**

AI 引擎负责执行（代码生成/对话/调试/Shell），PAIOS 负责连续性（Task/Handoff/Knowledge/Governance）。
这一定位比"跨引擎继承"更稳定，也是本 ADR 所有设计的根本出发点。

执行过程（Session、日志、内部格式）属于各引擎自身。PAIOS 不保存引擎运行日志的完整副本，只保存连续性所需的索引和交接文件。

---

## Decision

建立四层架构：

```
Engine          → 各引擎保持私有目录，PAIOS 不碰
    ↓
Adapter         → 统一接口层（Read/Write/Export/Import Context）
    ↓
Task            → 平台级对象（Task = 可继承的工作单元）
    ↓
Knowledge       → 最终沉淀（ADR / 文档 / 知识）
```

### 第 1 层：Engine（引擎私有层）

每个引擎保持自有存储格式，PAIOS **不要求改动**：

| 引擎 | 私有目录 | 原生痕迹格式 |
|------|----------|-------------|
| Reasonix | `.reasonix/` | session JSON |
| WorkBuddy | `.workbuddy/memory/` | Markdown 日志 |
| Codex | 对话历史 | 平台无关 |
| ChatGPT | 对话历史 | 平台无关 |
| Claude | `.claude/`（未来） | 会话记录 |

**原则**：PAIOS 不保存运行日志的完整副本。PAIOS 只保存 **Index（索引）**。

### 第 2 层：Adapter（适配器层）

每个引擎实现一个 Adapter，提供 4 个统一接口：

```yaml
# Adapter 接口定义
adapter_id: "reasonix-adapter"
engine_id: "reasonix"
version: "1.0"

interfaces:
  read_trace:      # 从引擎私有格式读取痕迹 → 返回统一 TraceRecord
  write_trace:     # 写入痕迹（写入引擎私有格式 + 更新 Index）
  export_context:  # 导出当前工作上下文 → 标准 Handoff 格式
  import_context:  # 从标准 Handoff 格式导入上下文 → 恢复引擎状态
```

Adapter 位于 `40_AUTOMATION/00_REGISTRY/adapters.yaml`，适配器脚本在 `40_AUTOMATION/04_ADAPTERS/`。

**好处**：
- 新引擎只需写一个 Adapter，无需改造 PAIOS
- 引擎升级也不影响平台
- 能力探测由 Adapter 在运行时完成，不写死在 Registry

### 第 3 层：Task（任务层 — 平台核心对象）

**Task 是 PAIOS 的跨引擎继承单元**，不是 Session。

Session 是引擎私有的运行时概念。Task 才是平台级持久化对象。

每个 Task 对应 `10_WORK/{task_id}/`（与现有 7 层目录对齐），包含：

```
10_WORK/{task_id}/
├── task.yaml         # 任务定义（不变信息）
├── handoff.yaml      # 交接文件（可变 — 跨引擎接力核心）
├── manifest.yaml     # 任务清单（资产/产出/状态）
└── inputs/           # 输入（已有约定）
    outputs/          # 输出（已有约定）
    notes.md          # 笔记（已有约定）
```

#### task.yaml — 任务定义（任务创建时写入，基本不修改）

```yaml
task_id: "photo-organize"
display_name: "照片整理"
created_at: "2026-07-01T10:00:00+08:00"
status: "in_progress"  # 对应 ADR-0007 生命周期

goals:
  - "完成照片入库索引"
  - "实现人脸检索与人物策展"
  - "持续提升标注密度"
```

#### handoff.yaml — 交接文件（跨引擎接力核心，频繁更新）

```yaml
# handoff.yaml — 标准交接格式
# 任何引擎打开此文件即可恢复上下文继续工作
task_id: "photo-organize"
current_step: "face_clustering"
workflow_id: "photo_organizer_flow"

completed:
  - step: "ingest"
    engine: "reasonix"
    summary: "入库索引完成，11,954 张照片已写入 photo_index.db"
    trace_uri: ".reasonix/session-xxx.json"
  - step: "face_detection"
    engine: "workbuddy"
    summary: "人脸检测完成，19,842 个人脸"
    trace_uri: ".workbuddy/memory/2026-07-08.md"

next:
  step: "face_clustering"
  input: "face_index.db + FAISS 索引"
  engine_hint: "reasonix"  # 建议引擎，非强制绑定
  priority: "high"

known_issues:
  - "20年年龄跨度使同人聚类分裂"
  - "Person A = 运丰（不确定，需确认）"

required_input:
  - "E:/PAIOS/10_WORK/photos_organizer/face_index/face_index.db"
  - "E:/PAIOS/10_WORK/photos_organizer/face_index/faiss_index.bin"

context_summary: |
  照片整理项目第二阶段。已完成入库和人脸检测。
  下一步对 19,842 个人脸进行聚类。
  注意年龄跨度可能导致同人分裂，不追求自动认人。
```

### 第 4 层：Knowledge（知识沉淀层）

Task 完成后，关键产出沉淀到 `20_KNOWLEDGE/`：
- ADR 架构决策
- SOP 操作流程
- 经验总结文档

而非沉淀 Session 记录。

---

### Trace Index（痕迹索引）

不保存完整痕迹内容。只保存**引用**，指向各引擎的原生痕迹：

```yaml
# 40_AUTOMATION/10_TRACES/index/2026-07-11-T.yaml
traces:
  - trace_id: "20260711T090000-reasonix-1"
    engine: "reasonix"
    timestamp: "2026-07-11T09:00:00+08:00"
    trace_type: "milestone"
    summary: "完成人脸检测脚本编写"
    uri: ".reasonix/session-xxx.json"       # 指向引擎原生痕迹
    task_id: "photo-organize"               # 关联 Task
    workflow_id: "photo_organizer_flow"
    workflow_step: "face_detection"
    tags: ["photo", "face", "development"]
    continuation: "见 10_WORK/photo-organize/handoff.yaml"  # 指向 handoff
```

**为什么是 Index 不是 Store？**
- 无双写（Double Write），引擎写自己的格式，Index 只加一行引用
- 引擎升级/换引擎，Index 中的历史引用仍然有效
- Index 可跨引擎查询过滤，真正的上下文在 Task/handoff 中

---

### Workflow（工作流定义 — 引擎无关）

工作流只定义**业务步骤**，不绑定具体引擎：

```
capture_flow:
  steps: [capture, classify, route]

knowledge_flow:
  steps: [validate, index, review]
```

至于 Classify 由谁执行，由 **Engine Scheduler**（引擎调度层）动态决定：
- 如果 Reasonix 在线 → Reasonix
- 如果 Reasonix 不在线 → Claude
- Workflow 本身不需要修改

### Engine Registry（引擎注册 — 简化版）

只记录引擎身份、运行时路径、Adapter 引用、能力标签。**不写死能力清单**，由 Adapter 运行时探测。

```yaml
engines:
  - engine_id: "reasonix"
    display_name: "Reasonix"
    adapter: "reasonix-adapter"
    runtime_path: ".reasonix/"
    capability_tags: ["reasoning", "code_gen", "shell"]
```

---

## Rationale

### 为什么用 Index 不用 Store？
- 避免 Double Write 漂移（一个事实，两个副本 → 一定会不一致）
- 尊重各引擎的私有存储格式，PAIOS 不强行统一
- 引擎可以随时换，Index 中的 URI 引用仍然有效

### 为什么用 Task 不用 Session？
- Session 是引擎私有的运行时概念（连接/对话/轮次）
- Task 是平台持久化对象（目标/产出/状态/交接）
- `10_WORK/` 已有 Task 目录，task.yaml + handoff.yaml 直接放在工作目录中

### 为什么 Workflow 不知道 Engine？
- 引擎是执行者，不是定义的一部分
- 同一工作流可以今天由 Reasonix 跑、明天由 Claude 跑
- 符合 Engine Scheduler 的未来扩展

### 为什么加 Adapter 层？
- 新引擎只需写一个 Adapter，不需要改造 PAIOS 核心
- 引擎升级不影响平台
- 能力探测由 Adapter 在运行时完成，Registry 只需标签

### 为什么 State File 保留？
用户反馈"这个我反而很喜欢"。State File 解决了 **AI 最难的恢复上下文**问题。标准化 handoff 文件让任何 AI 打开即继续。

---

## Consequences

### Positive
- ✅ 无 Double Write — 引擎保持自有格式，Index 只存引用
- ✅ 引擎可插拔 — 新引擎写 Adapter 即可接入
- ✅ 工作流与引擎解耦 — 引擎调度层决定执行者
- ✅ Task 为中心 — 与现有 10_WORK/ 目录结构一致
- ✅ Handoff 标准化 — 任何 AI 打开 handoff.yaml 即恢复上下文
- ✅ 符合 Platform Purity — PAIOS 不碰引擎私有数据

### Negative
- ⚠️ 需要为每个引擎写 Adapter（初始成本）
- ⚠️ 需要 Engine Scheduler 来动态分配工作流步骤（未来工作）
- ⚠️ 引擎切换时需要显式更新 handoff.yaml（需遵守约定）

### Migration

- 旧版 ADR-0017 的 `10_TRACES/traces/` 目录保留但标记为 deprecated
- `10_TRACES/sessions/` 替换为 `10_TRACES/tasks/`
- 各引擎逐步添加 Adapter 实现
- `engine_hints` 从 workflow 定义中移除，改为调度层配置

---

## Related

- ADR-0005: Workflow Pipeline（9 阶段工作流）
- ADR-0007: Lifecycle Model（7 状态生命周期）
- ADR-0008: Automation Layer（40_AUTOMATION 层设计）
- ADR-0012: Platform-Application Architecture
- `40_AUTOMATION/00_REGISTRY/agents.yaml`
- `40_AUTOMATION/00_REGISTRY/workflows.yaml`
- `40_AUTOMATION/00_REGISTRY/adapters.yaml`
