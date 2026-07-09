# PAIOS 架构与维护审查报告

- **审查日期**：2026-07-09
- **审查范围**：F:\PAIOS 全量（目录结构、配置、脚本、治理文档、git 同步状态）
- **方法**：文档意图（README / MANIFEST / ADR-0003 / SYNC_STRATEGY）vs 实际状态逐层对比；全量 Python 语法/编码编译校验；git 状态与历史核对
- **前提**：架构已于 2026-06-29 冻结（ADR-0002 / ADR-0003），结构性变动须满足解冻条件（3+ 个月连续使用 / 真实项目暴露同构问题 / 明确收益且迁移成本可接受）。本次审查区分「可直接维护」与「需 Evan 决策的结构性事项」。

---

## 0. 摘要

PAIOS 核心架构健康：**所有 8 个 Python 脚本编译通过，无语法/编码错误**；7 层生命周期骨架（00→90）清晰且运行有效。主要问题集中在**文档与现实的漂移**、**少量未文档化的目录**、**同步卫生**与**治理记录过期**，均属可修复的维护性缺陷，未触及架构内核。

**本次已执行的维护（详见第 6 节）**：
- `.gitignore` 增补 `50_DATA/`、`50_IMPORT/`（运行时目录防误提交）
- `00_REGISTRY/scripts.yaml` 注册 3 个未登记的活动脚本（SCRIPT-0006~0008）
- `10_MANIFEST/manifest.yaml` 与 `inventory.yaml` 刷新脚本计数 5→8 及日期
- `ADR-INDEX.md` 移除从未存在的幽灵条目 ADR-0001，并加注说明

---

## 1. 架构与目录问题（高）

### 1.1 未文档化的顶层目录 + 重复数字前缀
ADR-0003 定义的规范顶层为 7 层 + 2 辅助（60_EXTERNAL、70_TMP），实际多出 3 个顶层目录，且与规范目录**数字前缀冲突**：

| 目录 | 状态 | 是否规范 | 问题 |
|------|------|----------|------|
| `40_AUDIT/` | 仅含空子目录 `CodeTrust/`（0 文件） | ❌ 非规范 | 与 `40_AUTOMATION` 重复前缀 `40_`；违反 Principle #6（顶层数量控制） |
| `50_IMPORT/` | 含 `Imported/`、`Pending/`、`Verified/`（导入流水线，0 文件） | ❌ 非规范 | 与 `50_DATA` 重复前缀 `50_` |
| `Claw/` | 空目录（本次会话创建，无文件） | ❌ 非规范 | 被 `reasonix.toml` 与 `archive_workbuddy.py` 引用 → ** intentional 但未文档化** |

> 注：早期 Glob `F:\PAIOS/*` 误报（大小写/模式问题），经 `ls` 复核确认上述目录均真实存在。

**建议**：架构冻结期内**不删不改结构**，在 `30_SYSTEM/Evolution/` 或本 Governance 目录追加一份「辅助目录说明」记录 `Claw/`、`40_AUDIT/`、`50_IMPORT/` 的用途，待满足解冻条件时正式写入 ADR-0003 增补条款。`40_AUDIT/CodeTrust/` 为空，可清空保留目录或合并进 `90_ARCHIVE` 审计记录。

### 1.2 文档盘符不一致（E:\ vs F:\）
- `MANIFEST.json`、`paths.yaml`、`reasonix.toml`、各 `ADR` 已正确改用环境变量 `${PAIOS_DRIVE}`（evan=E / feng=F），实际运行在 `F:\PAIOS` ✅
- 但 `DEPLOYMENT.md`、`SYNC_STRATEGY.md` 全文硬编码 `E:\PAIOS` 与 `E:\QuarkSync\DATA`，与当前 `F:` 实况不符，且 git 历史显示曾做过 E→F 迁移（commit `03b0134` 仅改了 reasonix.toml）

**建议**：将两份部署文档中的 `E:\PAIOS` 统一改为 `${PAIOS_DRIVE}:/PAIOS`（与 `paths.yaml` 一致），避免新电脑部署时路径错误。

---

## 2. 文档与治理不一致（中）

### 2.1 ADR-0001 幽灵引用（已修复索引，引用待清）
- `git log --all` 确认 `ADR-0001`（Core API Freeze）**从未入库**，文件从未创建
- `ADR-INDEX.md` 原将其列为 `Active`；`Necessity_Impact_Audit.md` 已自述「不含 ADR-0001」→ 内部矛盾
- 另有 `99_Appendix.md`、`06_Governance.md`、`05_Decision_Layer.md`、`ADR-0003` 仍引用 ADR-0001 为存在

**已处理**：`ADR-INDEX.md` 移除 ADR-0001 行并加注（2026-07-09）。
**待办**：统一清理上述 4 处过期引用（建议全局替换说明「ADR-0001 未正式立项」）。

### 2.2 `paios_installer` 模块不存在
- `README.md`、`DEPLOYMENT.md`、`CHANGELOG.md` 均描述 `python -m paios_installer init/doctor/validate`，且 DEPLOYMENT 校验清单依赖 Doctor（≥90 分）、Validate（0 错误）
- 实际仓库**无** `setup.py` / `pyproject.toml` / `paios_installer/` → 安装与自检流程为「文档中的愿景」，当前不可执行

**建议（二选一）**：
1. 实现最小 `paios_installer` 包（doctor/validate 检查目录存在性、registry 可读性、ADR 完整性）；或
2. 改写 README/DEPLOYMENT，将自检描述为「人工核对清单」而非可执行命令，避免误导。

### 2.3 manifest / inventory 计数过时（已修复）
- 原 `scripts: 5`（2026-06-29），实际注册脚本现为 8（5 legacy + 3 active）
- `00_REGISTRY/scripts.yaml` 已于 2026-07-06 增补活动脚本，但 manifest/inventory 未同步

**已处理**：`manifest.yaml`、`inventory.yaml` 刷新为 `scripts: 8`，日期更新为 2026-07-09。

### 2.4 活动脚本未登记（已修复）
`40_AUTOMATION/05_SCRIPTS/` 下 `classify_files.py`、`vision_query.py`、`check_vision_payload.py` 三个活动脚本此前未写入 `scripts.yaml`，违反 `40_AUTOMATION/README.md`「All assets must be registered in 00_REGISTRY」。

**已处理**：新增 SCRIPT-0006~0008 登记条目。

---

## 3. 同步与版本卫生（中）

### 3.1 `50_DATA/` 未纳入 .gitignore（已修复）
- ADR-0003 将 `50_DATA` 与 `70_TMP` 同列为运行时（不同步），但 `.gitignore` 仅忽略 `70_TMP/`，遗漏 `50_DATA/`
- `git check-ignore` 验证：`70_TMP` 命中，`50_DATA/Databases/x.db` 未命中 → 一旦产生数据文件即会被误提交，仓库膨胀风险

**已处理**：`.gitignore` 增补 `50_DATA/`、`50_IMPORT/`。

### 3.2 git 工作树 dirty（待提交）
`git status` 存在未提交改动：
```
 M 40_AUTOMATION/05_SCRIPTS/douyin.bat
 M 40_AUTOMATION/05_SCRIPTS/douyin.sh
 M MANIFEST.json
 M SYSTEM_VERSION.md
 M reasonix.toml
?? 30_SYSTEM/Governance/Reasonix运维故障复盘.md
?? 40_AUTOMATION/05_SCRIPTS/check_vision_payload.py
?? 40_AUTOMATION/05_SCRIPTS/vision_query.py
```
最近提交为 `968e099`（2026-07-06），距今日 3 天。违反 SYNC_STRATEGY「结束工作即 commit+push」约定，双电脑同步会出现缺失。

**建议**：本次维护改动 + 上述历史改动一并 `git add -A && git commit && git push`（需 Evan 确认是否自动推送）。

### 3.3 `__pycache__` 物理残留
`40_AUTOMATION/09_LEGACY/original/__pycache__/`（2026-07-06）已正确被 `.gitignore` 忽略（git status 未显示），但磁盘上残留编译产物。无害，可定期清理。

---

## 4. 配置问题（低）

### 4.1 `reasonix.toml` allow 列表膨胀/重复
`[permissions] allow` 含一条超长命令字符串，混合了多条调试用 `echo`/`ls`/`grep` 命令，且 Whitepaper/ADR 列举命令出现**重复变体**（带 `\"` 转义与不带）。属权限策略堆积，可读性差、维护风险高。

**建议**：将 `allow` 收敛为权限模式（如 `Bash(python F:\PAIOS\40_AUTOMATION\**\*.py:*)`），移除一次性调试命令。修改前建议先备份该文件。

### 4.2 `default_model` 前缀疑似不匹配
`default_model = "deepseek/deepseek-v4-flash"`，而 provider `name` 为 `deepseek-flash`/`deepseek-pro`/`deepseek`。`deepseek/` 前缀是否与 provider 解析规则一致需结合 reasonix 实际行为验证（非阻断，待确认）。

### 4.3 脚本路径策略违反自动化规则
`40_AUTOMATION/README.md` 规定「Scripts must use config-based paths」（读 `30_SYSTEM/Config/paths.yaml`）。实际 `classify_files.py` 用 `PAIOS_DRIVE:\QuarkSync\DATA` 环境变量拼路径，`douyin.sh/bat` 用 `${PAIOS_DRIVE:-F}:/PAIOS/...` 硬编码兜底。属「env 变量近似合规」，但与「config-based」明文要求有差距。

**建议**：低优先级，可后续统一为从 `paths.yaml` 读取；当前 env 变量方式可接受。

---

## 5. 编码质量（良好）

- **Python 编译校验**：`py_compile` 对 `40_AUTOMATION` 下全部 8 个 `.py` 通过，无语法错误、无中文注释编码问题（utf-8 读取正常）。
- **`douyin.sh`/`douyin.bat` 引用核查**：早期 Glob 误报 `douyin_full_pipeline.py` 缺失；经 `ls` 复核该文件**真实存在**（15905 字节，2026-07-06 更新），脚本入口有效 ✅
- `classify_files.py`：逻辑完整，项目清单解析（简单/扩展两种格式）、冲突规则、dry-run 齐备，无缺陷。
- `vision_query.py` / `check_vision_payload.py`：依赖检查、错误码（0/1/2/3）、友好退出齐备，质量良好。

**结论**：代码层无「编码错误」类缺陷，主要风险在结构与治理层面。

---

## 6. 本次已执行的维护动作

| # | 文件 | 动作 |
|---|------|------|
| 1 | `.gitignore` | 新增 `50_DATA/`、`50_IMPORT/` |
| 2 | `40_AUTOMATION/00_REGISTRY/scripts.yaml` | 新增 SCRIPT-0006/0007/0008（classify_files / vision_query / check_vision_payload） |
| 3 | `40_AUTOMATION/10_MANIFEST/manifest.yaml` | `scripts: 5 → 8`；`updated: 2026-07-09` |
| 4 | `40_AUTOMATION/10_MANIFEST/inventory.yaml` | `scripts: 5 → 8`；`generated: 2026-07-09` |
| 5 | `30_SYSTEM/ADR/ADR-INDEX.md` | 移除幽灵 ADR-0001 行 + 加注说明 |

---

## 7. 待 Evan 决策 / 待办清单

| 优先级 | 事项 | 建议动作 |
|--------|------|----------|
| 高 | 未文档化目录 `Claw/`、`40_AUDIT/`、`50_IMPORT/` | 冻结期内加辅助说明文档；解冻后正式写入 ADR-0003 增补 |
| 高 | git 工作树 dirty（含本次维护改动） | 核对后 `git commit` + 确认是否 `git push` |
| 中 | `DEPLOYMENT.md`/`SYNC_STRATEGY.md` 盘符 E:\ → F:\ | 改为 `${PAIOS_DRIVE}:/PAIOS` |
| 中 | `paios_installer` 缺失 | 实现最小包 或 改写文档为人工清单 |
| 中 | ADR-0001 过期引用 | 清理 `99_Appendix.md`、`06_Governance.md`、`05_Decision_Layer.md`、`ADR-0003` 共 4 处 |
| 低 | `reasonix.toml` allow 膨胀/重复 | 收敛为权限模式，移除调试命令（先备份） |
| 低 | `default_model` 前缀验证 | 结合 reasonix 行为确认解析正确 |
| 低 | 脚本路径策略 | 后续统一读 `paths.yaml` |
| 低 | `__pycache__` 残留 | 定期清理（已被 gitignore） |

---

*报告生成：2026-07-09 · 由 PAIOS 维护审查产出*
