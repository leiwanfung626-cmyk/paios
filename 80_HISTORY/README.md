# Project History

> PAIOS Platform 的**工程历史档案**。
> 与 `CHANGELOG.md`（发布了什么）和 `ADR/`（为什么这样决定）互补，
> 本目录保存**思维轨迹**——当时是怎么想的、经历了哪些取舍、有什么认知变化。

---

## Directory Structure

```
60_HISTORY/
├── README.md            # 本文件
├── CHANGELOG.md         # 指向根目录 CHANGELOG.md（镜像引用）
└── JOURNAL/             # 工程日志（Engineering Journal）
    ├── TEMPLATE.md      # 日志模板
    ├── 2026-07-12.md    # 第一篇日志
    └── ...              # 后续按日期增加
```

## What Goes Where

| 资产 | 位置 | 回答的问题 |
|------|------|-----------|
| **Git** | `git log` | 改了什么？ |
| **ADR** | `30_SYSTEM/ADR/` | 为什么这样决定？ |
| **CHANGELOG** | `CHANGELOG.md` | 发布了什么？ |
| **Engineering Journal** | `60_HISTORY/JOURNAL/` | 当时是怎么思考的？ |

## Why This Exists

> **代码可以被 AI 重写，而为什么这样设计、哪些路走不通、哪些原则是在实践中沉淀出来的——这些经验才是最难复制、也是最有价值的部分。**

Engineering Journal 记录的是思维的演化过程，而不是工作量。它让 PAIOS 的演进不只是代码和文档的变更，而是一份可追溯的工程成长史。

---

## Version Correlation

PAIOS 版本与 Journal 的对应关系：

| 版本 | 日期 | 核心主题 | 关联 Journal |
|------|------|----------|-------------|
| v1.0.1 | 2026-07-10 | Multi-Instance Architecture Baseline | — |
| v1.0.1+ | 2026-07-12 | Project Infrastructure + Engineering Journal 启动 | `2026-07-12.md` |

---

> 详见 [docs/](../docs/) | [CHANGELOG](../CHANGELOG.md) | [ADR Index](../30_SYSTEM/ADR/ADR-INDEX.md)
