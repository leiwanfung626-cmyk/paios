# Proposal: Add PILOT-ROLE-VALIDATION Evidence to Manifest

## Background
Pilot Exit 条件要求 Case-02/03 角色验证完成。当前无标准化反馈通道让实例通知 Maintainer「验证已完成」。

## Solution
在 Manifest 的 `evidence` 字段中新增一种标准证据类型 `PILOT-ROLE-VALIDATION`。实例完成角色验证后运行 `collect_manifest.py`，生成的 manifest 中携带该证据，回流到 Fleet。

## Impact
- 修改 `collect_manifest.py`：新增 `--add-evidence` 参数
- 不修改 Manifest Schema，复用现有 `evidence[]` 数组

## Risk
低——仅新增参数，不改变现有行为

## Completion Criteria
- [ ] `collect_manifest.py --add-evidence PILOT-ROLE-VALIDATION "note"` 能在 manifest 中增加证据行
- [ ] 生成的 manifest YAML 合法
- [ ] 不影响现有 evidence 结构
