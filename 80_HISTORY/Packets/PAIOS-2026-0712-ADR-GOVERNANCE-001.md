type: handoff_packet

id: PAIOS-2026-0712-ADR-GOVERNANCE-001

title: "PAIOS ADR 生命周期治理规则确立"

generated_at: 2026-07-12T15:00:00+08:00

generated_by:
  ChatGPT / External API

baseline:
  architecture: v1.0.1
  governance: ADR-based evolution


packet:

  context:

    system:
      "PAIOS Platform — Personal AI Operating System"

    target:
      "ADR maintenance and future architecture evolution"

    current_state:

      adr_count:
        "19 existing ADRs"

      previous_event:
        "ADR documentation has already undergone one repair/update cycle"

      new_rule:
        "Future ADR handling follows lifecycle governance instead of direct rewriting"


  core_decision:

    - id: ADR-GOV-001

      decision:
        "ADR is historical decision evidence, not a living specification document"

      principle:
        - "事实不可修改"
        - "决策可以演进"
        - "状态必须透明"


    - id: ADR-GOV-002

      decision:
        "Architecture changes must not erase previous ADR history"

      forbidden:

        - "直接删除旧ADR"
        - "覆盖历史决策原因"
        - "修改过去已经发生的事实"


      required:

        - "更新ADR状态"
        - "建立替代关系"
        - "新增后续ADR"


  adr_lifecycle_model:


    states:

      Proposed:
        meaning:
          "提出但未正式采用"

      Accepted:
        meaning:
          "当前有效架构决策"

      Implemented:
        meaning:
          "已经落地"

      Superseded:
        meaning:
          "被新的ADR替代，但历史有效"

      Deprecated:
        meaning:
          "不再推荐使用"

      Archived:
        meaning:
          "仅保留历史"


    transition:

      example:

        ADR_old:

          status:
            "Accepted"


        architecture_change:

          action:
            "Create new ADR"


        ADR_old_after:

          status:
            "Superseded"

          superseded_by:
            "ADR_new"



  decision_rules:


    rule_001:

      question:
        "ADR描述是否只是落后于当前实现？"

      action:

        - "更新补充说明"
        - "保持Accepted"

      example:

        case:
          "7层模型文档更新为00-90十层模型"

        judgment:
          "不是架构推翻，是文档演进"

        result:
          "ADR-0003保持Accepted"



    rule_002:

      question:
        "原设计是否被新设计替代？"

      action:

        - "保留旧ADR"
        - "标记Superseded"
        - "创建新ADR"


      example:

        old:
          "50_RUNTIME独立层"

        new:
          "40_AUTOMATION/11_ENGINES + 12_SCHEDULER"


        result:

          old_status:
            "Superseded"

          new:
            "ADR-New Runtime Architecture"



    rule_003:

      question:
        "历史决策是否证明错误？"

      action:

        - "Deprecated"
        - "增加Correction说明"
        - "保留错误背景"


  PAIOS_specific_application:


    case_001:

      topic:
        "00-90生命周期模型"

      current_status:

        ADR:
          "ADR-0003"

        status:
          "Accepted"


      interpretation:

        old:
          "7层冻结"

        corrected:

          "PAIOS冻结的是生命周期模型，不是历史层数量"


      required:

        - "保持ADR-0003历史连续性"
        - "补充Evolution章节"


    case_002:

      topic:
        "Runtime架构变化"


      example:

        old:
          "50_RUNTIME"


        new:

          "40_AUTOMATION"

          children:

            - "11_ENGINES"

            - "12_SCHEDULER"


      required:

        - "创建新ADR"
        - "旧ADR标记Superseded"



  governance_rules_for_ai:


    when_reading_ADR:

      AI_should:

        - "先读取Status"
        - "检查Superseded关系"
        - "理解Decision Context"
        - "避免重新提出已解决问题"


    when_proposing_change:

      AI_must:

        - "判断是否影响架构"
        - "如果影响架构，建议ADR"
        - "不能直接修改Frozen原则"


    prohibited_behavior:

      - "为了简洁删除旧ADR"
      - "为了符合现状修改历史原因"
      - "忽略ADR演进链"


  required_actions:


    Reasonix:

      - action:
          "将本packet保存至"

        path:
          "80_HISTORY/PACKETS/"

        filename:
          "PAIOS-2026-0712-ADR-GOVERNANCE-001.md"



    Case-01 Maintainer:

      - action:
          "确认ADR目录包含生命周期状态管理"

      - action:
          "必要时新增ADR README说明"



    Future AI Engines:

      - action:
          "采用本packet作为ADR处理标准"



  final_statement:

    architecture_rule:

      >
      ADR不是为了证明过去永远正确，
      而是为了让未来知道系统为什么从过去走向现在。


    operational_rule:

      >
      修改架构时修改的是未来决策，
      不是删除过去事实。


    status:

      "ADR Governance Standard Established"
