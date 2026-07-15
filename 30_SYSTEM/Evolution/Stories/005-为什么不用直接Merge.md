# Story-005: 为什么不用直接 Merge

> **时间线**：2026-07-10 ~ 2026-07-11（CASE-001 期间逐步形成）
> **关联**：`30_SYSTEM/ADR/ADR-0016-Multi-Instance-Architecture-Baseline.md` · `30_SYSTEM/ADR/ADR-0018-Multi-Instance-Role-Model.md` · `30_SYSTEM/Governance/Operating-Model.md`
> **状态**：定稿

---

## 最初的假设

在设计多实例架构时，最初大家的直觉是：

```
Case-01 → push → 共享仓库
Case-02 → push → 共享仓库
Case-03 → push → 共享仓库

互相推送，版本以最新为准。
```

这个模型很直接——所有人向同一个仓库推送，Git 负责合并。看起来没问题。

## 第一次并流暴露问题

当三个实例第一次实际并流时，问题立刻暴露：

**不是代码冲突，而是 Role 冲突。**

三个实例都以 Developer 身份运行——都能 push、都能改平台文件、都能改别人写的配置。Git 可以处理代码合并，但处理不了"两个 Developer 对同一个平台配置有不同想法"的情况。

## Git 的局限

Git 是一个版本管理工具，不是治理工具。它能告诉你：

- 谁改了哪一行
- 两个版本有什么区别
- 如何自动合并

但它回答不了：

- 这个改动应该发生吗？
- 谁有权做这个改动？
- Case-02 的 manifest 和 Case-01 的 manifest 哪个是权威？
- Case-03 的配置修改该不该同步给其他人？

## Review → Promote 机制的设计

核心洞察是：

> **多实例之间不是"同步"关系，而是"Review → Promote"关系。**

```
错误模型：所有实例互相 push（同步）
正确模型：实例 → 提交 Manifest → Developer Review → Promote 到平台
```

这个机制的关键点：

1. **User 不直接改平台**——Case-02/03 对 Core 仓库只有只读权限
2. **Manifest 只读收集**——`collect_manifest.py` 只读现有结构，不改变系统
3. **单向数据流**——User → Developer（Manifest），Developer → User（Release）
4. **平台唯一写入口**——只有 Case-01（Maintainer）可以发布 Release

## 三个层面的分离

最终，Review → Promote 机制在三个层面同时实现：

| 层面 | 机制 | 关联文档 |
|------|------|---------|
| **内容分离** | Core / Workspace / Instance-State 三桶隔离 | ADR-0017 |
| **角色分离** | Maintainer 写 / User 读 | ADR-0018 |
| **流程分离** | Manifest 收集 → Developer Review → Promote 到 Fleet | SOP Release Flow |

三重分离确保任何一层的失效都不会导致系统污染。

## 被放弃的方案

| 方案 | 为什么放弃 |
|------|-----------|
| 所有人都有写权限 | CASE-001 证明了行不通 |
| 加 Git hook 做写入审查 | hook 可以被绕过，且维护成本高 |
| 分支 + PR 模式 | 日常用户不适用——用户不应该需要懂 Git 分支 |
| 定期手动同步 | 不可靠，且无法扩展 |

## 认知总结

> **不用 Merge，用 Review → Promote。**

这个设计决策不是在选择一种技术方案，而是在重新定义多实例之间的关系——不是平等的"对等同步"，而是有层级的"单向提升"。

这也是 PAIOS 从"工具"走向"平台"的标志性设计之一。工具可以被所有人平等使用；平台需要定义谁可以做什么。

## 后记（Retrospective）

> *本故事撰写于 2026-07-12。*
> *随着 PAIOS 演进，后续发现可在此补充——架构思想本身也是会成长的。*

---

*关联阅读：[Operating Model](../Governance/Operating-Model.md) 展示了 Review → Promote 的实际数据结构；[ADR-0018](../ADR/ADR-0018-Multi-Instance-Role-Model.md) 记录了角色模型的完整决策。*
