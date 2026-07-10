# 照片整理任务 — 方案与进度

> **最后更新**: 2026-07-10
> **状态**: 活跃 — Phase 3 人物理解与智能检索
> **详细日志**: `.workbuddy/memory/2026-07-07.md` ~ `2026-07-10.md`

## 背景
- 目标目录：`E:\待整理照片`（100GB 混合媒体库，时间跨度 20 年，15,530 文件）
- 输出至 `E:\QuarkSync\照片归档` → 后续 PAIOS 再分类到夸克数据盘
- 目标：建立可复用、增量的照片索引工具，而非一次性脚本

## 关键发现（扫描于 2026-07-07）
实际不是"照片库"，是**混合媒体库**：

| 类型 | 文件数 | 大小 | 占比 |
|------|--------|------|------|
| 视频 (.mp4/.3gp/.mov) | 1,074 | 60.5 GB | 60.6% |
| 照片 (.jpg/.png/.jpeg/.webp/.bmp/.gif) | 12,199 | 25.6 GB | 25.1% |
| Live Photo (.livp) | 1,429 | 9.2 GB | 9.0% |
| RAW (.cr2) | 291 | 7.0 GB | 6.8% |
| 文档/压缩包 (.pdf/.ppt/.rar/.csv) | 19 | 0.6 GB | 0.6% |

## 分类逻辑（最终决策）
**物理目录仅用「来源」一层主轴 + 「时间」二级；内容/人物/地点交给 SQLite 标签。**

```
E:\QuarkSync\照片归档\
├── 01_Personal\    个人生活/家庭/旅行（按 年/事件）
├── 02_Work\        工作活动（按 年/活动）
├── 03_Screenshots\ 截图
├── 04_Downloads\   网络图片/素材
├── 05_Documents\   证件/合同/发票
├── 06_Videos\      视频
├── 07_ToReview\    AI 置信度低
└── 90_Trash\       重复/模糊/无价值
```

## 分类引擎选型
**双引擎混合（CLIP 主力 + GLM-4V-Flash 补判）**

| 引擎 | 类型 | 成本 | 速度 | 质量 |
|------|------|------|------|------|
| Chinese-CLIP (ViT-B-16) | 本地 | 0 | 3.6/s (CPU) | 中等（需温度缩放） |
| GLM-4V-Flash | 云端 | 0 (免费) | 1-2/s (网络) | 高（VLM语义理解） |

策略：CLIP 批量跑全量 → 置信度 < 0.40 的样本自动调用 GLM-4V-Flash 补判。成本 = 0。

## 处理流水线（增量 + 不可变原则）
1. 扫描 input，计算 md5
2. 查 SQLite，跳过已处理 path（增量核心）
3. 提取 EXIF（日期/GPS/相机）
4. MD5 精确去重 → 90_Trash
5. pHash/dHash 感知去重 → 标记 duplicate_group + master=0
6. 多标签分类（CLIP主力 + GLM多标签补判）→ primary_category + tags + source + confidence
7. 写入 photo_versions（分类历史追踪，可追溯）
8. 写入 tags 表（EAV多标签，词表约束）
9. 写入 photos 表（当前值）+ jobs 表（批次审计）
10. 按 source 复制到 E:\QuarkSync\照片归档\对应目录（**原图永远不修改**）
11. 导出 CSV 报表

---

## 进度总览

### Phase A — 入库索引（V1，2026-07-07 完成）

- [x] Step 1: 扫描库存，发现 57% 为视频，调整结构加 06_Videos
- [x] Step 2: 01_extract_exif.py（EXIF/文件时间兜底）
- [x] Step 3: 02_md5_dedup.py（精确去重）
- [x] Step 4: 03_phash_dedup.py（感知去重）
- [x] Step 5: 04_classify.py（hybrid: CLIP主力 + GLM补判）
- [x] Step 6: organize_photos.py（统一入口，增量模式）
- [x] Step 7: V1.1 多标签架构改造（单标签→多标签JSON+词表+规则映射）
- [x] Step 8: V1.0-final Schema 冻结（25列 photos + tags + vocabulary + jobs + photo_versions + corrections）
- [x] Step 9: 全量运行完成（15,530 文件 → 15,469 照片入库 + 归档落盘）
- [x] Step 10: 反馈闭环工具链（05_review_report → 06_correct → 07_analyze_corrections）

**V1 产物**：`database/photo_index.db`（15,469 条）+ `E:\QuarkSync\照片归档`（七类落盘）

### Phase B — 人脸检索（V2，2026-07-08~09 完成）

- [x] InsightFace buffalo_l 全量提取：11,904 张静图 → **28,317 张人脸**（0 错误，151 min CPU）
- [x] FAISS 索引 + 聚类（sim_thr=0.38 → 巨簇不可用，预判验证）
- [x] 种子检索：皓祥 32 张种子→匹配 1684 张（≥0.7 高置信 540）；运丰 28 张种子→958 张（≥0.7 高置信 604）
- [x] 交互式审查页（report.html 内嵌 ✓/✗/? 按钮，一键导出 judgments.json）
- [x] commit_judgments.py 回写链路（accept→person_id / reject→-1 / unsure→不动）
- [x] 重叠检测与处理：235 张重叠脸（皓祥↔运丰），115 张经 review_ambiguous 双人指认
- [x] 纠偏闭环：review_corrections.py 噪声页 → 逐张人审（推翻"下载=噪声"假设）
- [x] 三步审查闭环完成：种子检索→人工审查→噪声纠偏→重叠指认→导出清单

**V2 最终人物库**：皓祥 389 张人脸/389 照片 ｜ 运丰 502 张人脸/502 照片 ｜ 排除 213 ｜ 未判定 27,213

**V2 产物**：`face_index/face_index.db` + `faiss_index.bin` + `export/`（CSV + timeline.html + 画廊）

### Phase 3 — 人物理解与智能检索（2026-07-09~10，进行中）

**战略决策（2026-07-09）**：不再换/升级识别人脸的模型。价值重心转向人物元数据 + 共现网络 + 时间轴/事件 + 基于人物的检索。判定即资产——person_judgments 1352 条人工判定是长期资产，不可重获。

- [x] 人物元数据：persons 扩展 6 字段（name/display_name/aliases/relationship/birth_year/cover_face_id）
- [x] 共现网络：build_cooccurrence.py → photo_persons 物化 891 行 + person_pairs 视图 + cooccurrence_matrix.csv + cooccurrence_by_year.csv
- [x] 人物报告：export_person_report.py（CSV + SVG 逐年柱状图 + 年度区块 + 年×人矩阵）
- [x] 人物画廊：export_person_gallery.py（HTML 缩略图网格 + 来源筛选）
- [x] 实体导出：export_person_by_year.py（按人物+年份复制到 `E:\待整理照片\{人名}/`）
- [ ] 统一人物检索层 search.py（别名解析 + 日期范围 + 类别/标签 + 多人 AND 共现）
- [ ] 事件聚合表 events（起止日期/地点/参与人/源照片）
- [ ] 持续人物命名标注（真实瓶颈：3995 簇仅 2 人具名）

### Phase C — 人物文件夹策展（2026-07-09~10，运丰/皓祥已落地）

- [x] photo_tool.py 整合工具（reindex / gen_reclassify + apply_reclassify / gen_timeline / gen_delete + apply_delete / regen_html）
- [x] 三级优先级重分类：EXIF 年份 > 文件名日期 > embedding 推断（带证据徽章 + undo_map）
- [x] 可编辑人生大事记时间线（gen_timeline.py，事件挂照片）
- [x] 删除审查页（gen_delete + apply_delete，lightbox 大图，默认 reject 可恢复）
- [x] 运丰文件夹：`E:\待整理照片\运丰\`（2002–2026，466 张，含 timeline.html）
- [x] 皓祥文件夹：`E:\待整理照片\皓祥\`（2001–2026，358 张，含 _preview/）

**Phase C 磁盘结构**：`<人名>/<年份>/` + `<人名>/_preview/`（index.html/index.csv/thumbs/review.csv/_detect.json/undo_map.csv）

---

## 架构评审（2026-07-10）

**评分：9.1/10** — 分层设计经受住真实项目考验。

**核心资产判定**：
- `person_judgments`（1352 条人工判定）是真正长期资产——512 维向量可重算，但「这是谁」不可重获
- CLIP/GLM/InsightFace/FAISS/SQLite 皆可替换，人物判定不会变
- Knowledge Graph > Face Recognition：共现网络比单张识别更有价值

**短板**：产品层（Person Page / 检索入口 / 事件表达），非技术层。

**演进优先级**（标注密度是真正瓶颈，当前仅 2 具名人物 / 3,995 簇）：
1. 持续人物命名标注 → 2. 统一检索层 search.py → 3. 自动事件聚合 events → 4. Timeline 增强 → 5. 共现可视化 → 6. 视频/RAW 抽帧 → 7. 模型升级（已否决）

---

## 使用方法

### Phase A — 入库分类
```bash
# 全量运行（hybrid模式：CLIP主力 + GLM补判）
python organize_photos.py

# 指定输入/输出
python organize_photos.py "E:\待整理照片" "E:\QuarkSync\照片归档"

# 测试：只处理前 50 个
python organize_photos.py --limit 50

# 预演：不写库不复制，仅统计
python organize_photos.py --dry-run
```
Python 解释器：`C:\Users\liyun\.workbuddy\binaries\python\versions\3.13.12\python.exe`

### Phase B — 人脸检索
```bash
cd face_index
# 提取人脸（增量）
python face_extract.py [--limit N]
# 聚类 + 建索引
python cluster.py
# 种子检索
python retrieve.py --seeds "E:\待整理照片\皓祥" --name 皓祥 --topk 400
# 审查报告后回写
python commit_judgments.py --tag 皓祥
```
Venv：`C:\Users\liyun\.workbuddy\binaries\python\envs\default`（insightface + faiss-cpu + onnxruntime CPU）

### Phase C — 人物策展
```bash
cd face_index
# 重建索引（按物理文件夹定年份，不推断移动）
python photo_tool.py --person 运丰 --action reindex
# 生成重分类确认页（EXIF>文件名>embedding，带证据徽章）
python photo_tool.py --person 运丰 --action genreclassify
# 应用重分类（用户勾选导出后）
python photo_tool.py --person 运丰 --action applyreclassify --list reclassify_decisions.json
# 生成删除审查页
python photo_tool.py --person 运丰 --action gendelete
# 应用删除
python photo_tool.py --person 运丰 --action applydelete --list delete_list.json --yes
# 生成时间线
python photo_tool.py --person 运丰 --action gentimeline
# 重新生成预览页（可移植相对路径）
python photo_tool.py --person 运丰 --action regenhtml
```

## 环境与依赖
- **Phase A**: Python 3.13.12 + cn_clip + torch(CPU) + zhipuai + Pillow
- **Phase B/C**: venv `C:\Users\liyun\.workbuddy\binaries\python\envs\default` + insightface 1.0.1 + faiss-cpu 1.14.3 + onnxruntime 1.27.0
- **硬件**: CMP 40HX (Turing 8GB, 无 CUDA 运行时) — 全部 CPU 推理
- **GLM API**: ZHIPU_API_KEY 已设置（.env）
- **百度 API**: 未激活（Key 疑似标签，非实际 Key）

## 已知限制 / 待增强
- HEIC/LIVP/CR2：未装 pillow_heif/rawpy，EXIF 降级文件时间
- 视频/LIVP/RAW 不在 V1 人脸范围（需 ffmpeg+HEIF 抽帧）
- 年龄跨度导致同一人聚类分裂属预期；可靠检索靠种子图
- 真实瓶颈：cluster→person 标注（3995 簇仅 2 人具名），标注效率决定后续所有能力的数据厚度
- 环境无 OCR（tesseract/paddleocr 未装），时间水印用文件名日期作等价证据

## 关键约定
- **原图不可变**：原始文件永远不修改、不覆盖、不重命名。所有 AI 输出写入元数据。Metadata Evolves, Assets Don't.
- **判定即资产**：person_judgments 是长期资产，不可重获
- **高风险操作**：必须 dry-run → 展示方案 → 用户确认 → --yes 执行 → 立即核验磁盘计数
- **后台删除不可靠**：前台直接执行删除并立即核验，不依赖后台输出
- SOP 文档：`20_KNOWLEDGE/SOP/Photo-Organizer-SOP.md`
- Skill：`C:\Users\liyun\.workbuddy\skills\photo-organizer\SKILL.md`
