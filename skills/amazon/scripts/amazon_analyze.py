#!/usr/bin/env python3
"""
Amazon Product Analyzer - 使用 MECE + Hardest 方法分析商品和差评
生成深度分析报告，支持 Markdown 和 DOCX 输出
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime
from typing import Optional


def load_data(output_dir: str) -> tuple[list, dict]:
    """加载爬取的数据"""
    products_path = os.path.join(output_dir, "products.json")
    reviews_path = os.path.join(output_dir, "negative_reviews.json")

    products = []
    reviews = {}

    if os.path.exists(products_path):
        with open(products_path, "r", encoding="utf-8") as f:
            products = json.load(f)

    if os.path.exists(reviews_path):
        with open(reviews_path, "r", encoding="utf-8") as f:
            reviews = json.load(f)

    return products, reviews


def extract_keywords(texts: list[str], min_length: int = 3) -> Counter:
    """提取关键词"""
    # 停用词
    stopwords = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "was", "are", "were", "been", "be",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "this", "that", "these", "those",
        "it", "its", "i", "my", "me", "you", "your", "we", "they", "them",
        "not", "no", "very", "just", "so", "if", "when", "than", "as", "about",
        "out", "up", "all", "also", "only", "even", "more", "some", "any",
        "what", "which", "who", "how", "why", "where", "there", "here"
    }

    words = []
    for text in texts:
        # 提取单词
        tokens = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        words.extend([t for t in tokens if t not in stopwords])

    return Counter(words)


def mece_analyze_reviews(reviews: dict, products: list) -> dict:
    """
    MECE 差评分析 - 将差评问题拆解为互斥穷尽的类别
    """
    all_reviews = []
    for asin, review_list in reviews.items():
        for r in review_list:
            r["product_asin"] = asin
            all_reviews.append(r)

    if not all_reviews:
        return {"categories": {}, "insights": []}

    # MECE 分类维度
    categories = {
        "产品质量问题": {
            "keywords": ["quality", "broke", "broken", "defective", "defect", "poor", "cheap",
                        "cheaply", "made", "material", "build", "construction", "flimsy",
                        "durability", "stopped working", "failed", "failure", "fall apart"],
            "reviews": [],
            "severity": "高"
        },
        "功能/性能问题": {
            "keywords": ["work", "working", "function", "performance", "slow", "lag",
                        "connection", "connect", "disconnect", "signal", "range", "distance",
                        "resolution", "quality", "audio", "video", "sound", "image", "picture"],
            "reviews": [],
            "severity": "高"
        },
        "安装/使用问题": {
            "keywords": ["install", "setup", "set up", "use", "using", "instruction", "manual",
                        "complicated", "confusing", "difficult", "hard", "complex", "figure out"],
            "reviews": [],
            "severity": "中"
        },
        "兼容性问题": {
            "keywords": ["compatible", "compatibility", "support", "device", "work with",
                        "mac", "windows", "iphone", "android", "tv", "laptop", "phone"],
            "reviews": [],
            "severity": "中"
        },
        "物流/包装问题": {
            "keywords": ["shipping", "delivery", "arrived", "package", "packaging", "damaged",
                        "box", "late", "delayed", "missing", "parts"],
            "reviews": [],
            "severity": "低"
        },
        "价格/价值问题": {
            "keywords": ["price", "value", "worth", "money", "expensive", "overpriced",
                        "cost", "waste", "return", "refund"],
            "reviews": [],
            "severity": "中"
        },
        "客服/售后问题": {
            "keywords": ["customer service", "support", "warranty", "contact", "response",
                        "help", "replace", "replacement"],
            "reviews": [],
            "severity": "中"
        }
    }

    # 分类每条差评
    for review in all_reviews:
        text = f"{review.get('title', '')} {review.get('body', '')}".lower()
        review["matched_categories"] = []

        for cat_name, cat_info in categories.items():
            for keyword in cat_info["keywords"]:
                if keyword in text:
                    cat_info["reviews"].append(review)
                    review["matched_categories"].append(cat_name)
                    break

    # 提取高频问题词
    all_texts = [f"{r.get('title', '')} {r.get('body', '')}" for r in all_reviews]
    keyword_freq = extract_keywords(all_texts)

    # 获取问题关键词（负面相关）
    problem_keywords = {}
    negative_indicators = ["not", "doesn't", "don't", "didn't", "won't", "can't",
                          "never", "bad", "terrible", "horrible", "awful", "worst",
                          "disappointed", "waste", "return", "broken", "failed"]

    for review in all_reviews:
        text = f"{r.get('title', '')} {r.get('body', '')}".lower()
        for r in all_reviews:
            text = f"{r.get('title', '')} {r.get('body', '')}".lower()
            break
        text = f"{review.get('title', '')} {review.get('body', '')}".lower()

        # 找到否定词后面的名词
        for neg in negative_indicators:
            if neg in text:
                words = text.split()
                for i, word in enumerate(words):
                    if word == neg.replace("'", "") or word == neg:
                        # 获取后续3个词
                        context = " ".join(words[i:i+4])
                        for kw, count in keyword_freq.most_common(50):
                            if kw in context and kw not in problem_keywords:
                                problem_keywords[kw] = problem_keywords.get(kw, 0) + 1

    # 统计分析
    analysis = {
        "total_reviews": len(all_reviews),
        "categories": {},
        "top_problems": [],
        "products_affected": {}
    }

    for cat_name, cat_info in categories.items():
        if cat_info["reviews"]:
            analysis["categories"][cat_name] = {
                "count": len(cat_info["reviews"]),
                "severity": cat_info["severity"],
                "percentage": round(len(cat_info["reviews"]) / len(all_reviews) * 100, 1),
                "sample_reviews": cat_info["reviews"][:3]
            }

    # Top 问题关键词
    analysis["top_problems"] = keyword_freq.most_common(30)

    # 受影响产品统计
    for review in all_reviews:
        asin = review.get("product_asin")
        if asin not in analysis["products_affected"]:
            analysis["products_affected"][asin] = {"count": 0, "issues": []}
        analysis["products_affected"][asin]["count"] += 1
        analysis["products_affected"][asin]["issues"].extend(review.get("matched_categories", []))

    return analysis


def hardest_deep_analysis(products: list, reviews_analysis: dict) -> dict:
    """
    Hardest 深度分析 - Think deep, deeper, deepest
    对关键问题进行六维度认知极限推演
    """

    deep_analysis = {
        "market_overview": {},
        "common_pain_points": [],
        "opportunity_gaps": [],
        "recommendations": []
    }

    # 市场概览分析
    if products:
        ratings = [float(p.get("rating", 0)) for p in products if p.get("rating")]
        prices = []
        for p in products:
            price_str = p.get("price", "")
            if price_str:
                match = re.search(r'[\d,]+\.?\d*', price_str.replace(",", ""))
                if match:
                    prices.append(float(match.group()))

        deep_analysis["market_overview"] = {
            "total_products": len(products),
            "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0,
            "rating_range": f"{min(ratings):.1f} - {max(ratings):.1f}" if ratings else "N/A",
            "avg_price": round(sum(prices) / len(prices), 2) if prices else 0,
            "price_range": f"${min(prices):.0f} - ${max(prices):.0f}" if prices else "N/A"
        }

    # 深度分析每个问题类别
    for cat_name, cat_data in reviews_analysis.get("categories", {}).items():
        pain_point = {
            "category": cat_name,
            "severity": cat_data["severity"],
            "frequency": f"{cat_data['count']} reviews ({cat_data['percentage']}%)",
            "deep_analysis": {}
        }

        # Six Dimensions Analysis
        samples = cat_data.get("sample_reviews", [])
        sample_texts = [f"{r.get('title', '')}: {r.get('body', '')[:200]}" for r in samples]

        pain_point["deep_analysis"] = {
            "逻辑推理极限": {
                "root_cause": f"从{cat_data['count']}条差评推断，{cat_name}是主要痛点",
                "evidence": sample_texts[0] if sample_texts else ""
            },
            "直觉洞察极限": {
                "first_intuition": f"用户期望与实际体验存在差距",
                "hidden_assumption": "产品可能在该方面存在设计或执行缺陷"
            },
            "类比迁移极限": {
                "similar_cases": "同类产品可能存在相同问题",
                "lesson": "这是品类共性问题还是单品问题？"
            },
            "元认知审查极限": {
                "bias_check": "样本是否足够代表性？差评是否有情绪放大？",
                "blind_spot": "好评中是否也隐含了这些问题但表达较委婉？"
            },
            "系统思维极限": {
                "upstream": "供应链/设计/品控哪个环节出问题？",
                "downstream": "问题是否会导致退货率上升？"
            },
            "第一性原理极限": {
                "fundamental": f"用户购买{cat_name.split('/')[0]}产品的核心需求是什么？",
                "rebuild": "如何从根本上解决这个问题？"
            }
        }

        deep_analysis["common_pain_points"].append(pain_point)

    # 机会缺口分析
    top_categories = sorted(
        reviews_analysis.get("categories", {}).items(),
        key=lambda x: x[1]["count"],
        reverse=True
    )[:3]

    for cat_name, cat_data in top_categories:
        opportunity = {
            "pain_point": cat_name,
            "market_gap": f"{cat_data['percentage']}%的差评集中在此问题",
            "opportunity": f"如果能解决{cat_name}，可获得差异化竞争优势",
            "action": f"重点关注{cat_name}相关的设计改进或营销规避策略"
        }
        deep_analysis["opportunity_gaps"].append(opportunity)

    # 综合建议
    deep_analysis["recommendations"] = [
        {
            "priority": "高",
            "area": "产品开发",
            "action": "针对高频差评问题进行产品改进",
            "detail": "重点关注产品质量和功能性能问题"
        },
        {
            "priority": "中",
            "area": "Listing优化",
            "action": "在Bullet Points中主动回应常见顾虑",
            "detail": "将解决方案写入产品描述中"
        },
        {
            "priority": "中",
            "area": "竞品分析",
            "action": "分析竞争对手是否有相同问题",
            "detail": "找到差异化切入点"
        },
        {
            "priority": "低",
            "area": "客服策略",
            "action": "建立常见问题快速响应模板",
            "detail": "提升售后体验降低差评率"
        }
    ]

    return deep_analysis


def generate_report(products: list, reviews: dict, analysis: dict,
                   deep_analysis: dict, keyword: str, output_dir: str) -> str:
    """生成 Markdown 分析报告"""

    report = f"""# Amazon 商品深度分析报告

## 报告概要

| 项目 | 内容 |
|------|------|
| 分析关键词 | {keyword} |
| 分析时间 | {datetime.now().strftime("%Y-%m-%d %H:%M")} |
| 商品数量 | {len(products)} |
| 差评数量 | {analysis.get("total_reviews", 0)} |

---

## 📊 市场概览

| 指标 | 数值 |
|------|------|
| 样本商品数 | {deep_analysis["market_overview"].get("total_products", "N/A")} |
| 平均评分 | {deep_analysis["market_overview"].get("avg_rating", "N/A")} |
| 评分范围 | {deep_analysis["market_overview"].get("rating_range", "N/A")} |
| 平均价格 | ${deep_analysis["market_overview"].get("avg_price", "N/A")} |
| 价格范围 | {deep_analysis["market_overview"].get("price_range", "N/A")} |

---

## 🧩 MECE 差评分类分析

> 使用 MECE 方法将差评拆解为互斥穷尽的类别

"""

    # 差评分类
    for cat_name, cat_data in sorted(
        analysis.get("categories", {}).items(),
        key=lambda x: x[1]["count"],
        reverse=True
    ):
        severity_emoji = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(cat_data["severity"], "⚪")
        report += f"""
### {severity_emoji} {cat_name}

| 指标 | 数值 |
|------|------|
| 差评数量 | {cat_data["count"]} 条 |
| 占比 | {cat_data["percentage"]}% |
| 严重程度 | {cat_data["severity"]} |

**典型差评:**
"""
        for i, review in enumerate(cat_data.get("sample_reviews", [])[:2], 1):
            title = review.get("title", "")[:50]
            body = review.get("body", "")[:200]
            rating = review.get("rating", "?")
            report += f"""
{i}. **{rating}星** - {title}
   > {body}...

"""

    # 深度分析部分
    report += """---

## 🧠 Hardest 深度分析

> Think deep, deeper, and deepest. 对关键问题进行六维度认知极限推演

"""

    for pain_point in deep_analysis.get("common_pain_points", [])[:5]:
        report += f"""
### {pain_point["category"]}

**频率:** {pain_point["frequency"]} | **严重度:** {pain_point["severity"]}

"""
        da = pain_point.get("deep_analysis", {})
        for dim, analysis_data in da.items():
            report += f"""
#### {dim}

"""
            for key, value in analysis_data.items():
                report += f"- **{key}:** {value}\n"
            report += "\n"

    # 机会缺口
    report += """---

## 🔥 市场机会缺口

"""

    for i, opp in enumerate(deep_analysis.get("opportunity_gaps", []), 1):
        report += f"""
### 机会 {i}: {opp["pain_point"]}

- **痛点规模:** {opp["market_gap"]}
- **机会:** {opp["opportunity"]}
- **行动建议:** {opp["action"]}

"""

    # 商品列表
    report += """---

## 📋 商品数据汇总

| # | ASIN | 标题 | 价格 | 评分 | 差评数 |
|---|------|------|------|------|--------|
"""
    for i, p in enumerate(products[:30], 1):
        title = p.get("title", "")[:40] + "..." if len(p.get("title", "")) > 40 else p.get("title", "")
        asin = p.get("asin", "")
        price = p.get("price", "")
        rating = p.get("rating", "")
        neg_count = p.get("negative_review_count", 0)
        report += f"| {i} | {asin} | {title} | {price} | {rating} | {neg_count} |\n"

    # 建议
    report += """---

## 💡 综合建议

"""
    for rec in deep_analysis.get("recommendations", []):
        priority_emoji = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(rec["priority"], "⚪")
        report += f"""
### {priority_emoji} [{rec["priority"]}] {rec["area"]}

**行动:** {rec["action"]}
**详情:** {rec["detail"]}

"""

    report += """---

## ⚠️ 分析限制

1. **样本偏差:** 差评分析基于公开数据，可能存在选择偏差
2. **时效性:** 亚马逊数据实时变化，分析结果反映采集时刻状态
3. **因果关系:** 相关性不等于因果性，需要进一步验证
4. **置信度:** 基于有限样本，建议结合其他数据源交叉验证

---

*报告由 Amazon Deep Analyzer 生成，使用 MECE + Hardest 分析方法*
"""

    return report


def generate_docx(report_md: str, output_path: str) -> bool:
    """将 Markdown 转换为 DOCX"""
    try:
        from docx import Document
        from docx.shared import Inches, Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        doc = Document()

        # 解析 Markdown 并转换为 DOCX
        lines = report_md.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]

            # 标题
            if line.startswith("# "):
                p = doc.add_heading(line[2:], level=1)
            elif line.startswith("## "):
                p = doc.add_heading(line[3:], level=2)
            elif line.startswith("### "):
                p = doc.add_heading(line[4:], level=3)
            elif line.startswith("#### "):
                p = doc.add_heading(line[5:], level=4)
            # 分隔线
            elif line.startswith("---"):
                doc.add_paragraph("─" * 50)
            # 表格
            elif line.startswith("|") and "|" in line:
                # 收集表格行
                table_lines = []
                while i < len(lines) and lines[i].startswith("|"):
                    table_lines.append(lines[i])
                    i += 1
                i -= 1

                # 解析表格
                if len(table_lines) >= 2:
                    headers = [cell.strip() for cell in table_lines[0].split("|")[1:-1]]
                    rows = []
                    for tl in table_lines[2:]:  # 跳过分隔行
                        row = [cell.strip() for cell in tl.split("|")[1:-1]]
                        if row:
                            rows.append(row)

                    if headers and rows:
                        table = doc.add_table(rows=len(rows)+1, cols=len(headers))
                        table.style = 'Table Grid'

                        # 表头
                        for j, header in enumerate(headers):
                            table.rows[0].cells[j].text = header

                        # 数据行
                        for row_idx, row_data in enumerate(rows):
                            for col_idx, cell_data in enumerate(row_data):
                                if col_idx < len(table.rows[row_idx+1].cells):
                                    table.rows[row_idx+1].cells[col_idx].text = cell_data
            # 引用
            elif line.startswith("> "):
                p = doc.add_paragraph(line[2:])
                p.style = 'Quote'
            # 列表
            elif line.startswith("- "):
                doc.add_paragraph(line[2:], style='List Bullet')
            elif re.match(r'^\d+\. ', line):
                text = re.sub(r'^\d+\. ', '', line)
                doc.add_paragraph(text, style='List Number')
            # 普通段落
            elif line.strip():
                # 处理加粗
                text = line.replace("**", "")
                doc.add_paragraph(text)

            i += 1

        doc.save(output_path)
        return True

    except ImportError:
        print("Warning: python-docx not installed. Skipping DOCX generation.")
        print("Install with: pip install python-docx")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Amazon Product Analyzer - MECE + Hardest 深度分析"
    )
    parser.add_argument("keyword", help="搜索关键词（用于报告标题）")
    parser.add_argument("-d", "--data-dir", default="~/Desktop/amazon",
                        help="数据目录（默认 ~/Desktop/amazon）")
    parser.add_argument("-o", "--output", help="输出报告路径")
    parser.add_argument("--no-docx", action="store_true",
                        help="不生成 DOCX 文件")

    args = parser.parse_args()

    data_dir = os.path.expanduser(args.data_dir)

    print(f"\n{'='*60}")
    print("Amazon Product Analyzer")
    print("Using MECE + Hardest Analysis Framework")
    print(f"{'='*60}\n")

    # 加载数据
    print("[Step 1] Loading data...")
    products, reviews = load_data(data_dir)
    print(f"  Products: {len(products)}")
    print(f"  Reviews entries: {len(reviews)}")

    if not products:
        print("No products found. Run amazon_crawler.py first.")
        return

    # MECE 分析
    print("\n[Step 2] MECE Analysis on reviews...")
    reviews_analysis = mece_analyze_reviews(reviews, products)
    print(f"  Categories identified: {len(reviews_analysis.get('categories', {}))}")

    # Hardest 深度分析
    print("\n[Step 3] Hardest Deep Analysis...")
    deep_analysis = hardest_deep_analysis(products, reviews_analysis)
    print(f"  Pain points analyzed: {len(deep_analysis.get('common_pain_points', []))}")

    # 生成报告
    print("\n[Step 4] Generating report...")
    report = generate_report(products, reviews, reviews_analysis, deep_analysis,
                            args.keyword, data_dir)

    # 确定输出路径
    if args.output:
        md_path = args.output if args.output.endswith(".md") else f"{args.output}.md"
    else:
        safe_keyword = re.sub(r'[^\w\-]', '_', args.keyword)[:30]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        md_path = os.path.join(data_dir, f"analysis_report_{safe_keyword}_{timestamp}.md")

    # 保存 Markdown
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"  Markdown: {md_path}")

    # 生成 DOCX
    if not args.no_docx:
        docx_path = md_path.replace(".md", ".docx")
        if generate_docx(report, docx_path):
            print(f"  DOCX: {docx_path}")

    print(f"\n{'='*60}")
    print("✅ Analysis completed!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
