# 人脸索引模块 (face_index) — Face Retrieval Pipeline

## 定位
照片整理项目（photos_organizer）的**第二阶段**：在第一次全量分类+去重之后，
从"照片分类"切换到"人脸检索"。目标 = 全库人脸检测 + 特征提取 + 聚类 + 特定人物检索。

## 技术路线
- 检测+识别：**InsightFace `buffalo_l`**（scrfd_10g 检测 + arcface w600k_r50 识别，512维 embedding）
- 向量索引：**FAISS**（IndexFlatIP，余弦相似度）
- 运行：**onnxruntime CPU**（机器无 CUDA 运行时；GPU CMP 40HX 暂未启用，留作加速）
- 环境：managed python venv `C:\Users\liyun\.workbuddy\binaries\python\envs\default`（--system-site-packages 继承 torch/numpy/opencv/PIL）

## 数据范围
- 源：`photo_index.db` 中 `media_type='photo' AND master=1` → **11,954 张**（已排除 612 张重复标记）
- 读 `photos.path`（指向源目录 `E:\待整理照片` 原始图，只读，符合 Immutable Original Principle）
- 格式：jpg/png/webp/bmp/gif，PIL 原生可读；用 `ImageOps.exif_transpose` 尊重 EXIF 方向

## 文件
- `face_extract.py` — 检测+识别+入库+裁缩略图（增量，--limit 试点，--reset 重跑）
- `cluster.py` — FAISS 建索引 + 连通分量聚类（余弦阈值，默认 0.38）+ 写回 cluster_id
- `retrieve.py` — 特定人物检索（种子图/簇 → TopK）+ **交互式 HTML 报告**（✓/✗/? 审查 + 导出 judgments.json）+ 人物命名
- `commit_judgments.py` — **人工判断回写**：读 judgments.json / 编辑后的 results.csv → 更新 persons 人物库 + faces.person_id + person_judgments 审计表
- `face_index.db` — 独立库：faces / processed / persons / clusters / person_judgments / meta
- `faces/` — 112x112 人脸缩略图（命名 `{photo_id}_{face_idx}.jpg`）
- `faiss_index.bin` / `face_ids.npy` / `norm_emb.npy` — 检索索引持久化

## 使用
```bash
PY="$USERPROFILE/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
# 1. 全量提取（增量续跑；首次会下载 buffalo_l ~280MB）
$PY face_extract.py
# 2. 聚类 + 建索引
$PY cluster.py
# 3. 检索某目标人物（准备 10~30 张清晰照放一个文件夹）
$PY retrieve.py --seeds "路径/到/儿子照片" --tag 儿子 --topk 300
#    -> 打开 face_index/retrieval/儿子/report.html 交互式审查
# 4. 人工审查并回写（PAIOS 提交闭环）
#    4a. 在 report.html 里逐张点 ✓接受 / ✗排除 / ?存疑，按相似度过滤，
#        也可"全选≥X为接受"批量，然后"导出 judgments.json"。
#    4b. 把判断提交给 PAIOS（写回 face_index.db）：
$PY commit_judgments.py --tag 儿子
#        （默认读 retrieval/儿子/judgments.json；也支持 --csv 手动编辑的 results.csv）
#    可选：旧式整批确认（无逐张审查）
$PY retrieve.py --name 儿子 --confirm-faceids 12,45,78
$PY retrieve.py --name 父亲 --confirm-cluster 23
```

### 人工判断如何提交给 PAIOS（闭环说明）
1. **检索**：`retrieve.py` 产出 `retrieval/<人物>/report.html`（交互式）与 `results.csv`。
2. **审查**：人在 report.html 里逐张判 ✓/✗/?，点"导出 judgments.json"下载判断产物。
   - 判断产物是 PAIOS 一等公民元数据（JSON），原图零改动（Immutable Original Principle）。
3. **回写**：`commit_judgments.py --tag <人物>` 读 judgments.json →
   - 建/复用 `persons` 行；`faces.person_id` 接受→人物id、排除→-1、存疑→不动；
   - 全部判断落 `person_judgments` 审计表（face_id, person_id, judgment, reviewer, ts）。
4. **复用**：后续检索/排除样本可反查 `persons` + `person_judgments`；未来可把 person 标签
   反向同步到主库 `photo_index.db` 的 `photo_persons` 表，使主库可按人物查询。

## 数据运营层扩展（#1 人物元数据 + #4 共现网络）
- `build_cooccurrence.py` — 幂等迁移脚本：扩展 persons 表 + 重建 photo_persons + 建 person_pairs 视图 + 导出共现 CSV。
- **persons 表扩展字段**：`display_name`(展示名) / `aliases`(JSON别名) / `relationship`(关系) / `birth_year`(可空) / `confidence`(人工确认占比) / `cover_face_id`(封面脸)。
  - 原 `name` 保留作 slug；`display_name` 已回填为 name；`cover_face_id` 取该人 det_score 最高的脸；`confidence` 由 person_judgments 的 accept 占比算出。
  - `aliases`/`relationship`/`birth_year` 当前为空，待人工在 DB 或后续 UI 补全。
- **photo_persons 物化表**：`(photo_id, person_id, face_id)`，每照片每人物去重到 1 行（891 行，全部联回 photo_index.db.photos.date，覆盖率 891/891）。
- **person_pairs 视图**：任意两人同框次数 `SELECT pA,pB,cooc ... GROUP BY`。
- **导出**：`export/cooccurrence_matrix.csv`（人物对共现）、`export/cooccurrence_by_year.csv`（逐年共现，联 photos.date）。
- 当前仅 皓祥/运丰 两人 → 共现对 1 个（22 次同框）。命名更多人物后，关系网自动变密。
- 下一步（未做）：#2 主动学习排序（驱动 27,213 张未判定收敛）、#3 质量评分轻量代理（det_score×尺寸）。

## 关键决策 / 已知限制
- **年龄跨度**：20 年跨度的同一人（5/15/25 岁）会被聚类拆成多个簇，属预期。
  聚类仅作候选分组辅助；**真正可靠的是种子检索（Phase 2）**。
- 检索对种子图取每张脸 max 相似，合影稀释影响已削弱；建议种子用单人清晰照，跨年龄多备几张。
- 视频/LIVP/RAW 不在 V1 范围（需 ffmpeg+HEIF 抽帧，后续单独做）。
- CPU 速率约 1.8s/图 → 全量 ~6 小时，后台过夜跑。
