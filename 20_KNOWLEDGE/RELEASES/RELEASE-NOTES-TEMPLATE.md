# PAIOS vX.Y.Z Release Notes

**发布日期**：YYYY-MM-DD
**类型**：（Non-breaking 功能新增 / Breaking 结构变更 / 安全修复）
**兼容性基线**：`core_version` A.B.C → X.Y.Z
**角色模型**：ADR-0018（Case-01 Maintainer / Case-02-03 User，单向流，见 `30_SYSTEM/Governance/Operating-Model.md`）

---

## 新增（What's New）

| 模块 | 说明 | 关联 |
|------|------|------|
| （填写） | （填写） | （ADR / SOP / SCRIPT） |

---

## 影响（Impact）

- （填写：是否破坏性、老用户是否需要动作）

---

## 📋 用户须知（Case-02 / Case-03 必读）

> 你是**平台用户**，不是平台开发者。升级后请花 1 分钟看这一节。

### 三条铁律（不可违反）
1. ❌ 不 `git push` Core（你机器上只有 `git pull` 权限）
2. ❌ 不 merge 远端
3. ❌ 不编辑平台文件（`30_SYSTEM/` `40_AUTOMATION/` `RELEASES/` 等）

### 升级后你要做的
1. `git pull` —— 只拉，不推
2. 按需升级（填 `profile.yaml` / 跑脚本）
3. `collect_manifest.py` → `publish`
4. 结束

### 完整资料（建议收藏）
- 一张图看懂 → `30_SYSTEM/SOP/User-Role-Model-Speed-View.html`
- 开机一页纸 → `30_SYSTEM/SOP/SOP-2026-07-11-0002-User-Iron-Rules-One-Pager.md`
- 想开机自动提醒？把 `30_SYSTEM/SOP/User-Boot-Reminder.cmd` 的快捷方式放进 Windows 启动文件夹

> 🌟 黄金纪律：**Workspace 可以每天变化；Platform 只能通过 Release 变化。**

---

## 需要用户做（Required Action）

（填写：必做 / 可选，约几分钟）

---

## 兼容性（Compatibility）

| 维度 | 版本/状态 |
|------|-----------|
| **Core** | >= X.Y.Z |
| **Manifest (FIM)** | v1 协议 |
| **Workspace** | 完全兼容旧用户数据，无需迁移 |
| **Migration** | （填写） |

---

## 升级流程（用户侧，三步）

1. **收到通知**：开发者发布本 Release Notes + 升级通知，随 Core 仓库 `git pull` 自动送达。
2. **自行决定**：读完"影响"与"用户须知"，选择是否执行。
3. **声明版本**：执行 `collect_manifest.py` 后，`manifest.yaml` 自动携带新 `core_version`，汇总方即知已升级。

---

**Related**：`ADR-0018` · `30_SYSTEM/Governance/Operating-Model.md` · `30_SYSTEM/SOP/SOP-2026-07-11-0001-User-Daily-Operations.md` · `30_SYSTEM/SOP/User-Role-Model-Speed-View.html` · `30_SYSTEM/SOP/SOP-2026-07-11-0002-User-Iron-Rules-One-Pager.md` · `CHANGELOG.md` · `SOP-2026-07-10-0001-Release-Flow.md`
