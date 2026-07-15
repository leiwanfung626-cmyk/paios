# PAIOS v1.0.1 升级回执（Upgrade Receipt）

> **用途**：跟踪三个 PAIOS 实例的 v1.0.1 升级进度。
> **更新者**：Evan（平台维护者）
> **更新规则**：收到用户回传的 manifest.yaml 后，更新对应状态栏。
> **最终目标**：三栏全 ✅ 后，输出第一份 fleet.md 聚合周报。

---

## 升级状态总览

| Case | Core Version | profile.yaml | manifest.yaml | Manifest Received | 更新日期 |
|------|-------------|-------------|---------------|-------------------|----------|
| **Case-01**（工作） | ✅ 1.0.1 | ✅ case-01/work | ✅ v1 | ✅ 2026-07-10 | 2026-07-10 |
| **Case-02**（个人） | ✅ 1.0.1 | ✅ case-02/personal | ✅ v1 | ✅ 2026-07-10 | 2026-07-10 |
| **Case-03**（考研） | ✅ 1.0.1 | ✅ case-03/study | ✅ v1 | ✅ 2026-07-10 | 2026-07-10 |

> **所有 3/3 实例已升级并回传** ✅ —— W28 Fleet 周报已于 2026-07-11 输出。

---

## 各案例详情

### Case-01（工作）

| 字段 | 值 |
|------|-----|
| instance.id | case-01 |
| manifest 路径 | `F:\Fleet\incoming\case-01.yaml` |
| profile.primary | work |
| core_version | v1.0.1 |
| manifest_version | 1 |
| 回传日期 | 2026-07-10 |
| 备注 | 本机（Maintainer），profile 齐全 |

### Case-02（个人）

| 字段 | 值 |
|------|-----|
| instance.id | case-02 |
| manifest 路径 | `F:\Fleet\incoming\case-02.yaml` |
| profile.primary | personal |
| secondary | photo-organizing, ai-visual |
| core_version | v1.0.1 |
| manifest_version | 1 |
| 回传日期 | 2026-07-10 |
| 备注 | 唯一启用 Photo 的实例 |

### Case-03（考研）

| 字段 | 值 |
|------|-----|
| instance.id | case-03 |
| manifest 路径 | `F:\Fleet\incoming\case-03.yaml` |
| profile.primary | study |
| secondary | kaoyan, math, english, politics |
| core_version | v1.0.1 |
| manifest_version | 1 |
| 回传日期 | 2026-07-10 |
| 备注 | 资产最厚（References 16，Commits 27） |

---

## 收集验证

| 检查项 | 结果 | 数据源 |
|--------|------|--------|
| 三份 manifest 文件在检 | ✅ | `F:\Fleet\incoming/{case-01,case-02,case-03}.yaml` |
| manifest_version 一致 | ✅ | 全部 v1 |
| core_version 对齐 | ✅ | 全部 v1.0.1 |
| profile 完整 | ✅ | 三份均有 primary/secondary/owner |
| 可解析 | ✅ | 三份均为合法 YAML |
| 无冲突 | ✅ | instance.id 唯一、路径唯一 |

---

## 升级流程提醒（下一版本 v1.0.2）

1. **通知用户**：发送 upgrade-notice 给 User2/User3
2. **用户操作**：`git pull` → 填 profile.yaml → `collect_manifest.py` → publish manifest（out-of-band 至 `F:\Fleet\incoming\`）
3. **开发者收到** manifest → 更新本回执 → 放入 `Fleet/incoming/<case-id>.yaml`
4. **全部完成**后 → 输出 Fleet 周报
