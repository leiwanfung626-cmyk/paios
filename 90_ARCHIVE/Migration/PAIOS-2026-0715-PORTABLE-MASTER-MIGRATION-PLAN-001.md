# PAIOS Portable Master Migration Plan v1.0

> **Packet ID**: PAIOS-2026-0715-PORTABLE-MASTER-MIGRATION-PLAN-001
> **Status**: Active (Phase 1 completed)
> **Date**: 2026-07-15
> **Architecture Reference**: ADR-0020 (Portability Principle), Instance-Consolidation-Principle (ADR-0021 candidate)

---

## 背景

PAIOS 当前有两个运行实例，分别部署在不同电脑上：

| 实例 | 电脑 | 位置 | Git 分支 | 场景 |
|------|------|------|----------|------|
| Case-01 (DEV) | feng | F:\PAIOS | pilot | 平台维护、开发工作、工作流验证 |
| Case-02 (WORK) | evan | G:\2in1\PAIOS | feature/case-02-dev | 个人知识管理、照片整理、工作项目 |

两者通过同一个 GitHub 仓库 `github.com:leiwanfung626-cmyk/paios.git` 同步系统层，但本地资产（10_WORK、20_KNOWLEDGE/Personal、00_CAPTURE 等）各自独立积累。

**驱动因素**：一台便携 SSD 主实例 = 插到哪台电脑都能继续工作，同时消除双实例未来可能出现的合并成本。

---

## 目标架构

```
现状：                             目标：

Case-01 (feng)     Case-02 (evan)       PAIOS-PORTABLE（三层架构）
    │                   │                  │
    │                   │                  ├── Core/       ← 系统本体 (git)
    │                   │                  ├── ASSETS/     ← 大文件资产
    │                   │                  └── INDEX/      ← AI 索引
    └─────── 审计 + 合并 ────────┘
                   │
                   ↓
           Portable Master Instance
                   │
         ┌─────────┴──────────┐
         ▼                    ▼
     PC-A (feng)          PC-B (evan)
     SSD 即插即用          SSD 即插即用
```

**核心原则**：
- 不绑定硬件 — Core/ASSETS/INDEX 三层在任意盘根目录平级
- Identity 与 Runtime 分离 — 系统在 Core 中，运行环境在宿主机
- 路径协议化 — 使用 `$PAIOS_ROOT` / `$PAIOS_ASSET_ROOT`，永不出现硬编码盘符

---

## 迁移状态机

```
INIT → AUDITED → CONVERGED → GOVERNED → STABLE → REFACTORED → COMPLETED
```

每个 Phase 对应一个状态转换，下一 Phase 从上一状态继续。

---

## Phase 1 — Init（骨架建立）✓ 已完成

| 步骤 | 状态 | 说明 |
|------|------|------|
| 创建目录结构 | ✅ | H:\PAIOS-PORTABLE\ 含 Core/ ASSETS/ INDEX/ |
| Git clone | ✅ | 完整 51 commits，origin SSH |
| 创建分支 | ✅ | portable-master（从 master 分出） |
| 路径协议 | ✅ | paths.yaml v2，引入 $PAIOS_ROOT / $PAIOS_ASSET_ROOT |
| 迁移状态机 | ✅ | migration-20260715.yaml，状态 INIT→AUDITED |
| Packet 文档 | ✅ | 本文件 |

---

## Phase 2 — Converge（逻辑合并）

**目标**：将双实例资产合并到 portable-master，文件层收敛。

### 步骤

1. **Git 历史合并**：
   - 从 F:\PAIOS 的 `pilot` 分支拉取 15 commits → merge 到 `portable-master`
   - 从 G:\2in1\PAIOS 的 `feature/case-02-dev` 分支拉取内容 → merge 到 `portable-master`
   - 确保 git 历史完整可追溯

2. **系统层验证**（30_SYSTEM / 40_AUTOMATION）：
   - 通过 git 已统一，仅验证一致性
   - 检查是否有仅存在于某一实例的本地配置差异

3. **知识层合并**（20_KNOWLEDGE）：
   - 从 F:\PAIOS 和 G:\2in1\PAIOS 分别复制到 `Core/20_KNOWLEDGE/`
   - 同名冲突标 `MERGE_REVIEW`，不覆盖
   - 核心资产（ADR/Principle/SOP）保留来源标记
   - 普通知识靠 MERGE-LOG 追溯

4. **工作层迁移**（10_WORK）：
   - Active 项目 → `Core/10_WORK/Active/`
   - Done / Review / Waiting → 评估后入 Archive

5. **历史层合并**（90_ARCHIVE / 80_HISTORY / 60_HISTORY）：
   - 合并双方归档，保留来源标记

### 产出
- `MERGE-LOG-001.md` — 所有合并决策记录
- `migration-20260715.yaml` 状态 → `CONVERGED`

---

## Phase 3 — Governance（资产治理）

**目标**：只评审不改代码，输出决策清单备用。

### 资产决策矩阵

| 决策 | 条件 | 处理 |
|------|------|------|
| **Keep** | 当前使用 + 符合架构 | 直接保留 |
| **Merge** | 多实例重复解决同一问题 | 合并为单一资产 |
| **Refactor** | 有价值但设计过时（硬编码等） | 标记，Phase 5 执行 |
| **Archive** | 已完成的历史项目 | 移入 90_ARCHIVE |
| **Deprecate** | 无价值实验文件 | 留废弃说明，删除 |

### 产出
- `merge-gap-analysis.md` — 差异清单
- `environment-gap-analysis.md` — 环境差异
- `30_SYSTEM/governance/asset-review.yaml` — YAML 决策数据库

---

## Phase 4 — Stabilize（稳定验证）

**目标**：功能冻结，≥7天真实工作验证。

### 验证清单
- [ ] git 完整（portable-master 分支）
- [ ] 20_KNOWLEDGE 双实例知识可读无丢失
- [ ] 10_WORK Active 项目正常
- [ ] health_check.py 通过
- [ ] AI 引擎加载治理信息正常
- [ ] 日常 Capture → Work → Knowledge 流程可跑通

### Bug 分级规则

| 等级 | 定义 | 处理 |
|------|------|------|
| **P0** | 无法工作（脚本报错/路径错误/流程中断） | 允许修复 |
| **P1** | 影响效率但不阻塞 | 记录，不立即改 |
| **P2** | 优化需求 | 进 Phase 5 backlog |

---

## Phase 5 — Refactor（重构阶段）

**目标**：执行 Phase 3 产出的治理决策，自动化绞杀者重构。

### 自动化重构
- 旧脚本原地不动，新增统一 CLI 入口（`paios audit / manifest / health`）
- 旧脚本添加委托包装器，保持向后兼容
- 旧脚本移入 `40_AUTOMATION/09_LEGACY/`

### 新目录布局
```
40_AUTOMATION/
├── cli/          ← 统一入口
├── modules/      ← 模块化能力
└── 09_LEGACY/    ← 旧脚本（仍可单独调用）
```

### 其他清理
- 硬编码盘符替换为 `$PAIOS_ROOT` / `$PAIOS_ASSET_ROOT`
- 规则清理：删除过时约束，更新 SOP 路径引用
- 更新 MANIFEST.json 和 Identity.md 的路径声明

---

## Phase 6 — Identity Upgrade（身份升级 + 分发）

**目标**：验证通过后正式升级身份，复制到 SSD。

### Identity 内容
```yaml
identity:
  id: PAIOS-PORTABLE-001
  lineage:
    source_instances:
      - id: CASE-01-WORK    computer: feng  path: F:/PAIOS
      - id: CASE-02-PERSONAL computer: evan path: G:/2in1/PAIOS
  migration:
    type: instance_consolidation
    date: 2026-07-15
    packet: PAIOS-2026-0715-PORTABLE-MASTER-MIGRATION-PLAN-001
```

### 分发
- `migration-20260715.yaml` 状态 → `COMPLETED`
- 整盘 `H:\PAIOS-PORTABLE\` 复制到 SSD
- 原 F:\PAIOS 和 G:\2in1\PAIOS 降级为只读备份（保留 30 天）
- 发布变更记录到 CHANGELOG.md

---

## 架构原则符合性

| 原则 | 符合情况 |
|------|---------|
| Need Driven Promotion | ✅ 双实例真实需求驱动 |
| Platform Purity | ✅ Core / ASSETS / INDEX 物理分离 |
| Evidence-based Evolution | ✅ Phase 4 用 ≥7 天真实使用作为验收证据 |
| Tool Independence | ✅ $PAIOS_ROOT 路径协议，不绑定工具 |
| Migration ≠ Refactor | ✅ Phase 2-4 冻结功能，Phase 5 才重构 |
| Identity 与 Runtime 分离 | ✅ Identity 在 Core 中，Runtime 在宿主机配置 |
| Backward Compatibility | ✅ 旧 CLI 包装委托，不破坏现有 SOP |
| Lineage Preservation | ✅ Identity 保留 source_instances 谱系 |

---

## CHANGELOG

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-07-15 | v1.0 | 初始版本，Packet 文档成立 |
