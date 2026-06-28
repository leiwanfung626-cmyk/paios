# PAOS 5.0 核心规则 — WorkBuddy 执行手册

> 版本: v5.0 | 引擎: Reasonix | 更新: 2026-06-20
> 作用域: H:\workspace 全局 + G:\workspace 禁毒工作站

---

## 一、哲学规则（顶层）

1. **聊天记录 ≠ 知识库** — 对话是思考过程，经提炼才成知识
2. **不写代码替代 LLM** — 分类/去重/关联由 LLM 做，Python 只做文件操作
3. **不建数据库** — Markdown 文件就是数据库
4. **不依赖外部平台** — Reasonix 就是引擎
5. **多用少升** — 多用系统干活，不只升级系统

---

## 二、架构规则

### 目录结构

```
H:\workspace\
├── 总控台.md           ← 日常入口
├── AGENTS.md            ← 执行规则
├── README.md            ← 技术结构
│
├── 00_Inbox/            ← 待整理输入（每周清理）
├── 01_Projects/         ← 进行中项目
│   ├── 工作/禁毒/       ← G 盘索引页
│   ├── AI学习工程/
│   ├── Reasonix工程/
│   ├── 个人成长系统/
│   └── 父子成长计划/
├── 02_Knowledge/        ← 可复用知识 + source_material/
├── 03_Decisions/        ← 决策与复盘
├── 04_Archive/          ← 历史归档
├── 05_Templates/
├── Agents/
├── Automation/
├── Infrastructure/
│   ├── System/          ← 认证模块
│   ├── drs/             ← DRS 数字分身
│   ├── data/            ← 运行时数据
│   │   ├── TaskPool.json
│   │   ├── .runtime/
│   │   └── workbuddy_output/  ← WorkBuddy 产出归档（见双盘协同节）
│   └── scripts/
└── Prompts/
```

### 四层管理

| 层级 | 目录 | 内容 | 清理 |
|------|------|------|------|
| L1 ACTIVE | 01_Projects/ | 进行中项目 | 不清理 |
| L2 BUFFER | 00_Inbox/ | 待整理输入 | 每周 |
| L3 REFERENCE | 02_Knowledge/ + 03_Decisions/ | 知识 + 决策 | 只追加 |
| L4 ARCHIVE | 04_Archive/ | 已完成 | 永久保留 |

---

## 三、项目结构规则

每个项目固定**三件套**：

```
项目名/
├── 当前状态.md     ← 状态、进度、目标
├── 任务清单.md     ← 可执行任务（TaskPool 数据源）
└── 关键决策.md     ← 项目内决策记录
```

---

## 四、双盘协同规则（H 盘 + G 盘 + WorkBuddy）

### 三区架构

| 区 | 路径 | 角色 | 结构 |
|----|------|------|------|
| **H 盘** | `H:\workspace\` | PAOS 主系统 | 分层 PAOS 结构 |
| **G 盘** | `G:\workspace\` | 禁毒工作站 | 独立 PAOS 结构 |
| **WorkBuddy** | `C:\Users\liyun\WorkBuddy\` | 通用 AI 产出区 | 按会话时间戳组织 |

### 路由规则

| 话题 | 操作区 | 说明 |
|------|--------|------|
| 工作/禁毒（活动、报表、走访、626 等） | **G 盘** | 完整工作站，G 盘自有一套 PAOS 结构 |
| AI学习、Reasonix工程、个人成长、父子成长 | **H 盘** | 主系统 |
| 总控台 / 全局概览 | **两盘都读** | 先读 H 盘再补充 G 盘 |
| WorkBuddy 产出 | **H 盘归档** | 有价值产出由 Reasonix 桥接入库 |
| 不明确时 | **问用户** | "操作 H 盘还是 G 盘？" |

### WorkBuddy 产出归档流程

WorkBuddy 的 workspace 保持独立运行（C:/Users/liyun/WorkBuddy/），不做物理合并。桥接分两种方式：

#### 方式一：Reasonix 调用 WorkBuddy CLI 产出
Reasonix 知道产出的内容和价值，直接归档到知识库对应目录。

#### 方式二：定时扫描归档（兜底）
`Automation/archive_workbuddy.py` 由 Windows 任务计划程序定期调用（建议每天一次）：

```
扫描 C:/Users/liyun/WorkBuddy/ 中未归档的会话目录
  -> 复制到 H:/workspace/Infrastructure/data/workbuddy_output/
  -> 记录日志到 _archive_log.jsonl
  -> 物理文件留在原处不删除（WorkBuddy 不受影响）
```

Reasonix 在收到"整理 WorkBuddy 产出"指令时：
  1. 读 _archive_log.jsonl 查看新增内容
  2. 判断价值，有价值的提取到 02_Knowledge/ 对应领域
  3. 无价值的不处理

---


## 六、数据流规则

### 对话归档

```
对话 / "整理 Inbox"
  → 00_Inbox/YYYY-MM-DD/YYYY-MM-DD_<主题>.md
  → 分析内容
    ├ 有长期价值 → 02_Knowledge/<领域>/
    ├ 涉及决策   → 03_Decisions/
    ├ 属于项目   → 更新 01_Projects/<项目>/ 状态
    └ 无价值     → 标记不写入
```

### 知识库分类

- `02_Knowledge/<领域>/` ← 稳定知识条目（.md）
- `02_Knowledge/<领域>/source_material/` ← 原始素材（不提炼）

---

## 七、TaskPool 规则

文件: `Infrastructure/data/TaskPool.json`

| 字段 | 说明 |
|------|------|
| status | ACTIVE（最多 1 个）/ BUFFER / ARCHIVE |
| value/urgency/blocking/growth | VUBG 评分 0-10 |
| next_action | 下一步动作 |
| created_at / updated_at | 时间戳 |

**排序**：按 Vx0.4 + Ux0.3 + Bx0.2 + Gx0.1 降序，Top 1 置 ACTIVE。

| 分数 | 优先级 |
|------|--------|
| >= 8.0 | 最高 |
| >= 6.0 | 高 |
| >= 4.0 | 中 |
| < 4.0 | 低 |

---

## 八、文件操作规则

- **Reasonix 生成文档** → 转为 .docx 存一份到 H:\Desktop\归档
- **WorkBuddy 生成文档** → 转为 .docx 存一份到 H:\Desktop\归档
- **临时文件** → 用完清理
- **目录改名** → 同步更新 总控台.md 和相关索引
- **知识索引** → _index.md 随新增自动更新

---

## 九、敏感数据规则

- 不提交：users.json / .sessions/ / .chat-logs/ / .runtime/
- 运行时缓存统一放 Infrastructure/data/.runtime/

---

## 十、抖音 Pipeline

| 步骤 | 工具 | 说明 |
|------|------|------|
| 下载 | yt-dlp | 提取音频 |
| 转写 | whisper（small 默认） | 语音转文字 |
| 入库 | 生成知识条目 | 写入 02_Knowledge/<领域>/ |
