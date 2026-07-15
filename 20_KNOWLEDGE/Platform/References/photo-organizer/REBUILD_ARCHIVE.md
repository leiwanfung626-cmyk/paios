# 重建 face_index 于归档 — 任务记录

## 决策（2026-07-11, Evan 授权"自行判断最优路径"）
原源 `E:\待整理照片` 已消失，旧 `face_index.db` 路径全悬空 → 旧库废。
归档 `E:\QuarkSync\照片归档` 现存 **16,958 张**媒体（排除 90_Trash，8 类齐全），是可用新源。
不走运丰照片补全的 gallery 权宜法，直接重建 face_index 全链路（基础设施），顺带产出运丰差集。
依据：对 15,809 张图片只扫一次，既重建全库人物索引/共现/事件能力，又得运丰差集；与 gallery scan 时间成本相同，但资产更厚。

## 流程
1. `orchestrate_archive.py`：扫归档 → `archive_photo_index.db`（path 指向归档真实文件）
2. `face_extract.py --db archive_photo_index.db --out archive_face_index.db`：全量提脸（CPU，无 CUDA，预计 ~4-8h，增量续跑）
3. `retrieve_missed.py --person all`：**双人遗漏差集检索**（运丰+皓祥，同一人脸库，一次提取多人复用）
4. （可选）`cluster.py`：全库聚类，供后续共现/事件

## 双人差集检索（2026-07-11 追加，Evan：加皓祥，一次提取不跑两次）
- 参照系 R（已挑选好，只用年份真图，排除 _preview/_duplicates/_rejected）：
  - 运丰：`D:\重要数据\我的图片\Camera Roll\运丰` = 466 真图（+466 预览排除）
  - 皓祥：`D:\重要数据\我的图片\Camera Roll\皓祥` = 358 真图（+358 预览排除）
- 关键认知：**提脸只跑一次**，运丰/皓祥都是提取完成后在同一 `archive_face_index.db` 上做种子检索；加人 = 0 次额外提取。
- 脚本 `retrieve_missed.py`（新）：多人配置 PERSONS；暴力余弦（不依赖 FAISS/cluster）；候选按 photo 去重取最高 sim；md5 去重(候选∈R真图md5→标 is_dup 排除)；缩略图从归档原图按 bbox 现裁到 missed/<人名>/thumbs/（防 faces/ 命名碰撞）；自包含 review.html（内联数据+相对图片，file:// 直开）。
- 设计要点：archive_face_index.db 无 md5/cluster_id → md5 对候选现算；FAISS 未建 → numpy 暴力算，16k 脸毫秒级。
- 阈值 τ=0.30（可调）。md5 只识别字节相同副本；R 中被编辑过的图对应归档原图仍会作候选交人工判。

## 状态
- [x] `orchestrate_archive.py` 已写
- [x] `archive_photo_index.db` 已建（16958：photo 15809 / video 1149）
- [x] `face_extract` 全量提取完成（18:45:43，211.2 min，**33919 张脸**，错误 0）
- [x] `archive_face_index.db` 已建（33919 脸全有 embedding，DB 已解锁）
- [x] `retrieve_missed.py` 已写 + 验证 + 跑通（自动化 automation-... 触发）
- [x] **双人差集检索完成**（运丰 19:36 / 皓祥 20:46，τ=0.30）
  - 运丰：候选 6568（已收录 466 / 疑似遗漏 6102）；≥0.50 有 4232，0.40-0.50 有 734，0.35-0.40 有 698，0.30-0.35 有 904
  - 皓祥：候选 5795（已收录 357 / 疑似遗漏 5438）；≥0.50 有 3442，0.40-0.50 有 793，0.35-0.40 有 634，0.30-0.35 有 926
  - **精度结论**：τ=0.30 在 0.30–0.50 低分段误报多（运丰参照才 466 张却出 6102 候选）。≥0.50 为高置信区，建议先收；0.30–0.50 交人工按滑块筛。
  - 产物：`missed/运丰/{review.html,candidates.csv,thumbs/}`、`missed/皓祥/{...}`
- [ ] （可选）`cluster` 完成（共现/事件待建）

## 环境
- venv：`C:\Users\liyun\.workbuddy\binaries\python\envs\default`（insightface + onnxruntime 1.27 CPU，已验证全量跑通过）
- buffalo_l 权重：`C:\Users\liyun\.insightface\models\buffalo_l`
- 坑：cv2.imread 本环境坏 → face_extract 已用 PIL 读；无 CUDA，纯 CPU
- 旧 `face_index.db`(117MB) / `faiss_index.bin` 保留不动（历史参考，不覆盖）
