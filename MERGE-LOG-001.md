# MERGE-LOG-001 — PAIOS Portable Master 双实例合并记录

> **迁移 ID**: MIG-2026-0715-001
> **日期**: 2026-07-15
> **执行阶段**: Phase 2 — Converge

---

## 合并来源

| 实例 | 电脑 | Git 分支 | 路径 |
|------|------|----------|------|
| Case-01-WORK | feng | `pilot` (15 commits ahead of master) | F:\PAIOS |
| Case-02-PERSONAL | evan | `feature/case-02-dev` | G:\2in1\PAIOS |
| **目标** | — | `portable-master` | H:\PAIOS-PORTABLE\Core |

---

## 1. Git 历史合并

### Merge-1: pilot → portable-master
- **来源**: case01/pilot (15 commits)
- **冲突**:
  - `.gitignore` — 接受 pilot 版本（含增强的忽略规则）
  - `reasonix.toml` — 接受 pilot 版本（最新工具权限配置）
  - `PAIOS-Usage/manifest.yaml` — 接受 pilot 版本
  - `RELEASES/upgrade-receipt-*` — 接受 pilot 版本
  - 7 个 directory rename: `20_KNOWLEDGE/Decisions/`, `References/`, `Concepts/`, `Methods/`, `Models/`, `SOP/` → `20_KNOWLEDGE/Platform/` — **接受 pilot 重构**
- **决策**: 全部接受 pilot 的目录重构和配置变更

### Merge-2: case-02-dev → portable-master
- **来源**: case02/feature/case-02-dev
- **冲突**:
  - `40_AUTOMATION/05_SCRIPTS/collect_manifest.py` — 保留 HEAD (pilot 版本)
  - Directory rename: `60_HISTORY/JOURNAL/*` → `80_HISTORY/JOURNAL/*` — **接受 case-02 重命名**
  - `Fleet/cases/README.md` — 保留 HEAD
  - `PAIOS-Usage/` — 保留 HEAD (该目录已在 pilot 中更新)
  - `Today.md` — 保留 HEAD
  - `reasonix.toml` — 保留 HEAD (pilot 版本)
- **决策**: 接受 80_HISTORY 结构，其余配置保留 pilot 版本

---

## 2. 系统层（30_SYSTEM / 40_AUTOMATION）

| 子目录 | 状态 | 说明 |
|--------|------|------|
| 30_SYSTEM/ADR | ✅ git 统一 | 21 个 ADR 文件 |
| 30_SYSTEM/Governance | ✅ git 统一 | 15 个治理文件 |
| 30_SYSTEM/SOP | ✅ git 统一 | 8 个 SOP 文件 |
| 30_SYSTEM/Config | ✅ 已升级 | paths.yaml → v2（PAIOS_ROOT 协议） |
| 30_SYSTEM/migration | ✅ 新增 | migration-20260715.yaml 状态机 |
| 40_AUTOMATION/05_SCRIPTS | ✅ git 统一 | collect_manifest.py 等 |
| 40_AUTOMATION/00_REGISTRY | ✅ git 统一 | 能力注册表 |

---

## 3. 知识层（20_KNOWLEDGE）

| 子目录 | 来源 | 文件数 | 说明 |
|--------|------|--------|------|
| Platform/ | git 统一 | 50 | 概念/决策/方法/模型/参考/SOP |
| Personal/ | 合并 | 7 | 4 文件来自 git(Case-02) + 3 文件补充自 Case-01 |
| RELEASES/ | git 统一 | — | 版本发布知识 |
| SOP/ | git 统一 | — | 知识级 SOP |

**Case-01 独有补充**:
- PAIOS-Kaoyan-100Day-Guide.pdf
- Proxy-Setup-Guide-一楼PC.md
- 阅读目录索引.md

**无内容冲突**——同名文件 diff 仅为换行符差异（CRLF vs LF）

---

## 4. 工作层（10_WORK）

| 区域 | 来源 | 内容 |
|------|------|------|
| Active/ | 合并 | Kaoyan-2026, Safety-Net（共同）、photos-organizer, 照片归档清理, 运丰照片补全, 运丰皓祥遗漏照片（Case-02） |
| Done/ | Case-01 | 已完成项目 |
| Review/ | Case-01 | 待评审项目 |
| Waiting/ | Case-01 | 待处理项目 |
| Templates/ | Case-01 | 项目模板 |

**历史项目**（原 Case-01 日期标记项目）→ 移入 90_ARCHIVE/Work-History/：
- 2026-07-15-底层逻辑对比
- 2026-07-15-非暴力沟通

---

## 5. 捕获层（00_CAPTURE）

| 子目录 | 来源 | 说明 |
|--------|------|------|
| Daily/ | Case-01 | 每日捕获 |
| Downloads/ | Case-01 | 下载文件 |
| Images/ | Case-01 | 图片捕获 |
| Imported/ | Case-01 | 导入内容 |
| Voice/ | Case-01 | 语音记录 |
| Inbox.md | Case-01 | 入口 Inbox |

**Case-02 捕获为空**——未复制

---

## 6. 归档层（90_ARCHIVE）

| 子目录 | 来源 | 说明 |
|--------|------|------|
| Migration/ | git 统一 | 迁移计划 + Packet 文档 |
| Snapshots/ | 合并 | 双实例快照 |
| Knowledge/ | Case-01 | 归档知识 |
| Logs/ | Case-01 | 操作日志 |
| Projects/ | Case-01 | 归档项目 |
| Versions/ | Case-01 | 版本记录 |
| Work-History/ | 新建 | 历史工作项目 |

---

## 7. 资产边界（ASSETS / INDEX）

ASSETS 和 INDEX 目录已创建，当前为空。遵循 Phase 5 设计：
- 照片/视频/PDF 大文件 → ASSETS/
- AI 索引 → INDEX/
- Core 中仅保存引用路径

---

## 8. 未合并项

| 项 | 原因 |
|----|------|
| 70_TMP/ | 临时文件，不迁移 |
| 50_DATA/ | 照片数据，留在原地 |
| .reasonix/ | AI 引擎状态，重新生成 |
| .workbuddy/ | AI 引擎状态，重新生成 |
| Claw/ | 实验工具，已从旧实例清理 |

---

## 合并总结

| 维度 | 数量 |
|------|------|
| Git commits | 51 (master) + 15 (pilot) + case-02-dev = 保留全部 |
| 分支 | master, pilot, feature/case-02-dev, portable-master（新增） |
| 20_KNOWLEDGE 文件 | 66 |
| 10_WORK Active 项目 | 7 |
| 冲突解决 | 2 次 merge，共 12 个冲突，全部手动裁决 |

---

**下一阶段**: Phase 3 — Governance（资产治理审计）
