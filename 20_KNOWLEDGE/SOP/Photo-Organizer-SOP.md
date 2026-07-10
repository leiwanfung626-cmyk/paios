# 照片整理 SOP（Personal Photo Intelligence Pipeline）

> **版本**：v1.1 ｜ **整理日期**：2026-07-10 ｜ **状态**：三阶段流水线已跑通，进入人物策展期；架构评审定调为「个人数字智能流水线」雏形
> **适用**：`E:\待整理照片`（100GB，20 年跨度混合媒体库）→ 归档 + 人脸索引 + 人物档案
> **核心库**：`photo_index.db`（入库索引）｜`face_index.db`（人脸/人物）
> **定位**：不是「照片分类脚本」，而是一套 **Personal Photo Intelligence Pipeline（PPIP）**——资产化、知识图谱化、可检索的个人数字资产管理流水线。

---

## 0. 核心原则（不可违反）

1. **Immutable Original Principle（原图不可变）**：原始文件永远不修改、不覆盖、不重命名、不剪切。所有处理结果只写元数据（SQLite / YAML / JSON）。`Metadata Evolves, Assets Don't.`
2. **物理目录 = 来源主轴 + 时间二级**：`E:\QuarkSync\照片归档\` 下只按「来源」分 8 类（01_Personal…90_Trash），内容/人物/地点全部交给 SQLite 标签，避免目录爆炸。
3. **增量优先**：所有脚本按 `path` / `md5` 去重续跑；首次全量跑完后可随时增量处理新下载批次。
4. **反馈闭环**：AI 产出 → 人工审查 → 回写判定表 → 复用。判定即资产，原图零改动。

---

## 0.5 战略定位（Architecture Review，2026-07-10）

本项目已超出「照片分类脚本」范畴，是一套 **个人数字智能流水线（Personal Photo Intelligence Pipeline, PPIP）** 的雏形。架构评审：9.1/10，**短板在产品层（Person Page / 检索入口 / 事件表达），不在代码层**。

- **资产演化链**：`照片 → 不可变资产 → 元数据 → SQLite → 人物 → 事件 → 关系 → 检索`。目录式整理（旅游/工作/宝宝）已升级为资产化知识图谱（Asset / Metadata / Embedding / Person / Tag / Event / Co-occurrence）。
- **判定即资产（全项目最值钱的一句话）**：512 维向量可随时重算，但「这是谁」不可重新获得。`person_judgments` 是真正的长期资产，不是 embedding。CLIP / GLM / InsightFace / FAISS / SQLite 都可替换，人物判定不会变。
- **Knowledge Graph > Face Recognition**：共现网络（A 与 B 同框 23 次，时间 2008/2010/2013）比单张人脸识别更有价值。关系是自然浮现的，而非识别出来的。
- **Phase B 方向修正（最重要决策）**：不升级识别模型——20 年跨度（孩子/成人/老人/角度/光照/遮挡）无任何通用模型能根治；路线应为 `自动识别 → 人工确认 → person_judgments → 永久资产`。
- **Phase C 应演进为 Person Page（人物档案）**：运丰/皓祥不应止于「文件夹」，而应成为含头像/简介/首末出现/时间轴/地点/共现人物/重要事件/照片视频的**人物档案**。

---

## 1. 环境

| 项 | 值 |
|----|----|
| Python | managed venv：`$USERPROFILE/.workbuddy/binaries/python/envs/default/Scripts/python.exe`（简称 `PY`）|
| 分类 VLM | GLM-4V-Flash（免费，需 `ZHIPU_API_KEY`）|
| 密钥持久化 | **必须写入 `photos_organizer/.env`**（`cp .env.example .env` 后填值），**不要**只靠交互 shell `export` |
| 人脸引擎 | InsightFace `buffalo_l`（scrfd_10g 检测 + arcface w600k_r50 识别，512 维）|
| 向量索引 | FAISS `IndexFlatIP`（余弦相似度）|
| 推理后端 | onnxruntime **CPU**（机器无 CUDA 运行时；GPU CMP 40HX 暂未启用）|
| 速率 | 人脸提取 ~1.8s/图；全量 11,954 图 ≈ 6 小时（后台过夜）|

> 运行任何脚本前先 `export PY="$USERPROFILE/.workbuddy/binaries/python/envs/default/Scripts/python.exe"`。

> ⚠️ **密钥陷阱（2026-07-10 实测踩坑）**：`ZHIPU_API_KEY` 只在交互 shell `export` 过、未持久化到 `.env`。后台 Bash 是全新 shell，取不到 env → GLM 补判被**静默跳过**（日志 0 报错、0 补判）。后果：278 张本批低置信照片（共全库 1,094 张 `classifier=local_clip AND conf<0.40`）只走了 CLIP 粗判。
> **修复**：把 `ZHIPU_API_KEY=...` 写入 `photos_organizer/.env`（已有 `.env.example`）。脚本启动时自动 `load_local_env()` 读取，后台运行也生效。修复后跑 `reclassify_lowconf_glm.py` 回填。
>
> ⚠️ **大图陷阱（2026-07-10 实测）**：`glm-4v-flash` 对请求体体积有上限。原始大图（如 4608×3456 / 5.9MB → base64 7.9MB）会返回 **400 code 1210「参数有误」**，而非鉴权失败——纯文本模型 `glm-4-flash` 与该 key 完全正常，可借此区分。
> **修复**：`04_classify.py` 的 `classify_glm4v_flash` 在编码前用 PIL 把图降采样到最长边 ≤1280、转 JPEG q85；若仍 >2MB 再逐步降质（q-15 直至 >40）。小图（2×2、文本调用）不受影响。重新分类脚本 `reclassify_lowconf_glm.py` 直接复用该函数，已验证端到端。
> **排查顺序**：① 先确认 key 生效（文本模型能答）→ ② 再查图片体积（大图必 1210）→ ③ 别盲猜模型名。

---

## 2. 当前资产盘点（2026-07-10 实测）

**`database/photo_index.db`**
- `photos` 15,469 ｜ `tags` 27,717 ｜ `vocabulary` 91 ｜ `jobs` 2（job2 全量 15,454，2026-07-08 完成）｜ `photo_versions` 15,538 ｜ `corrections` 205
- media_type：photo 12,566 / livephoto 1,429 / video 1,084 / raw 317 / other 62 / document 7 / archive 4

**`face_index/face_index.db`**
- `faces` 28,317 ｜ `processed` 11,954 ｜ `clusters` 3,995 ｜ `persons` 2（皓祥 conf 0.839、运丰 conf 0.745）｜ `person_judgments` 1,352 ｜ `photo_persons` 891

**人物文件夹（Phase C 产物）**
- `运丰`：`E:\待整理照片\运丰\`（2002–2026 年份目录 + `_preview/`，466 张，含 `timeline.html`）
- `皓祥`：检索集 `face_index/retrieval/皓祥/`

---

## 3. 三阶段流水线

### Phase A — 入库索引（`scripts/organize_photos.py`）
对源目录做：扫描 → md5 去重 → EXIF 提取 → pHash/dHash 感知去重 → 多标签分类（CLIP 主力 + GLM-4V-Flash 补判）→ 按来源复制到归档 → 写 SQLite。
```bash
cd E:\PAIOS\10_WORK\photos_organizer\scripts
$PY organize_photos.py                         # 全量 hybrid
$PY organize_photos.py --limit 50              # 试点
$PY organize_photos.py --dry-run              # 预演（不写库不复制）
$PY organize_photos.py --provider local_clip  # 纯 CLIP，不调 GLM
```
辅助脚本：`01_extract_exif.py` / `02_md5_dedup.py` / `03_phash_dedup.py` / `04_classify.py` / `05_review_report.py` / `06_correct.py` / `07_analyze_corrections.py`。
**GLM 补判回填**（密钥缺失后的补救）：`reclassify_lowconf_glm.py`（目标 `classifier=local_clip AND conf<0.40 AND media_type=photo`，支持 `--dry-run/--limit/--all-local-clip`）。
配置：`../config.yaml`（来源目录、词表、引擎阈值）。

### Phase B — 人脸索引与检索（`face_index/`）
```bash
cd E:\PAIOS\10_WORK\photos_organizer\face_index
$PY face_extract.py          # 检测+识别+入库+缩略图（增量；首跑下载 buffalo_l ~280MB）
$PY cluster.py               # FAISS 建索引 + 连通分量聚类（余弦阈值默认 0.38）
$PY retrieve.py --seeds "种子图文件夹" --tag 人名 --topk 300   # 种子检索
#   打开 retrieval/<人名>/report.html 逐张 ✓/✗/? 审查 → 导出 judgments.json
$PY commit_judgments.py --tag 人名      # 回写 persons + faces.person_id + person_judgments
$PY build_cooccurrence.py   # 扩展 persons 字段 + 重建 photo_persons + 共现 CSV
```
导出：`export_person_report.py`（人物报告）/ `export_person_gallery.py`（画廊）/ `export_person_by_year.py`（逐年）。
> 关键决策：20 年年龄跨度使同一人聚类分裂（3,995 簇），**不追求自动认人**；可靠检索靠种子图（Phase 2）。视频/LIVP/RAW 不在 V1 人脸范围。

### Phase C — 人物档案策展（`face_index/photo_tool.py`，2026-07-10 成形）

> 演进方向：当前产出是「人物年份文件夹」，最终应升级为 **Person Page（人物档案）**——头像 / 简介 / 首末出现 / 时间轴 / 地点 / 共现人物 / 重要事件 / 照片视频，而非单纯文件夹。
对具名人物建专属年份文件夹 + 可编辑时间线。证据优先级：**EXIF 年份 > 文件名日期(时间水印等价) > embedding 原型余弦推断**。
```bash
cd E:\PAIOS\10_WORK\photos_organizer\face_index
$PY photo_tool.py reindex --person 运丰          # 检测+建 index.csv + _preview/index.html
$PY photo_tool.py gen_reclassify --person 运丰  # 生成年份重分类审查页（仅候选，不移动）
#   用户勾选 + 填目标年 → 导出 reclassify_decisions.json
$PY photo_tool.py apply_reclassify --person 运丰 # 仅移动确认项 + 写 undo_map.csv 可还原
$PY photo_tool.py gen_timeline --person 运丰    # 可编辑「人生大事记」时间线 timeline.html
$PY photo_tool.py gen_delete --person 运丰      # 疑似/无脸删除审查页（默认 reject 移 _rejected，可恢复）
$PY photo_tool.py apply_delete --person 运丰
$PY photo_tool.py regen_html --person 运丰      # 改完重建预览
```
> 人物文件夹磁盘结构：`<人名>/<年份>/` + `<人名>/_preview/`（index.html、index.csv、thumbs/、review.csv、_detect.json、undo_map.csv）。全部相对路径，整包可移植。

---

## 4. 关键命令速查

| 意图 | 命令 |
|------|------|
| 全量分类+去重 | `scripts/organize_photos.py` |
| 人脸提取续跑 | `face_index/face_extract.py` |
| 重聚类 | `face_index/cluster.py` |
| 检索某人 | `face_index/retrieve.py --seeds <dir> --tag <名> --topk 300` |
| 提交判定 | `face_index/commit_judgments.py --tag <名>` |
| 共现网络 | `face_index/build_cooccurrence.py` |
| 建人物年份文件夹 | `face_index/photo_tool.py reindex/gen_reclassify/apply_reclassify --person <名>` |
| 生成时间线 | `face_index/photo_tool.py gen_timeline --person <名>` |

---

## 5. 架构决策与已知限制

**已定决策**
- 来源主轴 + 时间二级 + 标签化内容，避免目录爆炸。
- hybrid 分类（CLIP 83% + GLM 补判 17%）成本 0、质量≈纯 VLM、速度远快。
- 战略转向（2026-07-09）：不再升级识别模型（20 年跨度同人必分裂，通用模型无法根治，且换模型不积累资产）；价值重心 = 人物元数据 + 共现网络 + 时间轴 + 人物检索。
- 人工判定是唯一可靠标注来源；`person_judgments`（已 1,352 条）是未来监督微调的燃料，但须先映射到具名 persons。

**已知限制 / 风险**
- HEIC/LIVP/CR2：需 `pillow_heif` / `rawpy` 才能读 EXIF，否则降级文件时间。
- 环境**无 OCR**：真实图像内烧录水印无法自动提取，以「文件名日期」作时间水印等价证据（`parse_reliable_year` 支持 `.` 分隔与 `mmexport`+13 位时间戳）。
- 视频/RAW 人脸：需 ffmpeg + HEIF 抽帧，未做。
- 高风险操作（移动/删除）必须走「审查页 + 用户填目标 + undo_map 可还原」三件套。

---

## 6. 演进路线（Backlog，按架构评审重排，2026-07-10）

> **核心约束**：真正限制系统价值的是**标注覆盖率，不是功能缺失**（当前仅 2 位具名人物 / 3,995 簇）。事件、时间线、关系网络都建立在人物标注密度之上。
> 标注提升**数据质量**，检索提升**系统可用性**，事件层提升**知识表达能力**——三者构成下一阶段最有价值的能力闭环。

| 优先级 | 项 | 说明 | 依赖 |
|--------|----|----|------|
| ① 高 | **持续人物命名标注** | 瓶颈项。扩大具名 persons 覆盖（3,995 簇 → 更多具名）；标注提升数据质量 | — |
| ② 高 | **统一检索层 `search.py`** | 系统查询入口（非脚本）。组合查询：人物(AND/NOT)、时间范围、地点、标签、多人共现；先解析为 SQL，不必急于引入 LLM | ① |
| ③ 中 | **自动事件聚合 `events`** | 基于检索结果构建事件层：起止日期/地点/参与人/源照片，让时间线从「照片集合」升级为「人生事件」 | ① ② |
| ④ 中 | **Timeline 增强** | 时间轴 / 人物关系从照片集合升级为知识表达 | ① ② |
| ⑤ 中 | **共现可视化** | 共现网络图（人物关系图），呼应 Knowledge Graph 定位 | ① |
| ⑥ 低 | 视频 / LIVP / RAW 抽帧人脸 | ffmpeg + HEIF 扩展人脸范围 | — |
| ⑦ 低 | 模型升级 | **已否决**：收益递减、不积累资产 | — |

**`search.py` 设计要点（Phase D 候选，系统查询入口）**
- 组合查询：`人物: 运丰` / `人物: 运丰 AND 皓祥` / `人物: 运丰 AND 父亲 NOT 工作`
- 维度：`时间: 2008~2012` / `地点: 广州` / `标签: 旅行`
- 实现：先解析为 SQL（别名解析 + 日期范围 + 类别/标签 + 多人 AND 共现），不急于上大模型；未来可扩展自然语言（「2012–2015 我和皓祥出去玩的照片」）→ 同样先落 SQL。

---

## 7. 相关文件索引

- 方案文档：`10_WORK/photos_organizer/notes.md`、`face_index/notes.md`
- 配置：`10_WORK/photos_organizer/config.yaml`
- 主库：`10_WORK/photos_organizer/database/photo_index.db`
- 人脸库：`10_WORK/photos_organizer/face_index/face_index.db`
- 人物工具：`10_WORK/photos_organizer/face_index/photo_tool.py`
- 输出：`10_WORK/photos_organizer/outputs/`（review_report 等）、`E:\QuarkSync\照片归档\`
