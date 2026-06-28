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
