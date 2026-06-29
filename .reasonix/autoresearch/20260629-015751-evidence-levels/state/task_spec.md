# Task Spec: Evidence Level System

## Goal
Formalize the unified evidence level system for PAIOS documentation, extending "validated-by-engineering-practice" into a complete 5-level hierarchy that applies across all document types.

## Scope
- Create `30_SYSTEM/Engineering/Evidence_Level_System.md` — full definition with levels, criteria, metadata schema
- Create `30_SYSTEM/Engineering/README.md` — directory index
- Update `30_SYSTEM/Engineering/Requirement_Emergence.md` frontmatter to use the full evidence metadata format
- Map all existing document types to their evidence levels in a reference table

## Success Criteria
- Evidence_Level_System.md written (≥60 lines, all 5 levels defined, metadata schema, mapping table)
- Engineering/README.md written
- Requirement_Emergence.md frontmatter updated with new fields (First Observed, Validated By, Related ADR)
- Verification: bash check confirms all files exist and key sections are present

## Non-Goals
- Do not modify Principles.md (too risky for a single pass)
- Do not modify ADR frontmatter (would require ADR-by-ADR audit)
- Do not modify Vision/ or Governance/ frontmatter
