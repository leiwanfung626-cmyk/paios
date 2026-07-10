# PAIOS v1.0.1 升级回执

> **用途**：跟踪三个 PAIOS 实例的升级进度。
> **更新者**：Evan（平台维护者）
> **更新规则**：收到用户回传的 manifest.yaml 后，更新对应状态栏。
> **最终目标**：三栏全 ✅ 后，输出第一份 fleet.md 聚合周报。

---

## 升级状态总览

| Case | Core Version | profile.yaml | manifest.yaml | Manifest Received | 备注 |
|------|-------------|-------------|---------------|-------------------|------|
| **Case-01**（工作） | ✅ 1.0.1 | ✅ case-01/work | ✅ v1 | ✅ 2026-07-10 | 已提交 |
| **Case-02**（个人） | ✅ 1.0.1 | ✅ case-02/personal | ✅ v1 | ✅ 2026-07-10 | evan 本机 |
| **Case-03**（考研） | ⏳ — | ⏳ | ⏳ | ⏳ | 待升级 |

---

## 各案例详情

### Case-01（工作）

| 字段 | 值 |
|------|-----|
| instance.id | case-01 |
| profile.primary | work |
| core_version | v1.0.1 |
| manifest_version | 1 |
| 升级日期 | 2026-07-10 |
| manifest 回传 | ✅ 已收到 |
| 备注 | — |

### Case-02（个人）

| 字段 | 值 |
|------|-----|
| instance.id | case-02 |
| profile.primary | personal |
| core_version | v1.0.1 |
| manifest_version | 1 |
| 升级日期 | 2026-07-10 |
| manifest 回传 | ✅ 已收到 |
| 备注 | evan 本机（照片整理 + AI视觉） |

### Case-03（考研）

| 字段 | 值 |
|------|-----|
| instance.id | 待填写 |
| profile.primary | 待填写 |
| core_version | ⏳ |
| manifest_version | ⏳ |
| 升级日期 | ⏳ |
| manifest 回传 | ⏳ |
| 备注 | 等待用户升级 |

---

## 升级流程提醒

1. **通知用户**：发送 `upgrade-notice-1.0.1.md` 给 User2/User3
2. **用户操作**：`git pull` → 填 profile.yaml → `collect_manifest.py` → `git commit && git push`
3. **开发者收到** manifest → 更新本回执 → 放入 `Fleet/manifests/<case-id>.yaml`
4. **全部完成**后 → 输出 `Fleet/reports/fleet-2026-Wxx.md` 周报
