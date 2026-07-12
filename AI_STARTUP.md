# PAIOS AI Startup — 所有 AI 引擎首次会话必读

> 无论你是 Reasonix、WorkBuddy、Codex、ChatGPT 还是其他 AI，
> 在编辑 PAIOS 任何文件之前，请先读完这份一页纸规则。

## 三秒记住三件事

| # | 规则 | 一句话 |
|---|------|--------|
| 1 | **数据不进 PAIOS** | 下载的文件、图片、视频 → `E:\QuarkSync\DATA\` |
| 2 | **Cache 不进 Active** | .venv、模型缓存、临时输出 → `10_WORK/Runtime/` 或 `70_TMP/` |
| 3 | **衍生数据不进 Git** | 人脸索引、嵌入向量等 → `50_DATA/`（不同步） |

## 详细

### 数据放在哪

| 内容类型 | 目的地 | 理由 |
|---------|--------|------|
| 系统文件（ADR、配置、脚本） | `E:\PAIOS\` → Git | 版本管理 |
| 知识资产（.md 文档） | `E:\PAIOS\20_KNOWLEDGE\` → Git | 文本资产随系统走 |
| **下载文件、图片、视频** | **`E:\QuarkSync\DATA\`** ← ⚠️ 最容易犯错 | 夸克自动同步 |
| **运行时缓存（.venv、模型）** | `10_WORK/Runtime/` 或 `70_TMP/` ← ⚠️ 第二大犯错点 | 随时可删，不同步 |
| **衍生数据（DB、索引）** | `50_DATA/` | 本地不同步 |
| 业务文件（Excel、Word） | `E:\QuarkSync\DATA\` | 夸克自动分类 |

### 禁止行为

- ❌ 把下载文件放到 `E:\PAIOS\` 根目录
- ❌ 把 .venv 放在项目源码目录（放 `Runtime/`）
- ❌ 把 git 不跟踪的大文件提交到仓库

### 设计哲学

> PA IOS = 系统层（Git 管理）
> QuarkSync = 数据层（夸克自动同步）
> 两者不混合。
