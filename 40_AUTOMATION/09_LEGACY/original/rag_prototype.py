#!/usr/bin/env python3
"""
禁毒宣传 RAG 原型 v0.1
轻量级：sentence-transformers 本地嵌入 + FAISS 向量检索 + DeepSeek API 生成

用法:
  # 构建索引（首次运行）
  python rag_prototype.py --build

  # 查询
  python rag_prototype.py --query "写一篇关于新型毒品的宣传稿"
  python rag_prototype.py --query "6月26日禁毒进校园活动怎么总结？"
"""

import sys
import os
import re
import json
import argparse
import glob
import pickle
from pathlib import Path

# ── 路径常量 ──────────────────────────────────────────────
KNOWLEDGE_DIRS = [
    # L1 - 永久知识 (最高优先级)
    r"H:\workspace\00_Personal_OS",
    # L1 - 参考资料 (已验证)
    r"H:\workspace\02_Reference",
    # L2 - 当前活跃工作区 (选择性)
    # r"H:\workspace\01_Workspaces",  # 按需取消注释
]

# 给每个来源标注层级
def get_layer(path):
    if "00_Personal_OS" in path:
        return "L1-永久"
    if "02_Reference" in path:
        return "L1-参考"
    if "01_Workspaces" in path:
        return "L2-项目"
    if "03_Assets" in path:
        return "L3-素材"
    if "04_Archive" in path or "05_Backup" in path:
        return "L4-归档"
    return "L0-未分类"

INDEX_FILE = r"G:\workspace\.temp_douyin\rag_index.pkl"
CHUNK_FILE = r"G:\workspace\.temp_douyin\rag_chunks.pkl"

# DeepSeek API
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"  # 或 deepseek-flash


def log(msg):
    print(f"[RAG] {msg}", flush=True)


# ── 文件读取与分块 ──────────────────────────────────────

def read_md_files(base_dirs):
    """读取多个知识库目录下所有 .md 文件"""
    docs = []
    for base_dir in base_dirs:
        if not os.path.exists(base_dir):
            log(f"⚠️ 目录不存在: {base_dir}")
            continue
        layer = get_layer(base_dir)
        files = glob.glob(os.path.join(base_dir, "**/*.md"), recursive=True)
        for fp in sorted(files):
            rel = os.path.relpath(fp, base_dir)
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception as e:
                continue
            if len(text.strip()) < 20:
                continue
            docs.append({"path": rel, "text": text, "layer": layer, "source": base_dir})
        log(f"  {base_dir} → {len(files)} files (layer: {layer})")
    return docs


def chunk_text(doc, max_chars=800, overlap=100):
    """将文档按段落分块"""
    sections = re.split(r"\n(?=#|\d\.\s|[-*]\s)", doc["text"])
    chunks = []
    for sec in sections:
        sec = sec.strip()
        if len(sec) < 30:
            continue
        if len(sec) <= max_chars:
            chunks.append({
                "path": doc["path"],
                "text": sec,
                "layer": doc.get("layer", "L0"),
                "source": doc.get("source", ""),
                "section": sec.split("\n")[0][:80]
            })
        else:
            words = sec.split()
            for i in range(0, len(words), max_chars - overlap):
                chunk_text = " ".join(words[i:i + max_chars])
                chunks.append({
                    "path": doc["path"],
                    "text": chunk_text,
                    "layer": doc.get("layer", "L0"),
                    "source": doc.get("source", ""),
                    "section": sec.split("\n")[0][:80]
                })
    return chunks


# ── 嵌入与索引 ──────────────────────────────────────────

def build_index():
    """构建向量索引"""
    log("读取知识库文件...")
    docs = read_md_files(KNOWLEDGE_DIRS)
    log(f"读取了 {len(docs)} 个文件")

    chunks = []
    for d in docs:
        chunks.extend(chunk_text(d))
    log(f"分块后共 {len(chunks)} 个段落")

    log("加载嵌入模型 (all-MiniLM-L6-v2)...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    texts = [c["text"] for c in chunks]
    log(f"生成 {len(texts)} 个嵌入向量...")
    embeddings = model.encode(texts, show_progress_bar=True)
    
    log("构建 FAISS 索引...")
    import faiss
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings.astype("float32"))
    
    # 保存
    faiss.write_index(index, INDEX_FILE)
    with open(CHUNK_FILE, "wb") as f:
        pickle.dump(chunks, f)
    
    log(f"索引构建完成！{len(chunks)} 个段落，维度 {dim}")
    log(f"   FAISS 索引: {INDEX_FILE}")
    log(f"   段落数据: {CHUNK_FILE}")


def load_index():
    """加载索引"""
    if not os.path.exists(INDEX_FILE) or not os.path.exists(CHUNK_FILE):
        log("❌ 索引文件不存在，请先运行 --build")
        sys.exit(1)
    
    import faiss
    index = faiss.read_index(INDEX_FILE)
    with open(CHUNK_FILE, "rb") as f:
        chunks = pickle.load(f)
    
    log(f"加载了 {len(chunks)} 个段落")
    return index, chunks


def retrieve(query, index, chunks, model, top_k=5):
    """检索最相关的段落"""
    query_vec = model.encode([query]).astype("float32")
    distances, indices = index.search(query_vec, top_k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < 0 or idx >= len(chunks):
            continue
        results.append({
            "score": float(distances[0][i]),
            "chunk": chunks[idx]
        })
    
    return results


# ── LLM 生成 ────────────────────────────────────────────

def call_llm(prompt, system_prompt=None):
    """调用 DeepSeek API"""
    import openai
    
    client = openai.OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL
    )
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    try:
        r = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=2000,
        )
        return r.choices[0].message.content
    except Exception as e:
        log(f"⚠️ API 调用失败: {e}")
        return f"[API Error: {e}]"


def query(query_text, show_context=False):
    """RAG 查询主流程"""
    log(f"查询: {query_text}")
    
    # 1. 加载索引和模型
    index, chunks = load_index()
    
    log("加载嵌入模型...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # 2. 检索
    log("检索相关段落...")
    results = retrieve(query_text, index, chunks, model, top_k=5)
    
    # 3. 构建上下文
    context_parts = []
    for r in results:
        source = r["chunk"]["path"]
        text = r["chunk"]["text"]
        layer = r["chunk"].get("layer", "L0")
        context_parts.append(f"[来源: {source}] [层级: {layer}]\n{text}\n")
    
    context = "\n---\n".join(context_parts)
    
    if show_context:
        print("\n" + "=" * 60)
        print("📚 检索到的上下文:")
        print("=" * 60)
        for i, r in enumerate(results):
            layer = r["chunk"].get("layer", "L0")
            print(f"\n--- [{i+1}] {r['chunk']['path']} (层级:{layer}, 距离:{r['score']:.2f}) ---")
            print(r['chunk']['text'][:300])
            if len(r['chunk']['text']) > 300:
                print("...")
    
    # 4. 生成回答
    system_prompt = """你是一个禁毒宣传领域的写作助手。
请基于提供的知识库内容回答用户的问题。
要求：
- 回答要符合政策规范，用词准确
- 引用具体来源（法规、案例、工作流程）
- 如果知识库中找不到相关信息，明确告知用户
- 回答风格要通俗易懂，适合面向公众的宣传场景"""
    
    rag_prompt = f"""请根据以下知识库内容回答问题。

知识库内容：
{context}

---
用户问题：{query_text}

请基于知识库内容给出回答。如果知识库内容不足以回答，请说明缺少什么信息。"""
    
    log("调用 DeepSeek 生成回答...")
    answer = call_llm(rag_prompt, system_prompt)
    
    return answer, results


def interactive():
    """交互式查询模式"""
    log("进入交互模式，输入 'quit' 退出\n")
    
    while True:
        try:
            q = input("\n🔍 请输入问题: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q or q.lower() == "quit":
            break
        
        answer, _ = query(q)
        print("\n" + "=" * 60)
        print("💡 回答:")
        print("=" * 60)
        print(answer)
        print()


# ── 主入口 ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="禁毒宣传 RAG 原型")
    parser.add_argument("--build", action="store_true", help="构建索引")
    parser.add_argument("--query", type=str, help="查询问题")
    parser.add_argument("--context", action="store_true", help="显示检索上下文")
    parser.add_argument("--interactive", action="store_true", help="交互模式")
    args = parser.parse_args()
    
    if args.build:
        build_index()
        return
    
    if args.query:
        answer, results = query(args.query, show_context=args.context)
        print("\n" + "=" * 60)
        print("💡 回答:")
        print("=" * 60)
        print(answer)
        return
    
    if args.interactive:
        interactive()
        return
    
    # 默认：交互模式
    interactive()


if __name__ == "__main__":
    main()
