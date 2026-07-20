# PAIOS

> **A governance-driven AI operating system platform.** Not a tool. Not a config. An OS for your AI life.

[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-Architecture%20Frozen-blue)](SYSTEM_VERSION.md)
[![Version](https://img.shields.io/badge/version-v1.0.1-orange)](CHANGELOG.md)
[![Tests](https://github.com/leiwanfung626-cmyk/paios/actions/workflows/test.yml/badge.svg)](https://github.com/leiwanfung626-cmyk/paios/actions/workflows/test.yml)

---

## Quick Start (30 seconds)

```bash
git clone git@github.com:leiwanfung626-cmyk/paios.git
cd paios/Core
python 40_AUTOMATION/05_SCRIPTS/paios_mcp_server.py stats
```

You should see:
```json
{
  "total_nodes": 90,
  "declared_edges": 98,
  "backlinks": 76,
  "supersedes": 1,
  "by_type": { "adr": 24, "reference": 15, "knowledge": 20, ... }
}
```

If you see `total_nodes`, PAIOS is running. You just queried a **live knowledge graph** of 90 interconnected documents.

---

## What is PAIOS?

PAIOS (Personal AI Operating System) treats your knowledge the way an OS treats files — through a **lifecycle, not a folder hierarchy.**

```
00_CAPTURE → 10_WORK → 20_KNOWLEDGE → 30_SYSTEM → 90_ARCHIVE
 (inbox)     (drafts)    (verified)     (rules)     (done)
```

Everything enters through Inbox. The system routes it through stages — draft, verify, codify, archive — instead of you manually organizing folders. **The directory IS the lifecycle.**

PAIOS is not a ChatGPT wrapper. It's not a prompt library. It's the **operating system** that AI tools (Claude, ChatGPT, Cursor, Codex, Reasonix, WorkBuddy) connect to as clients.

> **Tool Independence (Principle #8):** PAIOS is the platform. AI tools are the clients. Switch tools without rebuilding your assets.

---

## What can PAIOS do right now?

| Capability | Description | Status |
|-----------|-------------|--------|
| **Relationship Engine** | Bidirectional knowledge graph: 90 nodes, 98 edges, supersedes chain tracing | ✅ v0.1 |
| **MCP Server** | Query PAIOS from any AI tool: search, get module, relationships, stats — 5 tools | ✅ v0.1 |
| **Usage Tracker** | Record AI knowledge usage as runtime evidence for system evolution | ✅ v0.1 |
| **Fleet Model** | Multi-instance federation (Maintainer / Developer / Pilot User) | ✅ v0.1 |
| **ADR System** | 24 Architecture Decision Records with full traceability | ✅ |
| **AI Fleet Governance** | 3-layer AI operating model (roles → routing → structured communication) | ✅ v0.1 |
| **Scheduler** | Engine scheduling with fallback chains + capability mapping | ✅ v0.1 |

### Try it

```bash
# Search knowledge (BM25 + tag matching)
python 40_AUTOMATION/05_SCRIPTS/paios_mcp_server.py search "OpenWRT" --top-k 5

# Read a module (ADR-0017: Platform Purity Principle)
python 40_AUTOMATION/05_SCRIPTS/paios_mcp_server.py get-module ADR-0017

# See what references a node
python 40_AUTOMATION/05_SCRIPTS/paios_mcp_server.py relationships ADR-0017

# List all ADRs
python 40_AUTOMATION/05_SCRIPTS/paios_mcp_server.py list adr

# Build the relationship graph
python 40_AUTOMATION/05_SCRIPTS/relationship_engine.py build

# Run all tests
python 40_AUTOMATION/05_SCRIPTS/test_relationship_engine.py
python 40_AUTOMATION/05_SCRIPTS/test_usage_tracker.py
```

---

## Layer Model

| # | Layer | Directory | Purpose |
|---|-------|-----------|---------|
| 00 | **Capture** | `00_CAPTURE/` | All new input enters here. Think before you sort. |
| 10 | **Work** | `10_WORK/` | Active projects. Temporary by nature (Principle #3). |
| 20 | **Knowledge** | `20_KNOWLEDGE/` | Verified knowledge. Must pass validation (Principle #4). |
| 30 | **System** | `30_SYSTEM/` | Platform kernel: ADRs, governance, principles, specs. |
| 40 | **Automation** | `40_AUTOMATION/` | Scripts, agents, registry, scheduler, MCP server. |
| 50 | **Data** | `50_DATA/` | Data infrastructure (reserved). |
| 60 | **External** | `60_EXTERNAL/` | External references. |
| 70 | **TMP** | `70_TMP/` | Runtime temp files. Delete anytime. |
| 80 | **History** | `80_HISTORY/` | Engineering journal + release history. |
| 90 | **Archive** | `90_ARCHIVE/` | Completed tasks, no reuse value. |

---

## Core Principles

| # | Principle |
|---|-----------|
| 1 | Directories express lifecycle, not content |
| 2 | Everything has exactly one formal location |
| 3 | Workspace is always temporary |
| 8 | **Tool Independence** — platform ≠ AI client |
| 9 | **Bootstrap First** — AI loads governance before acting |
| 10 | **Immutable Originals** — never modify source files |

> Full list: [Principles](30_SYSTEM/Principles.md)

---

## Governance

PAIOS has a complete governance framework in `30_SYSTEM/Governance/`:

| Area | Description |
|------|-------------|
| **ADR** | 24 Architecture Decision Records with full traceability (Evidence → Implements → Frozen By → Supersedes) |
| **Architecture Lifecycle** | 10-phase closed loop: Evidence → Case → ADR → Blueprint → Freeze → Boundary → Pilot → Rollout → Validate → Retrospective |
| **Change Control** | L0-L4 impact levels + freeze policy + evidence gates |
| **AI Operating Model** | 6 AI roles, 7-step standard routing flow, Context Packet v1.0 |
| **Multi-Instance** | 3 roles (Maintainer / Developer / Pilot User), one-way data flow |
| **Pilot Gate** | Entry/Exit criteria with 14-day stability requirement |

> [ADR Index](30_SYSTEM/ADR/ADR-INDEX.md) — [Governance docs](30_SYSTEM/Governance/) — [Documentation](docs/)

---

## Automation Scripts

| Script | Description |
|--------|-------------|
| `relationship_engine.py` | Bidirectional knowledge graph builder (build → query → DOT export) |
| `paios_mcp_server.py` | MCP server exposing PAIOS to any AI tool (5 tools, stdio transport) |
| `usage_tracker.py` | Runtime knowledge usage trace pipeline |
| `collect_manifest.py` | Federated Instance Manifest collector |
| `classify_files.py` | Auto-classifier for incoming files |
| `fim_validator.py` | FIM protocol validator |
| `capture.py` | Unified capture pipeline |
| `asset_store.py` | Asset ingestion helper |

---

## Architecture

PAIOS supports multi-instance federation (ADR-0016~0018):

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Case-01    │     │  Case-02    │     │  Case-03    │
│  Maintainer │     │  Developer  │     │  Pilot User  │
│  (read/write)│    │  (fork+PR)  │     │  (read-only) │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
                    ┌──────────────┐
                    │   Fleet/     │
                    │  (Federation)│
                    └──────────────┘
```

---

## License

MIT License © 2026 PAIOS Platform Contributors. See [LICENSE](LICENSE).

Built with AI tools (Reasonix, WorkBuddy, ChatGPT, Claude). PAIOS is the platform — AI tools are the clients.
