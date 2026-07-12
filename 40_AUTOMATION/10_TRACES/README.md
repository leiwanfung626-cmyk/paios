# 跨引擎工作上下文继承（Cross-Engine Work Context Inheritance）

## 用途

`40_AUTOMATION/10_TRACES/` 是 PAIOS 的跨引擎继承中枢，采用四层架构：

```
Engine          → 各引擎保持私有目录，PAIOS 不碰
    ↓
Adapter         → 统一接口层（Read/Write/Export/Import Context）
    ↓
Task            → 平台级对象（Task = 可继承的工作单元）
                 handoff.yaml 是接力核心
    ↓
Knowledge       → 最终沉淀（ADR / 文档 / 知识）
```

## 目录结构

```
10_TRACES/
├── README.md                # ← 本文件：使用说明
├── artifact-schema.yaml     # Artifact 引用格式定义
├── task-schema.yaml         # Task 定义格式
├── handoff-schema.yaml      # 交接文件标准格式
├── adapter-schema.yaml      # Adapter 接口定义
├── handoff-template.yaml    # 交接文件模板示例
└── artifacts/               # Artifact 引用（轻量，指向引擎原生产物）
    └── YYYY-MM-DD-A.yaml    # 按日期命名 (A 后缀标记为 Artifact)
```

## Artifact 是什么

**Artifact 是引用，不是存储。** Artifact 只保存**引用**，不保存完整内容。

```
[Artifact 记录]
artifact_id: 20260711T090000-reasonix-1
engine: reasonix
type: conversation                          ← 产物类型
summary: 完成人脸检测
uri: .reasonix/session-xxx.json             ← 指向引擎原生产物
continuation: 见 handoff.yaml               ← 指向 Task 交接文件
```

可引用的产物类型包括：conversation、document、image、video、git_commit、issue、adr、milestone 等。

**原则**：Artifact 不保存产物的完整内容。内容只存在于 `uri` 指向的位置。

## Task 是什么

Task 是 **PAIOS 的跨引擎继承单元**。

每个 Task = `10_WORK/{task_id}/` 目录（与现有 7 层目录对齐）：

```
10_WORK/{task_id}/
├── inputs/           # 输入文件
├── outputs/          # 输出文件
├── notes.md          # 工作笔记
├── task.yaml         # 任务定义（不变信息）
└── handoff.yaml      # ← 交接文件（跨引擎接力核心）
```

**任何引擎打开 handoff.yaml 即可恢复上下文继续工作。**

## Handoff 接力流程

```
引擎 A 开始工作
  ↓ 写 handoff.yaml（current_step + 已完成 + 已知问题）
  ↓ 写 artifacts/ 记录（引用引擎原生产物）
  ↓

引擎 B 接手
  ↓ 读 handoff.yaml → 知道当前进度 + 下一步
  ↓ 读 artifacts/ 记录 → 了解历史工作
  ↓ 继续工作，更新 handoff.yaml
  ↓

引擎 C 接手...
```

## 与相关目录的关系

| 目录 | 角色 | 示例 |
|------|------|------|
| `10_WORK/{task}/task.yaml` | 任务定义（不变） | 目标、范围、创建时间 |
| `10_WORK/{task}/handoff.yaml` | 交接文件（可变） | 当前进度、已完成、下一步、已知问题 |
| `10_TRACES/artifacts/` | Artifact 引用（轻量） | 引擎 + 时间 + URI 引用 |
| `50_RUNTIME/adapters/` | 引擎适配器（接口层） | read_trace / export_context / probe |
| `50_RUNTIME/engines/` | 引擎运行时配置 | 引擎调度、状态 |
| `.reasonix/` | Reasonix 私有痕迹 | session JSON（内容实际存储处） |
| `.workbuddy/memory/` | WorkBuddy 私有日志 | Markdown 日志（内容实际存储处） |

## 相关文档

- ADR-0017: Cross-Engine Work Context Inheritance（四层架构标准）
- `00_REGISTRY/agents.yaml`（引擎注册表）
- `00_REGISTRY/workflows.yaml`（工作流注册表）
- `00_REGISTRY/adapters.yaml`（Adapter 注册表）
- `50_RUNTIME/adapters/`（Adapter 脚本）
