# Architecture Stories — 架构思想的故事

> **这不是 ADR，不是 SOP，不是 Engineering Journal。**
>
> 这是 PAIOS 架构思想形成的故事——有些概念历经几十轮讨论才逐渐浮现，没有一个明确的"诞生时刻"。
> ADR 记录"最终决定"，Git 记录"改了什么"。
> Stories 记录的是**那些决定是怎么一步步走到的**——被否定的方案、偶然的发现、认知的转折。

---

## 为什么需要 Stories？

```
ADR          → 为什么最终这样决定（Decision）
Git          → 改了什么（Change）
CHANGELOG    → 发布了什么（Release）
Journal      → 今天发生了什么（Thinking）
Story        → 这个思想是怎么诞生的（Origin）
```

前四者合起来能回答"是什么"，但回答不了"为什么会想到这个"。

很多最有价值的思考发生在连续几十轮对话中，没有一个明确的诞生时刻。它慢慢浮现、反复修正、最后才凝固成一个原则或 ADR。

如果只有最终的文档，几年后你只会看到结论，看不到这条路曾经有过哪些岔路。

---

## Stories 列表

| # | Title | 主题 | 关联 ADR |
|---|-------|------|----------|
| 001 | [为什么 PAIOS 不是第二大脑](001-为什么PAIOS不是第二大脑.md) | 从"AI 知识库"到"操作系统"的认知转变 | ADR-0012 |
| 002 | [Platform Purity 是如何诞生的](002-Platform-Purity-是如何诞生的.md) | 平台层和运行层的边界发现过程 | ADR-0017 |
| 003 | [CASE-001 改变了什么](003-CASE-001-改变了什么.md) | 一次真实多实例并流如何重塑了治理体系 | ADR-0017, ADR-0018 |
| 004 | [Need Driven Promotion 的来源](004-Need-Driven-Promotion的来源.md) | "不要因为能做而去做"这一原则的形成 | ADR-0010 |
| 005 | [为什么不用直接 Merge](005-为什么不用直接Merge.md) | Review → Promote 机制的设计根源 | ADR-0016, ADR-0018 |

---

## ADR ↔ Story 映射

| ADR | Title | Story | 必要性 |
|-----|-------|-------|--------|
| ADR-0012 | Platform-Application Architecture | Story-001 | 重要（定义了 PAIOS 的定位） |
| ADR-0017 | Platform Purity & Physical Separation | Story-002, Story-003 | 重要（核心架构原则） |
| ADR-0010 | Evolution Strategy | Story-004 | 建议有（治理方法论） |
| ADR-0016 | Multi-Instance Architecture Baseline | Story-005 | 重要（多实例设计根源） |
| ADR-0018 | Multi-Instance Role Model | Story-003, Story-005 | 建议有（由 CASE-001 触发，可合并在已有 Story 中） |

**规则**：不是每个 ADR 都必须有 Story，但每一个改变平台方向的重要 ADR，都应该至少对应一篇 Story。

预计长期比例：ADR ~70 个 / Story ~20 个，完全合理。

---

## 写作公约

1. **不编造**——只写有据可查的讨论过程和认知变化
2. **记录被否定的方案**——那些没走通的路和放弃的理由同样重要
3. **标注时间线**——每个认知转折的大致时间
4. **关联现有文档**——链接到 ADR、Journal、CASE 等正式文档
5. **每篇 Story 末尾增加「后记（Retrospective）」段**——为未来的重新审视预留空间
6. **可以更新**——随着回忆或新发现，Stories 可以补充完善

---

## 经典故事

见 [Classics/](Classics/README.md)——PAIOS 建国史·必读五篇。

---

> *代码可以被 AI 重写，而为什么这样设计、哪些路走不通、哪些原则是在实践中沉淀出来的——这些经验才是最难复制、也是最有价值的部分。*
