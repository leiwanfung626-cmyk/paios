---
id: KB-2026-0719-CHATGPT-MCP
type: reference
title: PAIOS 知识库 MCP 接入 Codex CLI / IDE 扩展
summary: 把 PAIOS 知识库通过 stdio MCP 暴露给 OpenAI Codex（CLI + IDE 扩展）。注意：Codex 桌面应用 UI 不消费自定义 stdio MCP，必须用 CLI 或 IDE 扩展。
tags: [mcp, codex, paios, knowledge, integration, stdio, openai]
keywords: [PAIOS MCP, Codex CLI, Codex IDE, config.toml, stdio, 知识库连接, ChatGPT Desktop]
created: 2026-07-19
status: active
---

# PAIOS 知识库 MCP 接入 Codex CLI / IDE 扩展

> 一次踩坑后梳理的最终方案。**Codex 桌面应用 UI 不消费自定义 stdio MCP** — 必须用 **Codex CLI** 或 **Codex IDE 扩展**。

## 0. 关键认知（避免再踩坑）

| 表象 | 真相 |
|------|------|
| 任务管理器里看到 `ChatGPT.exe` 在跑 | 那其实是 **OpenAI Codex 桌面应用**（Windows Store 包 `OpenAI.Codex`），不是老的 ChatGPT Desktop |
| Codex 桌面应用 UI 里有"自定义 MCP"配置入口 | UI **只写配置到 `~/.codex/config.toml`**，但桌面应用**自己不消费** stdio MCP |
| `~/.codex/config.toml` 里有 `[mcp_servers.paios-knowledge]` | 配置是给 **Codex CLI** 和 **Codex IDE 扩展**用的（OpenAI 官方文档明确说："Codex supports MCP servers in both the CLI and the IDE extension"） |
| `AppData\Roaming\ChatGPT\mcp.json` | **遗留文件**，Codex 不读，已重命名为 `.legacy-not-used-by-codex` |
| ChatGPT 桌面应用对话里说"看不到 MCP 工具" | 预期行为，桌面应用 UI 不加载自定义 stdio MCP |

## 1. 架构（最终方案）

```
Codex CLI (codex.exe)              ← 用这个！
   │  读 ~/.codex/config.toml
   │  启动 stdio MCP
   ▼
python.exe (managed venv, 含 mcp 包)
   │
   ▼
paios_mcp_server.py
   │
   ▼
30_SYSTEM/Registry/relationship-graph.json
20_KNOWLEDGE/**/*.md
```

**Codex IDE 扩展**（VS Code / Cursor / Windsurf）也读同一份 `config.toml`，配置共享。

## 2. 配置位置和内容

**文件**：`C:\Users\liyun\.codex\config.toml`

**PAIOS MCP 配置段（已就位）**：
```toml
[mcp_servers.paios-knowledge]
enabled = true
command = 'C:\Users\liyun\.workbuddy\binaries\python\envs\default\Scripts\python.exe'
args = ['D:\PAIOS-PORTABLE\Core\40_AUTOMATION\05_SCRIPTS\paios_mcp_server.py']
startup_timeout_sec = 30   # 可选：Python 冷启动可能超过默认 10s

[mcp_servers.paios-knowledge.env]
PYTHONIOENCODING = "utf-8"
PYTHONUTF8 = "1"
```

**关键约束**：
- `command` 必须指向**装了 `mcp` 包**的 Python — 系统 Python（`C:\Users\liyun\AppData\Local\Programs\Python\Python313\python.exe`）**没装 mcp 包**，绝对不能用
- 路径用单引号（TOML 字面字符串），反斜杠不需要转义
- TOML 节名用中划线 `paios-knowledge` 或下划线 `paios_knowledge` 都行

## 3. 暴露的 5 个工具

| 工具 | 作用 | 入参 |
|------|------|------|
| `paios_search_knowledge` | BM25 + Tag 联合搜索 | `query` (str), `top_k` (int, 默认10) |
| `paios_get_module` | 读单条知识模块完整内容 | `node_id` (str, 如 `REF-0010`) |
| `paios_get_relationships` | 模块关系网 | `node_id` (str) |
| `paios_list_modules` | 按类型列出 | `filter_type` (str, 默认 `all`) |
| `paios_get_stats` | 知识库统计 | 无 |

## 4. 验证步骤

### 4.1 看配置是否被识别
```powershell
& "C:\Users\liyun\AppData\Local\OpenAI\Codex\bin\5dee10576ec7a5b8\codex.exe" mcp list
```
应该看到 `paios-knowledge  ...  Status: enabled  Auth: Unsupported`

### 4.2 看详细配置
```powershell
& "C:\Users\liyun\AppData\Local\OpenAI\Codex\bin\5dee10576ec7a5b8\codex.exe" mcp get paios-knowledge
```

### 4.3 在 Codex CLI 里调用
```powershell
cd D:\PAIOS-PORTABLE\Core
& "C:\Users\liyun\AppData\Local\OpenAI\Codex\bin\5dee10576ec7a5b8\codex.exe" exec --sandbox read-only "请用 paios_search_knowledge 工具搜索「双盘协同」"
```

### 4.4 在 TUI 里看活跃 MCP
启动 `codex` 进入 TUI → 输入 `/mcp` → 应该看到 `paios-knowledge` 处于 active 状态

### 4.5 在 VS Code 扩展里调用（已装好，2026-07-19 22:59）

**已装扩展**：`openai.chatgpt v26.715.31925`（VS Code Marketplace 官方扩展）

**安装命令**（如需在其他机器复刻）：
```bash
code --install-extension openai.chatgpt
```

**使用步骤**：
1. **重启 VS Code**（让扩展激活）
2. **右侧活动栏出现 Codex 图标**（如果没看到，左下角齿轮 → 命令面板 → `Codex: Focus on Codex View`）
3. 点 Codex 图标 → **用 ChatGPT 账号登录**（首次）
4. 打开 PAIOS 项目文件夹：`D:\PAIOS-PORTABLE\Core`
5. 在 Codex 对话面板里直接问：「用 paios_search_knowledge 工具搜索 PAIOS 知识库里关于双盘协同的模块」
6. Codex 会自动调用 PAIOS MCP（无需手动选工具）

**注意事项**：
- VS Code 扩展和 Codex 桌面应用共享 `~/.codex/auth.json`，可以同时开
- VS Code 扩展和 Codex CLI 共享 `~/.codex/config.toml`，配置一次三处通用
- 如果用量超限（`You've hit your usage limit`），扩展和 CLI 都不能用 — 等限额重置

## 5. 排错清单

| 现象 | 原因 | 解决 |
|------|------|------|
| **桌面应用 UI 里 ChatGPT 说看不到 MCP 工具** | **预期行为**！桌面应用 UI 不消费自定义 stdio MCP | 改用 Codex CLI 或 IDE 扩展 |
| `codex mcp list` 里没有 `paios-knowledge` | config.toml 没加载或格式错 | 用 `codex mcp add` 命令重写，别手改 |
| `codex mcp list` 显示但 `Status: disabled` | `enabled = false` 或被 `--disable` 标志关了 | 改 `enabled = true` |
| 启动报 `ModuleNotFoundError: No module named 'mcp'` | `command` 指向的 Python 没装 mcp 包 | 必须用 managed venv 的 python.exe |
| 启动报"关系图未构建" | `relationship-graph.json` 不在 | 跑 `relationship_engine.py build` 重建 |
| `You've hit your usage limit` | Codex 用量超限 | 等限额重置（提示里有时间），或升级 ChatGPT Plus |
| 中文乱码 | Windows GBK | env 里加 `PYTHONIOENCODING=utf-8` `PYTHONUTF8=1`（已配） |
| 进程堆积（多个 python.exe 残留） | MCP 客户端断开时未杀进程 | 跑 `70_TMP/kill_paios_procs.py` 清理 |

### 5.1 诊断流程（MCP 工具不出现时）

1. **确认你用的是哪个客户端**
   - 桌面应用 UI（ChatGPT.exe）→ **不支持**自定义 stdio MCP，放弃这条路
   - Codex CLI（codex.exe）→ 支持
   - Codex IDE 扩展 → 支持
2. **跑 `codex mcp list`** 看配置是否被识别
3. **看 `config.toml` 里的 `command`** — 必须指向装了 mcp 包的 Python
4. **跑一次启动命令** — `printf '' | <command> <args...>` 应静默退出 0
5. **看进程** — `python 70_TMP/check_paios_proc.py` 查是否有 paios_mcp 进程在跑
6. **看用量** — 如果 `codex exec` 立刻报 usage limit，是账户问题，不是配置问题

## 6. 添加 / 修改配置的正确方式

### 方式 A — 用 codex mcp add 命令（推荐）
```powershell
& "C:\Users\liyun\AppData\Local\OpenAI\Codex\bin\5dee10576ec7a5b8\codex.exe" mcp add paios-knowledge --env PYTHONIOENCODING=utf-8 --env PYTHONUTF8=1 -- "C:\Users\liyun\.workbuddy\binaries\python\envs\default\Scripts\python.exe" "D:\PAIOS-PORTABLE\Core\40_AUTOMATION\05_SCRIPTS\paios_mcp_server.py"
```

### 方式 B — 手改 config.toml
直接编辑 `C:\Users\liyun\.codex\config.toml`，加 `[mcp_servers.paios-knowledge]` 段（参考第 2 节）

### 方式 C — 桌面应用 UI（不推荐）
桌面应用 UI 的"自定义 MCP"配置入口**会写 config.toml 但自己不消费**，写完还是得用 CLI/IDE 才能调用。

## 7. 文件清单

| 路径 | 作用 | 状态 |
|------|------|------|
| `D:\PAIOS-PORTABLE\Core\40_AUTOMATION\05_SCRIPTS\paios_mcp_server.py` | MCP Server 主体 | 已存在 |
| `D:\PAIOS-PORTABLE\Core\40_AUTOMATION\05_SCRIPTS\paios-mcp.cmd` | 启动包装（备用） | 已存在 |
| `D:\PAIOS-PORTABLE\Core\30_SYSTEM\Registry\relationship-graph.json` | 关系图数据源 | 已存在 |
| `C:\Users\liyun\.codex\config.toml` | **Codex 真正读的配置** | ✅ 已配 paios-knowledge |
| `C:\Users\liyun\AppData\Roaming\ChatGPT\mcp.json.legacy-not-used-by-codex` | 遗留文件，Codex 不读 | 已重命名 |

## 8. 后续可选

- [ ] 加 SSE/HTTP 模式：让桌面应用 UI 也能连（需要把 paios_mcp_server.py 改成 SSE 传输）
- [ ] 加 token 限制：超大模块自动截断（已实现 `body[:2000]`）
- [ ] 把 PAIOS-Usage 的 Pocket 工具也通过 MCP 暴露
- [ ] 配置 `enabled_tools` 白名单，只暴露必要的工具给 Codex
- [ ] 配置 `default_tools_approval_mode = "auto"`，让 PAIOS 工具免确认调用

---

_创建于 2026-07-19 — by Buddy (WorkBuddy)_
_修订于 2026-07-19 — 桌面应用不支持 stdio MCP 的真相确认后_
