# ASSETS 资产索引

> **定位**：所有**非禁毒素材**（视频 / 音频 / 图片 / 文档 / 转写稿等原始生成物）的统一归档地，与知识库物理隔离。
> **适用范围**：本规则适用于一切非禁毒素材类型——原素材必须先归 ASSETS，加工模块才进知识库。
> **禁毒例外**：禁毒素材（涉密图片/视频/文档/业务产出）不进 ASSETS、不进 D 盘知识库，按双盘数据边界规则（D-001）仅落 G 盘。
> **铁律**：原素材**绝不进入知识库**（`20_KNOWLEDGE`）。知识库只接收经 Capture Pipeline 加工后的模块。
> **本索引是唯一权威**：负责溯源、去重、防知识库膨胀。每条原素材 ↔ 其加工出的知识模块在此一一对应。

## 分类规则

```
路径：ASSETS/{种类}/{门类}/{年份}/
命名：{YYYYMMDD}-{门类}-{来源}-{slug}.{ext}
```

- **种类 category**：`video` 视频 / `audio` 音频 / `image` 图片 / `text` 文本（转写稿/文档）
- **门类 genre**：`tech` 科技 / `reading` 读书 / `life` 生活 / `health` 健康 / `study` 学习 / `drug` 禁毒 / `growth` 个人成长 / `work` 工作 / `other` 其他
- **来源 source**：`douyin` / `bilibili` / `youtube` / `other`
- **slug**：短标题标识，视频与对应转写稿共用同一 slug 以便溯源

## 资产 ID

`AST-{年份}-{4位序号}`，如 `AST-2026-0001`。入库时由 `40_AUTOMATION/05_SCRIPTS/asset_store.py` 自动分配。

## 索引表

| 资产ID | 种类 | 门类 | 年份 | 来源 | 原链接 | 资产路径 | 转写稿 | 处理状态 | 对应知识模块 |
|--------|------|------|------|------|--------|----------|--------|----------|--------------|
| AST-2026-0001 | video | tech | 2026 | douyin | https://v.douyin.com/VUiqFwxmHls/ | video/tech/2026/20260716-tech-douyin-xiaodai-personal-kb.mp4 | text/tech/2026/20260716-tech-douyin-xiaodai-personal-kb.txt | promoted | 20_KNOWLEDGE/Platform/Methods/Personal-KB-Usage-Data-vs-Cognitive.md |

## 统计

- 总素材数：1（视频 1 / 文本 1 属同一资产）
- 已加工(promoted)：1
- 待加工(raw)：0
- 知识库直接存放原素材：0（违反铁律，必须为 0）

---
_最后更新：2026-07-17_
