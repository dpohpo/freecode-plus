---
name: saveraw
description: 保存原始对话记忆工具，支持双索引检索 (BM25 + BERT)。触发场景：(1) 用户说 "/saveraw" (2) 用户说 "保存对话" (3) 用户说 "保存记忆" (4) 用户想把对话存到 memory 文件夹并推送到 GitHub (5) 用户想搜索历史对话记忆。功能：把当前对话完整保存为 .md 文件，推送到 GitHub memory 仓库，自动建立 BM25 关键词索引和 BERT 语义索引，支持混合检索。
user-invocable: "true"
---

# SaveRaw - 对话记忆保存器 (双索引增强版)

把当前对话**完整、原始、一字不改**地保存到 Markdown 文件，推送到 GitHub，并自动建立**双索引**支持检索。

## 核心功能

1. **保存对话** - 保存完整对话到 `~/Desktop/memory/`
2. **自动归档** - 按月份归类 (如 `2026-02/`)
3. **Git 同步** - 自动提交并推送到 GitHub `memory` 仓库
4. **BM25 索引** - 关键词检索 (基于 bm25s)
5. **BERT 索引** - 语义检索 (基于 sentence-transformers + FAISS)
6. **混合检索** - BM25 + BERT 融合检索

## 使用方法

### 基本保存

```
/saveraw
```

执行后会：
1. 创建 `~/Desktop/memory/2026-02/conversation_20260213_193000.md`
2. 自动更新 BM25 和 BERT 索引
3. Git add/commit/push 到 memory 仓库

### 带标题保存

```
/saveraw 关于 BM25 算法的研究
```

### 搜索记忆

```
# 混合检索 (默认，效果最好)
/saveraw --search "BM25 算法"

# 只用 BM25 关键词检索
/saveraw --search "BM25" --mode bm25

# 只用 BERT 语义检索
/saveraw --search "相似度计算方法" --mode bert

# 混合检索 (BM25 40% + BERT 60%)
/saveraw --search "如何优化检索" --mode hybrid
```

### 命令行调用

```bash
# 保存对话
echo "对话内容" | python ~/.claude/skills/saveraw/scripts/saveraw.py

# 直接传入内容
python ~/.claude/skills/saveraw/scripts/saveraw.py --content "对话内容"

# 搜索记忆
python ~/.claude/skills/saveraw/scripts/saveraw.py --search "查询词"
python ~/.claude/skills/saveraw/scripts/saveraw.py --search "查询词" --mode bm25
python ~/.claude/skills/saveraw/scripts/saveraw.py --search "查询词" --mode bert
python ~/.claude/skills/saveraw/scripts/saveraw.py --search "查询词" --mode hybrid -k 10

# 列出所有记忆
python ~/.claude/skills/saveraw/scripts/saveraw.py --list

# 查看索引状态
python ~/.claude/skills/saveraw/scripts/saveraw.py --status

# 重建索引
python ~/.claude/skills/saveraw/scripts/saveraw.py --rebuild-index

# 只保存不推送
python ~/.claude/skills/saveraw/scripts/saveraw.py --no-push

# 保存但不更新索引
python ~/.claude/skills/saveraw/scripts/saveraw.py --no-index

# 初始化 Git 仓库
python ~/.claude/skills/saveraw/scripts/saveraw.py --init
```

## 文件结构

```
~/Desktop/memory/
├── .index/                      # 索引目录
│   ├── bm25/                    # BM25 索引
│   │   ├── index...             # 索引数据
│   │   ├── doc_map.json         # 文档映射
│   │   └── ...
│   ├── bert_index.faiss         # FAISS 向量索引
│   └── bert_metadata.pkl        # BERT 元数据
├── 2026-02/
│   ├── conversation_20260213_193000.md
│   ├── conversation_20260213_200000.md
│   └── ...
├── 2026-03/
│   └── ...
└── .git/
```

## 索引技术

### BM25 索引 (关键词检索)

- **库**: bm25s (比 rank_bm25 快 500 倍)
- **方法**: Lucene 变体 (k1=1.5, b=0.75)
- **特点**: 精确关键词匹配，适合专有名词、代码片段

### BERT 索引 (语义检索)

- **模型**: paraphrase-multilingual-MiniLM-L12-v2
- **维度**: 384
- **存储**: FAISS IndexFlatIP (内积相似度)
- **特点**: 理解语义，跨语言 (中英混合)

### 混合检索

- **算法**: 归一化加权融合
- **默认权重**: BM25 40% + BERT 60%
- **优势**: 兼顾精确匹配和语义理解

## 依赖安装

```bash
# BM25 依赖
pip install bm25s PyStemmer

# BERT 依赖
pip install sentence-transformers faiss-cpu
```

## 首次使用

1. 创建 GitHub 仓库 `memory`

2. 初始化本地仓库:
```bash
python ~/.claude/skills/saveraw/scripts/saveraw.py --init
```

3. 添加远程仓库:
```bash
cd ~/Desktop/memory
git remote add origin git@github.com:YOUR_USERNAME/memory.git
git push -u origin main
```

## Markdown 格式

```markdown
---
title: 对话记录 2026-02-13 19:30
created: 2026-02-13T19:30:00
type: conversation-memory
---

[原始对话内容，一字不改]
```

## 搜索结果示例

```
$ python saveraw.py --search "BM25 优化" --mode hybrid

找到 5 个相关结果 (hybrid 模式):

[1] 文件: /Users/.../conversation_20260213_193000.md
    综合分数: 0.8523 (BM25: 0.9123, BERT: 0.8211)
    内容: BM25 参数优化 k1 控制词频饱和度...

[2] 文件: /Users/.../conversation_20260212_150000.md
    综合分数: 0.7234 (BM25: 0.6521, BERT: 0.7689)
    内容: 检索系统优化方案包括...
```

## 脚本位置

```
~/.claude/skills/saveraw/scripts/saveraw.py
```
