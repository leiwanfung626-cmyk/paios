# ADR-0021: 引擎调度层（Engine Scheduling）

## Status
Experimental

> 2026-07-11: Scheduler 已实现（policy.yaml + rules.yaml），但尚未经多引擎运行时验证。进入 Experimental 阶段。
>
> **2026-07-12: 50_RUNTIME 内容已合并至 40_AUTOMATION。**
> Engine Scheduler → `40_AUTOMATION/12_SCHEDULER/`
> Engine Status   → `40_AUTOMATION/11_ENGINES/`
> Adapter 脚本    → `40_AUTOMATION/04_ADAPTERS/`
> 目录 50_RUNTIME/ 已删除。任何后续实现请直接写入 40_AUTOMATION/ 下对应子目录。

---

## Context

ADR-0017 实现了跨引擎工作上下文继承，但遗留了一个关键问题：

**谁来决定哪个引擎执行哪个步骤？**

目前 Workflow Registry（ADR-0017）只定义了业务步骤，不绑定引擎。但 PAIOS 还没有一个正式的调度层来决定执行者。

实际场景：

```
Workflow 定义:  photo_organizer_flow.ingest
                 ↓
可用引擎列表:    reasonix, workbuddy, claude, chatgpt
                 ↓
谁来选?          ❌ 人工选（当前做法）
                 ❌ 写死在 workflow 里（ADR-0017 v1 的错误）
                 ✅ 调度层自动选（需要 ADR-0021）
```

调度决策需要考虑的因素：

| 因素 | 例子 |
|------|------|
| **能力匹配** | face_clustering 需要 Python + InsightFace → reasonix 更适合 |
| **可用性** | ChatGPT 离线 → 跳过 |
| **延迟** | 简单分类 → 最快可用的引擎 |
| **成本** | 批量处理 → 低成本引擎（本地 > API） |
| **优先级** | 紧急任务 → 最可靠的引擎 |
| **重试/降级** | reasonix 失败 → 自动 fallback 到 codex |
| **用户偏好** | 编码任务 → reasonix；写作任务 → claude |

---

## Decision

建立 **Engine Scheduler** 作为 PAIOS 平台核心组件，定位在 `50_RUNTIME/` 中：

```
50_RUNTIME/
├── adapters/           # ADR-0017: 引擎适配器
├── engines/            # 引擎运行时状态
│   └── {engine_id}/
│       ├── status.yaml # 在线/离线/负载
│       └── queue.yaml  # 等待队列
└── scheduler/          # ← 新增: 引擎调度器
    ├── policy.yaml     # 调度策略配置
    ├── rules.yaml      # 调度规则（能力/成本/优先级）
    └── log/            # 调度决策日志
```

### 核心概念

#### 1. Capability Match（能力匹配）

每个引擎通过 Adapter `probe()` 在运行时报告可用能力：

```
reasonix probe → [reasoning, code_gen, shell, session_persistence, trace_aware]
workbuddy probe → [memory, automation, orchestration, state_tracking, daily_log, trace_aware]
claude probe → [reasoning, conversation, document_analysis, writing]
```

Workflow 步骤通过 `required_capability` 标签声明需求：

```yaml
# workflow 定义（在 00_REGISTRY/workflows.yaml 中）
steps:
  - step_id: "face_clustering"
    name: "人脸聚类"
    required_capability: ["python", "shell"]  # ← 能力需求，非引擎名
```

Scheduler 匹配逻辑：
```
for each step.required_capability:
    find engines where all capabilities ⊆ probe()
    if multiple: apply priority/cost/latency scoring
    if none: trigger fallback
```

#### 2. Scoring & Selection（评分与选择）

Scheduler 维护一个策略文件 `policy.yaml`：

```yaml
# 50_RUNTIME/scheduler/policy.yaml
scoring:
  priority_weight: 0.4     # 用户偏好权重
  cost_weight: 0.3         # 成本权重
  latency_weight: 0.2      # 延迟权重
  reliability_weight: 0.1  # 可靠性权重

preferences:               # 用户偏好（可动态调整）
  code_task: "reasonix"
  writing_task: "claude"
  default: "workbuddy"
```

评分公式（简化）：
```
score(e) = Σ(weight_i × score_i(e))
selected = argmax(score(e) for all available e)
```

#### 3. Availability & Health（可用性）

每个引擎在 `50_RUNTIME/engines/{engine_id}/status.yaml` 报告状态：

```yaml
# 50_RUNTIME/engines/reasonix/status.yaml
engine_id: "reasonix"
status: "online"           # online / offline / degraded
last_probe: "2026-07-11T12:00:00+08:00"
capabilities: ["reasoning", "code_gen", "shell"]
latency_ms: 850
error_rate: 0.02
```

Scheduler 定期（或按需）调用 Adapter `probe()` 刷新状态。

#### 4. Fallback Chain（降级链）

当首选引擎不可用时，沿 fallback 链自动降级：

```yaml
# 50_RUNTIME/scheduler/rules.yaml
fallback_chains:
  face_clustering:
    primary: "reasonix"
    fallback:
      - engine: "codex"           # 能力接近
        degrade_note: "无本地 InsightFace，使用云端 API"
      - engine: "workbuddy"       # 能力最弱但可用
        degrade_note: "仅能执行基础聚类，需人工复查"
    max_retries: 2
    timeout_minutes: 30
```

#### 5. Scheduling Log（调度日志）

每次调度决策写入日志：

```yaml
# 50_RUNTIME/scheduler/log/2026-07-11.yaml
decisions:
  - timestamp: "2026-07-11T10:00:00+08:00"
    task_id: "TASK-20260711-001"
    workflow_step: "face_clustering"
    required_capability: ["python", "shell"]
    candidates:
      - engine: "reasonix"      # score: 0.85 ← selected
      - engine: "codex"         # score: 0.52
      - engine: "workbuddy"     # score: 0.31
    selected: "reasonix"
    reason: "能力完全匹配 + 用户偏好 + 零成本（本地）"
```

---

## Rationale

### 为什么 Scheduler 不属于 Workflow？
- Workflow 定义**做什么**（业务步骤），Scheduler 决定**谁来做**（执行者）
- 分离后：Workflow 永远不需要因为引擎变化而修改
- 符合单一职责原则

### 为什么用运行时 probe 而不是 Registry 写死？
- 引擎可用性会变（离线、负载高、API 配额耗尽）
- 写死在 Registry 中的能力列表迟早与真实状态漂移
- Adapter `probe()` 在调用时刻返回真实状态

### 为什么放在 50_RUNTIME/ 而不是 40_AUTOMATION/？
- Scheduler 是平台运行时组件，不是自动化工作流
- 与 Adapter（运行时接口）和 Engine Status（运行时状态）同层
- 符合 ADR-0017 的"Engine→Adapter→Task→Knowledge"四层架构定位

---

## Consequences

### Positive
- ✅ 引擎切换完全自动化 — Claude 不在线自动走 fallback
- ✅ Workflow 永远不需要改 — 只定义业务步骤
- ✅ 可扩展评分模型 — 新增 scoring factor 不影响已有规则
- ✅ 调度可见性 — 每次决策写入日志，可审计可调试

### Negative
- ⚠️ 需要实现 Scheduler 运行时组件（当前 Policy/Rules 是声明式配置，执行器待实现）
- ⚠️ probe 成本 — 频繁 probe 可能影响引擎性能（建议缓存 + 按需刷新）
- ⚠️ 评分模型需要调参 — 初始权重为经验值，需实际数据校正

### Next Steps

1. ✅ 实现 `50_RUNTIME/scheduler/` 目录结构和 Policy/Rules 配置（已完成）
2. ⏳ 实现基础 Scheduler 引擎（Python）：读取 workflow step → 匹配 engine → 评分 → 选择
3. ⏳ 实现 Adapter `probe()` 标准化（已在 ADR-0017 中定义接口，待全部引擎实现）
4. ⏳ 集成到 handoff 流程：引擎交接时自动调用 Scheduler 决定下一执行者

### Path to Accepted

进入 Accepted 前需要完成以下验证：

1. **三组跨引擎 handoff 实验**：
   - ChatGPT → Reasonix → WorkBuddy
   - Reasonix → Codex → ChatGPT
   - WorkBuddy → ChatGPT → Reasonix
2. **至少 3 个引擎的 Adapter 完整实现**（read_trace + export_context + import_context + probe）
3. **Scheduler 实际运行 72 小时以上**，记录调度决策日志
4. **架构评审通过** — 经 Case-01 Maintainer 确认后升为 Accepted

---

## Related

- ADR-0017: Cross-Engine Work Context Inheritance（四层架构，Adapter + Handoff）
- ADR-0005: Workflow Pipeline（9 阶段工作流）
- `50_RUNTIME/adapters/`（Adapter 接口层）
- `50_RUNTIME/engines/`（引擎运行时状态）
