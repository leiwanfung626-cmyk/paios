---
title: "Release Checklist — 发布前检查清单"
status: Active
created: 2026-07-11
related:
  - ../../SOP/SOP-2026-07-10-0001-Release-Flow.md
  - version-policy.md
  - branching-policy.md
  - ../../../README.md
  - ../../ADR/ADR-INDEX.md
---

# Release Checklist

> 每次发布新版本前，逐项检查并标记。全部通过后再打 Tag、推送。

---

## Pre-Release Checks

- [ ] **pytest**：`python -m pytest 40_AUTOMATION/08_TESTS/ -v` — 全部通过
- [ ] **git status**：`git status` — 无未预期的脏文件
- [ ] **README.md**：是否需要更新（新功能、变更的架构信息）
- [ ] **CONTRIBUTING.md**：是否需要更新（流程变更）
- [ ] **CHANGELOG.md**：[Unreleased] 内容已移入新版本段，格式规范
- [ ] **SYSTEM_VERSION.md**：版本号已更新
- [ ] **MANIFEST.json**：版本号与 SYSTEM_VERSION 一致
- [ ] **ADR Index**（`ADR-INDEX.md`）：新增/变更的 ADR 已索引
- [ ] **Release Notes**（`RELEASES/vX.Y.Z.md`）：已按模板生成
- [ ] **Release Notes 检查**：包含「📋 用户须知（Case-02/03 必读）」段（三条铁律 + 升级步骤 + 速览图/一页纸链接）
- [ ] **版本标签**：确认 SemVer 合规（见 version-policy.md）
- [ ] **兼容性声明**：Release Notes 含 Core / Manifest / Workspace / Migration 兼容性
- [ ] **Fleet**：`F:\Fleet\` 状态已确认（如适用）

## Release Execution

- [ ] **Commit**：`git add -A && git commit -m "release: vX.Y.Z"`
- [ ] **Tag**：`git tag vX.Y.Z`
- [ ] **Push**：`git push origin master --tags`

## Post-Release

- [ ] **升级回执**：`RELEASES/upgrade-receipt-vX.Y.Z.md` 已创建或更新
- [ ] **用户通知**：Case-02/03 已被告知可 `git pull` 升级
- [ ] **Manifest**：收集升级后 Manifest 并归档到 Fleet

---

> 关联：[Release Flow SOP](../SOP/SOP-2026-07-10-0001-Release-Flow.md) | [Version Policy](version-policy.md) | [Branching Policy](branching-policy.md)
