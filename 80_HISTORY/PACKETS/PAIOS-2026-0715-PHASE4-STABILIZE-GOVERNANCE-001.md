type: PAIOS_HANDOVER_PACKET

id: PAIOS-2026-0715-PHASE4-STABILIZE-GOVERNANCE-001

from:
  engine: ChatGPT
  role: architecture_governance

to:
  - WorkBuddy
  - Reasonix

status:
  approved: true
  phase: Phase-4 Stabilize

---

context:

system:
  name: PAIOS-PORTABLE
  identity: PAIOS-PORTABLE-001 (pending Phase-6 activation)
  branch: portable-master

migration_state:

  completed:
    - Phase-1 Init
    - Phase-2 Converge
    - Phase-2.5 Freeze Check
    - Phase-3 Governance

  current:
    phase: Phase-4 Stabilize
    state: GOVERNED -> STABLE

  next:
    - Phase-5 Refactor
    - Phase-6 Identity Upgrade


architecture:

location:
  root: <dynamic>/PAIOS-PORTABLE/Core

layers:

  Core:
    contains:
      - 00_CAPTURE
      - 10_WORK
      - 20_KNOWLEDGE
      - 30_SYSTEM
      - 40_AUTOMATION
      - 90_ARCHIVE

  ASSETS:
    purpose:
      - large files
      - external assets

  INDEX:
    purpose:
      - AI metadata
      - face-index
      - derived indexes


migration_history:

source_instances:

  - id: CASE-01
    role: DEV
    path: F:/PAIOS

  - id: CASE-02
    role: WORK/PERSONAL
    path: G:/2in1/PAIOS

  - id: CASE-03
    role: STUDY
    status:
      not_merged_as_instance: true
      future_action: Phase-5/6 evaluation


---

phase4_rules:

title:
  "Stabilize before Refactor"

core_principle:

  "Phase-4 的目标不是优化系统，而是证明迁移后的 Master 可以稳定工作"


allowed:

  - use PAIOS-PORTABLE as daily working system
  - create new projects
  - use Capture -> Work -> Knowledge workflow
  - add valuable knowledge into 20_KNOWLEDGE
  - run existing automation scripts
  - use AI engines
  - use Reasonix/WorkBuddy handover workflow
  - discover issues
  - record feedback
  - fix P0 blocking bugs


forbidden:

  - architecture redesign
  - directory restructuring
  - CLI rewrite
  - deleting old scripts
  - replacing SOP
  - modifying governance rules
  - cleaning knowledge base
  - merging Case-03
  - implementing Runtime Bootstrap
  - creating permanent AI context system


---

issue_handling:

severity:

  P0:
    definition:
      system unusable
    action:
      allow_fix_immediately

  P1:
    definition:
      affects efficiency but not blocking
    action:
      record_only

  P2:
    definition:
      improvement idea
    action:
      move_to_Phase5_backlog


---

daily_workflow:

startup:

  step1:
    identify_runtime:
      check:
        - current machine
        - PAIOS_ROOT
        - branch
        - migration state

  step2:
    read:
      - Today.md
      - stabilization-log
      - approved handover packets

  step3:
    confirm:
      phase: Phase-4 Stabilize
      mode:
        - no_refactor
        - evidence_collection


work:

  workflow:

    Capture:
      location:
        - 00_CAPTURE

    Work:
      location:
        - 10_WORK/Active

    Knowledge:
      location:
        - 20_KNOWLEDGE


end_of_day:

  update:

    file:
      30_SYSTEM/validation/stabilization-log-20260715.md

    record:

      - date
      - completed_work
      - problems
      - stability_status


---

runtime_context_issue:

observed:

  problem:
    "AI启动时无法自动感知当前PAIOS实例、阶段、治理规则"

  evidence:

    - WorkBuddy需要人工加载上下文
    - PAIOS_RUNTIME_BRIEF尚不存在
    - Runtime Bootstrap属于Phase-5


decision:

  current:
    manual_context_injection

  future:
    Phase-5 Runtime Bootstrap design


---

multi_agent_rules:

Reasonix:

  role:
    architecture_review
    governance_analysis
    migration_consultation


WorkBuddy:

  role:
    daily_execution
    project_work
    knowledge_processing


handover_protocol:

  directory:
    .paios/context_handover/

  lifecycle:

    pending:
      new message

    approved:
      execute

    archive:
      completed


rule:

  "交接协议可以使用，但不升级为正式系统架构"


---

case03_policy:

current:

  Case-03:
    status:
      independent_instance

future:

  evaluate:
    - identity
    - lineage
    - knowledge ownership

do_not:

  - directly merge
  - copy blindly


---

acceptance:

Phase-4 completion requires:

minimum:

  - real usage period
  - Capture->Work->Knowledge completed
  - no P0 failure
  - AI collaboration usable

after_validation:

  transition:

    GOVERNED
      ->
    STABLE

then:

  start Phase-5 Refactor


---

final_instruction:

"当前阶段唯一任务：
使用 PAIOS-PORTABLE，收集真实运行证据。

不要让优化冲动破坏验证窗口。

所有改进想法：
记录 -> Backlog -> Phase-5处理。"
