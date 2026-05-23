#!/usr/bin/env python3
"""
BM25S 快速使用示例集合
======================

安装: pip install bm25s PyStemmer
"""

import bm25s
import Stemmer

# ============================================================
# 示例 1: 最简单的使用
# ============================================================
def example_basic():
    """最基础的 BM25 使用"""
    corpus = [
        "The quick brown fox jumps over the lazy dog",
        "Never jump over a lazy dog quickly",
        "A fast fox is better than a slow dog",
        "Dogs and foxes are both canines",
    ]

    # 分词 (使用默认设置)
    corpus_tokens = bm25s.tokenize(corpus)

    # 创建索引
    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)

    # 搜索
    query_tokens = bm25s.tokenize("fast fox jumping")
    results, scores = retriever.retrieve(query_tokens, k=2)

    print("=== 基础示例 ===")
    for i in range(results.shape[1]):
        print(f"Rank {i+1}: score={scores[0,i]:.4f}, doc={results[0,i]}")


# ============================================================
# 示例 2: 带词干提取
# ============================================================
def example_with_stemmer():
    """使用词干提取提升搜索质量"""
    corpus = [
        "running and jumping are fun activities",
        "the runner jumped over the hurdle",
        "she runs every morning for exercise",
    ]

    # 创建词干提取器
    stemmer = Stemmer.Stemmer("english")

    # 分词时应用词干提取
    corpus_tokens = bm25s.tokenize(corpus, stemmer=stemmer, stopwords="en")

    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)

    # 查询也需要同样的处理
    query_tokens = bm25s.tokenize("run jump", stemmer=stemmer)
    results, scores = retriever.retrieve(query_tokens, k=3)

    print("\n=== 词干提取示例 ===")
    for i in range(results.shape[1]):
        print(f"Rank {i+1}: score={scores[0,i]:.4f}")


# ============================================================
# 示例 3: 不同 BM25 变体
# ============================================================
def example_variants():
    """使用不同的 BM25 变体"""
    corpus = [
        "machine learning is a subset of artificial intelligence",
        "deep learning uses neural networks",
        "natural language processing is an AI field",
    ]

    corpus_tokens = bm25s.tokenize(corpus)

    variants = [
        ("robertson", {}),
        ("lucene", {}),
        ("atire", {}),
        ("bm25l", {"delta": 0.5}),
        ("bm25+", {"delta": 1.0}),
    ]

    print("\n=== BM25 变体对比 ===")
    query_tokens = bm25s.tokenize("artificial intelligence machine learning")

    for method, extra_params in variants:
        retriever = bm25s.BM25(method=method, **extra_params)
        retriever.index(corpus_tokens)
        results, scores = retriever.retrieve(query_tokens, k=1)
        print(f"{method:12s}: top score = {scores[0,0]:.4f}")


# ============================================================
# 示例 4: 保存和加载
# ============================================================
def example_save_load():
    """保存和加载索引"""
    import tempfile
    import os

    corpus = ["doc one", "doc two", "doc three"]

    # 创建并保存
    corpus_tokens = bm25s.tokenize(corpus)
    retriever = bm25s.BM25(corpus=corpus)
    retriever.index(corpus_tokens)

    with tempfile.TemporaryDirectory() as tmpdir:
        retriever.save(tmpdir, corpus=corpus)

        # 加载
        loaded = bm25s.BM25.load(tmpdir, load_corpus=True)

        # 测试
        query_tokens = bm25s.tokenize("doc")
        results, scores = loaded.retrieve(query_tokens, k=2)

        print("\n=== 保存/加载示例 ===")
        print(f"成功加载 {loaded.scores['num_docs']} 个文档的索引")


# ============================================================
# 示例 5: 批量查询
# ============================================================
def example_batch_queries():
    """批量处理多个查询"""
    corpus = [
        "Python is a programming language",
        "JavaScript is used for web development",
        "Java is also a popular language",
        "Go is known for concurrency",
    ]

    corpus_tokens = bm25s.tokenize(corpus)
    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)

    # 多个查询
    queries = ["python programming", "web development", "concurrency"]
    query_tokens = bm25s.tokenize(queries)

    results, scores = retriever.retrieve(query_tokens, k=2)

    print("\n=== 批量查询示例 ===")
    for q_idx, query in enumerate(queries):
        print(f"\n查询: {query}")
        for i in range(results.shape[1]):
            doc_idx = results[q_idx, i]
            print(f"  Rank {i+1}: score={scores[q_idx, i]:.4f}, doc={corpus[doc_idx]}")


# ============================================================
# 示例 6: 自定义 Tokenizer
# ============================================================
def example_custom_tokenizer():
    """使用自定义分词器"""
    from bm25s.tokenization import Tokenizer

    corpus = [
        "user@example.com sent an email",
        "contact us at support@company.org",
        "email: admin@test.net for help",
    ]

    # 自定义分隔器: 保留邮箱格式
    def custom_splitter(text):
        import re
        # 分词但保留邮箱
        tokens = re.findall(r'[\w.+-]+@[\w.-]+\.\w+|\w+', text)
        return tokens

    tokenizer = Tokenizer(
        splitter=custom_splitter,
        stopwords="en",
        lower=True,
    )

    corpus_tokens = tokenizer.tokenize(corpus, return_as="tuple")

    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)

    query_tokens = tokenizer.tokenize(["email address"], update_vocab=False)
    results, scores = retriever.retrieve(query_tokens, k=2)

    print("\n=== 自定义分词器示例 ===")
    print(f"词汇表: {list(tokenizer.get_vocab_dict().keys())[:10]}")


# ============================================================
# 示例 7: 获取所有分数
# ============================================================
def example_get_all_scores():
    """获取查询对所有文档的分数"""
    corpus = [
        "apple fruit healthy",
        "apple company technology",
        "banana fruit yellow",
        "orange fruit citrus",
    ]

    corpus_tokens = bm25s.tokenize(corpus)
    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)

    query_tokens = bm25s.tokenize("apple fruit")

    # 获取所有文档分数
    all_scores = retriever.get_scores(query_tokens[0])

    print("\n=== 所有分数示例 ===")
    for i, score in enumerate(all_scores):
        print(f"Doc {i}: score={score:.4f}, text={corpus[i]}")


# ============================================================
# 示例 8: 使用 Numba 加速
# ============================================================
def example_numba_backend():
    """使用 Numba 后端加速"""
    corpus = [f"document number {i} with some content" for i in range(1000)]

    corpus_tokens = bm25s.tokenize(corpus)

    # 使用 numba 后端
    try:
        retriever = bm25s.BM25(backend="numba")
        retriever.index(corpus_tokens)

        query_tokens = bm25s.tokenize("document content")
        results, scores = retriever.retrieve(query_tokens, k=5)

        print("\n=== Numba 后端示例 ===")
        print("Numba 后端已启用 (更快)")
    except ImportError:
        print("\n=== Numba 后端示例 ===")
        print("Numba 未安装，使用默认后端")


# ============================================================
# 主函数
# ============================================================
if __name__ == "__main__":
    example_basic()
    example_with_stemmer()
    example_variants()
    example_save_load()
    example_batch_queries()
    example_custom_tokenizer()
    example_get_all_scores()
    example_numba_backend()

    print("\n" + "="*50)
    print("所有示例运行完成!")
