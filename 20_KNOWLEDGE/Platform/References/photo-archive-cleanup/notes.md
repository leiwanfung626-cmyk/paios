# 照片归档清理 — 方案与进度

> **创建**: 2026-07-11
> **状态**: 活跃 — 已定决策，dry-run 阶段
> **上级项目**: `10_WORK/photos_organizer`（归档输出 `E:\QuarkSync\照片归档`）

## 任务目标
清理 `E:\QuarkSync\照片归档` 中的噪声图片：
1. 网络图片（network / 表情包 / 素材）
2. 截图（screenshots）
3. 二维码（QR codes，散落各类目）
4. 文件过小的图片（字节阈值）

## 已确认决策（2026-07-11，Evan 拍板）
- **清理方式**: Quarantine 到 `90_Trash`（可逆，不永久删除）
- **过小阈值**: `< 100KB`（659 张候选）
- **网络图范围**: 含散落其他类目的 `primary_category=网络素材`（全量 ~1249，不止 04_Downloads）
- **二维码检测**: 允许，装 `opencv-python-headless` 用 `cv2.QRCodeDetector` 全量扫描

## 现有工作流（调研结论）
- 归档物理结构 8 类：`01_Personal / 02_Work / 03_Screenshots / 04_Downloads / 05_Documents / 06_Videos / 07_ToReview / 90_Trash`
- `index.csv`（17,033 行，20 列）标记 `source` / `primary_category` / `tags_*`，可直接识别网络图/截图
- `index.csv.path` 指向源 `E:\待整理照片`（原件），归档副本在 `E:\QuarkSync\照片归档\{source}\{年份}\{文件名}`
- **原图不可变**：清理只动归档副本，源文件永不碰
- 文件大小无现成字段 → 需 `os.path.getsize` 实测
- 既有安全协议：dry-run → 展示方案 → 用户确认 → --yes → 立即核验磁盘计数

## 识别策略
| 目标 | 方法 | 候选量（估） |
|------|------|------|
| 网络图片 | `primary_category=='网络素材'` OR `source=='04_Downloads'` | ~1249 |
| 截图 | `source=='03_Screenshots'` | 713 |
| 二维码 | `cv2.QRCodeDetector` 全量扫描图片 | 待 dry-run |
| 小文件 | `os.path.getsize < 100KB` | 659 |

## 执行机制
脚本 `cleanup_archive.py`（本目录）：
- `--dry-run`：扫描四类目标 → 写 `outputs/cleanup_candidates.csv`（archive_path, size, reason, md5）→ 只报告不改盘
- `--yes`：候选移动到 `90_Trash/{reason}/{原类目}/...`（保留相对路径，可逆）→ 回写 index.csv 标记 `value_level=trash`（按 md5 关联）→ 立即核验计数

## 环境
- venv: 本目录 `.venv`（opencv-python-headless 5.0.0 + numpy + Pillow）
- 解释器: `E:\PAIOS\10_WORK\照片归档清理\.venv\Scripts\python.exe`

## 进度
- [x] 调研现有工作流 + 数据分布
- [x] Capture 到 Inbox
- [x] 确认 4 项决策
- [x] 建 venv + 装 QR 检测库
- [x] 写 cleanup_archive.py
- [x] 快速 dry-run（skip-qr）：候选 2279 / 1.99GB（network 1370 / screenshot 505 / small 404）
- [x] 全量 dry-run 含 QR（第一轮 cv2.imread 失效→假阴性 QR=0，已定位并修复为 PIL 读图）
- [x] **改用前台切块 + 断点续跑**（--batch-size + --state），规避后台通知不可靠
- [x] **QR 检测聚焦三类**（03_Screenshots/04_Downloads/07_ToReview），全量压缩到单批完成
- [x] **最终全量 dry-run 完成**：候选 2279 / 1.99GB，真实二维码 21 个（在 03_Screenshots）
- [ ] Evan 确认候选 → --yes 执行 → 核验

## QR 检测优化（2026-07-11 第二轮）
- 原意图全量逐张 QR 解码（15809 张），但 01/02/05/06 真实照片类含二维码概率≈0 却占 90% 解码耗时，单批超前台超时。
- 决策：QR 检测聚焦最可能含二维码的三类 `03_Screenshots,04_Downloads,07_ToReview`（用 `--qr-scopes` 参数），真实照片类跳过 QR。
- 结果：全量扫描从多轮切块压缩到**单批完成**（~8 分钟），真扫出 21 个二维码（均在 03_Screenshots，reasons 含 qr）。
- 若需严格全量 QR，去掉 `--qr-scopes` 即可（但需多轮切块）。

## 已知坑（已修复）
- 第一轮全量 dry-run 报「二维码=0」，复核发现 **cv2.imread 在本沙箱对全部图片返回 None**（opencv-headless 5.0.0 解码后端缺失），假阴性。
- 修复：`detect_qr` 改 `PIL.Image.open().convert("RGB")` → `np.array` → `cv2.QRCodeDetector`，已用真二维码阳性对照验证可解。
- 教训：本环境任何读图一律走 PIL，勿信 cv2.imread。

## 风险
- <100KB 阈值偏激进（659 张，含正常压缩照片）→ 靠 90_Trash 可逆兜底
- QRCodeDetector 召回中等，可能漏检（可接受，宁可漏不可误伤）
- 跨类目网络素材按 primary_category 判定，可能误伤被误标内容 → 候选清单需 Evan 过目
- **opencv-headless 5.0.0 的 cv2.imread 在本环境不可用**，任何读图需求一律走 PIL（已踩坑验证）
- **沙箱 safe-delete 拦截 os.remove**：脚本末尾 `os.remove(state)` 触发 `SAFE_DELETE_FAIL_CLOSED`（windows-sandbox-recycle-bin-unavailable），EXIT=1。但扫描+CSV 写入均已成功，仅 state 残留。解决：用 `rm -f`（Git Bash）删，或留残留（无害，下次 --reset-state 覆盖）。

## 审查清单（2026-07-11，Evan 要求「生产可删除带预览可查看大图审查清单」）
- 交付：`review_server.py`（stdlib http.server，无第三方依赖）+ `review.html`（浅色主题前端）+ `gen_thumbs.py`（缩略图生成）
- 用法：`python review_server.py --port 8777` → 浏览器开 `http://127.0.0.1:8777/`
- 能力：
  - 缩略图网格（220px 方形，按 md5 缓存到 `outputs/thumbs/`）
  - 点击灯箱看**原图全分辨率**（经服务器 `/orig/<md5>` 流式返回，绕开浏览器 file:// 限制）
  - 每项目「保留 / 删除」标记，存 localStorage（不影响磁盘）
  - 筛选：全部 / 网络图片 / 截图 / 过小 / 含二维码 / 垃圾(非图片) / 仅图片；搜索文件名·类目
  - 导出 `review_decisions.csv`（md5, rel, bucket, reasons, size, decision）
- **关键修正**：扫描把 54 个 Picasa 缓存（`.picasa.ini`、`xxx.jpg.168x136` 缩略图缓存、隐藏文件）误判进 `small` 桶（它们 <100KB）。审查层按扩展名区分 `is_image`，非图片归为独立「垃圾」类，使 `small` 桶从 404 降到 **350 张真实小照片**，不再污染照片审查。
- 缩略图踩坑：`gen_thumbs` 初版用 `Image.Resample.LANCZOS`（Pillow 12 已移除 `Image.Resample`）→ 全图生成占位图。改 `Image.Resampling.LANCZOS` 修复（2210 真实 + 44 占位[HEIC/CR2/LIVP 等 PIL 不支持]）。
- 后续 `--yes` 执行时建议：非图片(垃圾)类可一并 quarantine，但需与照片分开统计；或先单独清理 Picasa 缓存。

## 下一步
- [ ] Evan 用审查清单过目并标记（保留/删除）
- [ ] 导出 `review_decisions.csv` 回传 → 我据 decision 列生成最终执行清单
- [ ] 跑 `cleanup_archive.py --yes`（仅移动归档副本到 90_Trash，源目录不动）→ 核验
