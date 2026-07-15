# Story-002: Platform Purity 是如何诞生的

> **时间线**：2026-07-09 ~ 2026-07-11
> **关联**：`30_SYSTEM/ADR/ADR-0017-Platform-Purity-Physical-Separation.md` · `30_SYSTEM/Governance/Operating-Model.md` · `CHANGELOG.md`
> **状态**：定稿

---

## 最初的触发

一切始于一个简单的问题：

> **为什么我的 Workspace 也会进入 Platform？**

Case-01（工作机）在日常使用中，发现自己的项目文件、照片整理脚本、个人笔记——本应属于 Workspace 的内容——出现在了远端仓库中。这不是人为错误，而是架构上没有区分"平台"和"运行"。

## 误判阶段

最初认为是 Git 问题：

```
问题：Workspace 泄漏进共享仓库
假设：是 Git 操作不当
方案：加强 gitignore、增加提交审查
```

这个思路持续了一两天。Git 规则确实能缓解症状，但解决不了根本问题。

## 真正的发现

后来在分析多实例并流时，一个更深层的模式浮现出来：

```
Platform（平台定义）
    ↓
Application（应用逻辑）
    ↓
Workspace（工作内容）
    ↓
Runtime（运行时状态）
```

这四个层次的职责完全不同，但我们把它们全放在了一个仓库、一套目录结构里。

**真正的问题不是 Git，而是平台层和运行层之间没有边界。**

## Platform Purity 原则的形成

一旦意识到这是边界问题，解决方案就清晰了——不是加更多 Git 规则，而是定义边界。

核心判断标准经历了一次升级：

```
第一版："别人 pull 了有价值吗？"
    ↓
第二版（冻结版）："是否在定义平台能力？"
```

第二个版本更精确：平台仓库只包含"平台能力定义"，不包含"平台使用产生的内容"。

## 三桶隔离模型

```
Core（平台能力）     → 30_SYSTEM/、40_AUTOMATION/、根级配置
Workspace（工作内容） → 10_WORK/、20_KNOWLEDGE/Personal/、Today.md
Instance-State（实例状态）→ PAIOS-Usage/manifest.yaml、profile.yaml
```

- Core 是平台——进共享仓库，所有人都 pull
- Workspace 是个人——永远不进共享仓库
- Instance-State 是快照——只读汇总，单向回传

## 被放弃的方案

| 方案 | 为什么放弃 |
|------|-----------|
| 加强 .gitignore | 治标不治本，规则总有遗漏 |
| 增加提交审查流程 | 增加人力成本，且操作员不一定记得住规则 |
| 分多个 Git 仓库 | 增加同步复杂度，且当时已有 3 个实例 |

最终选择的是**物理隔离**（同一个仓库，通过 .gitignore 和目录设计隔离），因为它在不增加运维复杂度的前提下解决了根本问题。

## 认知总结

> **Workspace 进入 Platform 不是操作失误，而是架构上没有边界。**

这个认知转变影响了后续所有的治理决策：不是在人的行为层面加规则，而是在架构层面建边界。ADR-0017 因此成为 PAIOS 最重要的架构决策之一——它确立了一种判断标准，而不仅仅是一组规则。

## 后记（Retrospective）

> *本故事撰写于 2026-07-12。*
> *随着 PAIOS 演进，后续发现可在此补充——架构思想本身也是会成长的。*

---

*关联阅读：Platform Purity 随后与 ADR-0018（角色模型）形成了双重保险——内容分离 + 角色分离。详见 [Operating Model](../Governance/Operating-Model.md)。*
