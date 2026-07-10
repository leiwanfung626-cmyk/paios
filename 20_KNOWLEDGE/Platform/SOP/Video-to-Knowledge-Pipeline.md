---
type: sop
topic: "视频捕获到知识入库全链路"
lifecycle: active
id: "SOP-2026-07-02-0001"
created: "2026-07-02"
updated: "2026-07-02"
revised: "2026-07-02 — Step 2 重写（抖音CSR反爬），新增 Step 2b 语音转写"
source: "REF-0001 + REF-0002 + REF-0004 实践总结"
tags: [sop, video, transcript, knowledge-capture, pipeline]
attributes:
  trigger: "用户提供视频链接（抖音/B站/YouTube）"
  owner: "wanfung 发起，AI 执行"
  avg_duration: "5-10 分钟"
  verified_runs: 3
  run_log:
    - "2026-06-29 CodeTrust (REF-0001)"
    - "2026-07-02 NotebookLM (REF-0002)"
    - "2026-07-02 自动化AI大脑 (REF-0004) — 首次使用 Playwright + Whisper 全链路"
    - "2026-07-06 Codex CLI 教程 (REF-0006) — 修复 ffmpeg PATH + 代理问题，v2.2"
extensions:
  related_refs: ["REF-0001", "REF-0002", "REF-0004", "REF-0006"]
  related_principles: ["#4 知识验证", "#8 工具独立"]
  triggers_direction: "DEC-2026-07-02-0001 方向1（多模态捕获层）"
---

# SOP: 视频捕获到知识入库全链路

## 适用场景

用户看到有价值的视频（抖音/B站/YouTube），想把内容变成 PAIOS 知识库中的永久资产。

## 一键执行脚本

抖音视频推荐使用自动 Pipeline 脚本：

```bash
python F:\PAIOS\40_AUTOMATION\09_LEGACY\original\douyin_full_pipeline.py --url <抖音链接>
```

该脚本已注册为 `SCRIPT-0004`（`scripts.yaml`），支持 3 层下载回退策略：
1. **yt-dlp**（从 Edge 浏览器获取 cookies）
2. **Playwright cookies + yt-dlp**
3. **Playwright 直接下载**（拦截 API）

自动执行：下载视频 → 提取音频 → Whisper 转写 → 保存文本到 `70_TMP/`

可选参数：
- `--model small|base|tiny|medium|large` — 指定 Whisper 模型（默认 small）
- `--file <本地路径>` — 跳过下载，直接转写本地视频文件

本 SOP 覆盖两种场景：
- **循环 A（认知循环）**：视频 → 研究 → 知识入库。SOP Step 1-7（含 Step 2b 语音转写）。
- **循环 B（实践循环）**：知识触发工具采用 → 用工具工作 → 工作产物回流 PAIOS。SOP Step 8-11。

循环 A 产出"知道"，循环 B 产出"做到"。不是每个视频都会进入循环 B——只有 Decision 中标记"采用"的工具才触发。

## 前提条件

- 用户提供视频链接
- AI 可访问 Web 搜索（用于交叉验证）
- PAIOS 知识库目录可写
- **ffmpeg**（已下载至 `70_TMP/ffmpeg.exe`；whisper 解码音频需要）
- **Playwright**（用于无头浏览器获取抖音 cookies + 拦截API获取视频/音频直链）
- **openai-whisper**（语音转写，推荐 base 模型）

## 全链路 8 步

### Step 1 — 捕获链接（Capture）

用户把链接丢进对话。

```
用户输入示例：
5.12 O@x.Sy 04/15 :0pm TyT:/ 零门槛玩转NotebookLM...
https://v.douyin.com/3Eei7IG6QeY/
```

AI 动作：
- 写入 `00_CAPTURE/Inbox.md`，标注日期和来源
- 不思考分类，不决定目录

### Step 2 — 信息提取（Extract）

#### 抖音特殊流程（平台 CSR 反爬）

抖音 2026 年已升级为全站 Client-Side Rendering + 混淆 JSVM，服务端 `WebFetch` 无法获取任何内容。改用以下三层策略：

| 手段 | 工具 | 可用性 |
|------|------|--------|
| `curl -L` 短链解析 → 提取 videoID | curl/built-in | ✅ 始终可用 |
| Playwright 无头浏览器加载页面，拦截 API 回包 | Playwright | ✅ 需 headless=False（抖音检测 headless） |
| WebSearch 视频描述关键词（hashtag + 标题片段） | WebSearch | ✅ 兜底方案（信息量取决于搜索命中率） |

#### 抖音视频/音频直链获取（Playwright 方案）

```python
# 核心逻辑
page.on('response', lambda r: handle_api(r))  # 拦截 /aweme/v1/web/aweme/detail 响应
await page.goto(video_url, wait_until='domcontentloaded')
await asyncio.sleep(5)  # 等待API响应

# 从 API 响应提取
video_urls = aweme['video']['play_addr']['url_list']   # 视频下载直链
audio_url  = aweme['music']['play_url']['url_list'][0]  # 音频下载直链
title      = aweme['desc']                               # 标题
author     = aweme['author']['nickname']                  # 作者
hashtags   = [t['hashtag_name'] for t in aweme['text_extra']]  # 标签
```

> ⚠️ Playwright 需要 `headless=False`（抖音检测 headless 模式）。
> ⚠️ 抖音视频直链有时效性（~1小时），下载需在获取后尽快进行。

#### WebSearch 兜底

当 Playwright 不可用时（如环境限制），使用 WebSearch 搜索视频描述中的 hashtag + 标题片段：

```
WebSearch: "每天省出一半工作时间 搭建自动化AI大脑 抖音"
```

提取目标（任一方案）：
- 视频标题和主题
- 视频描述/简介中的关键信息
- 标签关键词
- **视频/音频下载直链**（仅 Playwright 方案）

### Step 2b — 语音转写（Transcribe）

> 新增步骤 — 本 SOP 原始版本不含此步，REF-0004 首次跑通。

抖音视频/音频下载后，使用 **Whisper** 将语音转为文字文稿。

#### 下载音频

```python
import requests
# 使用 Playwright 获取的音频直链（.mp3）
r = requests.get(audio_url, headers={'Referer': 'https://www.douyin.com/'})
with open('70_TMP/douyin_audio.mp3', 'wb') as f:
    f.write(r.content)
```

> 也可下载视频（.mp4），whisper 同样支持视频文件直接输入。

#### 转写

```python
import whisper, os
os.environ['PATH'] += os.pathsep + os.path.abspath('70_TMP')  # ffmpeg 路径

model = whisper.load_model('base')  # base 模型速度/精度均衡
result = model.transcribe('70_TMP/douyin_audio.mp3', language='zh')

# 输出
print(result['text'])                     # 完整文稿
for seg in result['segments']:            # 按时间分段
    print(f'[{seg["start"]:.0f}s-{seg["end"]:.0f}s] {seg["text"]}')

# 保存
with open('70_TMP/douyin_transcript.txt', 'w', encoding='utf-8') as f:
    f.write(result['text'])
```

#### 注意事项

| 项目 | 说明 |
|------|------|
| 模型选择 | `tiny`（快但质量低）→ `base`（推荐）→ `small/medium`（更准但慢） |
| 语言 | 中文视频指定 `language='zh'` |
| ffmpeg | 必须可用（whisper 内部调用 ffmpeg 解码音频） |
| 输出 | 原始文稿 + 按时间分段 + 同步保存到 `70_TMP/` |
| 时长 | ~2-3 分钟视频用 base 模型转写约需 30-60 秒（CPU） |

#### 转写产物用途

- 完整文稿 → 分析视频内容、提取关键信息
- 分段时间戳 → 便于引用视频具体片段
- 原始转写文件 → 存档在 `70_TMP/douyin_transcript.txt`，归档时清理或移入知识库

用 WebSearch 搜索视频主题，找到至少 1 个独立来源验证：

验证清单：
- [ ] 视频提到的事实是否有独立来源确认？
- [ ] 工具/产品是否存在？（官网、npm、GitHub）
- [ ] 功能描述是否与官方文档一致？
- [ ] 有没有视频中没有提到但重要的限制？

置信度标注：
- `high` — 有官方文档 + 多个独立来源
- `medium` — 有部分独立来源，部分仅来自视频
- `low` — 仅来自视频，无法独立验证

### Step 3 — 交叉验证（Validate）

> 原 Step 3，编号未变。

用 WebSearch 搜索视频主题，找到至少 1 个独立来源验证：

验证清单：
- [ ] 视频提到的事实是否有独立来源确认？
- [ ] 工具/产品是否存在？（官网、npm、GitHub）
- [ ] 功能描述是否与官方文档一致？
- [ ] 有没有视频中没有提到但重要的限制？

置信度标注：
- `high` — 有官方文档 + 多个独立来源
- `medium` — 有部分独立来源，部分仅来自视频
- `low` — 仅来自视频，无法独立验证

转写文稿辅助验证：Step 2b 产出的完整文稿可用于精确提取视频中提到的工具名、术语、数据，辅助 WebSearch 精准搜索。

### Step 4 — 结构化写入 Reference（Store）

> 原 Step 4，编号+1。

写入 `20_KNOWLEDGE/References/` 目录，文件名格式：`{Topic}-{Descriptor}.md`

frontmatter 必填字段：

```yaml
ref_id: REF-XXXX
title: "工具/主题名称"
type: tool
lifecycle: active
created: YYYY-MM-DD
source: [douyin, web-search, official-doc]
tags: [...]
keywords: [...]
summary: >
  一句话概括
abstract: >
  3-5 句详细描述
verification:
  status: web-verified | partial | unverified
  scope: [验证了哪些方面]
  last_verified: YYYY-MM-DD
  evidence_chain: [来源链]
confidence: high | medium | low
```

正文结构：
```
# 标题
> 信息来源 + 视频链接 + 验证状态
---
## 核心内容（按主题分节）
## 对 PAIOS 的价值（可选）
## 参考链接
```

### Step 5 — 深度加工（Process）

判断这个 Reference 是否能产出更深层知识：

| 问题 | 如果"是" | 产物 | 位置 |
|------|---------|------|------|
| 视频内容能与已有知识对比吗？ | 写对比模型 | Model | 20_KNOWLEDGE/Models/ |
| 视频引发了改进方向吗？ | 写决策记录 | Decision | 20_KNOWLEDGE/Decisions/ |
| 视频介绍了一个可操作的方法吗？ | 写方法文档 | Method | 20_KNOWLEDGE/Methods/ |
| 视频解释了一个概念吗？ | 写概念文档 | Concept | 20_KNOWLEDGE/Concepts/ |

不是每个视频都要产出全部类型。CodeTrust 产出了 1 个 Reference，NotebookLM 产出了 1 Reference + 1 Model + 1 Decision。

### Step 6 — 索引更新（Route）

更新对应的 `_index.md`：

```
20_KNOWLEDGE/References/_index.md  → 加 REF-XXXX 行
20_KNOWLEDGE/Models/_index.md      → 加 KB-XXXX 行（如有）
20_KNOWLEDGE/Decisions/_index.md   → 加 DEC-XXXX 行（如有）
20_KNOWLEDGE/Concepts/_index.md    → 加 KB-XXXX 行（如有）
20_KNOWLEDGE/Methods/_index.md     → 加 KB-XXXX 行（如有）
```

### Step 7 — 日志记录（Evolve）

- `00_CAPTURE/Inbox.md` — 标记条目为 `[x]`
- `Today.md` — 加完成项
- `.workbuddy/memory/YYYY-MM-DD.md` — 追加工作日志

## 质量检查

入库前必须回答：

| 检查项 | 通过标准 |
|--------|---------|
| 来源标注 | evidence_chain 至少 2 个来源 |
| 交叉验证 | 至少 1 个独立来源 |
| 语音转写 | 抖音视频需有转写文稿（Step 2b 产物） |
| 置信度 | 已标注 high/medium/low |
| 未验证部分 | 已用 ⚠️ 标注 |
| frontmatter | 必填字段完整 |
| 索引更新 | 对应 _index.md 已更新 |

## 两个验证案例

### 案例 1：CodeTrust（2026-06-29）— SOP v1（无语音转写）

| 步骤 | 产物 |
|------|------|
| Capture | Inbox 条目 |
| Extract | WebFetch 抖音页面 + WebSearch CodeTrust |
| Transcribe | ⛔ 本 SOP 当时无此步骤 |
| Validate | npm 官方页面交叉验证，标注 Node.js 未安装 |
| Store | REF-0001 → References/CodeTrust-AI-CodeReview.md |
| Process | 无额外产物（信息足够完整，无需对比） |
| Route | References/_index.md 更新 |
| Evolve | 工作日志记录 |

产出：1 个 Reference。置信度 medium（环境缺 Node.js 无法本地运行）。

### 案例 2：NotebookLM（2026-07-02）— SOP v1（无语音转写）

| 步骤 | 产物 |
|------|------|
| Capture | Inbox 条目 |
| Extract | WebFetch 抖音页面 + WebSearch NotebookLM |
| Transcribe | ⛔ 本 SOP 当时无此步骤 |
| Validate | penchan.co 完整教程交叉验证，多来源确认 |
| Store | REF-0002 → References/NotebookLM-Google-AI-Notebook.md |
| Process | KB-2026-07-02-0001（对比模型）+ DEC-2026-07-02-0001（决策记录） |
| Route | 3 个 _index.md 更新 |
| Evolve | 工作日志 + Today.md 状态更新 |

产出：1 Reference + 1 Model + 1 Decision。置信度 high（多来源交叉验证）。

### 案例 3：自动化AI大脑（2026-07-02）— SOP v2（首次全链路 Playwright + Whisper）

| 步骤 | 产物 |
|------|------|
| Capture | Inbox 条目 |
| Extract | Playwright 拦截 API → 获取视频/音频直链 + title/author/hashtags |
| Transcribe | Whisper base 中文转写 → 完整文稿 + 时间分段 |
| Validate | WebSearch 关键词搜索 + 转写文稿辅助精确验证 |
| Store | REF-0004 → References/AI-Brain-LLM-Hardware-Display-Setup.md |
| Process | 无额外产物（主题与已有 REF-0003 互补，但不属于同一具体主题） |
| Route | References/_index.md 更新 |
| Evolve | 工作日志 + Today.md + Inbox 状态更新 |

产出：1 Reference。首次实现从视频语音到结构化知识资产的完整自动化链路。

## 判断：什么时候不值得走全链

### 单条过滤

以下情况只需转写到 Inbox，不走向知识库：

- 纯娱乐/搞笑视频
- 信息密度低（5 分钟视频 1 个点）
- 与 PAIOS 关注领域无关（AI/知识管理/禁毒工作/个人成长）
- 重复内容（已知信息的换壳复述）

单条判断标准：**如果你不会在 30 天后回头看这个内容，就不值得入库。**

### 主题层过滤：持续输入 ≠ 每条都建新条目

当同一主题的视频持续进入时，不按单条判断，按主题模式判断：

| 模式 | 判断 | 处理方式 |
|------|------|---------|
| 单条有价值 + 主题偶发 | 值得入库 | 走全链，建新 Reference |
| 单条一般 + 主题持续 | 值得入库 | **不建新条目，更新已有 Reference** |
| 单条有价值 + 主题持续 | 最理想 | 全链 + 持续丰富 + 提炼 Method |
| 单条无价值 + 主题偶发 | 不入库 | 转写到 Inbox 即可 |

"主题持续"的判定：**同一具体主题（非大标签）2 周内出现 2 次以上。**

"具体主题"的边界：
- "NotebookLM 使用技巧" — 是主题 ✅
- "AI 工具推荐" — 太宽，不是主题 ❌
- "CodeTrust 代码审查" — 是主题 ✅
- "AI 新星计划" — 是标签，不是主题 ❌

### 持续输入时的操作规则

当判断为"主题持续"时：

1. **第一条** — 正常走全链，建立 Reference
2. **后续条目** — 不建新 Reference，更新已有条目：
   - 新增信息补入对应章节
   - 更新 `updated` 日期
   - 在 `evidence_chain` 追加来源
   - 如果新信息足以改变结论，更新 `confidence`
3. **积累 3 条以上** — 评估是否提炼为 Method 或 Concept（跨来源归纳）

### 反模式

- 把"AI"当主题 → 什么都往里塞，Reference 变垃圾场
- 每条视频都建新 Reference → 同一工具 5 个碎片条目，不如 1 个完整的
- 只更新不回顾 → 累积太多更新后，回头提炼一次 Method/Concept

---

## 循环 B：实践循环（Step 8-11）

当循环 A 的 Decision 中标记为"采用"时，进入循环 B。

不是每个视频都会进入循环 B。CodeTrust 的 Decision 是"不部署"（环境缺 Node.js），所以停在循环 A。NotebookLM 的 Decision 中方向 1 已标记"已触发"，如果用户实际开始使用 NotebookLM 工作，就进入循环 B。

### Step 8 — 工具采用（Adopt）

用户根据循环 A 的知识，下载/注册/打开工具。

AI 动作：
- 在对应 Reference 的 frontmatter 中新增 `adoption.status` 字段
- 记录采用日期

```yaml
adoption:
  status: adopted    # adopted | not-adopted | pending
  date: 2026-07-02
  notes: "用户已注册 Google 账号并开始使用"
```

### Step 9 — 用工具工作（Work）

用户使用工具产生实际工作产物。

AI 不参与工具内部操作，但可以：
- 协助用户把工具产物导入 PAIOS（如帮整理 NotebookLM 导出的转录稿）
- 在用户报告使用体验时，记录到 Reference 的"使用经验"章节

### Step 10 — 工作产物回流（Return）

工具产生的工作产物作为**新 Input** 进入 PAIOS。

工作产物 ≠ 原始视频，它是用户用工具创造的实际输出。

| 工具 | 典型工作产物 | 回流方式 |
|------|-------------|---------|
| NotebookLM | 转录稿、摘要、分析报告 | 作为新 Input → Inbox → 二次加工 |
| CodeTrust | 代码审查报告 | 作为新 Input → Inbox → 二次加工 |
| 通用 | 导出的 PDF/Markdown/数据 | 作为新 Input → Inbox → 二次加工 |

回流时的处理规则：
- 工作产物进入 Inbox，**不建新 Reference**（工具本身已有 Reference）
- 按 SOP Step 2-5 走二次加工，产物通常是 Concept / Method / SOP
- 如果工作产物本身有独立价值（如一份完整的研究报告），可建新 Reference

### Step 11 — 经验沉淀（Distill）

使用工具 3 次以上后，评估是否提炼经验：

| 积累 | 可提炼为 | 位置 |
|------|---------|------|
| 使用技巧、最佳实践 | Method | 20_KNOWLEDGE/Methods/ |
| 工具适用/不适用场景 | 更新 Reference 的"适用场景"章节 | 同文件 |
| 工具与 PAIOS 协同的工作流 | SOP | 20_KNOWLEDGE/SOP/ |
| 使用中发现工具的局限 | 更新 Decision 或新建 Decision | 20_KNOWLEDGE/Decisions/ |

### 循环 A ↔ 循环 B 的关系

```
循环 A（认知）          循环 B（实践）
看视频 → 研究 → 入库 → 采用 → 工作 → 产物回流 → 经验沉淀
                ↑                                    │
                └──── 经验反过来更新 Reference ───────┘
                     confidence 从 medium → high
```

循环 B 的经验反过来丰富循环 A 的知识：
- Reference 的 confidence 从 medium 升级为 high（有了实际使用验证）
- evidence_chain 追加"actual-usage"来源
- Decision 中的"不实施"可能升级为"已实施"（如 CodeTrust 装了 Node.js 后）

### 案例：NotebookLM 的完整双循环（假设用户开始使用）

| 阶段 | 步骤 | 产物 |
|------|------|------|
| 循环 A | Step 1-7 | REF-0002 + Model + Decision ✅ 已完成 |
| 循环 B | Step 8 采用 | Reference 更新 adoption.status = adopted |
| 循环 B | Step 9 工作 | 用户用 NotebookLM 转录会议录音 |
| 循环 B | Step 10 回流 | 转录稿进入 Inbox → 二次加工 → 会议记录 Method |
| 循环 B | Step 11 沉淀 | 提炼"NotebookLM 会议记录最佳实践" Method |

最终产出：1 Reference（updated）+ 1 Model + 1 Decision + 1 Method = 从"知道"到"做到"的完整闭环。

---

## 项目级双循环：多教程 + 实践辅助 + 经验升级

上面的双循环是"单工具"级别——一个视频 → 一个工具 → 用一次。但更常见的场景是**项目级**：一个项目持续数天/数周，期间多个教程不断进入，PAIOS 同时做知识积累和实时辅助。

### 场景：AI 视频制作项目

#### Phase 1 — 第一个教程进入（循环A）

用户在抖音看到一个 AI 视频制作教程，丢链接给 PAIOS。

PAIOS 跑 Step 1-7：
- 建立 REF-0003（AI 视频制作工具/教程参考）
- Decision 标记为"采用"（用户打算跟着学）

此时 PAIOS 知识状态：
- References: REF-0003（confidence: medium）
- Methods: 0
- 能回答："这个教程讲什么？用什么工具？"

#### Phase 2 — 开始制作（循环B启动）

用户按教程开始制作视频。PAIOS 更新 REF-0003 的 `adoption.status = adopted`。

#### Phase 3 — 交叉积累（循环A和B交替跑）

制作过程中，用户持续发现新的教程：

| 时间 | 输入 | PAIOS 处理 | 产物 |
|------|------|-----------|------|
| 第1天 | 教程2: 配音技巧 | 主题层过滤 → 更新 REF-0003 | 新增"配音"章节 |
| 第3天 | 教程3: 剪辑节奏 | 主题层过滤 → 更新 REF-0003 | 新增"剪辑"章节 |
| 第5天 | 教程4: 特效制作 | 主题层过滤 → 更新 REF-0003 | 新增"特效"章节 |
| 第7天 | 教程5: 导出设置 | 主题层过滤 → 更新 REF-0003 | 新增"导出"章节 |

关键规则：
- **不建新 Reference** — "AI视频制作"是具体主题，所有教程更新同一个 REF-0003
- evidence_chain 持续追加来源
- 累积 3 条以上 → 触发 Method 提炼评估

#### Phase 4 — PAIOS 作为制作助手

制作过程中，用户随时向 PAIOS 提问：

| 用户问题 | PAIOS 的回答依据 | 回流方式 |
|---------|-----------------|---------|
| "字幕怎么同步？" | REF-0003 教程内容 + WebSearch | 追加到 REF-0003 使用经验 |
| "导出什么格式？" | REF-0003 教程内容 + 已有 Decisions | 追加到 REF-0003 使用经验 |
| "渲染太慢怎么办？" | WebSearch 补充 | 追加到 REF-0003 + 可能新建 Decision |
| "哪个配音工具好？" | REF-0003 + REF-0002（NotebookLM）交叉引用 | 更新 Decision |

每次问答都是一次**迷你循环A**：
- Capture（问题进入对话）→ Extract（搜索/基于已有知识）→ Validate（确认）→ Store（追加到 REF-0003）

但这些迷你循环不走完整 7 步——不建新条目，只更新已有 Reference 的"使用经验"章节。

#### Phase 5 — 视频完成，产物回流

视频制作完成。产物回流 PAIOS：

| 产物 | 类型 | 去向 |
|------|------|------|
| 成品视频 | 工作产物 | 70_TMP/ 或外部存储，PAIOS 记录路径 |
| 制作过程记录 | 工作日志 | 更新 Today.md + memory |
| 踩坑清单 | 经验 | REF-0003 新增"踩坑"章节 |
| 工具参数配置 | Decision | 20_KNOWLEDGE/Decisions/ |

#### Phase 6 — 经验沉淀

Step 11 触发。一个完整项目下来，PAIOS 新增/更新的知识：

| 知识类型 | 产物 | 位置 |
|---------|------|------|
| Reference | REF-0003 更新 5 次+，新增使用经验章节 | References/ |
| Method | "AI视频制作标准流程" — 从实践提炼 | Methods/ |
| SOP | "AI视频制作工作流" — 可复用的操作步骤 | SOP/ |
| Decision | "视频制作工具选型" — 哪些工具好用哪些不好用 | Decisions/ |
| Concept | "视频制作要素" — 配音/剪辑/特效/导出的关系 | Concepts/ |
| confidence | REF-0003 从 medium 升级为 high | frontmatter 更新 |

#### Phase 7 — 下次做视频（PAIOS 升级复用）

用户说"再做一个视频"。此时 PAIOS 已经不是白纸：

| 维度 | 第一次（Phase 1） | 第二次（Phase 7） |
|------|------------------|------------------|
| 工具知识 | 从零研究 | REF-0003 已有完整参考 |
| 制作流程 | 跟着一个教程走 | Method 已有标准流程 |
| 工具选型 | 不知道用什么 | Decision 已有选型记录 |
| 踩坑预警 | 无 | REF-0003 有踩坑清单 |
| 辅助能力 | 只能搜索回答 | 基于已有知识+经验回答 |
| confidence | medium | high |

PAIOS 可以主动建议：
- "上次你用 X 工具做配音效果不错，这次还用吗？"
- "上次导出时踩了 Y 的坑，这次注意避开。"
- "根据上次的 Method，建议按 Z 流程来。"

### 项目级 vs 工具级的区别

| 维度 | 工具级双循环 | 项目级双循环 |
|------|------------|------------|
| 触发 | 单个视频 → 单个工具 | 多个教程 → 一个项目 |
| 循环A | 跑一次 | 跑多次（每条新教程一次迷你循环A） |
| 循环B | 用一次工具 | 持续数天/数周的工作 |
| PAIOS角色 | 知识存储 | 知识存储 + 实时辅助 |
| 产物 | 1 Reference + 1 Method | 1 Reference（多次更新）+ Method + SOP + Decision + Concept |
| 升级 | confidence: medium → high | 整个知识图谱 richer，下次复用能力质变 |

### 核心洞察

**PAIOS 的价值不是单次循环，是循环的积累。**

第一次做视频：PAIOS 从零学习，用户从零摸索。
第二次做视频：PAIOS 有 Method、有 Decision、有踩坑清单，辅助能力质变。
第三次做视频：PAIOS 可能比用户更熟悉流程，主动提示和预警。

这就是 PAIOS Principle #10（Requirement Emergence）的体现——知识不是预先设计的，而是在实践中涌现的。每个项目的完成都让 PAIOS 更厚一层。
