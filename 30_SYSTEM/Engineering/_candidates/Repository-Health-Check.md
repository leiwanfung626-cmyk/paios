# Design Exploration: Repository Health Check

> **状态**：Candidate（设计评估，未实现）
> **评估日期**：2026-07-12
> **评估结论**：Option B — 接受为未来能力，等待触发条件
> **关联 Packet**：PAIOS-2026-0712-REPO-HEALTH-001

---

## 评估摘要

| 维度 | 判定 | 理由 |
|------|------|------|
| 必要性 | 低 | 当前规模（35 commits, ~150 docs, 3 instances）下 Git + 人工检查足够 |
| 现有重叠 | 高 | Git status / Fleet / Pilot Report 已覆盖大部分检查项 |
| 推荐阶段 | Pilot Exit 后 | Engineering Pilot Day 02，不应引入新系统 |
| 是否需要 ADR | 否 | 证据不足 |

## 唯一增量价值

「孤立文档/重复资产检测」是目前治理盲区，但当前规模下手动可查。

## 触发条件

当以下条件**任一**满足时，可重新评估：

- `30_SYSTEM/` 文件数超过 100
- 出现至少 1 次「找不到对应 ADR 的文档」事故
- 多实例间 baseline 不一致且未被现有流程发现

## 实施边界（如果触发）

- **只读**：仅生成报告，不删除/移动/修改任何文件
- **单脚本**：不引入数据库或监控系统
- **输出到**：`60_HISTORY/HealthReports/`（未来）
- **人工决策**：报告由 Maintainer 审阅，不自动执行任何操作

## 参考

- 现有 Git 状态检查：`git status` / `git branch -vv`
- 现有实例对齐：`v1.1.0-pilot-baseline` tag + Fleet manifest
- 现有索引完整性：`collect_manifest.py` 自动扫描 ADR-INDEX.md
