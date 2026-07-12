# 跨引擎手递实验报告

## 基本信息

| 字段 | 值 |
|------|-----|
| 实验编号 | EXP-001 |
| 日期 | 2026-07-11 |
| 引擎链路 | Reasonix → WorkBuddy |
| 类型 | 正向接力（不同引擎类型） |
| 任务 | TASK-20260711-001 |

## 实验步骤

| 步骤 | 引擎 | 动作 | 产出 |
|------|------|------|------|
| 1 | Reasonix | 创建 task.yaml + 目录结构 | `10_WORK/.../task.yaml` |
| 2 | Reasonix | Handoff 格式合规审查（9 项检查全部通过） | `outputs/handoff-compliance-report.md` |
| 3 | Reasonix | 写 handoff.yaml + artifacts 记录 | `handoff.yaml` + `2026-07-11-A.yaml` |
| 4 | WorkBuddy | 读 handoff.yaml，验证上下文继承 | `outputs/context-verification-report.md` |
| 5 | WorkBuddy | 更新 handoff.yaml + artifacts 记录 | `handoff.yaml` + `2026-07-11-A.yaml` |

## Exit Criteria 验证

| 标准 | 预期 | 实际 | 结果 |
|------|------|------|------|
| Q1: 能描述引擎 A 进度 | Reasonix 完成 2 步 | ✅ 准确识别：setup + handoff_compliance_review | PASS |
| Q2: 能识别下一步 | handoff_context_verification | ✅ 准确识别 step + input + engine_hint | PASS |
| Q3: 能列出已知问题 | 至少 1 条 | ✅ 准确列出 2 条（v2迁移 + context_id） | PASS |
| Q4: 上下文汇总 | 有 | ✅ context_summary 含 3 条关键信息 | PASS |

## 实验结论

**Handoff 机制验证通过。** Reasonix → WorkBuddy 双引擎手递实验证明：

1. **handoff.yaml v2 格式有效** — 5 个必填字段 + 7 个可选字段全部正确传递
2. **上下文可恢复** — WorkBuddy 零额外解释即还原完整工作上下文
3. **Artifact 索引正确** — 引擎原生产物 URI 可追溯
4. **known_issues 跨引擎传递** — 关键的人类知识没有丢失

## 后续建议

| 优先级 | 项目 | 说明 |
|--------|------|------|
| P0 | 扩展三组实验 | ChatGPT→Reasonix→WorkBuddy / 回环 / 多类型 |
| P1 | 实现 export_context / import_context Adapter 接口 | 当前仅 probe 和 read_trace 可用 |
| P2 | 实现 Scheduler 执行器 | 当前 policy/rules 是声明式配置 |

## 产出物清单

```
10_WORK/TASK-20260711-001/
├── task.yaml
├── handoff.yaml
├── outputs/
│   ├── handoff-compliance-report.md
│   └── context-verification-report.md
```

```
40_AUTOMATION/10_TRACES/artifacts/2026-07-11-A.yaml
  └── 2 条新 artifact 记录（reasonix-handoff-1 + workbuddy-handoff-1）
```
