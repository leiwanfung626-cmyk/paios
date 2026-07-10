# CASE-001 复盘 —— 第一次真实多实例并流

> 类型：Background Briefing（背景说明 / 沟通文档）
> 受众：**Case-02（Personal）** · **Case-03（Study）**
> 关联：CASE-001 · ADR-0017 · Phase-B-Core-Workspace-Split.md · Architecture-Lifecycle.md
> 说明：本文不是给 Case-02/03 看"改了什么清单"，而是回答三个问题——
> **① 为什么会走到这一步？② 为什么不是立即修、而是分阶段修？③ 你们接下来要做什么、不该做什么？**

---

## 〇、一句话总览

PAIOS 第一次从"单实例平台"进入"多实例平台"，第一次真实并流就暴露了**架构边界没定义清楚**的问题。我们没有直接改代码，而是先建立治理（CASE→ADR→Blueprint→Freeze），再分阶段修复（Commit 1 架构 → 2 治理 → 3 Git Cleanup → 4 物理隔离），且只让 Case-01（Developer）作为 Pilot 先试。Case-02/03 目前**什么都不用改**，继续正常使用即可。

---

## 一、事件背景

PAIOS 最初只有一个实例（Case-01）。

整个架构都是围绕：

> 一个人、一台机器、一个 Workspace

设计的。

后来开始出现：

| Case    | 场景        | 说明           |
| ------- | ----------- | -------------- |
| Case-01 | Developer   | 工作（本机 feng）|
| Case-02 | Personal    | 个人           |
| Case-03 | Study       | 考研           |

三个实例都运行同一个 PAIOS Core。

这是第一次：

- 第一次开始真实升级
- 第一次真实 push
- 第一次真实 collect manifest
- 第一次真实并流

这意味着：

> **PAIOS 第一次从"单实例平台"进入"多实例平台"。**

而原来的架构假设（"只有一个实例"）在这种并流下开始失效——这正是所有问题的根源。

---

## 二、第一次收集 Manifest

Developer（Case-01）没有鲁莽地直接 merge，而是：

```
git fetch
   ↓
git show（只读提取远端 manifest）
   ↓
汇总到 F:\Fleet\incoming\
```

得到三份 Manifest：

```
Case-01
Case-02
Case-03
```

这是第一次可以看清**整个 Fleet 的真实状态**。

统计结果说明：

| 指标            | 三实例结果              |
| --------------- | ----------------------- |
| Core 版本       | 全部 v1.0.1（100% 一致）|
| Automation      | 全员开启                |
| Knowledge       | 全员开启                |
| Growth          | 全员开启                |

这说明：

> **平台共享能力的设计是成功的。**

但是。

真正的问题也同时暴露了。

---

## 三、发现的四个问题

### 问题一：Manifest 冲突

三个实例都写：

```
PAIOS-Usage/manifest.yaml
```

结果：最后 push 的，覆盖前面的。

这说明：

> Manifest 设计默认"只有一个实例"，而现在——已经不是了。

### 问题二：Fleet 放错地方

发现：

- 另一台机器建立了 `PAIOS/Fleet/`
- Developer 建立了 `F:\Fleet\`

两个 Fleet。

这说明：

> Fleet 的边界没有被定义清楚。

最终决定：

> **Fleet 属于 Developer（平台侧），不属于任何 Workspace。**

（即 `F:\Fleet` 在仓库之外，不随 `git pull` 回流到任何实例。）

### 问题三：Workspace 泄漏

远端出现：

```
10_WORK
20_KNOWLEDGE
Today
Archive
Photos
```

全部进入了 Core。

这意味着：

> 大家把 **Git 仓库当成了 Workspace**，而不是 Platform。

### 问题四：两套 Manifest 系统

- Developer 有 `collect_manifest.py`
- 另一台又建立了另一套 Manifest

这说明：

> 平台出现了**重复能力**。

这是典型的 **Platform Drift（平台漂移）**。

---

## 四、为什么不能马上修？

第一反应很容易是：

```
merge
  ↓
git rm
  ↓
gitignore
  ↓
push
```

全部做完。

但是 Developer 没有这样做。

原因：

> 我们发现，真正的问题**不是 Git**，而是**架构边界**。

如果边界还没定义清楚：

> 今天删，明天还会继续写回来。

所以决定：

> **先治理，再修复。**

先回答"平台应该是什么"，再回答"怎么迁"。而不是"先迁，再慢慢补文档"。

---

## 五、因此产生了哪些成果？

这次没有直接改代码，而是先建立治理，依次形成：

```
CASE-001
   ↓
ADR-0017
   ↓
Phase B Blueprint
   ↓
Commit Freeze（设计冻结）
```

也就是说：

> **先回答"平台应该是什么"，再回答"怎么迁"。**

而不是：

> 先迁，再慢慢补文档。

这条顺序，后来被沉淀为 PAIOS 的 **Architecture Lifecycle**（架构生命周期），成为后续所有重大演进的统一框架。

---

## 六、为什么要拆成四个 Commit？

以前可能一个 Commit 就把这些全做了：

```
目录 + merge + gitignore + rm cached + push
```

以后不是。

而是：

```
Commit 1  Architecture（架构）
   ↓
Commit 2  Governance（治理）
   ↓
Commit 3  Git Cleanup（Git 收敛 / merge）
   ↓
Commit 4  Physical Separation（物理隔离 / git rm --cached）
```

每一步**只有一个目标**。

出问题的时候，能立刻知道：

> 是哪一步错的。

而不是面对一个混杂的大提交无从排查。

> 注：上表是**设计的 Git History 形状**（即治理纪律）。实际执行到今天，已落地的是：Commit 1 设计冻结（`472e53d`）、治理层抽离（`bb855c4`）、Commit 2 建立边界（`30518f3`）、Architecture Lifecycle v1.0 冻结（`41c65a6`）；Commit 3 / 4 尚未开始。

---

## 七、为什么只有 Case-01 修？

| Case    | 角色       | 当前动作     |
| ------- | ---------- | ------------ |
| Case-01 | Developer  | 承担 Pilot，先试 |
| Case-02 | Personal   | 保持稳定     |
| Case-03 | Study      | 保持稳定     |

如果三台一起改，发现问题：

> 不知道到底哪里错。

所以：

> Case-01 先试。Case-02、Case-03 保持现状。

等 Pilot 连续稳定，再 Rollout。

---

## 八、Case-02、Case-03 现在需要做什么？

### 该做的

- **继续正常使用 PAIOS**，像以前一样。
- 保持你现有的目录、知识、项目不动。
- 等待 Developer 完成 Pilot 并正式发布新 Core。

### 不该做的（重要）

**不要**主动做以下任何操作：

- ❌ `git merge` / `git pull` 后手动改动 Core 结构
- ❌ 修改 `.gitignore`
- ❌ `git rm --cached`
- ❌ 目录迁移 / 重新组织 `20_KNOWLEDGE` 或 `10_WORK`
- ❌ 自行升级或"顺手帮忙整理"

这些动作都属于 Phase B 的某个 Commit 阶段，由 Developer 在 Pilot 验证后统一执行并发布。提前做会破坏实例间的一致性，反而增加回滚成本。

### 当前真实进度（截至本文）

| 阶段                       | 状态        | 说明                                     |
| -------------------------- | ----------- | ---------------------------------------- |
| Commit 1 设计冻结          | ✅ 完成      | `472e53d`（未 push）                     |
| 治理层抽离                 | ✅ 完成      | `bb855c4`（Governance 层 + Asset-Class） |
| Commit 2 建立边界          | ✅ 完成      | `30518f3`（仅 Case-01 本机执行，未 push）|
| **Pilot（Case-01 单实例）**| ⏳ 未启动    | 待约 14 天真实运行，满足 Exit Criteria   |
| Commit 3 Git Cleanup       | ⛔ 未开始    | 须 Pilot Exit 后才做                     |
| Commit 4 物理隔离          | ⛔ 未开始    | 须 Git Cleanup 稳定后做                  |
| Rollout（Case-02/03）      | ⛔ 未开始    | 须物理隔离验证通过后才统一升级           |

> 结论：**你们现在什么都不用动。** 只有当 Developer 完成 Pilot、确认 Manifest / Registry / Fleet / Upgrade 全部稳定，并正式发布新 Core 后，Case-02 与 Case-03 才会被通知统一升级。

---

## 九、这次最大的收获

这次真正修复的：

- 不是 Manifest
- 不是 Git
- 不是 Workspace

真正修复的是：

> **PAIOS 的演进方式。**

以前：

```
想到 → 设计 → 实现
```

现在：

```
真实运行 → 发现问题 → 形成 CASE → 形成 ADR → 形成 Blueprint
   → 冻结设计 → Pilot → Rollout → 验证 → 进入下一轮演进
```

这意味着：

> **PAIOS 从"一个人的项目"，开始走向"可以持续演进的平台"。**

---

## 给 Case-02、Case-03 的一句话

> 这次暂时不需要你们修改任何内容。Developer（Case-01）将作为 Pilot 完成边界治理和验证；只有当新架构经过验证并正式发布后，Case-02 与 Case-03 才会统一升级。这样既能保证个人和学习环境的稳定，也能确保所有实例最终回到同一架构基线。
