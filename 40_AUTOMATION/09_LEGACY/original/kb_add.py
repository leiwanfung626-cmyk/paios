#!/usr/bin/env python3
"""
知识库快速录入工具 kb_add.py
用途：快捷地向禁毒知识库添加知识条目
用法：python kb_add.py
      交互式问答，自动填写模板
"""

import os
import sys
from datetime import date

KNOWLEDGE_BASE = r"H:\workspace\02_Reference"

CATEGORIES = {
    "1": ("AI", "AI/技术"),
    "2": ("管理", "管理/方法论"),
    "3": ("禁毒政策法规", "禁毒宣传"),
    "4": ("考研", "考研"),
    "5": ("人文", "人文"),
    "6": ("健康", "健康"),
    "7": ("心理", "心理"),
    "8": ("创作", "创作"),
}


def main():
    print("=" * 50)
    print("  禁毒知识库 - 快速录入")
    print("=" * 50)

    # 1. 选择分类
    print("\n选择分类：")
    for key, (_, name) in CATEGORIES.items():
        print(f"  {key}. {name}")

    choice = input("\n分类编号: ").strip()
    if choice not in CATEGORIES:
        print("❌ 无效选择")
        return

    subdir, cat_name = CATEGORIES[choice]
    dest_dir = os.path.join(KNOWLEDGE_BASE, subdir)
    os.makedirs(dest_dir, exist_ok=True)

    # 2. 输入信息
    title = input("\n标题: ").strip()
    if not title:
        print("❌ 标题不能为空")
        return

    today = date.today().isoformat()
    filename = f"{today}_{title}.md"
    # 处理不合法文件名字符
    filename = "".join(c if c.isalnum() or c in " _-." else "_" for c in filename)
    filepath = os.path.join(dest_dir, filename)

    # 3. 检查是否已存在
    if os.path.exists(filepath):
        overwrite = input(f"⚠️ 文件已存在: {filename}\n覆盖? (y/n): ").strip().lower()
        if overwrite != "y":
            print("已取消")
            return

    # 4. 输入来源和关键词
    source = input("来源 (工作产出/政策文件/案例/其他): ").strip() or "工作产出"
    keywords = input("关键词 (逗号分隔): ").strip() or "待补充"

    # 5. 输入正文
    print("\n输入正文内容 (输入 --- 单独一行结束):")
    lines = []
    while True:
        line = input()
        if line.strip() == "---":
            break
        lines.append(line)
    content = "\n".join(lines)

    if not content.strip():
        # 如果没有正文，打开编辑器编辑
        print("⚠️ 内容为空，将创建空白模板")
        content = "待补充"

    # 6. 生成文件
    md_content = f"""# {title}

> **日期**: {today}
> **来源**: {source}
> **关键词**: {keywords}
> **分类**: {cat_name}

---

{content}
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\n✅ 已保存: {filepath}")
    print(f"   记得稍后运行 rag_prototype.py --build 重建索引")


if __name__ == "__main__":
    main()
