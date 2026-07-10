# PAIOS v1.0.1 升级回执（Upgrade Receipt）

> **作用**：实时跟踪三位用户是否已升级、是否已回传 Manifest。比聊天记录或记忆更可靠，也为用户数量增长打下基础。
> **维护者**：Developer（Evan）。每次用户回传 manifest 后更新对应行。
> **关联**：`RELEASES/1.0.1.md` · `30_SYSTEM/SOP/SOP-2026-07-10-0001-Release-Flow.md`

## 状态图例

- ✅ = 已完成
- ⏳ = 待处理
- 🚫 = 已拒绝 / 不需升级（备注原因）

## 回执表

| Case | 主场景 | 使用者 | Core Version | Profile | Manifest | 状态 |
|------|--------|--------|--------------|---------|----------|------|
| Case-01（工作） | work | user-a | ✅ 1.0.1 | ✅ | ✅ | 完成 |
| Case-02（个人） | personal | user-b | ⏳ | ⏳ | ⏳ | 待升级 |
| Case-03（考研） | study | user-c | ⏳ | ⏳ | ⏳ | 待升级 |

## 更新规则

1. 用户 `git pull` 并 `git commit` 含 `PAIOS-Usage/manifest.yaml`（`core_version: 1.0.1`）→ 勾选 **Core Version ✅ + Manifest ✅**
2. 用户填好 `PAIOS-Usage/profile.yaml` → 勾选 **Profile ✅**
3. 三者齐全 → **状态**改"完成"
4. 拒升级者 → 状态标 🚫 并备注原因（不影响其正常使用）

## 汇总（每次更新后重算）

- 已升级：1 / 3
- 已回传 Manifest：1 / 3
- 待跟进：Case-02、Case-03

---

_本回执随升级进度持续维护；新用户加入时在此表追加行即可。_
