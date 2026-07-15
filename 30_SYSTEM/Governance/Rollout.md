---
title: "Rollout — 全量推广"
status: Active
created: 2026-07-11
related:
  - Architecture-Lifecycle.md
  - Pilot-Gate.md
  - Change-Control.md
  - ../Evolution/Phase-B-Core-Workspace-Split.md
---

# Rollout（全量推广）

> Pilot Gate 过闸后，将变更推广到其他实例。
> 本规范独立于任何 Phase，Phase B / C / D 复用。

---

## 1. 前置条件

- ✅ Pilot Exit Criteria 全部满足（见 `Pilot-Gate.md`）
- ✅ 设计冻结 commit + 边界建立 commit 已落地（未 push 也可，但本机先稳）
- ✅ 备份锚点就位

---

## 2. 推广顺序

按实例角色分批，而非一次性全推：

1. **Pilot 实例**：已在跑，保持。
2. **第二批**：其余实例（如 Phase B 的 Case-02 Personal、Case-03 Study）一起升级到新边界。
3. **观察**：推广后继续记录，确认无新的分类歧义 / 冲突。

---

## 3. Rollout 在 Git History 上的展开（Commit 纪律）

Rollout 不是"一个 commit"，而是 Git History 上的四段展开（详见 `Architecture-Lifecycle.md` 与 Phase B 蓝图）：

| 段 | 类型 | 提交信息 | 实质 |
|----|------|----------|------|
| 1 | Architecture | `docs(architecture): ...` | 设计冻结 |
| 2 | Governance | `refactor(governance): establish ... boundaries` | 建立边界（不拆物理） |
| 3 | Git Cleanup | `chore(git): merge remote` | 解决分叉 / 冲突 |
| 4 | Physical Separation | `refactor(core): physical separation via git rm --cached` | 真正物理隔离 |

> 关键：**架构变更 commit 绝不混入 git cleanup commit**；"逻辑隔离"统一称"建立边界"，避免 History 被误读成"已开始拆分"。

---

## 4. 实例差异化处理

不同实例角色可能需微调：

- **Developer（Case-01）**：常是 Pilot，最早落地，承担验证责任。
- **Personal / Study（Case-02 / 03）**：跟随推广，重点确认其 Workspace 内容不被误共享。
- 每实例升级后各自 `collect_manifest.py` → `publish` → `F:\Fleet\incoming\`，Developer 侧聚合。

---

## 5. 复用规则

- Rollout 必在 Pilot 过闸之后，不可并行跳过。
- 推广后进入 `Architecture-Lifecycle.md` 的 **Validate** 阶段：连续多版本观察缺陷不再复现。
- 本规范与 `Pilot-Gate.md`、`Change-Control.md` 配套。
