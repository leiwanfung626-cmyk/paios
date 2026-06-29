# Goal: Complete PAIOS Theory Migration

## Background
PAIOS has completed "name migration" (DRS code removed) but not "theory migration" (design philosophy not yet documented). The user's analysis in [已粘贴文本 #3 · 243 行] called for creating a formal design philosophy hierarchy.

## Scope
- Create `30_SYSTEM/Vision/paios-philosophy.md` — First Principles (Why)
- Create `30_SYSTEM/Design_Notes/ai-capability-architecture.md` — AI Capability Architecture (How)
- Do NOT modify any operational files (rag.yaml, capabilities.yaml, scripts.yaml, etc.)
- Do NOT write to AI memory

## Non-Goals
- Creating Memory/Decision/Workflow Engine Design Notes (future scope)
- Modifying existing files under 30_SYSTEM or 40_AUTOMATION
- Writing to AI system memory

## Success Criteria
- [x] paios-philosophy.md exists with 5 sections: 不是什么/是什么/为什么变聪明/为什么不是训练模型/最高原则
- [x] ai-capability-architecture.md exists with: 四层能力模型/五层数据价值体系/三大引擎定义/DRS演化映射
- [x] No operational files modified
- [x] Document cross-references established
