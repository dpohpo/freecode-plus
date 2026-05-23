

---
name: searchin
description: >
user-invocable: "true"
  混合检索系统：BM25 + BERT(FAISS) + RRF + grep。
  对接现有的 semantic-search 系统（paraphrase-multilingual-MiniLM-L12-v2 + FAISS IndexFlatIP）。
  BM25 补充词频精确匹配能力，RRF 融合两路排名，grep 做确定性验证。
  触发：需要搜索 instincts、检索历史经验、为 session 提供上下文。
---
 **反幻觉铁律（全局生效 | 详见 ~/.claude/CLAUDE.md）**
> 1.诚信：不知道就说不知道，不编造 2.实事求是：证明之前保持怀疑，自证无效 3.98%门槛：置信度<98%禁止确定性语气 4.失效条件必标：技术声明必须标注何时不成立 5.代码交付：所有外部API/命令/配置必须验证真实性，未验证标注 UNVERIFIED | 豁免：仅用户主动声明时可跳过

> **编码铁律+自审清单（涉及代码时生效 | 详见 /coding）**
> 铁律：先扫描后编码 | 双轨验证(网络+执行)不可省 | 溯源到一手(官方文档/repo) | 98%才用确定语气 | 自建功能100%三轨验证 | 构建链每层VERIFIED | 失效条件必标 | 不存在要三轮证明
> 自审：所有外部声明已识别 | 所有依赖>=98%VERIFIED | 代码无未标注外部引用 | 技术声明含生效/失效/验证三元组 | 未使用should work

> **自对齐协议（全局生效 | 病毒式传染 — 所有模式/技能必须携带此段）**
> 每次执行前，用1行自检：`[ALIGN] 模式:<当前> | 任务:<描述> | 匹配:是/否 | 置信度:X%`
> 匹配=否 或 置信度<80% → 暂停，向用户建议切换模式。无模式时 → 评估是否需要模式。


# Cortex Search

在现有 FAISS 语义搜索基础上叠加 BM25 精确匹配的混合检索引擎。

## 现有系统

你已经有一套可用的语义搜索：

```
模型：paraphrase-multilingual-MiniLM-L12-v2（384 维，多语言）
索引：~/.claude/tools/semantic-search/index/index.faiss（133MB，IndexFlatIP）
元数据：~/.claude/tools/semantic-search/index/metadata.pkl（48MB）
分块：500 字符/块，100 字符重叠
覆盖：967 文件，90,876 块
调用：semsearch search "查询内容" -k 10
源码：~/.claude/tools/semantic-search/semantic_search.py
```

这套系统的优势是语义理解（"跨域" ≈ "CORS"）。
它的盲区是精确术语匹配——BM25 补这个缺。

## 架构

```
已有索引（不动）
  └─ FAISS IndexFlatIP（90,876 块，133MB）

新增索引（SessionStart 时构建，~100ms）
  └─ bm25s 索引（复用 FAISS 的分块数据）

每次查询（~60ms）
  ├─ bm25s top-50           (~5ms)  ─┐
  │                                   ├→ RRF 融合  (~<1ms)
  ├─ FAISS semsearch top-50 (~50ms) ─┘      │
  │                                         ▼
  └─ grep 精确匹配加权 ─────────→ 最终 top-5  (~3ms)
```

关键：**BM25 和 FAISS 在同一粒度上操作——chunk 级别（500 字符/块）**。
两者返回的都是 chunk ID，RRF 直接融合，无粒度冲突。

## 为什么在 FAISS 之上还要加 BM25

```
查询："ERR_CONNECTION_REFUSED"

FAISS（语义）：
  #1 "network connectivity issues and troubleshooting"    score=0.71
  #2 "connection timeout handling in Node.js"             score=0.68
  #3 文档含 "ERR_CONNECTION_REFUSED" 原文                  score=0.65

BM25（词频）：
  #1 文档含 "ERR_CONNECTION_REFUSED" 原文                  score=12.3
  #2 "ERR_CONNECTION_RESET vs ERR_CONNECTION_REFUSED"      score=8.7

→ FAISS 把精确包含错误码的文档排到了第三
→ BM25 直接把它排第一
→ RRF 融合后：精确文档排第一（两者共识）
```

FAISS 在语义上更"全面"的文档会排高，但用户搜错误码时要的是精确命中。
BM25 天然解决这个问题。

## 依赖安装

```bash
# 新增依赖（FAISS 和 sentence-transformers 你已经有了）
pip install bm25s PyStemmer
```

## 完整实现

```python
"""
cortex_search.py — 对接现有 FAISS 语义搜索的混合检索引擎

用法：
    searcher = CortexSearch()
    searcher.build_bm25_index()                # SessionStart 时调用一次
    results = searcher.search(query, top_k=5)   # 每次查询
"""

import os
import re
import pickle
import subprocess
import numpy as np
import bm25s
import Stemmer
from collections import defaultdict
from pathlib import Path


# ══════════════════════════════════════════════
# 配置（对接你的现有系统）
# ══════════════════════════════════════════════

SEMSEARCH_DIR = Path.home() / ".claude/tools/semantic-search"
INDEX_FILE = SEMSEARCH_DIR / "index/index.faiss"
METADATA_FILE = SEMSEARCH_DIR / "index/metadata.pkl"
SEMSEARCH_BIN = SEMSEARCH_DIR / "semsearch"

# BM25 索引缓存位置
BM25_CACHE_DIR = SEMSEARCH_DIR / "index/bm25_cache"


class CortexSearch:
    """
    混合搜索：BM25（词频）+ FAISS（语义）+ RRF + grep。
    FAISS 部分复用现有 semantic-search 系统。
    BM25 部分在 FAISS 的同粒度 chunk 上新建索引。
    """

    def __init__(self, rrf_k: int = 60, grep_boost: float = 1.3):
        self.rrf_k = rrf_k
        self.grep_boost = grep_boost
        self.stemmer = Stemmer.Stemmer("english")

        # BM25 状态
        self.bm25 = None
        self.chunks = []        # chunk 文本列表
        self.chunk_meta = []    # 每个 chunk 的元数据（文件路径、偏移等）

    # ──────────────────────────────────────────────
    # 索引构建
    # ──────────────────────────────────────────────

    def build_bm25_index(self):
        """
        从现有 FAISS metadata.pkl 中加载 chunk 数据，
        在同粒度上建立 BM25 索引。

        metadata.pkl 包含每个 chunk 的文本和源文件信息。
        BM25 索引复用这些 chunk，确保与 FAISS 粒度一致。

        耗时：~100-200ms（90,876 块）
        """
        # 加载现有元数据
        with open(METADATA_FILE, "rb") as f:
            metadata = pickle.load(f)

        # metadata 结构：[{"file": str, "file_hash": str, "chunk": str}, ...]
        self.chunk_meta = metadata
        self.chunks = [m["chunk"] for m in metadata]

        # 建 BM25 索引
        corpus_tokens = bm25s.tokenize(
            self.chunks, stopwords="en", stemmer=self.stemmer
        )
        self.bm25 = bm25s.BM25(method="lucene")
        self.bm25.index(corpus_tokens)

    # ──────────────────────────────────────────────
    # 搜索
    # ──────────────────────────────────────────────

    def search(
        self,
        query: str,
        top_k: int = 5,
        candidates: int = 50,
    ) -> list[dict]:
        """
        混合搜索：BM25 + FAISS → RRF 融合 → grep 加权 → top_k。

        返回：[{"chunk_id": int, "text": str, "source": str,
                "score": float}, ...]

        耗时：~60ms
        """
        k = min(candidates, len(self.chunks))

        # ── BM25 检索（chunk 级别）──
        bm25_results = self._bm25_search(query, k)

        # ── FAISS 检索（chunk 级别）──
        faiss_results = self._faiss_search(query, k)

        # ── RRF 融合 ──
        if bm25_results and faiss_results:
            weights = self._detect_weights(query)
            fused = self._rrf_fuse(
                [bm25_results, faiss_results],
                weights=weights,
            )
        elif bm25_results:
            fused = bm25_results
        elif faiss_results:
            fused = faiss_results
        else:
            return []

        # ── grep 精确匹配加权 ──
        keywords = self._extract_grep_keywords(query)
        if keywords:
            fused = self._grep_boost_results(fused, keywords)

        # ── 格式化输出 ──
        results = []
        for chunk_id, score in fused[:top_k]:
            meta = self.chunk_meta[chunk_id]
            results.append({
                "chunk_id": chunk_id,
                "text": self.chunks[chunk_id][:300],
                "file": meta.get("file", "unknown"),
                "score": round(score, 6),
            })

        return results

    # ── BM25 ──

    def _bm25_search(
        self, query: str, top_k: int
    ) -> list[tuple[int, float]]:
        """BM25 在 chunk 级别检索。返回 [(chunk_id, score), ...]"""
        query_tokens = bm25s.tokenize(query, stemmer=self.stemmer)
        results, scores = self.bm25.retrieve(query_tokens, k=top_k)

        output = []
        for i in range(len(results[0])):
            idx = int(results[0][i])
            score = float(scores[0][i])
            if score > 0:
                output.append((idx, score))
        return output

    # ── FAISS ──

    def _faiss_search(
        self, query: str, top_k: int
    ) -> list[tuple[int, float]]:
        """
        调用现有 FAISS 语义搜索。
        两种方式，按可用性选择：

        方式 A：直接调 semsearch CLI（简单，有进程开销）
        方式 B：直接加载 FAISS 索引 + 模型（快，需要内存）

        默认用方式 B（性能更好）。
        """
        return self._faiss_search_direct(query, top_k)

    def _faiss_search_direct(
        self, query: str, top_k: int
    ) -> list[tuple[int, float]]:
        """方式 B：直接用 FAISS 和模型查询。"""
        import faiss
        from sentence_transformers import SentenceTransformer

        # 懒加载（首次调用时加载，后续复用）
        if not hasattr(self, "_faiss_index"):
            self._faiss_index = faiss.read_index(str(INDEX_FILE))
            self._model = SentenceTransformer(
                "paraphrase-multilingual-MiniLM-L12-v2"
            )

        query_embedding = self._model.encode([query])
        faiss.normalize_L2(query_embedding)
        scores, indices = self._faiss_index.search(
            query_embedding, top_k
        )

        output = []
        for i in range(len(indices[0])):
            idx = int(indices[0][i])
            score = float(scores[0][i])
            if idx >= 0 and score > 0.3:  # 复用你的 threshold=0.3
                output.append((idx, score))
        return output

    def _faiss_search_cli(
        self, query: str, top_k: int
    ) -> list[tuple[int, float]]:
        """方式 A：通过 CLI 调用 semsearch。进程开销 ~100ms。"""
        cmd = [
            str(SEMSEARCH_BIN), "search", query,
            "-k", str(top_k),
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10
        )
        # 解析 semsearch 输出，提取 chunk_id 和 score
        # 具体解析逻辑取决于 semsearch 的输出格式
        # TODO: 根据实际输出格式实现
        return []

    # ── RRF 融合 ──

    def _rrf_fuse(
        self,
        ranked_lists: list[list[tuple[int, float]]],
        weights: list[float] = None,
    ) -> list[tuple[int, float]]:
        """
        Reciprocal Rank Fusion。延迟 < 1ms。

        公式：RRF_score(d) = Σ weight_i / (k + rank_i(d))
        k=60，Cormack et al. SIGIR 2009。

        单路输入时退化为 passthrough（零成本保留，合理冗余）。
        """
        n = len(ranked_lists)
        if weights is None:
            weights = [1.0] * n

        total_w = sum(weights)
        weights = [w / total_w for w in weights]

        rrf_scores = defaultdict(float)
        for i, ranked_list in enumerate(ranked_lists):
            for rank, (doc_id, _score) in enumerate(ranked_list, start=1):
                rrf_scores[doc_id] += weights[i] / (self.rrf_k + rank)

        return sorted(
            rrf_scores.items(), key=lambda x: x[1], reverse=True
        )

    # ── 动态权重 ──

    def _detect_weights(self, query: str) -> list[float]:
        """
        技术术语密集 → BM25 权重高（精确匹配重要）
        自然语言描述 → FAISS 权重高（语义理解重要）
        """
        signals = 0
        signals += len(re.findall(r"\b[A-Z]{2,}\b", query))
        signals += len(re.findall(r"\b[a-z]+[A-Z][a-zA-Z]*\b", query))
        signals += len(re.findall(r"\b\w+_\w+\b", query))
        signals += len(re.findall(r"\b[a-zA-Z]+\.\w+\b", query))
        signals += len(re.findall(r"\b[A-Z]*\d{3,}\b", query))

        if signals >= 2:
            return [0.6, 0.4]   # BM25 主导
        elif signals == 0:
            return [0.3, 0.7]   # FAISS 主导
        else:
            return [0.4, 0.6]   # 默认略偏 FAISS

    # ── grep 精确匹配加权 ──

    def _extract_grep_keywords(self, query: str) -> list[str]:
        """
        提取适合精确匹配的关键词：
        大写缩写、驼峰命名、下划线命名、点号路径、错误码。
        不提取普通英文词（BM25 处理更好）。
        """
        keywords = []
        keywords.extend(re.findall(r"\b[A-Z]{2,}\b", query))
        keywords.extend(re.findall(r"\b[a-z]+[A-Z][a-zA-Z]*\b", query))
        keywords.extend(re.findall(r"\b\w+_\w+\b", query))
        keywords.extend(re.findall(r"\b[a-zA-Z]+\.[a-zA-Z]+\b", query))
        keywords.extend(re.findall(r"\b[A-Z]*\d{3,}\b", query))
        return list(set(keywords))

    def _grep_boost_results(
        self,
        fused_results: list[tuple[int, float]],
        keywords: list[str],
    ) -> list[tuple[int, float]]:
        """
        对 RRF top-50 中精确包含关键词的 chunk 加权。
        在内存中的 chunk 文本上做字符串搜索，~3ms。
        不删除任何结果，只调整分数。
        """
        boosted = []
        for chunk_id, score in fused_results:
            text = self.chunks[chunk_id]
            if any(kw in text for kw in keywords):
                boosted.append((chunk_id, score * self.grep_boost))
            else:
                boosted.append((chunk_id, score))
        return sorted(boosted, key=lambda x: x[1], reverse=True)
```

## 延迟预算

```
操作                    耗时          何时执行
──────────────────────────────────────────────────────
FAISS 索引              已有          已构建（133MB）
BM25 建索引（chunk级）  ~100-200ms    SessionStart（一次性）
FAISS 模型加载          ~1s           首次查询（后续复用）
BM25 查询               ~5ms          每次查询
FAISS 查询              ~50ms         每次查询
RRF 融合                < 1ms         每次查询
grep 加权               ~3ms          每次查询（内存内）
──────────────────────────────────────────────────────
每次查询总计            ~60ms
```

## 关键设计决策

**为什么 BM25 在 chunk 级别而不是文件级别？**
你的 FAISS 索引是 chunk 级别的（500 字符/块，90,876 块）。
如果 BM25 在文件级别（967 文件），RRF 融合时两边返回的 ID 粒度不一致——
一个返回 chunk_id，一个返回 file_path，无法直接融合。
BM25 复用 FAISS 的分块数据，确保两者在同一粒度上操作。

**为什么不重建 FAISS 索引？**
你的索引已经覆盖 967 文件、90,876 块，用的是多语言模型，训练花了时间。
重建没有任何好处。BM25 是**叠加**在现有系统上的增量能力，不是替换。

**为什么用 bm25s 而不是 rank_bm25？**
bm25s 预计算分数存储在 scipy 稀疏矩阵中，比 rank_bm25 快 100-500 倍。
90,876 块的索引构建 ~100-200ms，rank_bm25 在这个规模会明显慢。

**为什么 FAISS 直接加载而不是走 CLI？**
CLI 调用有 ~100ms 进程启动开销。直接加载 FAISS 索引 + 模型到内存，
查询延迟 ~50ms。首次加载模型 ~1s，后续复用。

**为什么 grep 在内存中做而不是调系统 grep？**
所有 chunk 文本在 build_bm25_index 时已经加载到内存（从 metadata.pkl）。
在内存中做 `kw in text` 比 fork 一个 grep 进程快得多。
50 个 chunk 的内存字符串搜索 < 3ms。

**为什么保留 RRF 即使只有一路输入？**
单路输入时 RRF 退化为 passthrough，零成本。
合理冗余——未来加 Cross-Encoder 或其他检索器只需多传一路输入。

## metadata.pkl 结构

已确认（90,876 条）：

```python
meta[0] = {
    "file": "/Users/poincare/.claude/paste-cache/xxx.txt",  # 源文件路径
    "file_hash": "eb525f38...",                               # MD5（增量更新用）
    "chunk": "# SUPERPLANER 当前状态快照\n..."                 # 500字符文本块
}
```

BM25 索引 `chunk` 字段，与 FAISS 共享同一组 90,876 块。

## 与 SessionStart hook 集成

```python
def session_start_search(task_description: str, top_k: int = 5):
    """SessionStart hook 入口。"""
    searcher = CortexSearch()
    searcher.build_bm25_index()     # ~100-200ms
    results = searcher.search(task_description, top_k=top_k)

    # 去重：同一文件的多个 chunk 合并
    seen_files = set()
    unique_results = []
    for r in results:
        if r["file"] not in seen_files:
            seen_files.add(r["file"])
            unique_results.append(r)

    return unique_results
```

## 扩展路径

1. **Cross-Encoder reranker** — 对 RRF top-20 精排，+20-35% 准确率，+200ms
2. **BM25 索引持久化** — 避免每次 SessionStart 重建，省 100ms
3. **增量更新** — 新 instinct 生成后，BM25 重建 + FAISS 追加 embedding
