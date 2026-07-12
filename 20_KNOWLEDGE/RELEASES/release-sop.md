# PAIOS 发布标准操作流程（Release SOP）

> **适用版本**：v1.0.1 起
> **适用范围**：所有 PAIOS Core 版本发布
> **核心原则**：用户不强制升级；Manifest 单向回流；Fleet 不同步给用户。

---

## 流程概览（5 步）

```
Developer:   Commit & Tag → Push (GitHub)
                                  │
                  ┌───────────────┼───────────────┐
                  ▼               ▼               ▼
              User-2 pull     User-3 pull     (更多用户)
                  │               │
                  ▼               ▼
              Upgrade         Upgrade
              (profile)       (profile)
              (manifest)      (manifest)
                  │               │
              git push        git push
                  │               │
                  └───────┬───────┘
                          ▼
                Developer pull manifests
                          │
                          ▼
                Fleet/cases/ 更新
                upgrade-receipt 更新
                fleet.md 周报
                          │
                          ▼
                    Commit & Push
                    （用户不再 pull）
```

---

## 详细步骤

### 第一步：开发者发布

1. 确保所有变更已测试、已文档化、已通过 Architecture Review
2. 更新：
   - `SYSTEM_VERSION.md` — 版本号 + 变更说明
   - `CHANGELOG.md` — 完整的变更日志
   - `RELEASES/<version>.md` — Release Notes（新增/影响/兼容性/迁移）
   - `RELEASES/upgrade-notice-<version>.md` — 给用户的升级通知
3. `git add` → `git commit -m "v<version>: <summary>"`
4. `git tag v<version>`
5. `git push`（含 tags）

### 第二步：用户升级

用户收到通知后，可选执行：

```bash
cd <PAIOS_DIR>
git pull                                          # 拉取新版本
# 填写 PAIOS-Usage/profile.yaml（按自身场景）
python 40_AUTOMATION/05_SCRIPTS/collect_manifest.py  # 生成 manifest
git add PAIOS-Usage/
git commit -m "v<version> upgrade: <user-id>"
git push                                          # 回传 manifest
```

### 第三步：开发者接收 Manifest

1. 用户 `git push` 后，开发者 `git pull`
2. 将用户的 `PAIOS-Usage/manifest.yaml` 复制到 `Fleet/manifests/<case-id>.yaml`
3. 更新 `RELEASES/upgrade-receipt-<version>.md` 对应状态栏

### 第四步：聚合周报

当所有用户的 manifest 都收到后：

1. 对比三份 manifest，汇总到 `Fleet/reports/fleet-<YYYY>-W<ww>.md`
2. 内容包括：版本分布、活跃天数、功能采用率、场景分类、风险提示

### 第五步：归档发布

1. `git add Fleet/ RELEASES/upgrade-receipt-*.md`
2. `git commit -m "release v<version>: fleet report + receipt"`
3. `git push`
4. **流程结束。用户不需要再次 pull**（Fleet 和回执是开发者运营数据）

---

## 数据流方向

```
┌──────────┐    Core/Release    ┌──────────┐
│ Developer│ ──────────────────▶│  User-2  │
│          │                    │          │
│          │◀───────────────────│ manifest │
│          │     git push       └──────────┘
│          │
│          │    Core/Release    ┌──────────┐
│          │ ──────────────────▶│  User-3  │
│          │                    │          │
│          │◀───────────────────│ manifest │
└────┬─────┘     git push       └──────────┘
     │
     │ Fleet/ + upgrade-receipt（不同步给用户）
     ▼
  Commit & Push（用户 no-op）
```

---

## 组件职责

| 组件 | 属于谁 | 是否同步给用户 |
|------|--------|---------------|
| **Core**（PAIOS 目录结构、脚本、配置） | 平台开发者 | ✅ 是 |
| **Release**（CHANGELOG、RELEASE、Upgrade Notice） | 平台开发者 | ✅ 是 |
| **Workspace**（10_WORK、20_KNOWLEDGE 等用户资产） | 用户 | ❌ 各自维护 |
| **PAIOS-Usage**（profile + manifest） | 用户生成 | ✅ 仅 manifest 回传给开发者 |
| **Fleet**（manifests 副本、cases、reports） | 开发者运营 | ❌ 不同步给用户 |
| **upgrade-receipt** | 开发者运营 | ❌ 不同步给用户 |

---

## 版本号规范

```
v<major>.<minor>.<patch>

major：架构性变更（需新 ADR + 架构冻结审查）
minor：功能性新增（非破坏性，向后兼容）
patch：Bug 修复、文档、配置调整
```

当前版本：v1.0.1（minor，非破坏性功能新增）
