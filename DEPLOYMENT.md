# DEPLOYMENT — PAIOS 新电脑部署指南

> **目标**：从零开始在一台新电脑上部署 PAIOS
> **预计时间**：15-30 分钟

## 前置条件

- Git
- Python >= 3.10
- PAIOS 所在盘可用（或自定义路径）

## 部署步骤

### Step 1: 获取平台

```bash
git clone <remote> E:\PAIOS
```

### Step 2: 创建 Runtime 环境

```bash
cd E:\PAIOS
python -m venv .venv
.venv\Scripts\activate     # Windows
pip install --upgrade pip
```

### Step 3: Bootstrap 验证

```bash
# 运行诊断
python -m paios_installer doctor

# 运行完整性校验
python -m paios_installer validate
```

### Step 4: 确认状态

| 检查 | 预期 |
|------|------|
| Doctor Health Score | >= 90 |
| Validate Status | success (0 errors) |
| Registry | 5 YAMLs readable |
| Principles | 9 principles present |
| ADR | 2 ADRs present |

### Step 5: 开始使用

```bash
# 打开 Today.md，确认当天状态
# AI 工具设置 Workspace = E:\PAIOS
# 执行 Bootstrap: Principles → ADR → Registry → Manifest
```

## 跨电脑同步

参见 `SYNC_STRATEGY.md`

## 版本回退

```bash
git log --oneline
git checkout v1.0.0
```

## 常见问题

**Q: Python 版本不够**
A: 安装 Python 3.10+，确认 `python --version`

**Q: PAIOS 所在盘不存在**
A: PAIOS 可部署到任意路径，修改 AI 工具的 Workspace 设置即可

**Q: Doctor 报告 Ollama/FFmpeg 不存在**
A: 可选组件，不影响平台核心功能
