# PAIOS 演化节点复盘：从静态知识治理到运行反馈系统

> 日期：2026-07-19 | 对应 Packet：PKT-GOV-20260719-001 + PKT-EXE-20260719-001 + PKT-EXE-20260719-002
> 作者：Evan（复盘提炼）+ WorkBuddy（记录固化）
> 定位：架构演化里程碑记录 — 标识 PAIOS 从 v1.0 架构稳定阶段进入 Pilot 验证阶段

---

## 一、核心变化：Before → After

### Before：静态治理型 PAIOS

此前 PAIOS 已经具备：

- 生命周期管理
- 知识分层
- ADR 决策体系
- 多 Agent 协作治理
- Relationship 声明字段

但本质仍是：**Knowledge Repository + Manual Governance**，存在三个关键缺口。

---

### 缺口 1：有关系声明，没有关系计算

之前：

```
Markdown → related: ADR-0017
```

关系引擎是 CLI 工具，需人工触发查询，Agent 无法自然消费。关系只是"存在于文件中的字段"。

### 缺口 2：知道连接，不知道可信度

之前：

```json
{"source": "A", "target": "B"}
```

只能回答"A 和 B 有关系"。不能回答：谁建立？为什么存在？是否可信？人工还是机器推导？

### 缺口 3：没有反馈闭环

之前：

```
AI读取知识 → 完成任务 → 结束
```

系统不知道：哪些知识被用了、哪些 ADR 影响决策、哪些长期无人调用、哪里有知识缺口。

---

### After：具备运行反馈能力的 PAIOS

三个基础能力加入：

---

## 二、新增能力 1：关系引擎从工具变成基础设施

变化：`CLI 工具 → Knowledge Relationship Infrastructure`

五类查询原语：

```
locate     — 节点位置和元数据
traverse   — 关系链路（in/out/both）
chain      — 沿 supersedes 追溯决策历史
scan       — 全图健康检查（manual only）
resolve    — 自然语言 → 候选 node_ids
```

意义：AI 不需要加载整个知识库，而是：

```
任务 → 判断需要什么关系 → 查询 Graph → 获取最小必要上下文 → 推理
```

符合：**System 负责记忆，Model 负责推理。**

---

## 三、新增能力 2：边从"连接"升级为"可解释关系"

之前：`A → B`

之后：

```yaml
edge:
  source:        # 源节点 ID
  target:        # 目标节点 ID
  type:          # declared / backlink / supersedes
  confidence:    # 1.0（确定性）；<1.0 预留为 AI 推测边 gate
  source_type:   # human_frontmatter / engine_derived / adr_text_scan / ai_inferred
  created_by:    # human / relationship_engine
  created_time:  # ISO 8601（first_observed_time 语义）
```

三类边获得各自的身份标识：

| source_type | 含义 | confidence |
|-------------|------|------------|
| human_frontmatter | 人工确认关系 | 1.0 |
| engine_derived | 系统推导（可追踪） | 1.0 |
| adr_text_scan | ADR 文本正则提取 | 1.0 |
| ai_inferred | AI 推测（**预留，v0.1 禁止**） | <1.0 |

治理门槛：**AI 可以提出关系，不可以直接成为事实。**

---

## 四、新增能力 3：运行时从"一次性会话"升级为 Evidence Layer

新增 `usage_tracker.py`，形成：

```
Runtime Session → Usage Trace → Memory Loop → Candidate Improvement → Human Governance
```

记录：谁调用、调用了什么、为什么调用、结果如何。

输出：

```
40_AUTOMATION/10_TRACES/usage/YYYY-MM-DD/UT-YYYYMMDD-NNNN.yaml
```

特点：
- **Evidence，不是 Knowledge**
- 可删除、可重建
- 90 天生命周期
- 纯 Python 标准库，零外部依赖

---

## 五、三个数字背后的意义

| 指标 | 之前 | 之后 | 变化 |
|------|------|------|------|
| 测试规模 | 36 | 63 | 从单模块验证到系统能力验证 |
| 协作闭环完成 | 2 条 | 5 条 | 从开发闭环进入治理闭环 |
| 系统定位 | "好架构" | "好架构 + 价值证明" | 从设计正确性进入运行有效性 |

---

## 六、更深层变化

真正变化不是增加了 `relationship_engine.py` + `usage_tracker.py`，而是 PAIOS 开始形成完整的垂直链路：

```
        Human Governance
              ↑
        Memory Loop
              ↑
        Usage Trace
              ↑
        AI Runtime
              ↑
        Relationship Engine
              ↑
        Knowledge Layer
```

即：**从"管理知识"升级为"管理知识如何被使用、验证和演化"。**

---

## 七、评审语言总结

> **此前的 PAIOS 证明了"如何组织个人 AI 系统"；今天之后的 PAIOS 开始证明"如何让个人 AI 系统通过运行产生自身演化证据"。**

这也是从 v1.0 架构稳定阶段进入真正 Pilot 验证阶段的标志。
