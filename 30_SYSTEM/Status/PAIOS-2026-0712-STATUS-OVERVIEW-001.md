type: handoff_packet
id: PAIOS-2026-0712-STATUS-OVERVIEW-001
title: "PAIOS 全景状态：架构 / 实例 / 引擎"
generated_at: 2026-07-12T13:55:00+08:00
generated_by: Case-02 (Developer) / Reasonix
baseline: v1.1.0-pilot-baseline (ce72446)

packet:

  context:
    system: PAIOS Platform — Personal AI Operating System
    version: v1.0.1 (Architecture Frozen)
    phase: Phase B Stage 1 — Core/Workspace boundary established, physical split pending
    directory_model:
      00_CAPTURE: Information intake (Inbox)
      10_WORK: Active workspace (temporary)
      20_KNOWLEDGE: Verified knowledge base
      30_SYSTEM: System kernel (Governance, ADR, Principles)
      40_AUTOMATION: Automation engine (Registry, Scripts, Agents)
      50_DATA: Data infrastructure (runtime)
      60_HISTORY: Engineering history archive
      Fleet: Validation cases (gitignored, local only)
    lifecycle: Capture → Work → Knowledge → System/Automation → Archive

    instances:
      L1_Platform: PAIOS Core — git pull, read-only for non-maintainers
      L2_Instance: Per-user deployment, independent runtime
      L3_Manifest: FIM protocol — instance actively declares state
      L4_Fleet: Read-only aggregation, no write-back

    ai_engines:
      Reasonix: Primary coding engine (local, zero-cost, adapter active)
      WorkBuddy: Primary knowledge/daily engine (local, zero-cost, adapter active)
      ChatGPT: External API engine (cloud, cost 2.5, adapter not implemented)
      Collaboration: Adapter + handoff.yaml + Scheduler — verified Reasonix↔WorkBuddy bidirectional

  decision:
    - "Multi-Instance Architecture Baseline (ADR-0016): Four-Layer model adopted — Core / Instance / Manifest / Fleet"
    - "Three-Tier Role Model (ADR-0018): Case-01=Maintainer(merge gate), Case-02=Developer(feature branches only), Case-03=Pilot User(read-only Core)"
    - "Fleet Manifest Exchange (per ADR-0015/0017): Fleet does NOT go into Git. Uses independent channels: Quark Cloud Drive / Tailscale / LAN"
    - "Case-02 cannot merge into mainline, cannot modify baseline directly, cannot redefine architecture decisions"
    - "All development must happen in feature/* branches; maintainer reviews before merge"
    - "Platform Purity (ADR-0017): Workspace data stays out of Core repo"

  evidence:
    - adr_0002-0011: Foundation Layer — all Accepted (Automation, Directory, Knowledge, Workflow, Metadata, Lifecycle, Governance, Evolution, Decision)
    - adr_0012: Platform-Application Architecture — Accepted
    - adr_0016: Multi-Instance Architecture Baseline (4-layer) — Accepted
    - adr_0017: Platform Purity & Physical Separation — Accepted
    - adr_0018: Multi-Instance Role Model & One-Way Flow — Accepted
    - adr_0019: AI Engine Role Model — Accepted
    - adr_0013-0015: FIM / Upgrade / Federation — Proposed
    - case_001: First Real Multi-Instance Convergence — Validated (Major). Triggered ADR-0017+0018. Root cause: equal Developer permissions across all 3 instances
    - pilot_role_validation: Case-02 baseline synced to v1.1.0-pilot-baseline (ce72446), feature branch feature/case-02-dev created
    - handoff_experiment: Reasonix↔WorkBuddy bidirectional handoff validated at 100% context retention

  open_questions:
    - "Phase B physical split (git rm --cached) not yet executed — workspace files still tracked in Core repo"
    - "FleetExchange shared channel not yet configured — E:\FleetExchange\ directory created but Quark/Tailscale/LAN not set up"
    - "Case-03 (Pilot User / Kaoyan) not yet onboarded — no profile.yaml, no manifest"
    - "Windows Task Scheduler for daily fleet-push not yet configured — script ready but trigger not set"
    - "First fleet.md weekly report pending — requires all 3 instances generating manifests"
    - "Stage 1 exit criteria not met — needs 14 consecutive days stable running"
    - "ChatGPT adapter (codex-adapter) not implemented — ChatGPT cannot currently participate in Adapter-based handoff"
    - "Mirror struct for PAIOS 仍有待创建（之前由 ChatGPT 提到的设计建议）"

  required_action:
    - actor: Any AI reading this packet
      task: "Understand PAIOS current state before making changes. Respect governance rules: Case-02 may write feature branches but not merge, must not touch Fleet via Git."
    - actor: Case-02 (Developer / evan)
      task: "Configure Windows Task Scheduler to run fleet-push-case-02.bat daily"
      depends_on: "Script created ✅"
    - actor: Case-01 (Maintainer / feng) + Case-02
      task: "Set up FleetExchange shared channel (Quark Cloud Drive / Tailscale / LAN) so manifests can cross instances"
    - actor: Case-01 (Maintainer)
      task: "Review and approve Phase B physical split plan before Stage 2 execution"
      gate: "Pilot exit criteria: 14 days stable"
    - actor: Any AI (future)
      task: "When asked to 'generate a packet', use this structure: packet { context, decision, evidence, open_questions, required_action }"
