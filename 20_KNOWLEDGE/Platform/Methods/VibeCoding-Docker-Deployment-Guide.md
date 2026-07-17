---
type: methods
topic: "Vibe Coding 项目 Docker 部署与避坑指南"
lifecycle: draft
id: "KB-2026-07-17-0001"
created: "2026-07-17"
updated: "2026-07-17"
source: "抖音 — https://www.douyin.com/video/7663292888863821075"
tags: [methods, docker, deployment, vibe-coding, devops]
attributes:
  media_type: douyin-video
  duration_sec: ~600
  transcriber: whisper-base
  transcribed_at: "2026-07-17"
extensions:
  related_refs: []
  related_principles: []
---

# Methods: Vibe Coding 项目 Docker 部署与避坑指南

## 来源

抖音视频，Whisper 语音转写，约 10 分钟，4620 字。

## 核心观点

Docker 不一定是适合所有人，尤其是没有技术背景、只会跟着 AI 操作的人。

> Docker 把简单放在了启动那一刻，把复杂留在了后面的维护里。

---

## 一、Docker 到底简化了什么

| 方式 | 说明 | 优点 | 缺点 |
|------|------|------|------|
| 原生部署 | 直接装语言环境/系统工具/依赖到服务器 | 透明 | 步骤多 |
| Docker | 镜像 → 容器，Compose 编排 | 标准化、可重复 | 黑盒难排查 |

核心概念：
- **镜像 (Image)**：提前配好的安装包
- **容器 (Container)**：镜像跑起来的样子
- **Dockerfile**：定义镜像怎么制作
- **Compose (docker-compose.yml)**：定义多个容器怎么一起运行

---

## 二、部署前必须完成的 5 件事

1. **读懂项目** — 弄清前端/后端/数据库/缓存分别怎么运行
2. **检查服务器** — 系统版本、CPU 架构、磁盘、端口、Docker/Compose 是否安装
3. **放好配置** — 密码/令牌不能写进镜像，数据库/上传文件用数据卷持久化
4. **制作镜像 → 启动容器**
5. **接上域名和 HTTPS**

---

## 三、部署后必须验收的 5 件事

1. **容器状态** — 不只是"正在运行"，还要检查日志、后端连数据库、服务不崩溃
2. **真实功能测试** — 登录、保存数据、上传文件 — 整条业务链路都通才算
3. **重启与重建验证** — 存一条测试数据 → 重启/重建容器 → 数据还在才算持久化生效
4. **端口检查** — Compose ports / Docker 实际发布端口 / 云服务器安全组，三个地方一致
5. **备份与恢复验证** — 有备份文件不代表能恢复，实测一次恢复流程

---

## 四、新手最容易踩的 5 个坑

| 坑 | 问题 | 解决 |
|----|------|------|
| 数据没持久化 | 数据存在容器可写层，删除容器数据跟着丢 | 挂载数据卷，重建后验证数据还在 |
| 端口开太多 | Compose ports 默认监听所有网卡，可能绕过防火墙 | 数据库/缓存只在 Docker 内部网络访问，不给公网端口 |
| 容器内临时修改 | 改了文件但容器重建后就消失 | 改 Dockerfile/Compose 配置，不进容器改 |
| 权限过大 | 高权限运行、挂载 Docker 控制接口、挂载重要目录 | 逐项审查，不需要就去掉 |
| 资源没限制 | 容器可能抢占全部 CPU/内存 | 设置资源上限，留出余量 |

---

## 五、关键建议

> 用不用 Docker，不看那条启动命令有多短，要看命令背后的东西你和 AI 能不能管得住。

**给 AI 的提示词模板（见转写原文第 3 节）：**
先检查 → 再给方案 → 最后才动手。不要甩一句"帮我用 Docker 部署"就让 AI 直接在服务器上开干。

## 转写原文

见 `70_TMP/vibecoding_docker_transcript.txt`（4620 字，whisper base 模型转写）。
