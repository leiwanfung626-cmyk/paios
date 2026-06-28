# 40_AUTOMATION — PAIOS Automation Platform

> **Purpose**: AI automation engine — agents, capabilities, scripts, and MCP
> **Architecture**: Frozen per ADR-0002

## Structure

| Directory | Purpose |
|-----------|---------|
| 00_REGISTRY | Central registry of all automation assets |
| 01_CAPABILITIES | Atomic, reusable capabilities |
| 02_PROMPTS | Prompt templates by role |
| 03_AGENTS | Agent definitions (capability combinations) |
| 04_MCP | MCP server configurations |
| 05_SCRIPTS | Operational scripts (by business domain) |
| 06_PROVIDERS | Model/API provider configurations |
| 07_WORKFLOWS | Multi-agent workflows |
| 08_TESTS | Automation tests |
| 09_LEGACY | Historical assets from H: drive (read-only) |
| 10_MANIFEST | Automation platform metadata |

## Rules

- All assets must be registered in 00_REGISTRY
- Capabilities must not reference disk paths
- Scripts must use config-based paths
- **All assets are tool-agnostic**. AI tools discover capabilities
  through the Registry, not through hardcoded paths or tool-specific
  configurations.
