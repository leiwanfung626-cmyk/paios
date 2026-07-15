# FIM v1 Specification — Federated Instance Manifest

> **Status**: Draft (v1, 2026-07-10)
> **Supersedes**: informal manifest schema in `collect_manifest.py` and ADR-0013
> **Applies to**: All PAIOS instances that publish or consume Instance State

---

## 1. Purpose

FIM is a **zero-intrusion, pull-based protocol** by which a PAIOS instance
declares its identity, capability, health, and asset state — **never its
content** — so that a Fleet aggregator can observe the instance without
touching the Workspace.

Any system that outputs a valid FIM manifest (Growth OS, Photo OS, Study OS)
can be observed by the same Fleet Aggregator **without modifying the aggregator**.

---

## 2. Protocol Layer (7-layer OSI analogy)

```
PAIOS Core
    │
    ├── L1 Platform (PAIOS Core)
    ├── L2 Instance (deployed PAIOS)
    ├── L3 Manifest ← FIM (this specification)
    └── L4 Fleet (aggregation / viewing)
```

---

## 3. Transport

Manifest is produced as a **local file** at:

```
30_SYSTEM/PAIOS-Usage/manifest.yaml
```

**Only this file ever leaves the instance** — and only when the user
actively shares it (git push / copy / shared drive). Aggregator **pull**
is the only reading model; no push, no event bus, no API.

---

## 4. Schema

### 4.1 Root

```yaml
manifest_version: 1          # required, integer, must be first line

instance:                    # required
  id: "case-01"              # string: semantic ID from profile, else UUID
  version: "v1.0.1"          # string: core_version from SYSTEM_VERSION.md
  profile:                   # required
    primary: work            # string: work | personal | study
    secondary: []            # list of strings, may be empty
  owner: "user-a"            # optional string
  privacy: share             # optional: share | private

usage:                       # required, system health
  last_active: 2026-07-10    # date, last git commit date
  active_days_30d: 8         # integer, distinct days with git activity in last 30
  git_commits_total: 18      # integer, total git commits in repo

features:                    # required, capability adoption
  capture: true              # boolean: 00_CAPTURE exists
  knowledge: true            # boolean: 20_KNOWLEDGE exists
  automation: true           # boolean: 40_AUTOMATION/05_SCRIPTS has .py files
  git: true                  # boolean: .git exists
  photo: false               # boolean: Photo-OS/ directory or feature-photo marker
  growth: false              # boolean: 20_KNOWLEDGE/Concepts/Growth-OS-*.md exists
  review: false              # boolean: 40_AUDIT has .md files

assets:                      # required, asset growth (counts, not content)
  references: 11             # integer, non-index .md files in 20_KNOWLEDGE/References
  concepts: 3                # integer, non-index .md files in 20_KNOWLEDGE/Concepts
  decisions: 3               # integer, non-index .md files in 20_KNOWLEDGE/Decisions
  models: 2                  # integer, non-index .md files in 20_KNOWLEDGE/Models
  methods: 2                 # integer, non-index .md files in 20_KNOWLEDGE/Methods
  sops: 2                    # integer, non-index .md files in 20_KNOWLEDGE/SOP
  projects: 2                # integer, active project directories in 10_WORK/Active

projects:                    # optional, active project list
  - id: KAOYAN-2026          # slug, uppercase, max 16 chars
    name: Kaoyan-2026        # display name
    status: archived         # string: active | archived

evidence:                    # optional, ADR governance state
  - object: ADR-0012         # ADR identifier
    level: Accepted          # string: Accepted | Active | Proposed

feedback:                    # optional, user pain points (future use)
  pain_points: []            # list of strings, empty until reported
```

### 4.2 Field Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | UTF-8 text | `"case-01"` |
| `integer` | JSON number, no decimal | `11` |
| `boolean` | `true` or `false` | `true` |
| `date` | ISO 8601 date | `2026-07-10` |
| `list` | YAML list | `- office` |

### 4.3 Required vs Optional

- **Required**: `manifest_version`, `instance` (id, version, profile), `usage`, `features`, `assets`
- **Optional**: `instance.owner`, `instance.privacy`, `projects`, `evidence`, `feedback`

Aggregator MUST handle missing optional fields gracefully — they default
to the zero value of their type (empty list, empty string, `false`).

---

## 5. Version Compatibility

| FIM Version | First PAIOS Core | Status |
|-------------|------------------|--------|
| v1 | v1.0.1 | Current |

Aggregator MUST `switch(manifest_version)` to handle schema evolution.
A future v2 manifest fields MUST NOT break an aggregator that only
understands v1 — it ignores unknown top-level keys.

---

## 6. Implementation Contract

Any component implementing FIM v1 MUST:

1. Output a YAML file matching the schema in §4
2. Read only existing files and directories (`Observe, Don't Own`)
3. Never read user content (body of .md files, photo binary data)
4. Never write to Workspace directories outside `PAIOS-Usage/`
5. Never push or transmit data over a network

---

## 7. Extension

FIM is **not PAIOS-specific**. A Growth OS manifest or Photo OS manifest
that outputs the same schema can be consumed by the same Fleet Aggregator.

To add a new `feature` flag:
1. Add the boolean to `get_features()` in `collect_manifest.py`
2. Update §4.1 feature list in this spec
3. Bump `manifest_version` only if the change breaks backward compatibility

---

## 8. Related

- ADR-0013: Federated Instance Manifest
- ADR-0015: Federated Aggregation & Viewing
- ADR-0016: Multi-Instance Architecture Baseline
- `40_AUTOMATION/05_SCRIPTS/collect_manifest.py` — reference implementation
