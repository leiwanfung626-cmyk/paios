# Context Packet

> 任务在引擎间流转时携带的上下文信息。
> 由当前引擎发出，下一个引擎接收。不超过一页。

```yaml
context:
  version: 1.0
  task_id: "PAIOS-YYYYMMDD-NNN"
  from: "[当前引擎]"
  to: "[下一个引擎]"

background: |
  任务背景——一句话说清楚前因。

current_state: |
  当前进展到哪一步了？
  已完成什么？未完成什么？

decision: |
  已经做过的关键决策（如有）。

open_question: |
  尚待解决的问题（如有）。

expected_output: |
  期望下一个引擎产出什么。
```
