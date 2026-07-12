# Task Packet

> 指派具体开发/修改任务。由 Architect 发出，Developer 接收并执行。

```yaml
task:
  id: "PAIOS-YYYYMMDD-NNN"
  title: "[简短的标题]"

background: |
  为什么需要做这件事？
  当前状态 + 触发原因 + 关联上下文。

question: |
  需要解决什么问题？

current_decision: |
  已经确定的方案（如有）。

need: |
  需要修改哪些文件/模块？
  - 文件 1
  - 文件 2

constraints: |
  约束条件：
  - 不修改的范围
  - 必须遵守的原则（如 Platform Purity）
  - 兼容性要求

expected_output: |
  期望的输出：
  - 修改后的文件
  - Diff
  - 风险说明
```
