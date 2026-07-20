# PAIOS

> **Personal AI Operating System** — a governance-driven platform for building your own AI operating system.

[![MIT License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Architecture](https://img.shields.io/badge/architecture-frozen-blue)](30_SYSTEM/ADR/ADR-0002-Automation-Platform-Freeze.md)
[![Version](https://img.shields.io/badge/version-1.0.1-blue)](SYSTEM_VERSION.md)
[![CI](https://github.com/leiwanfung626-cmyk/paios/actions/workflows/test.yml/badge.svg)](https://github.com/leiwanfung626-cmyk/paios/actions/workflows/test.yml)

---

## Quick Start

```bash
git clone git@github.com:leiwanfung626-cmyk/paios.git
cd paios/Core
python 40_AUTOMATION/05_SCRIPTS/paios_mcp_server.py stats
```

See `"total_nodes": 91`? You're connected to the PAIOS knowledge graph.

To explore what's inside:

```bash
# Search the knowledge base
python 40_AUTOMATION/05_SCRIPTS/paios_mcp_server.py search "architecture" --top-k 5

# Read a specific module (e.g. ADR on Platform Purity)
python 40_AUTOMATION/05_SCRIPTS/paios_mcp_server.py get-module ADR-0017

# See who references whom
python 40_AUTOMATION/05_SCRIPTS/paios_mcp_server.py relationships ADR-0017

# List all Architecture Decision Records
python 40_AUTOMATION/05_SCRIPTS/paios_mcp_server.py list adr
```

**Prerequisites:** Python >= 3.10. No pip install needed — pure stdlib.

---

## What is PAIOS?

PAIOS is not an AI tool. It is a **platform** that treats AI tools (Claude, ChatGPT, Codex, etc.) as interchangeable clients, and your knowledge as the permanent asset.

Think of it as the operating system layer between your raw data and whatever AI you choose to work with:

```
AI Tools (clients)  ← interchangeable
     │
PAIOS (platform)    ← governance + knowledge graph + automation
     │
Your Data           ← the permanent asset
```

### How it works

PAIOS organizes everything through a **lifecycle pipeline**:

```
Capture → Work → Knowledge → System → Archive
```

- **Capture** — every new piece of information enters through a single Inbox
- **Work** — active projects live in a temporary workspace
- **Knowledge** — validated content gets promoted to the permanent knowledge base
- **System** — rules, ADRs, and governance form the platform kernel
- **Archive** — completed or deprecated work gets archived

The platform doesn't tell you what to think. It just ensures that every decision, reference, and relationship is traceable.

### Core Principles

1. **Everything has exactly one formal location** — no duplicates, no ambiguity
2. **Workspace is always temporary** — projects come and go; the platform persists
3. **Knowledge must be validated** — raw information goes through verification before entering the knowledge base
4. **Tool independence** — PAIOS is the platform; AI tools are clients. Swap tools without rebuilding assets.
5. **Metadata is the primary classification system** — tags and frontmatter, not folder hierarchy, organize content

[All 10 principles →](30_SYSTEM/Principles.md)

---

## What can PAIOS do right now?

### Relationship Engine

A bidirectional knowledge graph built from your existing Markdown files. 91 nodes, 98 declared edges, 76 backlinks — all auto-generated from `related:` fields.

```bash
python 40_AUTOMATION/05_SCRIPTS/relationship_engine.py stats
# Nodes: 91 | Declared edges: 98 | Backlinks: 76 | Supersedes: 1
```

Tolerates 4 different frontmatter formats, auto-generates reverse edges, and records all broken links for manual repair.

### MCP Server

Exposes the knowledge graph to any AI tool via the Model Context Protocol. 5 tools:

| Tool | What it does |
|------|-------------|
| `paios_search_knowledge` | BM25 + tag search across the entire knowledge base |
| `paios_get_module` | Fetch full content of any module (with body) |
| `paios_get_relationships` | Show inbound + outbound edges, including supersedes chains |
| `paios_list_modules` | List all modules by type (adr, reference, concept, etc.) |
| `paios_get_stats` | Knowledge base stats: nodes, edges, orphans, unresolved refs |

### Usage Tracker

Records how AI tools actually use your knowledge, building a runtime evidence loop:

```bash
python 40_AUTOMATION/05_SCRIPTS/usage_tracker.py record \
  --session SESSION-001 --task "architecture review" \
  --actor Reasonix --action retrieve \
  --assets "ADR-0017,adr"
```

Traces last 90 days, then reviewed for promotion into permanent knowledge.

### Architecture Decision Records

24 ADRs documenting every architectural decision — from directory structure to multi-instance federation. Includes supersedes chains, decision traceability, and evidence levels.

```bash
python 40_AUTOMATION/05_SCRIPTS/relationship_engine.py backlinks ADR-0017
```

### Multi-Instance Federation

Designed for multiple PAIOS instances (work, personal, study) sharing a common Core platform while keeping Workspace data isolated. Maintainer push → users pull → Manifest reports back.

---

## Layer Model

| Layer | Directory | Purpose |
|-------|-----------|---------|
| Capture | `00_CAPTURE/` | Single inbox for all incoming information |
| Work | `10_WORK/` | Active workspace — temporary project area |
| Knowledge | `20_KNOWLEDGE/` | Permanent knowledge base — validated content |
| System | `30_SYSTEM/` | Platform kernel — ADRs, governance, principles, SOPs |
| Automation | `40_AUTOMATION/` | Scripts, agents, registry, scheduler, MCP server |
| Data | `50_DATA/` | Local data infrastructure (gitignored) |
| External | `60_EXTERNAL/` | External references, read-only |
| TMP | `70_TMP/` | Runtime temporary files |
| History | `80_HISTORY/` | Engineering journal, release history |
| Archive | `90_ARCHIVE/` | Historical archive |

---

## Governance

PAIOS has a formal governance framework. All changes are tracked through:

- **Architecture Lifecycle** — 10-stage pipeline from Evidence to Retrospective
- **Change Control** — L1/L2/L3 impact classification with freeze policy
- **Decision Traceability** — Every ADR links to its evidence, implementation, and superseded predecessors
- **AI Fleet Model** — 6 AI roles (Architect, Developer, Executor, Architecture Reviewer, Code Reviewer, Auditor) with a 7-step standard flow
- **Pilot Gate** — Entry/exit criteria for production rollout

Key documents:
- [ADR Index](30_SYSTEM/ADR/ADR-INDEX.md) — all 24 decisions
- [Architecture Lifecycle](30_SYSTEM/Governance/Architecture-Lifecycle.md)
- [AI Operating Model](30_SYSTEM/Governance/AI-Operating-Model.md)

---

## Contributing

PAIOS uses a multi-instance role model. Before contributing, read:

- [Operating Model](30_SYSTEM/Governance/Operating-Model.md) — roles and data flow
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution guide
- All architectural changes must follow the [Architecture Lifecycle](30_SYSTEM/Governance/Architecture-Lifecycle.md)

---

## License

MIT — see [LICENSE](LICENSE).
