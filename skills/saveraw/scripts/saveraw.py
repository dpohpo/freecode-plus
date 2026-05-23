#!/usr/bin/env python3
"""
saveraw - 保存原始对话到 Markdown 文件并推送到 GitHub
         同时建立 BM25 + BERT 双索引，支持混合检索

功能:
1. 从 stdin 读取完整对话内容
2. 生成带时间戳的 .md 文件
3. 保存到 ~/Desktop/memory/
4. 推送到 GitHub memory 仓库
5. 自动更新 BM25 索引 (关键词检索)
6. 自动更新 BERT 索引 (语义检索)
7. 支持混合检索 (BM25 + BERT)

使用:
    echo "对话内容" | python saveraw.py
    cat conversation.txt | python saveraw.py
    python saveraw.py --search "查询词"
    python saveraw.py --hybrid "查询词"
"""

import os
import sys
import json
import pickle
import subprocess
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# 配置
MEMORY_DIR = Path.home() / "Desktop" / "memory"
INDEX_DIR = MEMORY_DIR / ".index"
GITHUB_REPO = "memory"

# 索引文件路径
BM25_INDEX_PATH = INDEX_DIR / "bm25"
BERT_INDEX_PATH = INDEX_DIR / "bert_index.faiss"
BERT_META_PATH = INDEX_DIR / "bert_metadata.pkl"
DOCS_META_PATH = INDEX_DIR / "docs_metadata.json"

# BERT 配置
BERT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
BERT_DIM = 384  # paraphrase-multilingual-MiniLM-L12-v2 输出维度
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


# ============== 索引基类 ==============

class IndexManager:
    """索引管理器基类"""

    def __init__(self):
        self.index_dir = INDEX_DIR
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_hash(self, filepath: str) -> str:
        """获取文件 MD5 哈希"""
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()


# ============== BM25 索引 ==============

class BM25Indexer(IndexManager):
    """BM25 索引管理器"""

    def __init__(self):
        super().__init__()
        self.retriever = None
        self.corpus = []
        self.doc_map = []  # 映射: corpus index -> (file_path, chunk_index)
        self.stemmer = None
        self.tokenizer = None

    def _init_bm25(self):
        """延迟初始化 BM25 组件"""
        if self.stemmer is None:
            try:
                import bm25s
                import Stemmer
                self.stemmer = Stemmer.Stemmer("english")
                self.bm25s = bm25s
            except ImportError:
                raise ImportError("请安装 bm25s: pip install bm25s PyStemmer")

    def load(self) -> bool:
        """加载已有索引"""
        self._init_bm25()

        if not BM25_INDEX_PATH.exists():
            return False

        try:
            self.retriever = self.bm25s.BM25.load(
                str(BM25_INDEX_PATH),
                load_corpus=True
            )
            self.corpus = self.retriever.corpus or []

            # 加载 tokenizer
            self.tokenizer = self.bm25s.tokenization.Tokenizer(stemmer=self.stemmer)
            self.tokenizer.load_vocab(str(BM25_INDEX_PATH))
            self.tokenizer.load_stopwords(str(BM25_INDEX_PATH))

            # 加载文档映射
            doc_map_path = BM25_INDEX_PATH / "doc_map.json"
            if doc_map_path.exists():
                with open(doc_map_path, 'r', encoding='utf-8') as f:
                    self.doc_map = json.load(f)

            return True
        except Exception as e:
            print(f"加载 BM25 索引失败: {e}")
            return False

    def build(self, documents: List[str], doc_map: List[Dict]) -> dict:
        """构建/更新 BM25 索引"""
        self._init_bm25()

        # 合并已有索引
        if self.load():
            # 获取已索引的文件
            indexed_files = {m.get('file') for m in self.doc_map}

            # 只添加新文档
            new_docs = []
            new_map = []
            for doc, meta in zip(documents, doc_map):
                if meta.get('file') not in indexed_files:
                    new_docs.append(doc)
                    new_map.append(meta)

            if not new_docs:
                return {"success": True, "message": "无新内容需要索引"}

            documents = self.corpus + new_docs
            doc_map = self.doc_map + new_map

        self.corpus = documents
        self.doc_map = doc_map

        # 创建 tokenizer
        self.tokenizer = self.bm25s.tokenization.Tokenizer(
            stemmer=self.stemmer,
            stopwords="en",
            lower=True,
        )

        corpus_tokens = self.tokenizer.tokenize(documents, return_as="tuple")

        self.retriever = self.bm25s.BM25(
            method="lucene",
            k1=1.5,
            b=0.75,
            corpus=documents
        )
        self.retriever.index(corpus_tokens)

        # 保存索引
        self.save()

        return {
            "success": True,
            "num_documents": len(documents),
            "index_path": str(BM25_INDEX_PATH)
        }

    def save(self):
        """保存索引"""
        if self.retriever is None:
            return

        BM25_INDEX_PATH.mkdir(parents=True, exist_ok=True)
        self.retriever.save(str(BM25_INDEX_PATH), corpus=self.corpus)
        self.tokenizer.save_vocab(str(BM25_INDEX_PATH))
        self.tokenizer.save_stopwords(str(BM25_INDEX_PATH))

        # 保存文档映射
        doc_map_path = BM25_INDEX_PATH / "doc_map.json"
        with open(doc_map_path, 'w', encoding='utf-8') as f:
            json.dump(self.doc_map, f, ensure_ascii=False, indent=2)

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """BM25 搜索"""
        if self.retriever is None:
            if not self.load():
                return []

        query_tokens = self.tokenizer.tokenize([query], update_vocab=False)
        results, scores = self.retriever.retrieve(query_tokens, k=k)

        output = []
        for i in range(results.shape[1]):
            doc_idx = int(results[0, i])
            score = float(scores[0, i])

            meta = self.doc_map[doc_idx] if doc_idx < len(self.doc_map) else {}
            output.append({
                "rank": i + 1,
                "score": round(score, 4),
                "file": meta.get("file", ""),
                "chunk": self.corpus[doc_idx] if doc_idx < len(self.corpus) else "",
                "source": "bm25"
            })

        return output


# ============== BERT 索引 ==============

class BERTIndexer(IndexManager):
    """BERT 语义索引管理器"""

    def __init__(self):
        super().__init__()
        self.index = None
        self.metadata = []
        self.model = None

    def _init_model(self):
        """延迟加载模型"""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                import faiss
                import numpy as np

                self.faiss = faiss
                self.np = np

                print(f"加载 BERT 模型: {BERT_MODEL}")
                self.model = SentenceTransformer(BERT_MODEL)
            except ImportError:
                raise ImportError("请安装依赖: pip install sentence-transformers faiss-cpu")

    def load(self) -> bool:
        """加载已有索引"""
        if not BERT_INDEX_PATH.exists() or not BERT_META_PATH.exists():
            return False

        try:
            self._init_model()
            self.index = self.faiss.read_index(str(BERT_INDEX_PATH))

            with open(BERT_META_PATH, 'rb') as f:
                self.metadata = pickle.load(f)

            return True
        except Exception as e:
            print(f"加载 BERT 索引失败: {e}")
            return False

    def _chunk_text(self, text: str) -> List[str]:
        """文本分块"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start += CHUNK_SIZE - CHUNK_OVERLAP
        return chunks

    def build(self, file_path: str) -> dict:
        """为文件构建 BERT 索引"""
        self._init_model()

        # 加载已有索引
        if self.index is None:
            if self.load():
                # 检查文件是否已索引
                file_hash = self._get_file_hash(file_path)
                indexed_hashes = {m.get('file_hash') for m in self.metadata}

                if file_hash in indexed_hashes:
                    return {"success": True, "message": "文件已索引"}
            else:
                # 创建新索引
                self.index = self.faiss.IndexFlatIP(BERT_DIM)
                self.metadata = []

        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 分块
        chunks = self._chunk_text(content)
        if not chunks:
            return {"success": True, "message": "无内容需要索引"}

        file_hash = self._get_file_hash(file_path)

        # 生成嵌入
        embeddings = self.model.encode(chunks, show_progress_bar=False)
        self.faiss.normalize_L2(embeddings)

        # 添加到索引
        self.index.add(embeddings)

        # 添加元数据
        for i, chunk in enumerate(chunks):
            self.metadata.append({
                'file': file_path,
                'file_hash': file_hash,
                'chunk_index': i,
                'chunk': chunk
            })

        # 保存索引
        self.save()

        return {
            "success": True,
            "chunks_added": len(chunks),
            "total_chunks": len(self.metadata)
        }

    def save(self):
        """保存索引"""
        if self.index is None:
            return

        self.faiss.write_index(self.index, str(BERT_INDEX_PATH))

        with open(BERT_META_PATH, 'wb') as f:
            pickle.dump(self.metadata, f)

    def search(self, query: str, k: int = 5, threshold: float = 0.3) -> List[Dict]:
        """BERT 语义搜索"""
        if self.index is None:
            if not self.load():
                return []

        query_embedding = self.model.encode([query])
        self.faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(query_embedding, k)

        output = []
        for score, idx in zip(scores[0], indices[0]):
            if score >= threshold and idx < len(self.metadata):
                meta = self.metadata[idx]
                output.append({
                    "rank": len(output) + 1,
                    "score": round(float(score), 4),
                    "file": meta['file'],
                    "chunk": meta['chunk'],
                    "source": "bert"
                })

        return output


# ============== 混合检索 ==============

class HybridSearcher:
    """混合检索器: BM25 + BERT"""

    def __init__(self):
        self.bm25 = BM25Indexer()
        self.bert = BERTIndexer()

    def search(self, query: str, k: int = 5, bm25_weight: float = 0.4, bert_weight: float = 0.6) -> List[Dict]:
        """
        混合搜索

        Args:
            query: 查询文本
            k: 返回结果数
            bm25_weight: BM25 权重
            bert_weight: BERT 权重
        """
        # 并行搜索
        bm25_results = self.bm25.search(query, k=k*2)  # 多取一些用于融合
        bert_results = self.bert.search(query, k=k*2, threshold=0.2)

        # 结果融合 (Reciprocal Rank Fusion)
        combined_scores = {}

        for r in bm25_results:
            key = (r['file'], r['chunk'][:100])  # 用文件+chunk前100字符作为key
            if key not in combined_scores:
                combined_scores[key] = {'bm25_score': 0, 'bert_score': 0, 'data': r}
            combined_scores[key]['bm25_score'] = r['score']

        for r in bert_results:
            key = (r['file'], r['chunk'][:100])
            if key not in combined_scores:
                combined_scores[key] = {'bm25_score': 0, 'bert_score': 0, 'data': r}
            combined_scores[key]['bert_score'] = r['score']

        # 归一化并融合
        max_bm25 = max((v['bm25_score'] for v in combined_scores.values()), default=1)
        max_bert = max((v['bert_score'] for v in combined_scores.values()), default=1)

        results = []
        for key, scores in combined_scores.items():
            norm_bm25 = scores['bm25_score'] / max_bm25 if max_bm25 > 0 else 0
            norm_bert = scores['bert_score'] / max_bert if max_bert > 0 else 0

            final_score = bm25_weight * norm_bm25 + bert_weight * norm_bert

            results.append({
                'file': scores['data']['file'],
                'chunk': scores['data']['chunk'],
                'bm25_score': round(scores['bm25_score'], 4),
                'bert_score': round(scores['bert_score'], 4),
                'final_score': round(final_score, 4),
                'source': 'hybrid'
            })

        # 按最终分数排序
        results.sort(key=lambda x: x['final_score'], reverse=True)

        # 添加排名
        for i, r in enumerate(results[:k]):
            r['rank'] = i + 1

        return results[:k]


# ============== 对话保存 ==============

def get_github_user():
    """获取 GitHub 用户名"""
    try:
        result = subprocess.run(
            ["git", "config", "--global", "user.name"],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except:
        return None


def ensure_git_repo():
    """确保 memory 目录是一个 git 仓库"""
    if not (MEMORY_DIR / ".git").exists():
        print(f"初始化 Git 仓库: {MEMORY_DIR}")
        os.chdir(MEMORY_DIR)
        subprocess.run(["git", "init"], check=True)

        gitignore = MEMORY_DIR / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("*.tmp\n.DS_Store\n")

        subprocess.run(["git", "add", ".gitignore"], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)

        print("\n请添加 GitHub 远程仓库:")
        print(f"  cd {MEMORY_DIR}")
        print(f"  git remote add origin git@github.com:YOUR_USERNAME/memory.git")
        print(f"  git push -u origin main")


def generate_filename():
    """生成唯一文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    date_prefix = datetime.now().strftime("%Y-%m")

    month_dir = MEMORY_DIR / date_prefix
    month_dir.mkdir(parents=True, exist_ok=True)

    return month_dir / f"conversation_{timestamp}.md"


def create_markdown(content: str, title: str = None) -> str:
    """创建 Markdown 文档"""
    now = datetime.now()

    if title is None:
        title = f"对话记录 {now.strftime('%Y-%m-%d %H:%M')}"

    frontmatter = f"""---
title: {title}
created: {now.isoformat()}
type: conversation-memory
---

"""

    return frontmatter + content


def save_to_file(content: str, filepath: Path) -> dict:
    """保存内容到文件"""
    filepath.write_text(content, encoding="utf-8")
    return {
        "success": True,
        "file": str(filepath),
        "size": len(content)
    }


def git_commit_push(filepath: Path, message: str = None) -> dict:
    """Git 提交并推送"""
    os.chdir(MEMORY_DIR)

    if message is None:
        rel_path = filepath.relative_to(MEMORY_DIR)
        message = f"Add conversation: {rel_path}"

    try:
        subprocess.run(["git", "add", str(filepath)], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)

        result = subprocess.run(
            ["git", "push"],
            capture_output=True, text=True
        )

        if result.returncode == 0:
            return {"success": True, "message": "已推送到 GitHub"}
        else:
            return {"success": True, "warning": "已提交但未推送，请检查远程仓库配置"}

    except subprocess.CalledProcessError as e:
        return {"success": False, "error": str(e)}


def update_indexes(filepath: str) -> dict:
    """更新所有索引"""
    results = {}

    # BM25 索引
    try:
        bm25_indexer = BM25Indexer()

        # 读取所有 .md 文件
        md_files = list(MEMORY_DIR.rglob("*.md"))
        documents = []
        doc_map = []

        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 简单分块
                lines = content.split('\n')
                chunk = []
                for line in lines:
                    chunk.append(line)
                    if len('\n'.join(chunk)) >= CHUNK_SIZE:
                        doc_text = '\n'.join(chunk).strip()
                        if doc_text:
                            documents.append(doc_text)
                            doc_map.append({'file': str(md_file)})
                        chunk = []

                # 处理剩余内容
                if chunk:
                    doc_text = '\n'.join(chunk).strip()
                    if doc_text:
                        documents.append(doc_text)
                        doc_map.append({'file': str(md_file)})

            except Exception as e:
                print(f"跳过文件 {md_file}: {e}")

        if documents:
            results['bm25'] = bm25_indexer.build(documents, doc_map)

    except Exception as e:
        results['bm25'] = {"success": False, "error": str(e)}

    # BERT 索引
    try:
        bert_indexer = BERTIndexer()
        results['bert'] = bert_indexer.build(filepath)
    except Exception as e:
        results['bert'] = {"success": False, "error": str(e)}

    return results


def search_memory(query: str, mode: str = "hybrid", k: int = 5) -> List[Dict]:
    """搜索记忆"""
    if mode == "bm25":
        indexer = BM25Indexer()
        return indexer.search(query, k)
    elif mode == "bert":
        indexer = BERTIndexer()
        return indexer.search(query, k)
    else:  # hybrid
        searcher = HybridSearcher()
        return searcher.search(query, k)


def main():
    parser = argparse.ArgumentParser(description="保存对话到 Markdown 并推送到 GitHub，支持双索引检索")

    # 保存相关
    parser.add_argument("--title", "-t", help="对话标题")
    parser.add_argument("--no-push", action="store_true", help="只保存不推送")
    parser.add_argument("--no-index", action="store_true", help="不更新索引")
    parser.add_argument("--content", "-c", help="直接传入内容")

    # 搜索相关
    parser.add_argument("--search", "-s", help="搜索查询")
    parser.add_argument("--mode", "-m", choices=["bm25", "bert", "hybrid"],
                        default="hybrid", help="搜索模式")
    parser.add_argument("--top-k", "-k", type=int, default=5, help="返回结果数")

    # 其他命令
    parser.add_argument("--list", "-l", action="store_true", help="列出所有记忆文件")
    parser.add_argument("--init", action="store_true", help="初始化 Git 仓库")
    parser.add_argument("--rebuild-index", action="store_true", help="重建所有索引")
    parser.add_argument("--status", action="store_true", help="查看索引状态")

    args = parser.parse_args()

    # 确保目录存在
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    # 初始化模式
    if args.init:
        ensure_git_repo()
        return

    # 状态查看
    if args.status:
        print("\n=== 索引状态 ===\n")

        # BM25 状态
        bm25_indexer = BM25Indexer()
        if bm25_indexer.load():
            print(f"BM25 索引: {len(bm25_indexer.corpus)} 个文档块")
        else:
            print("BM25 索引: 未建立")

        # BERT 状态
        bert_indexer = BERTIndexer()
        if bert_indexer.load():
            print(f"BERT 索引: {len(bert_indexer.metadata)} 个向量")
        else:
            print("BERT 索引: 未建立")

        print()
        return

    # 列表模式
    if args.list:
        files = list(MEMORY_DIR.rglob("*.md"))
        print(f"\n记忆文件 ({len(files)} 个):\n")
        for f in sorted(files, reverse=True)[:20]:
            rel = f.relative_to(MEMORY_DIR)
            size = f.stat().st_size
            mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            print(f"  {rel} ({size} bytes, {mtime})")
        return

    # 重建索引
    if args.rebuild_index:
        print("重建所有索引...")

        # 删除旧索引
        import shutil
        if BM25_INDEX_PATH.exists():
            shutil.rmtree(BM25_INDEX_PATH)
        if BERT_INDEX_PATH.exists():
            BERT_INDEX_PATH.unlink()
        if BERT_META_PATH.exists():
            BERT_META_PATH.unlink()

        # 重新索引所有文件
        md_files = list(MEMORY_DIR.rglob("*.md"))
        for md_file in md_files:
            print(f"索引: {md_file.name}")
            update_indexes(str(md_file))

        print("索引重建完成!")
        return

    # 搜索模式
    if args.search:
        results = search_memory(args.search, mode=args.mode, k=args.top_k)

        if results:
            print(f"\n找到 {len(results)} 个相关结果 ({args.mode} 模式):\n")
            for r in results:
                print(f"[{r['rank']}] 文件: {r['file']}")

                if args.mode == "hybrid":
                    print(f"    综合分数: {r['final_score']:.4f} (BM25: {r['bm25_score']:.4f}, BERT: {r['bert_score']:.4f})")
                else:
                    print(f"    分数: {r['score']:.4f}")

                chunk_preview = r['chunk'][:200].replace('\n', ' ')
                print(f"    内容: {chunk_preview}...")
                print()
        else:
            print("未找到相关结果")
        return

    # 保存模式
    if args.content:
        content = args.content
    elif not sys.stdin.isatty():
        content = sys.stdin.read()
    else:
        print("请通过 stdin 传入内容，或使用 --content 参数")
        print("或使用 --search 进行搜索")
        sys.exit(1)

    if not content.strip():
        print("错误: 内容为空")
        sys.exit(1)

    # 生成文件
    filepath = generate_filename()
    markdown = create_markdown(content, args.title)

    # 保存
    result = save_to_file(markdown, filepath)
    print(f"✅ 已保存: {filepath}")

    # 更新索引
    if not args.no_index:
        print("更新索引...")
        index_results = update_indexes(str(filepath))
        for idx_type, idx_result in index_results.items():
            if idx_result.get('success'):
                print(f"  ✅ {idx_type.upper()} 索引更新成功")
            else:
                print(f"  ⚠️ {idx_type.upper()} 索引更新失败: {idx_result.get('error')}")

    # Git 操作
    if not args.no_push:
        git_result = git_commit_push(filepath)
        if git_result.get("success"):
            print(f"✅ {git_result.get('message', git_result.get('warning', '完成'))}")
        else:
            print(f"⚠️ Git 操作失败: {git_result.get('error')}")

    print(f"\n📁 文件位置: {filepath}")


if __name__ == "__main__":
    main()
