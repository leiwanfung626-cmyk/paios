---
type: methods
topic: "个人知识库用法：资料型 vs 认知型"
lifecycle: draft
id: "KB-2026-07-16-0001"
created: "2026-07-16"
updated: "2026-07-16"
source: "抖音 @小戴AI学习 — https://v.douyin.com/VUiqFwxmHls/"
source_asset: "AST-2026-0001"
tags: [methods, knowledge-base, knowledge-management, personal-OS]
attributes:
  media_type: douyin-video
  duration_sec: 168
  transcriber: whisper-base
  transcribed_at: "2026-07-16"
extensions:
  related_refs: []
  related_principles: ["#4 知识验证", "PAIOS 知识治理"]
verification:
  status: partial
  scope: ["方法论观点，非工具/事实类声明，未做独立事实交叉验证"]
  last_verified: "2026-07-16"
  evidence_chain: ["抖音 @小戴AI学习 视频 whisper 转写稿"]
confidence: medium
---

# Methods: 个人知识库的两种用法 — 资料型 vs 认知型

## 来源

抖音 @小戴AI学习，2026年视频。Whisper 语音转写。

## 核心观点

知识库的用法取决于你想解决什么问题，分为两种场景：

### 场景一：资料型个人知识库

**适用人群：** 有大量素材和材料的人，希望通过 AI 基于这些资料输出内容。

**流程：**

```
资料入库前 → 内容拆分（概念/方法论/观点/知识块）
         ↓
入库 → 形成网状结构（信息与信息相互关联）
         ↓
加入新内容 → 新知识块关联到已有网状结构
         ↓
提问 → AI 根据关键点从网状结构找到知识点
         ↓
通过关联关系找到其他相关内容 → 整合输出
```

### 场景二：认知型个人知识库

**适用人群：** 希望知识库成为自己的"第二大脑"，AI 不只是总结输出，还能理解自己的想法和意图。

**额外要求：**

> 需要对入库的内容进行复核 —— 加上自己的思考和判断。

**流程：**

```
资料 + 自己的判断 → 一起写入知识库
         ↓
AI 参考你的判断标准 → 输出与你的思考一致
         ↓
基于知识库内容继续讨论 → 检查/修正观点
         ↓
结合新资料 → 补充修正原有想法
         ↓
新判断 → 写回知识库 → 更新原内容
         ↓
同一观点可反复调用 → 与新资料产生联系
         ↓
在讨论中被修正 → 用于后续判断和输出
```

## 与 PAIOS 的对应

| 知识库类型 | PAIOS 对应 | 状态 |
|-----------|-----------|------|
| 资料型 | ADR Registry / 资产清单 | ✅ Phase-4 已完成 |
| 认知型 | ADR Master Registry + 治理决策（含 Evan 的判断） | ⏳ 待 Phase-5 |

## 关键句

> AI 知道很多事情，并不代表它知道你。
> 
> 真正让 AI 输出越来越符合你的，不只是知识库里的资料越来越多，更重要的是里面经过你判断的内容、你的观点越来越多。

## 对 PAIOS 的启示

PAIOS 当前处于"资料型知识库"阶段（Phase-4 完成了资产盘点），
向"认知型"演进需要在 Phase-5 加入 Evan 的判断和决策（canonical 选择、重复处理策略等），
这样 AI（Reasonix/ChatGPT）在后续协作中才能输出与 Evan 的思考一致的内容。

## 转写原文

见 `70_TMP/douyin_transcript.txt`（930 字，whisper base 模型转写）。
