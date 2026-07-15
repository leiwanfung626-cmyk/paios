type: handoff_packet
id: PAIOS-2026-0712-WORKBUDDY-GOVERNANCE-001
title: "WorkBuddy PAIOS 工作规则 — 自动遵守协议"
generated_at: 2026-07-12T17:00:00+08:00
generated_by: Reasonix
target_engine: WorkBuddy
baseline: v1.0.1

packet:

  context:
    system: PAIOS Platform — Personal AI Operating System
    engine: WorkBuddy
    workspace: "E:\PAIOS"
    data_root: "E:\QuarkSync"

  rules:

    - id: RULE-001
      name: "数据不进 PAIOS"
      description: "下载的文件、图片、视频不能放入 E:\PAIOS 目录"
      enforcement: |
        ❌ E:\PAIOS\ 根目录 → 禁止写入媒体/压缩包/可执行文件
        ✅ E:\QuarkSync\DATA\ → 原始素材放这里，classify_files.py 自动分类

    - id: RULE-002
      name: "Runtime 不进 Active"
      description: "虚拟环境、模型缓存、临时输出不能放在项目源码目录"
      enforcement: |
        ❌ 10_WORK\Active\项目名\.venv → 禁止
        ✅ 10_WORK\Runtime\项目名\.venv → 允许（随时可删）
        ✅ 70_TMP\项目名-cache\ → 临时缓存

    - id: RULE-003
      name: "衍生数据不进 Git"
      description: "ML 索引、嵌入向量、大体积 DB 不进入版本控制"
      enforcement: |
        ✅ 50_DATA\ → 本地衍生数据（不同步）
        ✅ 70_TMP\ → 临时产物（不同步）
        ❌ 禁止 git add 大体积二进制文件

    - id: RULE-004
      name: "外部数据源只读引用"
      description: "G:\workspace 和 H:\workspace 的业务数据只读不写"
      enforcement: |
        G:\workspace → 只读，通过 source.md 引用
        H:\workspace → 只读，按需迁移至 20_KNOWLEDGE 后标记 Legacy

  lifecycle_rules:

    work_layer:
      description: "10_WORK 工作层使用规范"
      structure: |
        Active/  → 当前项目源码和文档
        Runtime/ → .venv、缓存、临时输出
        Done/    → 已完成项目
      promotion: |
        工作成果具有长期价值时：
        - 结构化数据 → 50_DATA/
        - 知识资产   → 20_KNOWLEDGE/
        - 历史记录   → 80_HISTORY/

    bootstrap:
      description: "WorkBuddy 每次新会话执行"
      sequence: |
        1. 读取 E:\PAIOS\AI_STARTUP.md — 一页纸启动规则
        2. 读取 E:\PAIOS\README.md — 层模型
        3. 确认工作区为 E:\PAIOS

  required_actions:

    WorkBuddy:
      - action: "每次新会话先读 AI_STARTUP.md"
      - action: "创建文件前判断目标路径是否合规"
      - action: "下载文件写入 E:\QuarkSync\DATA\ 而非 E:\PAIOS\"
      - action: "创建项目时同步创建 Active/项目名 + Runtime/项目名"
      - action: "不将 .venv 放在 Active/ 下"
      - action: "不 git add 50_DATA/ 和 70_TMP/ 的内容"
      - action: "不写入 G:\workspace 和 H:\workspace"
