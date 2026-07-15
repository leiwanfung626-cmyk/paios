# SOP: Case-03 Pilot User 日常操作（User Daily Operations）

- **状态**：Active（2026-07-12 修订：适配三级角色模型，Case-02 已升级为 Developer）
- **日期**：2026-07-11（初版）· 2026-07-12（v2）
- **Owner**：Pilot User（Case-03 Study）
- **关联**：`ADR-0018`（角色模型 v2：Maintainer/Developer/Pilot User）· `../Governance/Operating-Model.md` · `ADR-0017`（平台纯度）· `SOP-2026-07-10-0001-Release-Flow.md`（发布流程）

---

## 一句话

你是 **Case-03（Pilot User）**，是平台用户，不是平台开发者。日常只写自己的 Workspace，完全不用管 Git；升级时 `git pull` 一下、跑下 collect、publish 一下就结束；想改平台就提 Issue，别自己动手。

> 如果你是 **Case-02（Developer）**，请参考 `SOP-2026-07-10-0001-Release-Flow.md`（Feature Branch 开发 + Proposal 流程）和 `../Governance/Operating-Model.md` 的 Developer 章节。

---

## ① 日常工作（完全不用管 Git）

正常做你的事：

- 写知识 -> `20_KNOWLEDGE/`
- 做项目 -> `10_WORK/`
- 拍照 / 整理 -> `Photos` / `Archive`
- 考研 / 学习 -> `20_KNOWLEDGE/Personal/`
- 记日更 -> `Today.md`

**全部写进你的 Workspace。完全不用管 Git，不用 commit，不用 push。**

> 你的 Workspace 与平台 Core 在权限上已隔离（ADR-0018 D2/D3）。你日常怎么改都不会污染平台。

---

## ② 平台升级（收到 Release 时）

收到 Maintainer 发布的 Release（如 `v1.0.2`）：

1. `git pull` —— 拉取新平台（**只拉，不推**）
2. 按需升级（填 `profile.yaml` / 跑脚本）
3. `collect_manifest.py` —— 生成本机 Manifest
4. `publish` —— 回流到 `F:\Fleet\incoming\`（out-of-band）
5. 结束。

**不要**：修改任何平台文件（`30_SYSTEM/` `40_AUTOMATION/` `RELEASES/` 等）。

---

## ③ 想到平台改进时

**铁律**：任何系统修改需求不得直接实现，只能以 Feedback 或 Issue 提出——一旦开始自己修，用户视角就消失了。

**不要**直接改：ADR / Automation / Registry / Architecture / SOP。

而是：

1. 记录（Issue / Feedback / Observation / Experience Report）
2. 发给 Maintainer（Case-01）
3. 由 Maintainer 决定是否进入 CASE -> ADR -> Blueprint -> Release
4. 你在下一轮 Release 中 `git pull` 获得能力

---

## ④ publish Manifest（状态回流）

- 每天 / 升级后运行：`collect_manifest.py` -> `publish`
- 流向：`F:\Fleet\incoming\case-XX.yaml`（按 `instance.id` 命名）
- Maintainer 负责统计 / 聚合；**你不用 merge，不用看 Fleet**。

---

## ⑤ 绝对不要改的文件（Platform Protected）

| 文件 / 目录 | 说明 |
|------------|------|
| `30_SYSTEM/` | ADR / 架构 / 治理 / 生命周期 / Registry |
| `40_AUTOMATION/` | 脚本 / 能力 / 注册表 / 安装 / 升级 |
| `RELEASES/` | 发布记录 |
| `CHANGELOG.md` / `SYSTEM_VERSION.md` | 平台元信息 |
| `reasonix.toml` / `DEPLOYMENT.md` 等根级平台文件 | 平台配置 |

**这些你只读。改了也白改（Maintainer 不会 pull 你的），还可能破坏你自己的环境。**

---

## ⑥ 一定可以改的文件（你的 Workspace）

`10_WORK/` / `20_KNOWLEDGE/Personal/` / `Today.md` / `Archive` / `Projects` / `Photos` —— **永远属于你**。

---

## ⑦ 什么时候允许改平台？

**只有 Maintainer 发布时。**

流程：你提需求 -> Maintainer 进入 CASE -> ADR -> Blueprint -> Release -> 你 `git pull` 升级。

**不是**你直接改。

---

## ⑧ 黄金纪律（背下来）

> **Workspace 可以每天变化；Platform 只能通过 Release 变化。**

---

## ⑨ 推荐工作流

```
Maintainer 发布 Release v1.0.x
        |
        v
Case-03（Pilot User）
git pull
   |
正常工作
   |
publish Manifest
   |
   v
F:\Fleet\incoming\（Maintainer 收集）
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
- ✅ 提 Issue / Feedback 给 Maintainer

---

_本 SOP 是 Case-03（Pilot User）的操作标准。Case-02（Developer）的操作见 `SOP-2026-07-10-0001-Release-Flow.md` 和 `Operating-Model.md`。_
