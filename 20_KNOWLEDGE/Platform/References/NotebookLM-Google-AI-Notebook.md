---
ref_id: REF-0002
schema_version: 2
title: "NotebookLM — Google AI 笔记与来源整理工具"
type: tool
lifecycle: active
created: 2026-07-02
updated: 2026-07-02
source:
  - douyin
  - web-search
  - official-doc
tags:
  - ai
  - google
  - notebook
  - research
  - gemini
  - transcript
  - podcast
  - free-tool
keywords:
  - 来源整理
  - 转录稿
  - Audio Overview
  - Slide Deck
  - Gemini
  - 免费顶级模型
summary: >
  Google 推出的免费 AI 研究助手，基于 Gemini 模型，
  将 PDF、YouTube、音频、网页等来源转化为可追问、可引用、可输出的智能笔记本。
abstract: >
  NotebookLM 是 Google 的 AI 笔记与来源整理工具，核心价值是「忠于来源」——
  回答只来自用户上传的 sources，不会自行编造。
  支持 PDF、Google Docs、YouTube、音频、网页等多种来源，
  可输出转录稿、Audio Overview（播客）、Slide Deck（演示文稿）、心智图、问答等。
  免费版基于 Gemini 2.0 模型，个人使用已足够。
  最大亮点是零门槛使用顶级 AI 模型做素材整理与转录。
related:
  - REF-0001
verification:
  status: web-verified
  scope:
    - features
    - pricing
    - source-types
    - workflow
  last_verified: 2026-07-02
  evidence_chain:
    - douyin-url
    - web-search-results
    - official-doc (penchan.co 完整教程)
    - manual-summary
confidence: high
maintenance:
  owner: wanfung
  review_cycle_days: 180
  last_review: 2026-07-02
  next_review: 2027-01-02
---

# NotebookLM — Google AI 笔记与来源整理工具

> **信息来源**: 抖音视频 + Web 搜索 + 完整教程文档
> **视频链接**: https://v.douyin.com/3Eei7IG6QeY/
> **官网**: https://notebooklm.google.com
> **底层模型**: Google Gemini 2.0
> **验证状态**: ✅ 通过 Web 搜索交叉验证
> **标签**: #AI笔记 #Google #Gemini #免费工具 #来源整理 #转录稿

---

## 核心定位

NotebookLM 不是通用聊天机器人，而是**来源整理工具**。

关键区别：
- **ChatGPT / Claude** — 自由构思、跨主题推理、改写 voice
- **NotebookLM** — 忠于来源、精确引用、转录稿、素材整合

> 它的回答**只来自你上传的 sources**。没上传的东西，它不会自己编。数据不足时甚至不会回复。

---

## 套餐与限制

| 方案 | Notebooks | Sources/Notebook | Chats/Day | Audio/Day |
|------|-----------|------------------|-----------|-----------|
| **Standard（免费）** | 100 | 50 | 50 | 3 |
| Plus | 200 | 100 | 200 | 6 |
| Pro | 500 | 300 | 500 | 20 |
| Ultra | 500 | 600 | 5,000 | 200 |

其他限制：
- 单文件上传上限：200 MB 或 50 万字
- Google Slides 上限：100 slides
- Google Sheets 限 100k tokens
- Slide Decks 与 Infographics 水印移除仅 Ultra

> **免费版结论**：个人转录稿、YouTube 摘要、研究整理已经够用。

---

## 支持的来源类型

| 来源 | 注意事项 |
|------|---------|
| PDF / Word / Markdown / Text | 结构清楚（标题、条列）效果最好 |
| Google Docs / Sheets / Slides | 静态快照，后续更新需手动 resync |
| 图片 | 文字识别视图片质量而定 |
| 音频文件（多格式） | 质量太差会 import 失败 |
| 网页 URL | 仅导入纯文字；图片、嵌入视频、付费墙不收 |
| YouTube 公开视频 | 需有字幕；上传 < 72 小时可能 import 失败 |
| Fast Research / Deep Research | 自动加 web / Drive 来源到 notebook |

---

## 输出功能选型

| 你要完成的事 | 优先功能 | 后续搭配 |
|-------------|---------|---------|
| 会议录音变会议记录 | 音频上传 → transcript | Claude / ChatGPT 整理决策与待办 |
| 一小时 YouTube 快速吃完 | YouTube source → 转录稿 / 章节大纲 | 大模型重组成笔记或文章 |
| 长报告变可听摘要 | Audio Overview | 自己听懂可以；公开发布要后期制作 |
| PDF / 课程数据变演示文稿初稿 | Slide Deck | Google Slides / Canva 修中文字与排版 |
| 研究素材互相比对 | Q&A + citation | Perplexity / Deep Research 补外部来源 |

---

## 最实用的功能：转录稿输出

转录稿是 NotebookLM 在实际工作流里**最值钱的单一功能**。

### 工作流

```
音频/YouTube 来源
      │
      ▼
  NotebookLM 导入
      │
      ▼
  Studio 产转录稿（自动分段、去赘词）
      │
      ▼
  复制到大模型（Claude / ChatGPT）
      │
      ▼
  最终分析、改写、抽结论
```

为什么要分两段：
- **NotebookLM** — 忠于来源、引用精确
- **大模型** — 跨段提取结论、重组叙事架构、写出符合品牌需求的文稿

---

## Audio Overview（播客生成）

把 3-5 份同主题来源放进 notebook，补上受众与聚焦指令，生成两人对谈音频。

- 英文自然度高，中文仍有机械感
- 适合通勤听报告、检查文章逻辑
- 公开发布需下载 MP3 / 转录稿后人工录制或后期制作

---

## 中文视觉输出的坑

| 输出类型 | 中文支持 | 备注 |
|---------|---------|------|
| 转录稿 / 摘要 | ✅ 可用 | 文字类输出稳定 |
| Audio Overview | ✅ 可用 | 中文有机械感但能听 |
| Slide Deck | ⚠️ 有问题 | CJK 文字常扭曲、模糊、字形错 |
| Infographics | ⚠️ 有问题 | 同上 |
| Video Overview | ⚠️ 有问题 | 字卡中文会扭曲 |

**绕道方案**：内容定稿后改用 Google Slides / Canva 排版。

---

## 推荐工作流：NotebookLM + 大模型搭配

| 阶段 | 工具 |
|------|------|
| 收集 / 探索 | ChatGPT、Perplexity、Gemini Deep Research |
| 来源整理 + transcript / citation | **NotebookLM** |
| 深度分析 / 改写 / 重组 | Claude、ChatGPT |
| 最终视觉 / 演示文稿 | Google Slides、Canva |

> 把每个工具放在它最擅长的阶段，不要强迫 NotebookLM 做它不擅长的事。

---

## 对 PAIOS 的价值

### 可直接应用的场景

1. **会议录音 → 会议记录** — 上传录音，产转录稿，再用大模型整理
2. **研究素材整合** — 多份 PDF 放入同一 notebook，做 Q&A 比对
3. **YouTube 学习** — 公开课/教程视频快速提取字幕和要点
4. **播客化复习** — 把报告变成 Audio Overview 通勤听

### 与 PAIOS 协同

```
素材来源（PDF/YouTube/音频）
      │
      ▼
  NotebookLM 整理 + citation
      │
      ▼
  大模型深度分析 / 改写
      │
      ▼
  归档到 PAIOS 20_KNOWLEDGE/
```

NotebookLM 可作为 PAIOS 知识入库前的**素材预处理层**：
- 原始素材（视频、录音、长报告）→ NotebookLM 转录稿/摘要 → 提炼后写入 PAIOS 知识库

---

## 访问方式

- **官网**: https://notebooklm.google.com
- **要求**: Google 账号
- **中国用户**: 需要网络代理访问
- **免费**: Standard 方案免费，基于 Gemini 2.0

---

## 参考链接

- [NotebookLM 完整教程（2026）— penchan.co](https://penchan.co/zh-cn/ai/notebooklm/)
- [NotebookLM 使用全攻略 — 知乎](https://zhuanlan.zhihu.com/p/2024809929429512807)
- [NotebookLM 使用教程 — aifreeapi.com](https://www.aifreeapi.com/zh/posts/notebooklm-usage-guide)
- [NotebookLM 从入门到精通（2026版）— 知乎](https://zhuanlan.zhihu.com/p/1996626099799613649)
