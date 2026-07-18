type: handoff_packet
id: PAIOS-2026-0712-DIRECTORY-AUDIT-001
title: "PAIOS 目录结构审查与边界收敛建议"
generated_at: 2026-07-12T14:30:00+08:00
generated_by: ChatGPT / External API
baseline: v1.0.1-architecture-frozen

packet:

  context:
    system: PAIOS Platform — Personal AI Operating System
    scope: Directory Architecture Review
    current_state:
      directory_model:
        core_layers: "00-90 numbered layers (10 layers)"
        auxiliary_layers:
          - docs/
          - scripts/
          - hidden engine configs (.reasonix/.workbuddy)
      total_structure:
        numbered_layers: 10
        auxiliary_dirs: true
    lifecycle_model:
      - Capture
      - Work
      - Knowledge
      - System
      - Automation
      - Data
      - External
      - Temporary
      - History
      - Archive

  assessment:
    overall_status: "Governance-ready, boundary convergence required"
    conclusion:
      - "目录编号体系已稳定"
      - "核心架构未发生破坏"
      - "当前主要问题由快速演化产生的边界模糊导致"
      - "下一阶段重点不是扩展，而是资产边界治理"

  confirmed_decisions:
    accepted:
      - decision: "50_RUNTIME 合并进入 40_AUTOMATION"
        rationale:
          - "Runtime 属于能力执行层，不属于数据层"
          - "Engine lifecycle 与 Scheduler 属于 Automation domain"

      - decision: "Fleet 归入 30_SYSTEM"
        rationale:
          - "Fleet 属于治理和实例联邦，不属于工作空间"

      - decision: "PAIOS-Usage 归入 30_SYSTEM"
        rationale:
          - "实例身份、Manifest、元信息属于系统状态"

      - decision: "Platform Purity Principle 持续有效"
        rule:
          - "Workspace 数据不得污染 Core"
          - "Runtime Artifact 不进入知识库"

  findings:

    finding_001:
      topic: "10_WORK 边界模糊"
      severity: medium
      evidence:
        - "项目文件"
        - "实验数据"
        - ".venv 虚拟环境"
        - "模型文件"
        - "输出文件"
        mixed together
      recommendation:
        - "短期保留，不删除"
        - "逐步将 Runtime Artifact 移出"
        - "项目结构标准化"

    finding_002:
      topic: "项目目录命名"
      severity: low
      conclusion:
        - "中文目录不是问题"
        - "问题在于缺少生命周期管理"
      future_structure:
        suggested:
          - "Active/"
          - "Projects/"
          - "Legacy/"

    finding_003:
      topic: "50_DATA 空目录"
      severity: low
      decision:
        - "保持为空"
        - "不因目录存在制造数据需求"
      future_candidates:
        - indexes
        - embeddings
        - databases
        - datasets

    finding_004:
      topic: "70_TMP 清理脚本"
      severity: low
      decision:
        - "暂不删除"
        - "等待归类"
      candidates:
        - "40_AUTOMATION/05_SCRIPTS"
        - "90_ARCHIVE/scripts"

    finding_005:
      topic: "原则 #6 层数描述冲突"
      severity: medium
      issue:
        old_statement: "冻结为7层"
        current_reality: "00-90十个编号层"
      resolution:
        - "不修改冻结架构"
        - "更新原则表述"

  proposed_adr:

    - id: ADR-0020
      title: "Directory Model Clarification"
      status: Proposed
      purpose:
        - "解释7层历史模型与当前10层模型关系"
        - "定义核心层与辅助目录边界"
      suggested_rule:
        - "PAIOS Core Workspace 使用固定编号层模型"
        - "辅助工程目录不计入核心层模型"

  required_actions:

    P1:
      - action: "保存本 packet"
        target:
          path: "80_HISTORY/PACKETS/"
        filename:
          "PAIOS-2026-0712-DIRECTORY-AUDIT-001.md"

      - action: "清理 10_WORK 下虚拟环境"
        scope:
          - ".venv"
          - "cache"
          - "temporary runtime files"

      - action: "确认当前 git branch"

      - action: "处理 476MB youtube webm 文件"
        decision_rule:
          reference_material:
            "20_KNOWLEDGE/References"
          temporary:
            "70_TMP/media"
          unnecessary:
            "delete"

    P2:
      - action: "评估 ADR-0020"
      - action: "建立 10_WORK 项目生命周期规范"
      - action: "定义 50_DATA 使用规则"
      - action: "继续 Phase B physical split"

  final_state:

    architecture:
      status: "Stable"
      risk:
        - "Workspace/Core boundary drift"

    priority:
      now:
        - "Boundary cleanup"
        - "Governance documentation"
      avoid:
        - "Adding new layers"
        - "Creating unnecessary modules"

  handoff_note:
    message: >
      PAIOS 已从快速建设阶段进入治理阶段。
      后续维护者应优先保持 Core、Workspace、Runtime、History 四类资产隔离，
      避免通过新增目录解决管理问题。
