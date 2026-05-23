#!/usr/bin/env python3
"""
BM25 Core Operations - 使用 bm25s 库实现 BM25 文本检索

安装依赖:
    pip install bm25s PyStemmer

使用方法:
    python bm25_core.py index --corpus "doc1" "doc2" --output ./my_index
    python bm25_core.py search --index ./my_index --query "search text" --k 5
    python bm25_core.py batch --index ./my_index --queries "q1" "q2" --k 5
    python bm25_core.py save --index ./my_index --output ./saved_index
    python bm25_core.py load --path ./saved_index
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

try:
    import bm25s
    import Stemmer
except ImportError:
    print("Error: Please install dependencies: pip install bm25s PyStemmer")
    sys.exit(1)


class BM25Manager:
    """BM25 索引和检索管理器"""

    def __init__(self, method: str = "lucene", k1: float = 1.5, b: float = 0.75,
                 delta: float = 0.5, use_stemmer: bool = True, stopwords: str = "en"):
        self.method = method
        self.k1 = k1
        self.b = b
        self.delta = delta
        self.use_stemmer = use_stemmer
        self.stopwords = stopwords

        self.retriever: Optional[bm25s.BM25] = None
        self.tokenizer: Optional[bm25s.tokenization.Tokenizer] = None
        self.corpus: List[str] = []

        # 初始化词干提取器
        self.stemmer = Stemmer.Stemmer("english") if use_stemmer else None

    def create_index(self, documents: List[str]) -> dict:
        """创建 BM25 索引"""
        self.corpus = documents

        # 创建分词器
        self.tokenizer = bm25s.tokenization.Tokenizer(
            stemmer=self.stemmer,
            stopwords=self.stopwords if self.stopwords != "none" else [],
            lower=True,
        )

        # 分词
        corpus_tokens = self.tokenizer.tokenize(documents, return_as="tuple")

        # 创建检索器
        self.retriever = bm25s.BM25(
            method=self.method,
            k1=self.k1,
            b=self.b,
            delta=self.delta,
            corpus=documents,
        )
        self.retriever.index(corpus_tokens)

        return {
            "success": True,
            "num_documents": len(documents),
            "vocab_size": len(self.tokenizer.get_vocab_dict()),
            "method": self.method,
            "k1": self.k1,
            "b": self.b,
        }

    def search(self, query: str, k: int = 5, return_scores: bool = True) -> List[dict]:
        """搜索单个查询"""
        if self.retriever is None:
            raise ValueError("请先创建索引")

        query_tokens = self.tokenizer.tokenize([query], update_vocab=False)
        results, scores = self.retriever.retrieve(query_tokens, k=k)

        output = []
        for i in range(results.shape[1]):
            doc_idx = int(results[0, i])
            doc = self.corpus[doc_idx] if doc_idx < len(self.corpus) else str(doc_idx)
            score = float(scores[0, i])

            item = {"rank": i + 1, "doc_index": doc_idx, "document": doc}
            if return_scores:
                item["score"] = round(score, 4)
            output.append(item)

        return output

    def batch_search(self, queries: List[str], k: int = 5) -> List[dict]:
        """批量搜索多个查询"""
        if self.retriever is None:
            raise ValueError("请先创建索引")

        query_tokens = self.tokenizer.tokenize(queries, update_vocab=False)
        results, scores = self.retriever.retrieve(query_tokens, k=k)

        output = []
        for q_idx in range(len(queries)):
            query_results = []
            for i in range(results.shape[1]):
                doc_idx = int(results[q_idx, i])
                doc = self.corpus[doc_idx] if doc_idx < len(self.corpus) else str(doc_idx)
                score = float(scores[q_idx, i])
                query_results.append({
                    "rank": i + 1,
                    "doc_index": doc_idx,
                    "score": round(score, 4),
                    "document": doc
                })
            output.append({
                "query_index": q_idx,
                "query": queries[q_idx],
                "results": query_results
            })

        return output

    def save(self, path: str) -> dict:
        """保存索引到磁盘"""
        if self.retriever is None:
            raise ValueError("没有可保存的索引")

        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)

        self.retriever.save(str(save_path), corpus=self.corpus)
        self.tokenizer.save_vocab(str(save_path))
        self.tokenizer.save_stopwords(str(save_path))

        return {
            "success": True,
            "path": str(save_path),
            "num_documents": len(self.corpus)
        }

    def load(self, path: str, mmap: bool = False) -> dict:
        """从磁盘加载索引"""
        load_path = Path(path)

        self.retriever = bm25s.BM25.load(str(load_path), load_corpus=True, mmap=mmap)

        # 加载分词器
        self.tokenizer = bm25s.tokenization.Tokenizer(stemmer=self.stemmer)
        self.tokenizer.load_vocab(str(load_path))
        self.tokenizer.load_stopwords(str(load_path))

        if self.retriever.corpus:
            self.corpus = self.retriever.corpus

        return {
            "success": True,
            "path": str(load_path),
            "num_documents": self.retriever.scores["num_docs"],
            "mmap": mmap
        }

    def get_scores(self, query: str) -> List[dict]:
        """获取查询对所有文档的分数"""
        if self.retriever is None:
            raise ValueError("请先创建索引")

        query_tokens = self.tokenizer.tokenize([query], update_vocab=False)
        all_scores = self.retriever.get_scores(query_tokens[0])

        scored_docs = [(i, float(s)) for i, s in enumerate(all_scores)]
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        return [
            {
                "doc_index": i,
                "score": round(s, 4),
                "document": self.corpus[i][:200] + "..." if len(self.corpus[i]) > 200 else self.corpus[i]
            }
            for i, s in scored_docs
        ]

    def status(self) -> dict:
        """获取索引状态"""
        status = {
            "indexed": self.retriever is not None,
            "num_documents": len(self.corpus),
        }

        if self.retriever is not None:
            status["method"] = self.retriever.method
            status["k1"] = self.retriever.k1
            status["b"] = self.retriever.b
            status["num_docs_in_index"] = self.retriever.scores["num_docs"]

        if self.tokenizer is not None:
            status["vocab_size"] = len(self.tokenizer.get_vocab_dict())

        return status


def main():
    parser = argparse.ArgumentParser(description="BM25 文本检索工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # index 命令
    index_parser = subparsers.add_parser("index", help="创建 BM25 索引")
    index_parser.add_argument("--corpus", nargs="+", required=True, help="文档列表")
    index_parser.add_argument("--method", default="lucene", choices=["robertson", "lucene", "atire", "bm25l", "bm25+"], help="BM25 变体")
    index_parser.add_argument("--k1", type=float, default=1.5, help="词频饱和参数")
    index_parser.add_argument("--b", type=float, default=0.75, help="文档长度归一化参数")
    index_parser.add_argument("--delta", type=float, default=0.5, help="BM25L/BM25+ 的 delta 参数")
    index_parser.add_argument("--stopwords", default="en", help="停用词语言")
    index_parser.add_argument("--no-stemmer", action="store_true", help="禁用词干提取")

    # search 命令
    search_parser = subparsers.add_parser("search", help="搜索文档")
    search_parser.add_argument("--query", required=True, help="搜索查询")
    search_parser.add_argument("--k", type=int, default=5, help="返回结果数量")
    search_parser.add_argument("--no-scores", action="store_true", help="不返回分数")

    # batch 命令
    batch_parser = subparsers.add_parser("batch", help="批量搜索")
    batch_parser.add_argument("--queries", nargs="+", required=True, help="查询列表")
    batch_parser.add_argument("--k", type=int, default=5, help="每个查询返回结果数量")

    # save 命令
    save_parser = subparsers.add_parser("save", help="保存索引")
    save_parser.add_argument("--output", required=True, help="保存路径")

    # load 命令
    load_parser = subparsers.add_parser("load", help="加载索引")
    load_parser.add_argument("--path", required=True, help="索引路径")
    load_parser.add_argument("--mmap", action="store_true", help="使用内存映射模式")

    # scores 命令
    scores_parser = subparsers.add_parser("scores", help="获取所有分数")
    scores_parser.add_argument("--query", required=True, help="查询文本")

    # status 命令
    subparsers.add_parser("status", help="获取索引状态")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    # 全局管理器 (保持状态)
    manager = BM25Manager()

    # 检查是否有保存的状态文件
    state_file = Path("/tmp/bm25_state.json")
    if state_file.exists() and args.command not in ["index", "load"]:
        try:
            with open(state_file) as f:
                state = json.load(f)
            if state.get("index_path"):
                manager.load(state["index_path"])
        except:
            pass

    try:
        if args.command == "index":
            result = manager.create_index(
                documents=args.corpus,
                method=args.method,
                k1=args.k1,
                b=args.b,
                delta=args.delta,
                stopwords=args.stopwords,
                use_stemmer=not args.no_stemmer,
            )
            print(json.dumps(result, indent=2))

            # 保存临时索引
            temp_path = "/tmp/bm25_temp_index"
            manager.save(temp_path)
            with open(state_file, "w") as f:
                json.dump({"index_path": temp_path}, f)

        elif args.command == "search":
            results = manager.search(args.query, k=args.k, return_scores=not args.no_scores)
            print(json.dumps(results, indent=2, ensure_ascii=False))

        elif args.command == "batch":
            results = manager.batch_search(args.queries, k=args.k)
            print(json.dumps(results, indent=2, ensure_ascii=False))

        elif args.command == "save":
            result = manager.save(args.output)
            with open(state_file, "w") as f:
                json.dump({"index_path": args.output}, f)
            print(json.dumps(result, indent=2))

        elif args.command == "load":
            result = manager.load(args.path, mmap=args.mmap)
            with open(state_file, "w") as f:
                json.dump({"index_path": args.path}, f)
            print(json.dumps(result, indent=2))

        elif args.command == "scores":
            results = manager.get_scores(args.query)
            print(json.dumps(results[:20], indent=2, ensure_ascii=False))

        elif args.command == "status":
            result = manager.status()
            print(json.dumps(result, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
