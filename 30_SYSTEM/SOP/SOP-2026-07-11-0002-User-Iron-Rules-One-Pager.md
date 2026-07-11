# ⚡ PAIOS 用户铁律 · 开机一页纸（Case-02 / Case-03）

> 每次开机先瞄一眼这页，记住一句话：**你是平台用户，不是平台开发者。**

---

## 🔴 三条铁律（不可违反）

1. ❌ **不 `git push` Core** —— 你机器上只有 `git pull` 权限
2. ❌ **不 merge 远端**
3. ❌ **不编辑平台文件**（`30_SYSTEM/` `40_AUTOMATION/` `RELEASES/` 等）

> 写 Core 的能力**结构上不存在**于你的机器，所以你不会污染平台 —— 这不靠自律，靠机制。

---

## ✅ 你每天能做的事

- 写知识 → `20_KNOWLEDGE/`
- 做项目 → `10_WORK/`
- 考研 / 学习 → `20_KNOWLEDGE/Personal/`
- 记日更 → `Today.md`
- 拍照 / 整理 → `Photos` / `Archive`

**全部写进你的 Workspace。完全不用管 Git，不用 commit，不用 push。**

---

## 🔄 升级时（收到 Developer 发的 Release）

1. `git pull` —— 只拉，不推
2. 按需升级（填 `profile.yaml` / 跑脚本）
3. `collect_manifest.py` → `publish`
4. 结束

**不要**顺手改任何平台文件。

---

## 💡 想到平台改进？

不要自己改 ADR / Automation / Registry / Architecture。

→ 记成 **Issue / Feedback / Observation**
→ 发给 Developer（Case-01）
→ 他决定要不要进 CASE → ADR → Blueprint → Release
→ 你在下一轮 Release 里 `git pull` 就能拿到

---

## 🛡️ 受保护文件（只读，别碰）

`30_SYSTEM/` · `40_AUTOMATION/` · `RELEASES/` · `CHANGELOG.md` · `SYSTEM_VERSION.md` · `reasonix.toml` · `DEPLOYMENT.md`

> 改了也白改（Developer 不会 pull 你的），还可能弄坏你自己的环境。

## 🗂️ 永远属于你（随便改）

`10_WORK/` · `20_KNOWLEDGE/Personal/` · `Today.md` · `Archive` · `Projects` · `Photos`

---

## 🌟 黄金纪律（背下来）

> **Workspace 可以每天变化；Platform 只能通过 Release 变化。**

---

_完整操作见 `SOP-2026-07-11-0001-User-Daily-Operations.md`；角色与数据流见 `ADR-0018` / `Governance/Operating-Model.md`；可视化速览见 `User-Role-Model-Speed-View.html`。_
