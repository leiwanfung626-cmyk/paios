# Merge-Gap Analysis — 双实例差异分析

> **阶段**: Phase 3 — Governance
> **日期**: 2026-07-15
> **基线**: CONVERGED-SNAPSHOT-20260715.md (commit afae8b3)

---

## 1. Git 差异（已合并）

| 分支 | 来源 | Commits | 状态 |
|------|------|---------|------|
| `pilot` | Case-01 (feng) | 15 | ✅ 已合并到 portable-master |
| `feature/case-02-dev` | Case-02 (evan) | 若干 | ✅ 已合并到 portable-master |

## 2. 20_KNOWLEDGE 差异

| 差异项 | Case-01 有 | Case-02 有 | 处理 |
|--------|-----------|-----------|------|
| Personal 文件 | 7 个（含 3 个独有） | 4 个 | ✅ 合并为 7 个 |
| Platform 文件 | 50 | 50 (git 统一) | ✅ 无差异 |
| 知识内容冲突 | 无 | 无 | ✅ 同名文件仅换行符差异 |

## 3. 10_WORK 差异

| 项目 | Case-01 | Case-02 | 处理 |
|------|---------|---------|------|
| Kaoyan-2026 | ✅ Active | ✅ Active | ✅ 合并 |
| Safety-Net | ✅ Active | ✅ Active | ✅ 合并 |
| photos-organizer | ❌ 无 | ✅ Active | ✅ 从 Case-02 补充 |
| 照片归档清理 | ❌ 无 | ✅ Active | ✅ 从 Case-02 补充 |
| 运丰照片补全 | ❌ 无 | ✅ Active | ✅ 从 Case-02 补充 |
| 运丰皓祥遗漏照片 | ❌ 无 | ✅ Active | ✅ 从 Case-02 补充 |
| 2026-07-15 项目 | ✅ 工作区 | ❌ 无 | → 移入 90_ARCHIVE/Work-History |
| Done/Review/Waiting | ✅ 完整 | ❌ 无 | ✅ 从 Case-01 复制 |

## 4. 40_AUTOMATION 差异（git 统一）

| 差异 | Case-01 | Case-02 | 处理 |
|------|---------|---------|------|
| fleet-push-case-02 系列 | ❌ 无 | ✅ 有 | ✅ 保留（需重构） |
| 其余脚本 | 一致 | 一致 | ✅ git 已统一 |

## 5. 00_CAPTURE 差异

| 子目录 | Case-01 | Case-02 | 处理 |
|--------|---------|---------|------|
| Daily/Downloads/Images/Imported/Voice | ✅ 有内容 | ❌ 空 | ✅ 从 Case-01 复制 |
| Inbox.md | ✅ 有内容 | ❌ 空 | ✅ 从 Case-01 复制 |

## 6. 关键结论

- **无数据丢失**: 双实例全部知识/项目资产已收敛到 PAIOS-PORTABLE
- **无内容冲突**: 同名文件仅有换行符差异
- **唯一未合并**: 70_TMP, 50_DATA（照片）, .reasonix/.workbuddy（AI 引擎状态）— 以上不属于 PAIOS Core 资产
