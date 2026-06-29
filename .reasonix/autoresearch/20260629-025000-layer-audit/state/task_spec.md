# Task Spec: PAIOS Layer Integrity Audit

## Goal
Audit the existing PAIOS filesystem against the Necessity-Gated Architecture Principle and Layer Integrity Map (L0-L4). Produce documented audit findings, apply layer metadata tags, and surface layer contamination without destructive changes.

## Scope
- Scan all documents under 30_SYSTEM/ (ADR, Governance, Engineering, Design_Notes, Evolution)
- Scan _candidates/
- Map each document to its correct layer (L0-L4)
- Identify layer contamination events
- Apply layer: tag in frontmatter where absent
- Create 30_SYSTEM/Engineering/Layer_Integrity_Map.md as formal document

## Success Criteria
- Layer_Integrity_Map.md created with standard layer definitions and audit results
- Every document under Engineering/ and _candidates/ has layer: tag in frontmatter
- Layer contamination events documented with file:line evidence
- No destructive changes (no moves, no deletes, no status downgrades)
- Verification: bash check confirms all layer tags present

## Non-Goals
- Do not move files between directories
- Do not delete or deprecate any document
- Do not modify ADR frontmatter (would require ADR-by-ADR audit)
- Do not modify Governance documents
- Do not modify Design_Notes

## Allowed Operations
- Read all files under 30_SYSTEM/
- Add layer: and layer_status: fields to frontmatter of Engineering/* and _candidates/* files
- Create new file: Layer_Integrity_Map.md
- Update Engineering/README.md with layer reference
