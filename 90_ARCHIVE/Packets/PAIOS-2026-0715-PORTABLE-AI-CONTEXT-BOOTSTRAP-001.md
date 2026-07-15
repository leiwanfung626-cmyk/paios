type: methodology_packet

id: PAIOS-2026-0715-PORTABLE-AI-CONTEXT-BOOTSTRAP-001

title: "PAIOS Portable Runtime 自动上下文加载机制"

status: proposed
phase: Phase-5-backlog
source_phase: Phase-4-Stabilize

core_problem:
  description: >
    PAIOS-PORTABLE 已实现 Core/INDEX/ASSETS 分离和 U 盘迁移，
    但每次更换电脑或 AI 引擎时，仍需要人工说明当前实例、
    路径、阶段、治理规则和任务状态。

  current_issue:
    - AI 不自动知道当前 PAIOS 实例
    - AI 不自动知道 migration 状态
    - AI 不自动加载 ADR / Governance 约束
    - 多设备切换需要人工复制上下文


core_thesis:
  "PAIOS 不应该绑定某个 AI 工具，而应该提供标准化 Runtime Context，
   任何 AI 引擎启动时均可加载当前系统状态。"


proposed_solution:
  name: PAIOS Runtime Bootstrap

  architecture:

    PAIOS-PORTABLE:
      Core:
        - 30_SYSTEM/
        - 20_KNOWLEDGE/
        - 40_AUTOMATION/

      Runtime:
        - context generator
        - environment detector
        - launcher


workflow:

  startup:
    steps:
      - 插入 U 盘
      - 自动识别 PAIOS_ROOT
      - 检测当前机器环境
      - 读取 Identity / Manifest / Migration 状态
      - 加载 Governance Rules
      - 生成 current_context.md


generated_context:
  file:
    "30_SYSTEM/context/current_context.md"

  example:

    instance:
      id: PAIOS-PORTABLE-001

    runtime:
      location: "${PAIOS_ROOT}"

    phase:
      current: "Phase-4 Stabilize"

    constraints:
      - "禁止架构重构"
      - "禁止删除旧资产"
      - "P0问题允许修复"
      - "优化需求进入 backlog"

    loaded:
      - 30_SYSTEM
      - Governance
      - ADR
      - Today.md


implementation_plan:

  Phase-4:
    action:
      - 不开发
      - 记录需求
      - 观察真实使用问题

  Phase-5:
    action:
      - 开发 paios launcher
      - 开发 context generator
      - 支持多 AI 引擎

  Phase-6:
    action:
      - 集成 Reasonix
      - 集成 WorkBuddy
      - 集成 ChatGPT 工作流


design_principles:

  tool_independence:
    rule: >
      Context Packet 是 PAIOS 标准输出，
      不属于任何 AI 平台。

  need_driven:
    rule: >
      只有真实使用证明人工加载上下文成本过高，
      才升级为自动化能力。

  minimal_runtime:
    rule: >
      不建设复杂客户端，
      优先使用 Markdown/YAML/Python。


acceptance_criteria:

  - 任意电脑插入 PAIOS-PORTABLE 后可识别运行环境
  - 自动生成当前上下文文件
  - AI 可以通过 Context Packet 恢复工作状态
  - 不依赖单一 AI 平台
  - 不改变 Core 数据结构


decision:
  defer_to:
    - Phase-5 Refactor
    - Phase-5 Runtime Improvement

  current_action:
    "进入 backlog，不影响 Phase-4 Stabilize"
