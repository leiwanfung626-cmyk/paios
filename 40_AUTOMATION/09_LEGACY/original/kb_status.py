#!/usr/bin/env python3
"""
知识库状态统计工具 kb_status.py
用途：查看知识库当前状态
"""

import os
import glob
from datetime import datetime

KNOWLEDGE_BASE = r"H:\workspace\02_Reference"
RAG_INDEX = r"G:\workspace\.temp_douyin"


def count_files(directory):
    """统计目录下的 .md 文件"""
    files = glob.glob(os.path.join(directory, "**/*.md"), recursive=True)
    return len(files)


def get_latest(directory):
    """获取最近修改时间"""
    latest = 0
    for root, dirs, files in os.walk(directory):
        for f in files:
            path = os.path.join(root, f)
            mtime = os.path.getmtime(path)
            if mtime > latest:
                latest = mtime
    return latest


def format_size(directory):
    total = 0
    for root, dirs, files in os.walk(directory):
        for f in files:
            path = os.path.join(root, f)
            total += os.path.getsize(path)
    if total < 1024:
        return f"{total}B"
    elif total < 1024 * 1024:
        return f"{total/1024:.0f}KB"
    else:
        return f"{total/1024/1024:.1f}MB"


def main():
    print("=" * 60)
    print("  知识库状态报告")
    print("=" * 60)

    # 总览
    print("\n📚 各领域统计:")
    print(f"{'领域':<12} {'文件数':>8} {'大小':>10} {'最近更新':>12}")
    print("-" * 45)

    total_files = 0
    for d in sorted(os.listdir(KNOWLEDGE_BASE)):
        dir_path = os.path.join(KNOWLEDGE_BASE, d)
        if not os.path.isdir(dir_path):
            continue
        count = count_files(dir_path)
        total_files += count
        size = format_size(dir_path)
        latest_ts = get_latest(dir_path)
        if latest_ts:
            latest = datetime.fromtimestamp(latest_ts).strftime("%m-%d %H:%M")
        else:
            latest = "-"
        print(f"{d:<12} {count:>8} {size:>10} {latest:>12}")

    print("-" * 45)
    print(f"{'合计':<12} {total_files:>8}")

    # 禁毒专题 (02_Reference/禁毒政策法规)
    print(f"\n🚨 禁毒专题 (02_Reference/禁毒政策法规):")
    drug_dir = os.path.join(KNOWLEDGE_BASE, "禁毒政策法规")
    if os.path.exists(drug_dir):
        for d in sorted(os.listdir(drug_dir)):
            dir_path = os.path.join(drug_dir, d)
            if not os.path.isdir(dir_path):
                continue
            count = count_files(dir_path)
            print(f"  {d}: {count} 个文件")

    # RAG 索引状态
    print(f"\n🔍 RAG 索引状态:")
    index_file = os.path.join(RAG_INDEX, "rag_index.pkl")
    chunk_file = os.path.join(RAG_INDEX, "rag_chunks.pkl")
    if os.path.exists(index_file) and os.path.exists(chunk_file):
        import pickle
        with open(chunk_file, "rb") as f:
            chunks = pickle.load(f)
        index_size = os.path.getsize(index_file) / 1024
        print(f"  FAISS 索引: {index_size:.0f}KB")
        print(f"  段落数: {len(chunks)}")
        index_mtime = datetime.fromtimestamp(os.path.getmtime(index_file)).strftime("%m-%d %H:%M")
        print(f"  上次构建: {index_mtime}")
    else:
        print(f"  ❌ 未构建（运行 rag_prototype.py --build）")

    print()

    # 建议
    print("💡 建议:")
    print("  知识库有新增内容后 → python rag_prototype.py --build")


if __name__ == "__main__":
    main()
