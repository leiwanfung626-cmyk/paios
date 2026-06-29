{
  "task_id": "20260629-235000-knowledge-confidence-model",
  "goal": "Implement Knowledge Confidence Model for PAIOS: add verification metadata to Reference entries, distinguish source claims from verified practices, and establish evidence_chain tracking.",
  "scope": [
    "Update Reference _template.md with verification fields",
    "Update REF-0001 (CodeTrust) as first compliant entry",
    "Improve content quality per clipboard analysis"
  ],
  "non_goals": [
    "Do NOT implement L3 Vector RAG",
    "Do NOT promote rag_prototype.py",
    "Do NOT modify Registry or ADR"
  ],
  "allowed_operations": ["read_file", "write_file", "edit_file", "grep", "ls"],
  "success_criteria": [
    "SC-1: _template.md has verification section (source_type, verified, last_verified, evidence_chain)",
    "SC-2: REF-0001 has verification section with source_type=video, verified=false",
    "SC-3: REF-0001 content distinguishes video claims from verified facts",
    "SC-4: REF-0001 content includes WHY hallucinations, concrete rule examples, scoring clarification, flowchart, limitations"
  ],
  "verification_gates": [
    "grep verification in _template.md",
    "grep source_type in REF-0001",
    "grep 验证状态 in REF-0001"
  ],
  "created": "2026-06-29T23:50:00Z"
}
