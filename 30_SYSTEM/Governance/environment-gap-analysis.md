# Environment Gap Analysis — 运行环境差异

> **阶段**: Phase 3 — Governance
> **日期**: 2026-07-15
> **注意**: 本文件记录构建时已知的环境差异。Phase 4 Stabilize 验证时需补充完整。

---

## 1. 硬件层

| 维度 | 当前构建机 (H:) | PC-A (feng) | PC-B (evan) |
|------|----------------|-------------|-------------|
| 盘符 | H: | F: | E: |
| 类型 | 本地盘 (196G/157G可用) | 本地盘 (346G/343G可用) | SSD (391G/349G可用) |
| 目的 | 构建 + 验证 | 原 Case-01 运行机 | 原 Case-02 运行机 |

## 2. 软件层（待 Phase 4 确认）

| 依赖 | 本机 | PC-B (evan) | 说明 |
|------|------|-------------|------|
| Python | 3.13.14 | 待确认 | 需两侧版本兼容 |
| Git | 2.54.0 | 待确认 | 需两侧版本兼容 |
| PAIOS_DRIVE | 未设置 | E | 新系统需改为 PAIOS_ROOT |
| reasonix | 已配置 | 待确认 | 需重新绑定到 H:\ |
| workbuddy | 已配置 | 待确认 | 需重新绑定到 H:\ |

## 3. 外部工具路径

| 工具 | 本机 | 说明 |
|------|------|------|
| FFmpeg | 待确认 | 照片/视频处理依赖 |
| Pandoc | 待确认 | 文档转换依赖 |
| QuarkSync | 待确认 | 文件同步依赖 |

## 4. 环境变量要求

新系统需要在每台运行机上设置：

```bash
# PAIOS-PORTABLE 路径协议
export PAIOS_ROOT="H:/PAIOS-PORTABLE/Core"    # 根据实际盘符修改
export PAIOS_ASSET_ROOT="H:/PAIOS-PORTABLE/ASSETS"
```

## 5. 不可迁移的运行时

以下运行时不作为 PAIOS 资产迁移，需在每台机器上独立配置：

- Python 解释器 + 依赖包
- AI 引擎 (reasonix / workbuddy)
- API Keys (DeepSeek / GLM)
- Git 客户端配置
- 外部工具 (FFmpeg / Pandoc)
- SSH 密钥
- 代理配置
