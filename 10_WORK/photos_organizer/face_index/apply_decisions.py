# -*- coding: utf-8 -*-
"""应用 haoxiang_decisions.json 到皓祥文件夹。
分支规则（按 decision 值，不依赖 review.csv 的 无脸 标记）：
  bad  -> 大跨度年份项：从推断年份文件夹回退到原年份文件夹（用 undo_map.csv）
  ok   -> 大跨度年份项：保留推断年份（不动）
  has  -> 无脸项：保留在文件夹（不动）
  nohas-> 无脸项：移出皓祥文件夹到 _rejected/
未决的大跨度项：默认保留推断年份，报告中单列。
所有移动先建父目录、校验存在，并记录 apply_undo.csv 以便逆向。
"""
import csv, os, json, shutil

TARGET = r"E:\待整理照片\皓祥"
PV = os.path.join(TARGET, "_preview")
REVIEW = os.path.join(PV, "review.csv")
UNDOMAP = os.path.join(PV, "undo_map.csv")
INDEX = os.path.join(PV, "index.csv")
DEC = r"D:\重要数据\我的文档\Downloads\haoxiang_decisions.json"
REJECTED = os.path.join(TARGET, "_rejected")
APPLY_UNDO = os.path.join(PV, "apply_undo.csv")

# ---- 加载 ----
review = list(csv.DictReader(open(REVIEW, encoding="utf-8-sig")))
undo = {}  # new_abs -> original_abs
with open(UNDOMAP, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        undo[r["new_abs"].strip()] = r["original_abs"].strip()
decisions = {d["idx"]: d["decision"] for d in json.load(open(DEC, encoding="utf-8"))}

os.makedirs(REJECTED, exist_ok=True)

moves = []          # (src, dst, kind, note)
report_lines = []
undecided = []

# ---- 规划动作 ----
for idx, dec in decisions.items():
    if idx >= len(review):
        report_lines.append(f"[跳过] idx={idx} 超出 review.csv 范围")
        continue
    row = review[idx]
    cur = row["绝对路径"].strip()
    fname = os.path.basename(cur)
    if dec == "bad":
        orig = undo.get(cur)
        if not orig:
            report_lines.append(f"[缺 undo] idx={idx} {fname} 无原路径映射，跳过")
            continue
        if not os.path.exists(cur):
            report_lines.append(f"[缺失] idx={idx} {cur} 不存在，跳过")
            continue
        moves.append((cur, orig, "revert_year", f"idx{idx} bad: 回退到原年份"))
    elif dec == "nohas":
        dst = os.path.join(REJECTED, fname)
        if not os.path.exists(cur):
            report_lines.append(f"[缺失] idx={idx} {cur} 不存在，跳过")
            continue
        moves.append((cur, dst, "reject", f"idx{idx} nohas: 移出皓祥文件夹"))
    elif dec in ("ok", "has"):
        # 不动文件
        continue
    else:
        report_lines.append(f"[未知] idx={idx} decision={dec} 未知，跳过")

# 大跨度未决项检测：review 中 无脸=False 且跨度>=3 的行，若不在 decisions -> 未决
for i, row in enumerate(review):
    try:
        span = abs(int(row["推断年份"]) - int(row["原年份"]))
    except:
        span = 0
    if row["无脸"].strip().lower() != "true" and span >= 3:
        if i not in decisions:
            undecided.append((i, row["文件"], row["原年份"], row["推断年份"]))

# ---- 执行移动 ----
undo_rows = []
for src, dst, kind, note in moves:
    parent = os.path.dirname(dst)
    os.makedirs(parent, exist_ok=True)
    if os.path.abspath(src) == os.path.abspath(dst):
        report_lines.append(f"[同级] {src} 同路径，跳过")
        continue
    # 目标已存在则加后缀避免覆盖
    real_dst = dst
    if os.path.exists(real_dst):
        base, ext = os.path.splitext(real_dst)
        real_dst = f"{base}__dup{ext}"
    shutil.move(src, real_dst)
    undo_rows.append({"original_abs": real_dst, "new_abs": src, "kind": kind})
    report_lines.append(f"[{kind}] {os.path.basename(src)}  {os.path.dirname(src).split(chr(92))[-1]} -> {os.path.dirname(real_dst).split(chr(92))[-1]}")

# ---- 更新 index.csv ----
idx_rows = list(csv.DictReader(open(INDEX, encoding="utf-8-sig")))
fields = list(idx_rows[0].keys()) if idx_rows else []
rejected_names = {os.path.basename(m[1]) for m in moves if m[2] == "reject"}
reverted = {os.path.basename(m[0]): m[1] for m in moves if m[2] == "revert_year"}
new_rows = []
removed = 0
for r in idx_rows:
    name = os.path.basename(r["绝对路径"].strip())
    if name in rejected_names:
        removed += 1
        continue  # 移出的不进索引
    if name in reverted:
        new_abs = reverted[name]
        yr = os.path.dirname(new_abs).split(chr(92))[-1]
        r["绝对路径"] = new_abs
        r["相对路径"] = f"{yr}\\{name}"
        r["年份"] = yr
        r["是否变更"] = "False"
    new_rows.append(r)

with open(INDEX, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(new_rows)

# ---- 写 apply_undo.csv ----
with open(APPLY_UNDO, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["original_abs", "new_abs", "kind"])
    w.writeheader()
    w.writerows(undo_rows)

# ---- 报告 ----
n_revert = sum(1 for m in moves if m[2] == "revert_year")
n_reject = sum(1 for m in moves if m[2] == "reject")
rep = []
rep.append("==== 皓祥 decisions 回交执行报告 ====")
rep.append(f"决策条目: {len(decisions)}  |  实际执行移动: {len(moves)}")
rep.append(f"  回退年份(bad): {n_revert}")
rep.append(f"  移出文件夹(nohas): {n_reject}")
rep.append(f"  index.csv 移除行: {removed}")
rep.append(f"  未决大跨度项: {len(undecided)}")
for i, fn, o, n in undecided:
    rep.append(f"    - idx{i} {fn}: 原{o}->推断{n} 未决，默认保留推断年份")
rep.append("")
rep.append("---- 移动明细 ----")
rep.extend(report_lines)
rep.append("")
rep.append(f"剩余文件数(不含_preview/_duplicates): {sum(len(files) for _,_,files in os.walk(TARGET)) - len(os.listdir(REJECTED)) if False else ''}")
# 重新计数
total = 0
for dp, dn, fn in os.walk(TARGET):
    if "_preview" in dp or "_duplicates" in dp or "_rejected" in dp:
        continue
    total += len(fn)
rep.append(f"皓祥文件夹净文件数: {total}")
rep.append(f"已移出至 _rejected: {len(os.listdir(REJECTED))}")
rep.append("")
rep.append("逆向: 见 _preview/apply_undo.csv (original_abs->new_abs 反向移动即可复原)")

out = os.path.join(PV, "apply_report.txt")
open(out, "w", encoding="utf-8").write("\n".join(rep))
print("\n".join(rep))
