# PAIOS 技术白皮书 v1.0 — 架构

> **来源**：`paios-philosophy.md` + `ai-capability-architecture.md` + 实际目录结构

## 3.1 七层目录架构

```
F:\PAIOS/
├── 00_CAPTURE/      # 信息入口（Inbox）— 缓冲区，处理完成即清空
├── 10_WORK/         # 工作区（临时）— 项目进行中的内容
├── 20_KNOWLEDGE/    # 知识库（已验证）— 持久化结构化知识
│   ├── Concepts/    # 概念
│   ├── Methods/     # 方法
│   ├── SOP/         # 标准操作流程
│   ├── Decisions/   # 决策记录
│   ├── Models/      # 模型
│   └── References/  # 参考资料
├── 30_SYSTEM/       # 系统内核 — 治理、愿景、配置
│   ├── Vision/      # 愿景与哲学
│   ├── Principles.md
│   ├── Governance/  # 治理框架
│   ├── Design_Notes/ # 架构设计笔记
│   ├── ADR/         # 架构决策记录
│   ├── Evolution/   # 演化记录
│   └── Config/      # 系统配置
├── 40_AUTOMATION/   # 自动化引擎
│   ├── 00_REGISTRY/ # 注册中心
│   ├── 01_CAPABILITIES/
│   ├── 02_PROMPTS/
│   ├── 03_AGENTS/
│   ├── 04_MCP/
│   ├── 05_SCRIPTS/
│   ├── 06_PROVIDERS/
│   ├── 07_WORKFLOWS/
│   ├── 08_TESTS/
│   ├── 09_LEGACY/
│   └── 10_MANIFEST/
├── 50_DATA/         # 数据基础设施（运行时）
├── 60_EXTERNAL/     # 外部引用（G:、H: 盘）
├── 70_TMP/          # 运行时临时文件
└── 90_ARCHIVE/      # 历史归档
```

### 层级关系

```
生命周期：Capture → Work → Knowledge → System/Automation → Data → Archive
                 ↓
          00 → 10 → 20 → 30/40 → 50 → 90
```

## 3.2 四层能力模型

PAIOS 的 AI 能力来源于四层，每一层解决不同的问题：

```
┌─────────────────────────────────────────────────┐
│  L1  Foundation Intelligence（基础智能）           │
│  外部大模型：ChatGPT / Claude / Gemini / DeepSeek │
│  职责：推理、写作、编程、分析、总结                │
├─────────────────────────────────────────────────┤
│  L2  Memory（长期记忆）                           │
│  20_KNOWLEDGE 知识库 + 项目上下文 + 历史决策       │
│  职责：提供与你相关的上下文，让 AI 认识你          │
├─────────────────────────────────────────────────┤
│  L3  Decision Rules（决策规则）                    │
│  ADR + Decision Protocol + 决策模板               │
│  职责：约束 AI 的推理方式，按你的思维做决策        │
├─────────────────────────────────────────────────┤
│  L4  Feedback Loop（反馈闭环）                     │
│  复盘记录 + 踩坑日志 + ROI 评估                    │
│  职责：从经验中学习，持续校正，实现复利效应         │
└─────────────────────────────────────────────────┘
```

**AI 能力公式**：

```
AI 能力 = 大模型 + 长期记忆 + 决策协议 + 经验复利
```

**不可跳过任何一层**：只有 L1+L2 的系统是"搜索+总结"机器；加入 L3 才能做出判断；加入 L4 才能持续进化。

## 3.3 三大引擎

| 引擎 | 职责 | 对应层级 | 关键资产 |
|------|------|---------|---------|
| **Memory Engine** | 统一管理长期知识与检索 | L2 Knowledge | 20_KNOWLEDGE、知识元数据 |
| **Decision Engine** | 统一决策协议与 ADR | L3 Decision | ADR、Decision Protocol、决策模板 |
| **Learning Engine** | 复盘反馈与规则修订 | L4→L5 Evolution | 复盘记录、踩坑日志、ROI 评估 |

### 引擎关系

```
Memory Engine ──→ 提供上下文
      │
      ▼
Decision Engine ──→ 做出决策
      │
      ▼
Learning Engine ──→ 复盘优化
      │
      └─────────→ 反馈回 Memory & Decision
```

## 3.4 数据流

```
User → Decision Layer → Workflow Layer → Execution Layer → Knowledge Layer → Infrastructure
```

## 3.5 五层数据价值体系

```
价值
  ▲
  │            L5 Evolution（系统自我改进）
  │          L4 Feedback（经验复利）
  │        L3 Decision（决策约束）
  │      L2 Knowledge（个人上下文）
  │    L1 Foundation（通用智能）
  └──────────────────────────────→ 个性化程度
```

| 层级 | 内容 | 来源 | 稳定性 |
|------|------|------|--------|
| **L1 Foundation** | 大模型的预训练知识 | 外部 | 持续更新（模型升级） |
| **L2 Knowledge** | 事实、资料、项目、文档 | 用户沉淀 | 稳定，需维护 |
| **L3 Decision** | ADR、Decision Log、决策协议 | 用户决策 | 长期稳定 |
| **L4 Feedback** | 结果、复盘、踩坑、ROI | 执行反馈 | 持续增长 |
| **L5 Evolution** | 规则修订、流程优化、最佳实践 | 系统自我改进 | 持续演化 |

---

**关联文档**：[02_Principles.md](02_Principles.md) | [04_Workflow_Standard.md](04_Workflow_Standard.md) | `Design_Notes/ai-capability-architecture.md` | `paios-philosophy.md`
