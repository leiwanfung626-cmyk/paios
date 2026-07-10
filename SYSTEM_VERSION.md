# SYSTEM_VERSION

## PAIOS Platform Final v1.0 — Architecture Freeze

| Field | Value |
|-------|-------|
| System | PAIOS Platform |
| Version | 1.0.1 |
| Schema Version | 1.0 |
| Metadata Version | 1.0 |
| Config Version | 1.0 |
| Template Version | 1.0 |
| Created | 2026-06-28T14:33:16Z |
| Workspace | ${PAIOS_DRIVE}:/PAIOS |
| Tools | ${PAIOS_DRIVE}:/Tools |
| Architecture | Frozen |

This architecture is frozen. Any modification to the top-level directory
structure requires meeting at least two of the following criteria:
1. 3+ months of continuous use
2. Two or more real projects exposing the same structural issue
3. Clear benefit with acceptable migration cost

> **v1.0.1 (2026-07-10)**: **Architecture + Release Management.** PAIOS 第一次拥有了完整的版本治理：
>   - ADR-0012~0016 构成 Platform Evolution 专题（平台化 → 多实例架构冻结）
>   - Release 机制（CHANGELOG / RELEASE / Upgrade Notice / Manifest）
>   - 标志 PAIOS 从"一个项目"进入"一个可以持续发布的软件"
>   - Non-breaking feature addition; no top-level structure change; compliant with freeze policy.