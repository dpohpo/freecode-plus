---
name: bm25
description: BM25 文本检索引擎，用于创建全文搜索索引、语义搜索和文档检索。触发场景：(1) 用户说 "/bm25" 或 "创建 BM25 索引" (2) 需要全文搜索、文档检索 (3) 需要基于关键词的语义搜索 (4) 批量文档相似度匹配 (5) 构建搜索引擎。基于 bm25s 库，比 rank_bm25 快 500 倍。
user-invocable: "true"
---

# BM25 文本检索引擎

基于 **bm25s** 库的超快速 BM25 文本检索系统。

## 文件结构

```
bm25/
├── SKILL.md                    # 技能说明 (本文件)
├── BM25S_KNOWLEDGE.md          # 完整知识库 (算法原理、API、示例)
├── README.md                   # 官方文档
├── bm25s/                      # 源码
│   ├── __init__.py             # BM25 主类
│   ├── scoring.py              # 评分算法
│   ├── tokenization.py         # 分词器
│   ├── selection.py            # Top-K 选择
│   ├── stopwords.py            # 停用词
│   ├── hf.py                   # HuggingFace 集成
│   ├── numba/                  # Numba 加速
│   └── utils/                  # 工具函数
└── scripts/
    ├── bm25_core.py            # 核心操作脚本
    ├── bm25s_mcp_server.py     # MCP 服务器
    └── quickstart.py           # 快速示例
```

## 依赖安装

```bash
pip install bm25s PyStemmer
```

## 核心功能

| 命令 | 说明 | 示例 |
|------|------|------|
| `bm25_index` | 创建索引 | `/bm25 index 文档1 文档2` |
| `bm25_search` | 搜索 | `/bm25 search 查询词` |
| `bm25_batch` | 批量搜索 | `/bm25 batch 查询1 查询2` |
| `bm25_save` | 保存索引 | `/bm25 save ./my_index` |
| `bm25_load` | 加载索引 | `/bm25 load ./my_index` |

## 快速开始

### 1. 创建索引

```python
import bm25s
import Stemmer

corpus = [
    "Python is a programming language",
    "JavaScript is for web development",
    "Machine learning uses Python",
]

stemmer = Stemmer.Stemmer("english")
corpus_tokens = bm25s.tokenize(corpus, stopwords="en", stemmer=stemmer)

retriever = bm25s.BM25(method="lucene")
retriever.index(corpus_tokens)
```

### 2. 搜索

```python
query = "python programming"
query_tokens = bm25s.tokenize(query, stemmer=stemmer)
results, scores = retriever.retrieve(query_tokens, k=5)
```

### 3. 批量搜索

```python
queries = ["python", "web", "machine learning"]
query_tokens = bm25s.tokenize(queries, stemmer=stemmer)
results, scores = retriever.retrieve(query_tokens, k=3)
```

### 4. 保存/加载

```python
retriever.save("./my_index", corpus=corpus)
loaded = bm25s.BM25.load("./my_index", load_corpus=True)
```

## 使用脚本

```bash
# 创建索引
python scripts/bm25_core.py index --corpus "doc1" "doc2"

# 搜索
python scripts/bm25_core.py search --query "search text" --k 5

# 批量搜索
python scripts/bm25_core.py batch --queries "q1" "q2"

# 保存/加载
python scripts/bm25_core.py save --output ./index
python scripts/bm25_core.py load --path ./index
```

## MCP 服务器

```bash
# 启动 MCP 服务器
python scripts/bm25s_mcp_server.py
```

提供工具: `bm25_index`, `bm25_search`, `bm25_batch_search`, `bm25_save_index`, `bm25_load_index`

## BM25 变体

| 变体 | 说明 | 参数 |
|------|------|------|
| `lucene` | Lucene 实现 (默认) | k1=1.5, b=0.75 |
| `robertson` | 原始 Robertson | k1=1.5, b=0.75 |
| `atire` | ATIRE 实现 | k1=1.5, b=0.75 |
| `bm25l` | BM25L | k1=1.5, b=0.75, delta=0.5 |
| `bm25+` | BM25+ | k1=1.5, b=0.75, delta=1.0 |

## 停用词语言

支持: `en`, `en_plus`, `de`, `fr`, `es`, `pt`, `it`, `ru`, `zh`, `tr`

## 详细文档

- **[BM25S_KNOWLEDGE.md](BM25S_KNOWLEDGE.md)** - 完整算法原理、API 文档、性能基准
- **[README.md](README.md)** - 官方使用说明
- **[scripts/quickstart.py](scripts/quickstart.py)** - 8 个完整示例

## 性能优化

1. **Numba 后端**: `bm25s.BM25(backend="numba")`
2. **内存映射**: `BM25.load(path, mmap=True)`
3. **批量查询**: 使用 `retrieve()` 批量处理
