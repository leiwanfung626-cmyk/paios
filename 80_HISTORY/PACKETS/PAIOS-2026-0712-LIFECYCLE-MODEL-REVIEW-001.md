type: handoff_packet
id: PAIOS-2026-0712-LIFECYCLE-MODEL-REVIEW-001
title: "PAIOS 00-90 生命周期层模型确认与架构修正"
generated_at: 2026-07-12T14:45:00+08:00
generated_by: ChatGPT / External API
baseline: v1.0.1-architecture-frozen

packet:

  context:
    system: PAIOS Platform — Personal AI Operating System
    reference:
      - ADR-0003 Lifecycle Layer Model
      - Directory Audit PAIOS-2026-0712-DIRECTORY-AUDIT-001
    architecture_type:
      "Lifecycle Architecture, not Content Classification"
    current_model:
      layer_count: 10
      range: "00-90"
      status: Frozen

    core_principle:
      principle_1:
        title: "目录表达生命周期，不表达内容分类"
        meaning:
          - "文件位置由生命周期阶段决定"
          - "不是按主题、类型、人为分类"

  decision:

    - id: D001
      decision:
        "正式确认 PAIOS 当前架构为 00-90 十层生命周期模型"
      rationale:
        - "早期7层模型属于历史阶段"
        - "当前架构已经扩展并稳定为十层"
      impact:
        - "后续文档统一使用00-90模型"
        - "不再描述当前架构为7层"

    - id: D002
      decision:
        "10_WORK 保持作为活跃工作生命周期层"
      rationale:
        - "项目开发过程中的源码、文档、实验均属于加工阶段"
        - "存在项目运行环境不等于架构污染"
      clarification:
        invalid:
          - "因为包含项目文件而认为WORK污染"
        valid:
          - "Runtime Artifact需要隔离"

    - id: D003
      decision:
        "40_AUTOMATION 包含 Engine Runtime 与 Scheduler"
      rationale:
        - "Runtime属于能力执行，不属于数据存储"
        - "自动化系统负责让知识和流程流动"

    - id: D004
      decision:
        "50_DATA 保持为空状态"
      rationale:
        - "目录存在不代表必须产生数据"
        - "遵循 Need Driven Promotion"
      future_scope:
        - databases
        - indexes
        - embeddings
        - vector_store

    - id: D005
      decision:
        "80_HISTORY 与90_ARCHIVE保持生命周期区分"
      rationale:
        history:
          "记录发生过程"
        archive:
          "生命周期终点存档"

  lifecycle_model:

    layers:

      - id: "00"
        name: CAPTURE
        role: "统一输入入口"
        examples:
          - Inbox.md
          - Today.md

      - id: "10"
        name: WORK
        role: "活跃加工区"
        rules:
          - "项目进行期间停留"
          - "完成后进入知识化或归档"

      - id: "20"
        name: KNOWLEDGE
        role: "验证后的知识资产"
        rules:
          - "非草稿"
          - "非临时记录"

      - id: "30"
        name: SYSTEM
        role: "PAIOS治理内核"
        contains:
          - ADR
          - Governance
          - Fleet
          - PAIOS-Usage
          - Principles

      - id: "40"
        name: AUTOMATION
        role: "自动化能力层"
        contains:
          - Registry
          - Prompts
          - Adapters
          - Scripts
          - Engines
          - Scheduler

      - id: "50"
        name: DATA
        role: "结构化数据基础设施"

      - id: "60"
        name: EXTERNAL
        role: "外部资源引用"

      - id: "70"
        name: TMP
        role: "短生命周期临时资源"

      - id: "80"
        name: HISTORY
        role: "工程历史记录"

      - id: "90"
        name: ARCHIVE
        role: "最终归档"

  findings:

    finding_001:
      topic: "10_WORK Runtime Artifact治理"
      status: "需要优化，不需要迁移整个WORK"
      rule:
        - "项目资产保留在WORK"
        - "运行环境不进入正式资产"
      examples:
        remove_from_project_tracking:
          - ".venv"
          - "cache"
          - "temporary outputs"
        keep:
          - "src"
          - "scripts"
          - "docs"
          - "design"

    finding_002:
      topic: "目录模型历史描述"
      issue:
        "7层冻结表述与当前十层模型冲突"
      resolution:
        - "更新文字定义"
        - "保持架构冻结"

  proposed_document_update:

    target:
      "Principles / Architecture Documentation"

    recommended_statement:

      old:
        "PAIOS冻结为7个层"

      new:
        "PAIOS冻结生命周期层模型。当前正式模型为00-90十层结构。"

    reason:
      - "冻结对象是生命周期逻辑"
      - "不是早期版本数量"

  required_actions:

    P1:
      - action:
          "更新架构文档中的7层历史表述"
        owner:
          "Case-01 Maintainer"

      - action:
          "保存本packet"
        target:
          "80_HISTORY/PACKETS/"
        filename:
          "PAIOS-2026-0712-LIFECYCLE-MODEL-REVIEW-001.md"

      - action:
          "10_WORK项目内部清理Runtime Artifact"
        scope:
          - ".venv"
          - "cache"
          - "临时模型"

    P2:
      - action:
          "建立项目Runtime隔离规范"
      - action:
          "评估ADR-0020"
      - action:
          "继续Phase B物理边界拆分"

  final_assessment:

    architecture_status:
      "Stable"

    maturity_stage:
      "从建设阶段进入治理阶段"

    primary_focus:
      - "保持生命周期边界"
      - "减少无必要结构变化"
      - "强化Core / Work / Runtime / History隔离"

    prohibited_actions:
      - "新增目录解决管理问题"
      - "按内容分类破坏生命周期模型"
      - "将Runtime数据提升为知识资产"

  handoff_note:
    message: >
      PAIOS 当前目录模型应被理解为生命周期操作系统。
      后续维护者应根据对象所处生命周期决定位置，
      而不是根据对象主题决定目录。
