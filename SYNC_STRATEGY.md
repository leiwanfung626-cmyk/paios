# SYNC_STRATEGY — PAIOS 跨设备同步策略

> **适用场景**：两台或多台电脑共享同一个 PAIOS 平台
> **核心原则**：Platform 同步，Runtime 本地

## 同步分层

| 层 | 内容 | 同步方式 | 说明 |
|-----|------|---------|------|
| **平台层** | `30_SYSTEM/`、`40_AUTOMATION/`、根文档 | Git | 必须一致 |
| **知识层** | `20_KNOWLEDGE/` | Git | Markdown/YAML 文本资产 |
| **工作层** | `10_WORK/` | Git（文档）+ 同步盘（大文件） | 项目结构同步，大文件走云盘 |
| **入口层** | `00_CAPTURE/` | Git（同步但清空） | 缓冲区，不成为历史仓库 |
| **归档层** | `90_ARCHIVE/` | Git（文本）+ 云盘（附件） | 防仓库膨胀 |
| **外部引用** | `60_EXTERNAL/` | 独立管理 | 不纳入主仓库 |
| **运行时** | `70_TMP/`、`50_DATA/`、`venv/` | ❌ 不同步 | 每台电脑独立 |

## 两台电脑初始化流程

1. 电脑A：`git init` → `git add` → `git commit` → `git tag v1.0.0`
2. 电脑A：创建 remote（GitHub / GitLab / 自建）
3. 电脑A：`git push`
4. 电脑B：`git clone <remote> F:\PAIOS`
5. 电脑B：创建本地 Runtime（`70_TMP/`、`50_DATA/`、`venv/`）
6. 电脑B：`python -m paios_installer doctor`
7. 电脑B：`python -m paios_installer validate`

## 日常同步流程

```bash
# 开始工作前
git pull

# 工作完成后
git add <changed directories>
git commit -m "description"
git push
```

## 冲突处理

- Markdown/YAML 冲突：手动合并，保留双方有价值的内容
- Python 冲突：按代码合并流程处理
- 二进制文件：不同步，不存在冲突

## AI 工具工作区约定

- 所有电脑统一：`F:\PAIOS`
- Bootstrap 路径一致：Principles → ADR → Registry → Manifest

---

# 推荐架构：GitHub + 夸克云盘双轨同步

> **适用场景**：两台电脑轮流办公，无需多人同时编辑
> **上线时间**：2026-06-30
> **状态**：✅ 已启用

## 职责分工

| 内容 | 同步方式 | 说明 |
|------|---------|------|
| PAIOS 系统 (`30_SYSTEM/`, `40_AUTOMATION/`, 根文档) | GitHub | 版本管理，人工 commit/push |
| 知识库 (`20_KNOWLEDGE/`) | GitHub | Markdown/YAML 文本资产 |
| Prompt、脚本、配置 | GitHub | 随系统一起版本化 |
| 业务资料 (Excel/Word/PDF/图片/录音) | 夸克云盘 | 自动同步，无需手动操作 |
| 运行时 (`70_TMP/`, `50_DATA/`, `venv/`) | ❌ 不同步 | 每台电脑独立，首次手动创建 |

## 目录布局

```
电脑A
│
├── F:\PAIOS              ← GitHub 同步
│   ├── 50_DATA/          ← 本地运行时（不同步）
│   └── 70_TMP/           ← 本地缓存（不同步）
│
└── F:\QuarkSync\DATA     ← 夸克云盘自动同步
        ├── 项目档案/      ← 按项目分类（需填写项目清单）
        ├── 个案档案/      ← 文件名含「个案」「案主」
        ├── 工作报告/      ← 文件名含「月报」「报告」「总结」
        ├── 财务资料/      ← 文件名含「财务」「发票」「报销」
        ├── 媒体素材/      ← .jpg/.png/.mp4 等媒体文件
        ├── 归档/         ← 超过 30 天未修改的文件
        └── 模板/         ← 常用模板

电脑B（同上，夸克自动同步后完全一致）
```

## 新电脑首次配置

### 1️⃣ 安装软件

- Git
- Python（如果需要）
- 夸克云盘（登录同一账号）

### 2️⃣ 克隆 PAIOS

```bash
git clone https://github.com/leiwanfung626-cmyk/paios.git F:\PAIOS
```

### 3️⃣ 等待夸克同步

夸克云盘同步目录（例如 `F:\QuarkSync\DATA`）同步完成后，两台电脑的业务数据完全一致。

### 4️⃣ 创建本地运行时目录

```bash
mkdir F:\PAIOS\50_DATA
mkdir F:\PAIOS\70_TMP
```

> Git 不同步运行时目录，每台电脑只需创建一次。

## 每日工作流程

### 🔵 开始工作

```
① 等待夸克同步完成（确认状态：同步完成）
② git pull（获取另一台电脑修改的系统/知识/配置）
```

### 🔴 结束工作

如果修改了系统文件（`30_SYSTEM/`、`20_KNOWLEDGE/`、Prompt、脚本、配置等）：

```bash
git add -A
git commit -m "更新内容"
git push
```

> 如果今天只处理了 Excel/Word/PDF/图片等业务文件，无需任何操作——夸克已自动同步。

### 🔄 第二台电脑继续工作

```
打开电脑 → 等待夸克同步 → cd F:\PAIOS → git pull → 继续工作
```

## 最佳实践

- **业务数据**：统一放在夸克同步目录下（如 `F:\QuarkSync\DATA`），PAIOS 只引用不管理
- **避免冲突**：尽量不两台电脑同时编辑同一个业务文件，减少夸克产生冲突副本
- **版本管理**：Git 只管理系统/知识/规则/配置，业务数据不进入 Git 仓库
- **无需记忆**：日常只需记住两个步骤——开始工作时「等同步 + git pull」，结束时「add + commit + push」

---

## 自动分类脚本

> 将文件丢到 `F:\QuarkSync\DATA` 根目录，脚本自动归类到对应中文文件夹。

**脚本位置**：`F:\PAIOS\40_AUTOMATION\05_SCRIPTS\classify_files.py`

### 用法

```bash
# 试运行（先看看会怎么分，不实际移动）
python F:\PAIOS\40_AUTOMATION\05_SCRIPTS\classify_files.py --dry-run

# 实际分类
python F:\PAIOS\40_AUTOMATION\05_SCRIPTS\classify_files.py
```

### 分类规则（优先级）

| 优先级 | 规则 | 目标文件夹 |
|--------|------|-----------|
| 1 | `.jpg/.png/.mp4` 等媒体文件 | `媒体素材/` |
| 2 | 文件名含「个案」「案主」 | `个案档案/` |
| 3 | 文件名含「月报」「报告」「总结」「汇报」 | `工作报告/` |
| 4 | 文件名含「财务」「发票」「报销」「账单」 | `财务资料/` |
| 5 | 以**已知项目名**开头 | `项目档案/项目名/` |
| 6 | 超过 30 天未修改 | `归档/` |
| ⚠️ | 匹配 **多个** 规则 → 留在根目录，手动处理 | `DATA/` |

### 项目清单

在 `F:\PAIOS\QuarkSync\PROJECT_LIST.md` 中填写项目名，脚本会自动识别以项目名开头的文件。格式：

```markdown
- 项目A名称
- 项目B名称
```
