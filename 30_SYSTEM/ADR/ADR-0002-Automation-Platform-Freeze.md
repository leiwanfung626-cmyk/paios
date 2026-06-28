# ADR-0002: Automation Platform Freeze

**Status**: Active
**Date**: 2026-06-29
**Deciders**: PAIOS Platform Team
**Supersedes**: informal directory decisions before v1.0

## Context

The Automation Platform (40_AUTOMATION) had evolved through multiple
directory iterations.  To prevent "migration paralysis" — repeatedly
restructuring directories instead of migrating capability — a freeze
is needed.

## Decision

### Frozen (no changes without ADR)

1. 40_AUTOMATION first-level directory structure (00_REGISTRY–10_MANIFEST)
2. 00_REGISTRY schema (agents/capabilities/providers/scripts/workflows format)
3. 03_AGENTS YAML format (identity + capabilities + workflow + provider)
4. 10_MANIFEST schema (manifest + migration_status + inventory)
5. Registry ID format (CAP-NNNN, AGENT-NNNN, SCRIPT-NNNN, WF-NNNN)

### Allowed (no ADR needed)

1. Adding new capabilities, agents, scripts, providers, workflows
2. Updating migration_status.yaml with real progress
3. Adding README.md or documentation to any directory
4. Refactoring scripts as long as they still use config-based paths

### Thaw Conditions

Only the following justify modifying the frozen architecture:

1. **Unresolvable technical defect** — a bug that cannot be fixed
   within the current structure.
2. **Requirement cannot be met** — a new capability that cannot be
   implemented via Registry/Capability/Script/Workflow extension.
3. **Significant maintenance cost reduction** — the change would
   meaningfully reduce long-term maintenance cost, AND a new ADR
   has been written explaining the trade-off.

**It is never acceptable to thaw for "it would be more elegant."**

## Consequences

- Stable directory structure enables focused migration work.
- New assets are registered, not filed in ad-hoc locations.
- Future AI agents can trust the directory layout.

## 90-Day Rule

For the 90 days following this ADR, the architecture is frozen.
After 90 days (2026-09-29), evaluate whether thaw conditions are met.
