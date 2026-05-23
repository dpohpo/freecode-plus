# BM25S 完整知识库

## 概述

**BM25S** (BM25-Sparse) 是一个纯 Python 实现的超快速 BM25 算法库，由 Scipy 稀疏矩阵驱动。

### 核心特性

| 特性 | 描述 |
|------|------|
| **速度** | 比流行的 Python BM25 库快 500 倍 |
| **依赖** | 仅需 NumPy 和 SciPy |
| **技术** | 索引时"急切稀疏"分数计算 |
| **作者** | xhluca |
| **发布时间** | 2024年6月 |
| **论文** | [arXiv:2407.03618](https://arxiv.org/abs/2407.03618) |

---

## 核心算法原理

### BM25 公式

BM25 (Best Matching 25) 是一种用于信息检索的排序函数，用于根据查询对文档进行排名。

#### 基本公式

```
score(D, Q) = Σ IDF(qi) · (f(qi, D) · (k1 + 1)) / (f(qi, D) + k1 · (1 - b + b · |D|/avgdl))
```

其中:
- `f(qi, D)` = 词 qi 在文档 D 中的频率
- `|D|` = 文档 D 的长度
- `avgdl` = 平均文档长度
- `k1` = 词频饱和参数 (默认 1.5)
- `b` = 文档长度归一化参数 (默认 0.75)

#### IDF 计算 (不同变体)

```python
# Robertson (原始)
IDF(qi) = log((N - n(qi) + 0.5) / (n(qi) + 0.5))

# Lucene
IDF(qi) = log(1 + (N - n(qi) + 0.5) / (n(qi) + 0.5))

# ATIRE
IDF(qi) = log(N / n(qi))

# BM25L
IDF(qi) = log((N + 1) / (n(qi) + 0.5))

# BM25+
IDF(qi) = log((N + 1) / n(qi))
```

### BM25S 的核心创新: Eager Sparse Scoring

**关键思想**: 在索引阶段预先计算所有可能的 BM25 分数，存储为稀疏矩阵。

```
传统 BM25:  索引 → 查询时计算所有分数 → 排序
BM25S:      索引时预计算分数 → 稀疏矩阵存储 → 查询时仅需查找求和
```

这通过 CSC (压缩稀疏列) 格式存储，使得查询时的分数计算变成了简单的数组查找和累加操作。

---

## 安装

```bash
# 基础安装
pip install bm25s

# 完整安装 (包含词干提取等)
pip install "bm25s[full]"

# 额外依赖
pip install PyStemmer  # 词干提取
pip install "jax[cpu]" # 加速 top-k 选择
pip install numba      # Numba 后端加速
```

---

## 核心 API

### 1. BM25 类 (`bm25s/__init__.py`)

```python
import bm25s

# 初始化
retriever = bm25s.BM25(
    k1=1.5,           # 词频饱和参数
    b=0.75,           # 文档长度归一化
    delta=0.5,        # BM25L/BM25+ 的 delta 参数
    method="lucene",  # 算法变体: robertson, lucene, atire, bm25l, bm25+
    idf_method=None,  # IDF 计算方法 (None 表示与 method 相同)
    dtype="float32",  # 分数数据类型
    int_dtype="int32",# 索引数据类型
    corpus=None,      # 可选的语料库
    backend="numpy",  # 后端: numpy, numba, auto
)
```

#### 核心方法

| 方法 | 说明 |
|------|------|
| `index(corpus)` | 建立索引 |
| `retrieve(query_tokens, k=10)` | 检索 top-k 结果 |
| `get_scores(query_tokens)` | 获取所有文档分数 |
| `save(save_dir)` | 保存索引 |
| `BM25.load(save_dir)` | 加载索引 (类方法) |

### 2. Tokenization (`bm25s/tokenization.py`)

#### 快速分词函数

```python
import bm25s

# 简单分词
tokenized = bm25s.tokenize(
    texts,                    # 字符串或字符串列表
    lower=True,               # 转小写
    token_pattern=r"(?u)\b\w\w+\b",  # 正则模式
    stopwords="english",      # 停用词: "en", "en_plus", "de", "fr", "es", "pt", "it", "ru", "sv", "no", "zh", "tr"
    stemmer=None,             # 词干提取器
    return_ids=True,          # 返回 ID 还是字符串
)

# 返回 Tokenized 命名元组
tokenized.ids   # List[List[int]] - token ID 列表
tokenized.vocab # Dict[str, int] - 词汇表
```

#### Tokenizer 类 (高级用法)

```python
from bm25s.tokenization import Tokenizer

tokenizer = Tokenizer(
    lower=True,
    splitter=r"(?u)\b\w\w+\b",  # 正则或可调用函数
    stopwords="english",
    stemmer=None,  # PyStemmer.Stemmer("english") 或可调用对象
)

# 分词
corpus_tokens = tokenizer.tokenize(
    texts,
    update_vocab="if_empty",  # True, False, "if_empty", "never"
    return_as="ids",          # "ids", "string", "tuple", "stream"
)

# 词汇表管理
tokenizer.save_vocab(save_dir)
tokenizer.load_vocab(save_dir)
tokenizer.reset_vocab()
tokenizer.get_vocab_dict()

# 流式分词 (节省内存)
stream = tokenizer.streaming_tokenize(texts, update_vocab=False)
for doc_ids in stream:
    process(doc_ids)
```

### 3. 评分算法 (`bm25s/scoring.py`)

#### 词频分量 (TFC) 计算函数

```python
# Robertson (原始)
def _score_tfc_robertson(tf_array, l_d, l_avg, k1, b):
    return tf_array / (k1 * ((1 - b) + b * l_d / l_avg) + tf_array)

# ATIRE
def _score_tfc_atire(tf_array, l_d, l_avg, k1, b):
    return (tf_array * (k1 + 1)) / (tf_array + k1 * (1 - b + b * l_d / l_avg))

# BM25L
def _score_tfc_bm25l(tf_array, l_d, l_avg, k1, b, delta):
    c_array = tf_array / (1 - b + b * l_d / l_avg)
    return ((k1 + 1) * (c_array + delta)) / (k1 + c_array + delta)

# BM25+
def _score_tfc_bm25plus(tf_array, l_d, l_avg, k1, b, delta):
    num = (k1 + 1) * tf_array
    den = k1 * (1 - b + b * l_d / l_avg) + tf_array
    return (num / den) + delta
```

### 4. Top-K 选择 (`bm25s/selection.py`)

```python
from bm25s.selection import topk

scores, indices = topk(
    query_scores,      # 1D 分数数组
    k=10,              # 返回 top-k
    backend="auto",    # "numpy", "jax", "auto"
    sorted=True,       # 是否排序结果
)
```

---

## 完整使用示例

### 基础使用

```python
import bm25s
import Stemmer

# 语料库
corpus = [
    "a cat is a feline and likes to purr",
    "a dog is the human's best friend and loves to play",
    "a bird is a beautiful animal that can fly",
    "a fish is a creature that lives in water and swims",
]

# 词干提取器 (可选)
stemmer = Stemmer.Stemmer("english")

# 分词
corpus_tokens = bm25s.tokenize(corpus, stopwords="en", stemmer=stemmer)

# 创建索引
retriever = bm25s.BM25()
retriever.index(corpus_tokens)

# 查询
query = "does the fish purr like a cat?"
query_tokens = bm25s.tokenize(query, stemmer=stemmer)

# 检索 top-k
results, scores = retriever.retrieve(query_tokens, k=2)

for i in range(results.shape[1]):
    doc, score = results[0, i], scores[0, i]
    print(f"Rank {i+1} (score: {score:.2f}): {doc}")
```

### 保存和加载

```python
# 保存
retriever.save("animal_index_bm25", corpus=corpus)

# 加载
reloaded = bm25s.BM25.load("animal_index_bm25", load_corpus=True)

# 内存映射模式 (节省内存)
reloaded_mmap = bm25s.BM25.load("animal_index_bm25", mmap=True)
```

### 使用不同 BM25 变体

```python
# Robertson (原始)
retriever = bm25s.BM25(method="robertson", k1=1.5, b=0.75)

# Lucene (默认)
retriever = bm25s.BM25(method="lucene")

# ATIRE
retriever = bm25s.BM25(method="atire")

# BM25L (需要 delta)
retriever = bm25s.BM25(method="bm25l", delta=0.5)

# BM25+ (需要 delta)
retriever = bm25s.BM25(method="bm25+", delta=1.5)

# 混合: ATIRE 方法的 TFC + Robertson 的 IDF
retriever = bm25s.BM25(method="atire", idf_method="robertson")
```

### Hugging Face 集成

```python
import bm25s
from bm25s.hf import BM25HF
import os

# 创建索引
retriever = BM25HF()
corpus = ["doc1", "doc2", "doc3"]
corpus_tokens = bm25s.tokenize(corpus)
retriever.index(corpus_tokens)

# 保存到 Hugging Face Hub
token = os.environ["HF_TOKEN"]
retriever.save_to_hub("username/bm25s-model", token=token, corpus=corpus)

# 从 Hub 加载
reloaded = BM25HF.load_from_hub("username/bm25s-model", load_corpus=True)
```

### Numba 后端加速

```python
import bm25s

# 使用 Numba 后端
retriever = bm25s.BM25(backend="numba")

# 或自动选择
retriever = bm25s.BM25(backend="auto")
```

### 多进程检索

```python
results, scores = retriever.retrieve(
    query_tokens,
    k=10,
    n_threads=-1,      # -1 = 使用所有 CPU
    chunksize=50,      # 批处理大小
)
```

---

## 性能基准

### 查询吞吐量 (QPS) 对比

| 数据集 | BM25S | Elasticsearch | BM25-PT | Rank-BM25 |
|--------|-------|---------------|---------|-----------|
| arguana | **573.91** | 13.67 | 110.51 | 2 |
| fiqa | **507.03** | 16.96 | 20.52 | 4.46 |
| nfcorpus | **1196.16** | 45.84 | 256.67 | 224.66 |
| scifact | **952.92** | 20.81 | 184.3 | 47.6 |

### 内存效率

| 方法 | 加载索引(s) | 检索(s) | 加载后RAM(GB) | 检索后RAM(GB) |
|------|-------------|---------|---------------|---------------|
| In-memory | 8.61 | 21.09 | 4.36 | 4.45 |
| Memory-mapped | 0.53 | 20.22 | 0.49 | 2.16 |
| Mmap+Reload | 0.48 | 20.96 | 0.49 | 0.70 |

---

## 支持的停用词语言

| 代码 | 语言 |
|------|------|
| `en`, `english` | 英语 |
| `en_plus`, `english_plus` | 英语(扩展) |
| `de`, `german` | 德语 |
| `nl`, `dutch` | 荷兰语 |
| `fr`, `french` | 法语 |
| `es`, `spanish` | 西班牙语 |
| `pt`, `portuguese` | 葡萄牙语 |
| `it`, `italian` | 意大利语 |
| `ru`, `russian` | 俄语 |
| `sv`, `swedish` | 瑞典语 |
| `no`, `norwegian` | 挪威语 |
| `zh`, `chinese` | 中文 |
| `tr`, `turkish` | 土耳其语 |

---

## 源码结构

```
bm25s/
├── __init__.py      # BM25 主类
├── scoring.py       # 评分算法实现
├── tokenization.py  # 分词器和 tokenize 函数
├── selection.py     # Top-K 选择算法
├── stopwords.py     # 多语言停用词
├── hf.py            # Hugging Face 集成
├── version.py       # 版本号
├── numba/           # Numba JIT 加速
│   ├── __init__.py
│   ├── retrieve_utils.py
│   └── selection.py
└── utils/           # 工具函数
    ├── __init__.py
    ├── beir.py      # BEIR 数据集支持
    ├── corpus.py    # 语料库工具
    ├── benchmark.py # 性能基准
    └── json_functions.py
```

---

## 引用

```bibtex
@misc{bm25s,
      title={BM25S: Orders of magnitude faster lexical search via eager sparse scoring},
      author={Xing Han Lù},
      year={2024},
      eprint={2407.03618},
      archivePrefix={arXiv},
      primaryClass={cs.IR},
      url={https://arxiv.org/abs/2407.03618},
}
```

---

## 相关链接

- GitHub: https://github.com/xhluca/bm25s
- 文档: https://bm25s.github.io
- 论文: https://arxiv.org/abs/2407.03618
- HuggingFace 博客: https://huggingface.co/blog/xhluca/bm25s
