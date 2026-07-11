# SOP: Case-02 / Case-03 平台用户日常操作（User Daily Operations）

- **状态**：Active（2026-07-11 启用，ADR-0018 落地）
- **日期**：2026-07-11
- **Owner**：Platform User（Case-02 Personal / Case-03 Study）
- **关联**：`ADR-0018`（角色模型）· `../Governance/Operating-Model.md` · `ADR-0017`（平台纯度）· `SOP-2026-07-10-0001-Release-Flow.md`（Developer 侧发布）

---

## 一句话

你是**平台用户**，不是平台开发者。日常只写自己的 Workspace，完全不用管 Git；升级时 `git pull` 一下、跑下 collect、publish 一下就结束；想改平台就提反馈，别自己动手。

---

## ① 日常工作（完全不用管 Git）

正常做你的事：

- 写知识 → `20_KNOWLEDGE/`
- 做项目 → `10_WORK/`
- 拍照 / 整理 → `Photos` / `Archive`
- 考研 / 学习 → `20_KNOWLEDGE/Personal/`
- 记日更 → `Today.md`

**全部写进你的 Workspace。完全不用管 Git，不用 commit，不用 push。**

> 你的 Workspace 与平台 Core 在权限上已隔离（ADR-0018 D2/D3）。你日常怎么改都不会污染平台。

---

## ② 平台升级（收到 Release 时）

收到 Developer 发布的 Release（如 `v1.0.2`）：

1. `git pull` —— 拉取新平台（**只拉，不推**）
2. 按需升级（填 `profile.yaml` / 跑脚本）
3. `collect_manifest.py` —— 生成本机 Manifest
4. `publish` —— 回流到 `F:\Fleet\incoming\`（out-of-band）
5. 结束。

**不要**：修改任何平台文件（`30_SYSTEM/` `40_AUTOMATION/` `RELEASES/` 等）。

---

## ③ 想到平台改进时

**不要**直接改：ADR / Automation / Registry / Architecture。

而是：

1. 记录（Issue / Feedback / Observation）
2. 发给 Developer（Case-01）
3. 由 Developer 决定是否进入 CASE → ADR → Blueprint → Release
4. 你在下一轮 Release 中 `git pull` 获得能力

---

## ④ publish Manifest（状态回流）

- 每天 / 升级后运行：`collect_manifest.py` → `publish`
- 流向：`F:\Fleet\incoming\case-XX.yaml`（按 `instance.id` 命名）
- Developer 负责统计 / 聚合；**你不用 merge，不用看 Fleet**。

---

## ⑤ 绝对不要改的文件（Platform Protected · 只读）

| 文件 / 目录 | 说明 |
|------------|------|
| `30_SYSTEM/` | ADR / 架构 / 治理 / 生命周期 / Registry |
| `40_AUTOMATION/` | 脚本 / 能力 / 注册表 / 安装 / 升级 |
| `RELEASES/` | 发布记录 |
| `CHANGELOG.md` · `SYSTEM_VERSION.md` | 平台元信息 |
| `reasonix.toml` · `DEPLOYMENT.md` 等根级平台文件 | 平台配置 |

**这些你只读。改了也白改（Developer 不会 pull 你的），还可能破坏你自己的环境。**

---

## ⑥ 一定可以改的文件（你的 Workspace）

`10_WORK/` · `20_KNOWLEDGE/Personal/` · `Today.md` · `Archive` · `Projects` · `Photos` —— **永远属于你**。

---

## ⑦ 什么时候允许改平台？

**只有 Developer 发布时。**

流程：你提需求 → Developer 进入 CASE → ADR → Blueprint → Release → 你 `git pull` 升级。

**不是**你直接改。

---

## ⑧ 黄金纪律（背下来）

> **Workspace 可以每天变化；Platform 只能通过 Release 变化。**

---

## ⑨ 推荐工作流（你这一侧）

```
Developer 发布 Release v1.0.x
        │
   ──────────────
Case-02          Case-03
git pull         git pull
   │                │
正常工作          正常工作
   │                │
publish Manifest  publish Manifest
   └───────┬────────┘
           ▼
      F:\Fleet\incoming\（Developer 收集）
```

整个过程你**不需要 merge、不需要 push 平台、不需要维护 Core**。你唯一需要"向上"提供的是：**运行反馈（Issue）** 和 **Manifest（状态）**。

---

## 铁律（不可违反）

- ❌ 不 `git push` Core（你只有 pull 权限）
- ❌ 不 merge 远端
- ❌ 不编辑 `30_SYSTEM/` `40_AUTOMATION/` `RELEASES/` 等平台文件
- ❌ 不自行升级平台结构
- ✅ 写 Workspace（随便写）
- ✅ `git pull` 升级
- ✅ `collect_manifest` + `publish` 回流状态
- ✅ 提 Issue / Feedback 给 Developer

---

_本 SOP 是 Case-02/03 的用户侧操作标准，任何版本沿用此结构。平台侧发布见 `SOP-2026-07-10-0001-Release-Flow.md`。_

**配套速览（随 Release 分发）**
- 一张图看懂：`<../SOP/User-Role-Model-Speed-View.html>`（角色表 + 单向流 + 黄金纪律）
- 开机一页纸：`<SOP-2026-07-11-0002-User-Iron-Rules-One-Pager.md>`（铁律 + 每日操作）
