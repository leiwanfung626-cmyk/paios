# 引擎运行时（40_AUTOMATION/11_ENGINES/）

引擎运行时配置与状态。与 Adapter（接口层）和 Engine Registry（注册表）配合使用。

**原则**：
- PAIOS 不保存引擎运行日志（属于引擎私有）
- 11_ENGINES 只保存引擎调度、运行时状态
- 具体执行过程在 `.reasonix/` `.workbuddy/` 等引擎私有目录

**目录**：
- `11_ENGINES/` — 引擎运行时配置、调度队列
- `04_ADAPTERS/` — Adapter 接口脚本（read_trace/export_context/probe）

参见：ADR-0017、00_REGISTRY/agents.yaml、00_REGISTRY/adapters.yaml
