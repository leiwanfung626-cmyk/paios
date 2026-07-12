# Review Packet

> 发起审查请求。由 Developer 发出，Reviewer 接收并审查。

```yaml
review:
  author: "[提交审查的引擎]"
  target: "[被审查的文件/模块]"

summary: |
  修改了什么？一句话概括。

question: |
  需要 Reviewer 重点关注什么？
  例如：是否违反 Platform Purity？架构是否一致？

need_feedback:
  type: "architecture / code / independent"
  focus: "审查焦点描述"

context: |
  补充上下文（如有）。
```
