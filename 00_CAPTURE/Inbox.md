# 📥 Inbox — 统一入口

> **定位**：缓冲区（Buffer），不是仓库（Storage）
> **原则**：处理完成即清空
> **核心问题**：不要问"放哪里"，只问"交给 PAIOS 了吗？"

---

## Capture Pipeline 入口（2026-07-16 起）

结构化 AI 产出（文档/ADR/架构分析/研究/决策/Packet）统一经以下入口治理：

- **唯一入口**：`00_CAPTURE/inbox/`（命名 `YYYYMMDD-HHMMSS-source-type-title.md`）
- **助手**：`40_AUTOMATION/05_SCRIPTS/capture.py`（Stage-1+2，自动写 YAML 元数据）
- **晋升**：`40_AUTOMATION/05_SCRIPTS/classify_capture.py`（Stage-3，按 type 路由到 20/30/40）
- **禁止**：AI 日常产出不得直写 `20_KNOWLEDGE` / `30_SYSTEM` / `40_AUTOMATION`，必须先进 inbox 再晋升
- **原始素材桶**（保留）：`Daily / Images / Voice / Downloads / Imported` 仍可用作快速捕获
- **处理中间层**：`15_INBOX_PROCESSING/{classified,needs_review,failed}`

> ⚠️ **Capture Pipeline 数据边界**（ChatGPT 审查确认 2026-07-16）：
> - **排除**：外部工作产出数据 / 组织保密数据 / 受监管记录（按性质而非按盘符）
> - 禁毒宣传稿等敏感工作数据不走本便携管道，直达 G 盘
> - G 盘上的个人知识/项目仍可进入管道

---

## 2026-07-16

- [x] 抖音 @小戴AI学习「个人知识库应该怎么用」→ 20_KNOWLEDGE/Platform/Methods/Personal-KB-Usage-Data-vs-Cognitive.md ✅
- [x] 抖音「Vibe Coding项目部署：Docker部署与避坑指南」→ 20_KNOWLEDGE/Platform/Methods/VibeCoding-Docker-Deployment-Guide.md ✅

## 2026-07-15

- [x] 梁鸿作品集（三册）阅读分析 → 10_WORK/2026-07-15-梁鸿作品集/ ✅
- [x] 两本《底层逻辑》（张羽 vs 刘润）阅读分析对比 → 10_WORK/2026-07-15-底层逻辑对比/ ✅
- [x] 非暴力沟通 阅读分析 → 10_WORK/2026-07-15-非暴力沟通/ ✅

## 2026-07-08

- [x] OpenWrt 网络路由配置 + SSH 免密登录 ✅
- [x] mihomo/nikki 代理客户端安装（36节点，含香港/新加坡/美国/日本/台湾等） ✅
- [x] AdGuard Home 去广告 DNS 安装 + 配置 ✅
- [x] DNS 链配置：dnsmasq(53) → AdGuard Home(5353) → mihomo(1053) 全链路打通 ✅

## 2026-07-06

- [x] WorkBuddy 省积分攻略 — 老顽童周老师讲解选模式/强弱模型/控制范围等 → REF-0007 + Method(KB-2026-07-06-0001) 已归档 ✅

---
## 2026-07-03

- [ ] （待填）健康打卡 7月3日：晨压___/晚压___/服药✓/睡眠___h → Safety-Net/健康打卡.md
- [x] 抖音视频捕获：Agent 上下文占用率（Codex/WorkBuddy/Trae 使用提效）→ REF-0005 已归档 ✅

---

## 2026-07-02（已归档）

> 以下条目已全部处理完成，保留作为当日记录参考。

- [x] 工作环境初始化完成 ✅
- [x] NotebookLM 抖音视频捕获 → REF-0002 已归档 ✅
- [x] 抖音视频：蒸馏+vibecoding+智能体+超级个体+codex → REF-0003 已归档 ✅
- [x] 抖音视频：自动化AI大脑搭建 + LLM机制/AI硬件/显示方案 → REF-0004 已归档 ✅

> 注：0703 禁毒文件未走 Inbox 流程，按双盘协同规则直接路由到 G 盘工作方法与规范目录。

---

## 2026-06-29（已归档）

> 以下条目已全部处理完成，保留作为当日记录参考。

- [x] CodeTrust — AI代码缺陷检测开源工具 ✅ 已下载转写 → REF-0001
- [x] 统一入口原则 → 已写入 Principles.md（三条用户约定 + 四个统一） ✅
- [x] 认知升级："我负责输入，PAIOS 负责组织" → 已写入 Principles.md 核心心智模型 ✅
- [x] Inbox.md 创建完成 ✅

---

## 使用说明

1. 任何新输入先写在这里：想法、文件、对话、链接、截图、录音
2. 不思考分类，不决定目录
3. 系统根据生命周期自动路由：Work / Knowledge / Automation / Archive
4. 处理完成的项目标记 `[x]`，保留当日作为参考
5. 每天结束时，Inbox 应基本清空 — 内容已进入各自生命周期
