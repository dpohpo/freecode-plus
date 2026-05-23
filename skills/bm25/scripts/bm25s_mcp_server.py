#!/usr/bin/env python3
"""
BM25S MCP Server - 将 BM25S 暴露为 MCP 工具

安装依赖:
    pip install bm25s PyStemmer mcp

运行:
    python bm25s_mcp_server.py
"""

import json
import os
from pathlib import Path
from typing import Any, Optional

# MCP SDK
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# BM25S
import bm25s
import Stemmer

# 创建服务器实例
app = Server("bm25s-server")

# 全局状态
class BM25State:
    def __init__(self):
        self.retriever: Optional[bm25s.BM25] = None
        self.tokenizer: Optional[bm25s.tokenization.Tokenizer] = None
        self.corpus: list = []
        self.index_path: Optional[str] = None
        self.stemmer = Stemmer.Stemmer("english")

    def reset(self):
        self.retriever = None
        self.tokenizer = None
        self.corpus = []
        self.index_path = None

state = BM25State()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的 BM25S 工具"""
    return [
        Tool(
            name="bm25_index",
            description="为文档列表创建 BM25 索引",
            inputSchema={
                "type": "object",
                "properties": {
                    "documents": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "要索引的文档列表"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["robertson", "lucene", "atire", "bm25l", "bm25+"],
                        "default": "lucene",
                        "description": "BM25 算法变体"
                    },
                    "k1": {
                        "type": "number",
                        "default": 1.5,
                        "description": "词频饱和参数"
                    },
                    "b": {
                        "type": "number",
                        "default": 0.75,
                        "description": "文档长度归一化参数"
                    },
                    "stopwords": {
                        "type": "string",
                        "enum": ["en", "en_plus", "de", "fr", "es", "pt", "it", "ru", "zh", "tr", "none"],
                        "default": "en",
                        "description": "停用词语言"
                    },
                    "use_stemmer": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否使用词干提取"
                    }
                },
                "required": ["documents"]
            }
        ),
        Tool(
            name="bm25_search",
            description="使用 BM25 搜索最相关的文档",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询"
                    },
                    "k": {
                        "type": "integer",
                        "default": 5,
                        "description": "返回的文档数量"
                    },
                    "return_scores": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否返回分数"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="bm25_batch_search",
            description="批量搜索多个查询",
            inputSchema={
                "type": "object",
                "properties": {
                    "queries": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "搜索查询列表"
                    },
                    "k": {
                        "type": "integer",
                        "default": 5,
                        "description": "每个查询返回的文档数量"
                    }
                },
                "required": ["queries"]
            }
        ),
        Tool(
            name="bm25_save_index",
            description="保存 BM25 索引到磁盘",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "保存索引的目录路径"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="bm25_load_index",
            description="从磁盘加载 BM25 索引",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "索引目录路径"
                    },
                    "load_corpus": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否加载语料库"
                    },
                    "mmap": {
                        "type": "boolean",
                        "default": False,
                        "description": "是否使用内存映射模式"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="bm25_get_scores",
            description="获取查询对所有文档的 BM25 分数",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "查询文本"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="bm25_status",
            description="获取当前 BM25 索引状态",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """执行工具调用"""

    if name == "bm25_index":
        return await handle_index(arguments)
    elif name == "bm25_search":
        return await handle_search(arguments)
    elif name == "bm25_batch_search":
        return await handle_batch_search(arguments)
    elif name == "bm25_save_index":
        return await handle_save_index(arguments)
    elif name == "bm25_load_index":
        return await handle_load_index(arguments)
    elif name == "bm25_get_scores":
        return await handle_get_scores(arguments)
    elif name == "bm25_status":
        return await handle_status(arguments)
    else:
        return [TextContent(type="text", text=f"未知工具: {name}")]


async def handle_index(args: dict) -> list[TextContent]:
    """创建 BM25 索引"""
    try:
        documents = args["documents"]
        method = args.get("method", "lucene")
        k1 = args.get("k1", 1.5)
        b = args.get("b", 0.75)
        stopwords = args.get("stopwords", "en")
        use_stemmer = args.get("use_stemmer", True)

        if stopwords == "none":
            stopwords = None

        # 创建词干提取器
        stemmer = state.stemmer if use_stemmer else None

        # 分词
        tokenizer = bm25s.tokenization.Tokenizer(
            stemmer=stemmer,
            stopwords=stopwords,
            lower=True,
        )
        corpus_tokens = tokenizer.tokenize(documents, return_as="tuple")

        # 创建索引
        retriever = bm25s.BM25(
            method=method,
            k1=k1,
            b=b,
            corpus=documents,
        )
        retriever.index(corpus_tokens)

        # 保存状态
        state.retriever = retriever
        state.tokenizer = tokenizer
        state.corpus = documents

        result = {
            "success": True,
            "num_documents": len(documents),
            "vocab_size": len(tokenizer.get_vocab_dict()),
            "method": method,
            "k1": k1,
            "b": b,
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        return [TextContent(type="text", text=f"索引创建失败: {str(e)}")]


async def handle_search(args: dict) -> list[TextContent]:
    """搜索文档"""
    try:
        if state.retriever is None:
            return [TextContent(type="text", text="错误: 请先创建索引 (bm25_index)")]

        query = args["query"]
        k = args.get("k", 5)
        return_scores = args.get("return_scores", True)

        # 分词查询
        query_tokens = state.tokenizer.tokenize([query], update_vocab=False)

        # 检索
        results, scores = state.retriever.retrieve(query_tokens, k=k)

        # 格式化结果
        output = []
        for i in range(results.shape[1]):
            doc_idx = results[0, i]
            doc = state.corpus[doc_idx] if doc_idx < len(state.corpus) else str(doc_idx)
            score = float(scores[0, i])

            if return_scores:
                output.append({"rank": i + 1, "score": round(score, 4), "document": doc})
            else:
                output.append({"rank": i + 1, "document": doc})

        return [TextContent(type="text", text=json.dumps(output, indent=2, ensure_ascii=False))]

    except Exception as e:
        return [TextContent(type="text", text=f"搜索失败: {str(e)}")]


async def handle_batch_search(args: dict) -> list[TextContent]:
    """批量搜索"""
    try:
        if state.retriever is None:
            return [TextContent(type="text", text="错误: 请先创建索引 (bm25_index)")]

        queries = args["queries"]
        k = args.get("k", 5)

        # 分词所有查询
        query_tokens = state.tokenizer.tokenize(queries, update_vocab=False)

        # 批量检索
        results, scores = state.retriever.retrieve(query_tokens, k=k)

        # 格式化结果
        output = []
        for q_idx in range(len(queries)):
            query_results = []
            for i in range(results.shape[1]):
                doc_idx = results[q_idx, i]
                doc = state.corpus[doc_idx] if doc_idx < len(state.corpus) else str(doc_idx)
                score = float(scores[q_idx, i])
                query_results.append({
                    "rank": i + 1,
                    "score": round(score, 4),
                    "document": doc
                })
            output.append({
                "query": queries[q_idx],
                "results": query_results
            })

        return [TextContent(type="text", text=json.dumps(output, indent=2, ensure_ascii=False))]

    except Exception as e:
        return [TextContent(type="text", text=f"批量搜索失败: {str(e)}")]


async def handle_save_index(args: dict) -> list[TextContent]:
    """保存索引"""
    try:
        if state.retriever is None:
            return [TextContent(type="text", text="错误: 没有可保存的索引")]

        path = args["path"]
        Path(path).mkdir(parents=True, exist_ok=True)

        state.retriever.save(path, corpus=state.corpus)
        state.tokenizer.save_vocab(path)
        state.tokenizer.save_stopwords(path)
        state.index_path = path

        return [TextContent(type="text", text=f"索引已保存到: {path}")]

    except Exception as e:
        return [TextContent(type="text", text=f"保存失败: {str(e)}")]


async def handle_load_index(args: dict) -> list[TextContent]:
    """加载索引"""
    try:
        path = args["path"]
        load_corpus = args.get("load_corpus", True)
        mmap = args.get("mmap", False)

        state.retriever = bm25s.BM25.load(path, load_corpus=load_corpus, mmap=mmap)

        # 加载 tokenizer
        state.tokenizer = bm25s.tokenization.Tokenizer(stemmer=state.stemmer)
        state.tokenizer.load_vocab(path)
        state.tokenizer.load_stopwords(path)

        if load_corpus and state.retriever.corpus:
            state.corpus = state.retriever.corpus

        state.index_path = path

        result = {
            "success": True,
            "path": path,
            "num_documents": state.retriever.scores["num_docs"],
            "mmap": mmap,
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        return [TextContent(type="text", text=f"加载失败: {str(e)}")]


async def handle_get_scores(args: dict) -> list[TextContent]:
    """获取所有文档分数"""
    try:
        if state.retriever is None:
            return [TextContent(type="text", text="错误: 请先创建索引 (bm25_index)")]

        query = args["query"]

        # 分词
        query_tokens = state.tokenizer.tokenize([query], update_vocab=False)

        # 获取分数
        all_scores = state.retriever.get_scores(query_tokens[0])

        # 排序并显示
        scored_docs = [(i, float(s)) for i, s in enumerate(all_scores)]
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        output = {
            "query": query,
            "all_scores": [
                {"doc_idx": i, "score": round(s, 4), "document": state.corpus[i][:100] + "..." if len(state.corpus[i]) > 100 else state.corpus[i]}
                for i, s in scored_docs[:20]  # 只显示 top 20
            ]
        }

        return [TextContent(type="text", text=json.dumps(output, indent=2, ensure_ascii=False))]

    except Exception as e:
        return [TextContent(type="text", text=f"获取分数失败: {str(e)}")]


async def handle_status(args: dict) -> list[TextContent]:
    """获取索引状态"""
    status = {
        "indexed": state.retriever is not None,
        "num_documents": len(state.corpus),
        "index_path": state.index_path,
    }

    if state.retriever is not None:
        status["method"] = state.retriever.method
        status["k1"] = state.retriever.k1
        status["b"] = state.retriever.b
        status["num_docs_in_index"] = state.retriever.scores["num_docs"]

    if state.tokenizer is not None:
        status["vocab_size"] = len(state.tokenizer.get_vocab_dict())

    return [TextContent(type="text", text=json.dumps(status, indent=2))]


async def main():
    """运行 MCP 服务器"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
