# Usage Trace 目录

AI 知识使用行为的运行时追踪记录。

## 定位

Usage Trace 是 PAIOS Memory Loop 的 Runtime Evidence 层。它记录 AI 引擎在使用 PAIOS 知识资产时的行为（检索、引用、验证等），为后续分析和系统演化提供证据输入。

**Usage Trace 不等于知识。** Trace 是原始使用记录，90 天保留，仅经过人工治理分析后有价值的内容才晋升到 `20_KNOWLEDGE/`。

## 文件格式

每个 trace 是一个 YAML 文件，命名 `UT-YYYYMMDD-NNNN.yaml`，存放在 `YYYY-MM-DD/` 子目录下。

schema 见 `PKT-EXE-20260719-002` §4。

## 脚本

`40_AUTOMATION/05_SCRIPTS/usage_tracker.py`

```bash
# 记录一次使用
python usage_tracker.py record \
  --session SESSION-001 \
  --task "考研规划" \
  --actor Buddy \
  --action retrieve \
  --assets "ADR-0017,adr" "定位共识v2.1,knowledge"

# 查询今日 traces
python usage_tracker.py list

# 查询指定日期
python usage_tracker.py list --date 2026-07-19
```

## 保留策略

- **保留期**：90 天
- **清理方式**：手动（v0.1 不实现自动删除）
- **晋升目标**：经过分析 + Human Governance 后 → `20_KNOWLEDGE/`

## 数据流

```
AI Session → record_usage() → UT-YYYYMMDD-NNNN.yaml
                                    │
                              (90 天后手动清理)
                                    │
                         分析有价值 → Knowledge Candidate
                                    │
                           Human Governance → 20_KNOWLEDGE/
```
