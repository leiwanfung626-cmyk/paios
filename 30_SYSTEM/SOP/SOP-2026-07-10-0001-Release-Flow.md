# SOP: PAIOS 发布与多实例升级流程（v1.0.1 标准）

- **状态**：Active（v1.0.1 首次启用；Phase B 新增 publish 阶段）
- **日期**：2026-07-10（publish 阶段 2026-07-11 增补）
- **Owner**：Developer（Evan）
- **关联**：`ADR-0014`（升级机制）· `ADR-0015`（聚合与查看）· `ADR-0016`（架构基线）· `ADR-0017`（平台纯度 / 物理隔离）· `RELEASES/1.0.1.md` · `RELEASES/upgrade-receipt-1.0.1.md` · `F:\Fleet\README.md`

---

## 一句话

每次发版 = **Developer 提交并打 Tag → 用户 git pull 升级并回传 Manifest → Developer 拉取后 publish 到 Fleet → 人工生成 Fleet 周报**。Fleet 不回推用户。

数据流三阶段：**collect → publish → Fleet**（替代旧版含糊的「复制」表述）。

---

## 职责边界表（核心，所有决策由此导出）

| 组件 | 属于谁 | 是否同步给用户 |
|------|--------|----------------|
| **Core** | 平台（Developer 维护） | ✅ 是（`git pull`） |
| **Workspace** | 用户 | ❌ 否（各自维护，不入库） |
| **PAIOS-Usage（Manifest）** | 用户生成 | ✅ 仅 Manifest 回传给 Developer |
| **Release（Notes + Notice）** | 平台 | ✅ 所有用户同步（随 Core 仓库分发） |
| **Fleet（incoming / history / reports / stats / dashboards）** | Developer 运营 | ❌ 不同步给用户 |

---

## 标准流程（5 步 · v1.0.1 + publish 阶段）

```
① Developer                ② User2                  ③ User3
Commit & Tag v1.0.1         git pull                 git pull
（Core 仓库）               Upgrade                 Upgrade
  │                         (profile)               (profile)
  ▼                         (collect)               (collect)
Git Repository  ──►         commit                  commit
（Release + Core）          push PAIOS-Usage/       push PAIOS-Usage/
                              │                        │
                              └────────┐  ┌───────────┘
                                       ▼
                              ④ Developer Pull
                                 拿到三个 manifest（PAIOS-Usage/）
                                 publish → F:\Fleet\incoming\case-XX.yaml
                                 人工 fleet.md（F:\Fleet\reports\）
                                 旧数据归档（F:\Fleet\history\）
                                 commit（到 Fleet 目录）
                                       │
                                       ▼
                              ⑤ 结束 —— 不 push 回用户
```

1. **Developer 发布 v1.0.1**：在 Core 仓库 `Commit` + `Tag v1.0.1`。包含 Release Notes、Upgrade Notice、Core 代码。
2. **User2 `git pull`** → 升级（填 `profile.yaml` / 跑 `collect_manifest.py`）→ 生成 `PAIOS-Usage/manifest.yaml`（含 `manifest_version`）→ `commit` 仅 `PAIOS-Usage/` → `push`。
3. **User3** 同上（生成 `case-03`）。
4. **Developer `git pull`** → 取得三个 manifest → **publish** 复制到 `F:\Fleet\incoming\case-XX.yaml`（按 `instance.id` 命名）→ 人工聚合为 `fleet.md`（存 `F:\Fleet\reports\`）→ 历史 manifest / 旧周报归档至 `F:\Fleet\history\` → `commit` 到 Fleet 目录。
5. **结束**。不再 `push` 回用户——Fleet 不是 Core，用户不需要。

---

## 关键约束（铁律）

- **Manifest 单向流**：User → Developer。绝不反向。用户关心的是自己的 Self Dashboard，不是 Fleet Dashboard。
- **Manifest 发布（publish）**：用户 `git push` 自己的 `PAIOS-Usage/manifest.yaml` 后，Developer 拉取并 **publish** 到 `F:\Fleet\incoming\case-XX.yaml`（按 `instance.id` 命名）。这是 `collect → publish → Fleet` 单向流的中间步，替代旧版含糊的「复制」表述。
- **Push 范围**：用户只提交 `PAIOS-Usage/`（manifest + profile）。Workspace（知识 / 项目 / 照片）**不入库、不推送**。（Phase A 靠提交范围约束；Phase B 物理 Core/Workspace 拆分后由结构保证。）
- **Manifest 命名**：按 `instance.id` 命名（`case-01.yaml` / `case-02.yaml` / `case-03.yaml`），避免共享仓库同名文件互相覆盖。
- **Manifest 版本自声明**：manifest 自带 `manifest_version`（当前 1），Fleet 不解析兼容逻辑、只按声明版本归档；`collect_manifest.py` 升级时 bump 该字段。
- **Fleet 物理位置**：`F:\Fleet`（**独立于 `F:\PAIOS` Core 仓库**）。用户无此目录、不 pull。
- **升级回执**：`RELEASES/upgrade-receipt-1.0.1.md` 实时记录谁升级 / 谁回传，替代「靠记忆跟踪」。

---

## 与旧流程差异

| | 旧 | 新（本 SOP） |
|---|----|--------------|
| 谁升级了 | Developer 靠发微信问 / 记忆 | manifest 携带 `core_version` + 升级回执表可查 |
| Fleet 是否回推 | 无 Fleet 概念 | Fleet 独立、单向、不回推 |
| Manifest 中间步 | 含糊的「复制」 | 显式 **publish** 阶段：collect → publish → Fleet |
| 职责边界 | 模糊 | 上表钉死：Core 同步、Workspace 不碰、Manifest 单向、Fleet 私有 |

---

## 触发与演进

- 本 SOP 在 v1.0.1 首次启用；**publish** 阶段于 2026-07-11（Phase B Step 2）增补，对应 `F:\Fleet\incoming\` 新结构。
- **Phase B**（第二实例真实跑通）后：`collect_manifest.py` 输出富 schema（usage / assets / features）；`aggregate.py` 自动生成 `fleet.md`，本 SOP 第 ④ 步「人工聚合」被替代——但**职责表与单向流不变**。
- **Phase C**（远期）：HTTP API 模式若启用，仅替换 manifest 传输通道，职责边界不变。

---

_本 SOP 是平台级发布标准，任何后续版本（1.0.2 / 1.1.0 …）均沿用此 5 步结构与职责表。_
