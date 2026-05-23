#!/usr/bin/env python3
"""
Amazon ASIN Notion Report Generator
搜索关键词，获取前10个ASIN，为每个ASIN生成单独的Notion风格HTML报告
"""

import argparse
import os
import re
import sys
import time
import json
import html
from datetime import datetime
from urllib.parse import quote_plus
from pathlib import Path

import requests
from bs4 import BeautifulSoup


# Notion 风格 CSS - 优化版
NOTION_CSS = """
<style>
    :root {
        --bg-color: #ffffff;
        --page-bg: #ffffff;
        --text-color: #37352f;
        --gray-color: #787774;
        --light-gray: #e3e2de;
        --accent-color: #2383e2;
        --star-color: #f59e0b;
        --border-color: #e9e9e7;
        --code-bg: #f7f6f3;
        --callout-bg: #f7f6f3;
        --success-color: #0f7b6c;
        --warning-color: #d9730d;
        --error-color: #e03e3e;
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, 'Apple Color Emoji', Arial, sans-serif, 'Segoe UI Emoji', 'Segoe UI Symbol';
        background: var(--bg-color);
        color: var(--text-color);
        line-height: 1.7;
        font-size: 16px;
    }

    .page {
        max-width: 900px;
        margin: 0 auto;
        padding: 80px 96px;
        background: var(--page-bg);
    }

    /* Notion Callout */
    .callout {
        display: flex;
        padding: 16px;
        background: var(--callout-bg);
        border-radius: 4px;
        margin: 16px 0;
        gap: 12px;
    }

    .callout-icon {
        font-size: 20px;
        line-height: 1;
        flex-shrink: 0;
    }

    .callout-content {
        flex: 1;
    }

    .callout-title {
        font-weight: 600;
        margin-bottom: 4px;
    }

    /* Toggle */
    .toggle {
        margin: 8px 0;
    }

    .toggle-header {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 0;
        cursor: pointer;
        font-weight: 500;
    }

    .toggle-arrow {
        transition: transform 0.2s;
    }

    .toggle-content {
        padding-left: 24px;
        margin-top: 8px;
    }

    /* Header */
    .page-header {
        margin-bottom: 48px;
    }

    .page-icon {
        font-size: 78px;
        margin-bottom: 16px;
        line-height: 1;
    }

    .page-title {
        font-size: 40px;
        font-weight: 700;
        line-height: 1.2;
        letter-spacing: -0.5px;
    }

    .page-meta {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 12px;
    }

    .tag {
        display: inline-flex;
        align-items: center;
        padding: 2px 8px;
        background: rgba(55, 53, 47, 0.08);
        border-radius: 4px;
        font-size: 14px;
        color: var(--text-color);
    }

    .tag-blue {
        background: rgba(35, 131, 226, 0.15);
        color: var(--accent-color);
    }

    .tag-green {
        background: rgba(15, 123, 108, 0.15);
        color: var(--success-color);
    }

    .tag-orange {
        background: rgba(217, 115, 13, 0.15);
        color: var(--warning-color);
    }

    /* Divider */
    .divider {
        border: none;
        border-top: 1px solid var(--border-color);
        margin: 32px 0;
    }

    /* Section */
    .section {
        margin: 32px 0;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .section-title-icon {
        font-size: 20px;
    }

    /* Image */
    .product-image {
        width: 100%;
        max-width: 400px;
        border-radius: 4px;
        margin: 16px 0;
    }

    /* Price */
    .price-display {
        display: flex;
        align-items: baseline;
        gap: 8px;
    }

    .price-value {
        font-size: 32px;
        font-weight: 600;
        color: #b12704;
    }

    .price-original {
        font-size: 18px;
        color: var(--gray-color);
        text-decoration: line-through;
    }

    /* Rating */
    .rating-display {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 12px 16px;
        background: var(--code-bg);
        border-radius: 4px;
    }

    .stars {
        color: var(--star-color);
        font-size: 16px;
        letter-spacing: 1px;
    }

    .rating-number {
        font-size: 18px;
        font-weight: 600;
    }

    .review-count {
        color: var(--accent-color);
    }

    /* Bullet Points */
    .bullet-list {
        list-style: none;
        padding: 0;
    }

    .bullet-item {
        position: relative;
        padding: 8px 0 8px 24px;
    }

    .bullet-item::before {
        content: "•";
        position: absolute;
        left: 8px;
        color: var(--text-color);
    }

    /* Review Card */
    .review-card {
        padding: 16px;
        margin: 12px 0;
        border: 1px solid var(--border-color);
        border-radius: 4px;
        background: var(--page-bg);
    }

    .review-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;
    }

    .review-title {
        font-weight: 600;
        font-size: 15px;
    }

    .review-stars {
        color: var(--star-color);
        font-size: 14px;
    }

    .review-meta {
        font-size: 13px;
        color: var(--gray-color);
        margin-bottom: 8px;
    }

    .verified-badge {
        color: var(--success-color);
        font-size: 12px;
    }

    .review-body {
        font-size: 14px;
        line-height: 1.6;
    }

    /* Link */
    .amazon-button {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 10px 20px;
        background: linear-gradient(to bottom, #f7dfa5, #f0c14b);
        border: 1px solid #a88734;
        border-radius: 4px;
        color: #111;
        text-decoration: none;
        font-size: 14px;
        margin: 16px 0;
    }

    .amazon-button:hover {
        background: linear-gradient(to bottom, #f5d78e, #eeb933);
    }

    /* Table */
    .info-table {
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;
    }

    .info-table td {
        padding: 8px 12px;
        border-bottom: 1px solid var(--border-color);
    }

    .info-table td:first-child {
        font-weight: 500;
        width: 120px;
        color: var(--gray-color);
    }

    /* ASIN Badge */
    .asin-badge {
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
        background: var(--code-bg);
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 13px;
    }

    /* Footer */
    .page-footer {
        margin-top: 64px;
        padding-top: 16px;
        border-top: 1px solid var(--border-color);
        font-size: 12px;
        color: var(--gray-color);
    }

    /* Responsive */
    @media (max-width: 768px) {
        .page {
            padding: 32px 24px;
        }
        .page-title {
            font-size: 32px;
        }
    }

    @media print {
        body { background: white; }
        .page { padding: 0; }
        .amazon-button { display: none; }
    }
</style>
"""


class AmazonNotionReporter:
    """Amazon ASIN Notion风格报告生成器"""

    MARKETPLACES = {
        "com": "https://www.amazon.com",
        "cn": "https://www.amazon.cn",
        "jp": "https://www.amazon.co.jp",
        "uk": "https://www.amazon.co.uk",
        "de": "https://www.amazon.de",
    }

    MARKETPLACE_NAMES = {
        "com": "美国",
        "cn": "中国",
        "jp": "日本",
        "uk": "英国",
        "de": "德国",
    }

    def __init__(self, marketplace: str = "com"):
        self.marketplace = marketplace
        self.base_url = self.MARKETPLACES.get(marketplace, "https://www.amazon.com")
        self.marketplace_name = self.MARKETPLACE_NAMES.get(marketplace, "美国")
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        })
        return session

    def _delay(self):
        import random
        time.sleep(random.uniform(1.5, 3.0))

    def search_asins(self, keyword: str, limit: int = 10) -> list:
        """搜索关键词，返回前N个ASIN"""
        url = f"{self.base_url}/s?k={quote_plus(keyword)}"
        print(f"  🔍 搜索: {url}")

        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                print(f"    ⚠️ HTTP {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, "lxml")
            asins = []
            asin_pattern = re.compile(r'^[A-Z0-9]{10}$')

            for item in soup.find_all(attrs={"data-asin": True}):
                asin = item.get("data-asin", "")
                if asin and asin_pattern.match(asin) and asin not in asins:
                    asins.append(asin)
                    if len(asins) >= limit:
                        break

            print(f"    ✅ 找到 {len(asins)} 个 ASIN")
            return asins

        except Exception as e:
            print(f"    ❌ 错误: {e}")
            return []

    def get_product_detail(self, asin: str) -> dict:
        """获取商品详情（同时从商品页获取评论）"""
        url = f"{self.base_url}/dp/{asin}"
        print(f"  📦 获取商品: {asin}")

        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}", "asin": asin, "url": url}

            soup = BeautifulSoup(response.text, "lxml")

            # 标题
            title = ""
            title_elem = soup.find("span", id="productTitle")
            if title_elem:
                title = title_elem.get_text(strip=True)

            # 价格 - 修复价格解析bug
            price = ""
            # 方法1: 尝试从 a-offscreen 获取完整价格
            offscreen = soup.find("span", class_="a-offscreen")
            if offscreen:
                price = offscreen.get_text(strip=True)
            # 方法2: 尝试从 a-price-whole + a-price-fraction 组合
            if not price:
                price_elem = soup.find("span", class_="a-price-whole")
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    # 提取数字部分（移除货币符号和逗号）
                    match = re.search(r'[\d,]+\.?\d*', price_text)
                    if match:
                        whole_part = match.group(0)
                        fraction_elem = soup.find("span", class_="a-price-fraction")
                        if fraction_elem:
                            fraction = fraction_elem.get_text(strip=True)
                            price = f"${whole_part.rstrip('.').replace(',', '')}.{fraction}"
                        else:
                            price = f"${whole_part}"
            # 方法3: 尝试从其他价格元素
            if not price:
                price_whole = soup.find("span", class_="a-price")
                if price_whole:
                    price = price_whole.get_text(strip=True).split()[0] if price_whole.get_text(strip=True) else ""

            # 评分
            rating = ""
            rating_elem = soup.find("span", {"data-hook": "rating-average"})
            if rating_elem:
                rating = rating_elem.get_text(strip=True)
            else:
                rating_elem = soup.find("i", class_="a-icon-star")
                if rating_elem:
                    match = re.search(r'([\d.]+)', rating_elem.get_text())
                    if match:
                        rating = match.group(1)
                else:
                    # 尝试从 acrPopover 获取
                    acr = soup.find("span", id="acrPopover")
                    if acr:
                        match = re.search(r'([\d.]+)\s*out\s*of\s*5', acr.get_text())
                        if match:
                            rating = match.group(1)

            # 评论数
            review_count = ""
            review_elem = soup.find("span", {"data-hook": "total-review-count"})
            if review_elem:
                review_count = review_elem.get_text(strip=True)
            else:
                review_elem = soup.find("span", id="acrCustomerReviewText")
                if review_elem:
                    review_count = review_elem.get_text(strip=True)

            # Bullet Points
            bullets = []
            feature_bullets = soup.find("div", id="feature-bullets")
            if feature_bullets:
                for li in feature_bullets.find_all("li"):
                    text = li.get_text(strip=True)
                    if text and len(text) > 5 and "Make it a bundle" not in text:
                        bullets.append(text)

            # 主图
            image_url = ""
            img_elem = soup.find("img", id="landingImage")
            if img_elem:
                image_url = img_elem.get("data-old-hires") or img_elem.get("src") or ""

            # 品牌
            brand = ""
            brand_elem = soup.find("a", id="bylineInfo")
            if brand_elem:
                brand = brand_elem.get_text(strip=True)
                brand = re.sub(r"^(Visit the |Brand: )", "", brand)

            # 从商品页提取评论（新增）
            page_reviews = self._extract_reviews_from_product_page(soup)

            return {
                "asin": asin,
                "url": url,
                "title": title,
                "brand": brand,
                "price": price,
                "rating": rating,
                "review_count": review_count,
                "bullets": bullets[:5],  # 最多5个
                "image_url": image_url,
                "_page_reviews": page_reviews,  # 内部使用，评论数据
            }

        except Exception as e:
            return {"error": str(e), "asin": asin, "url": url}

    def _extract_reviews_from_product_page(self, soup) -> list:
        """从商品详情页提取评论"""
        reviews = []

        for review_elem in soup.find_all("div", {"data-hook": "review"}):
            # 标题
            title = ""
            title_elem = review_elem.find("a", {"data-hook": "review-title"})
            if title_elem:
                # 移除内部嵌套的星级span
                for span in title_elem.find_all("span", class_="a-icon-alt"):
                    span.decompose()
                title = title_elem.get_text(strip=True)

            # 评分
            rating = ""
            rating_elem = review_elem.find("i", {"data-hook": "review-star-rating"})
            if rating_elem:
                match = re.search(r'(\d)', rating_elem.get_text())
                if match:
                    rating = match.group(1)

            # 内容
            body = ""
            body_elem = review_elem.find("span", {"data-hook": "review-body"})
            if body_elem:
                body = body_elem.get_text(strip=True)

            # 日期和作者
            date = ""
            author = ""
            date_elem = review_elem.find("span", {"data-hook": "review-date"})
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                date = date_text

            author_elem = review_elem.find("span", class_="a-profile-name")
            if author_elem:
                author = author_elem.get_text(strip=True)

            # 验证购买
            verified = bool(review_elem.find("span", {"data-hook": "avp-badge"}))

            if body:  # 只保留有内容的评论
                reviews.append({
                    "title": title,
                    "rating": rating,
                    "body": body[:500],  # 限制长度
                    "date": date,
                    "author": author,
                    "verified": verified,
                })

        return reviews[:5]  # 最多5条

    def get_reviews(self, asin: str, limit: int = 5) -> list:
        """获取商品首页评论"""
        url = f"{self.base_url}/product-reviews/{asin}/?reviewerType=all_reviews&sortBy=recent"
        print(f"    💬 获取评论...")

        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, "lxml")
            reviews = []

            for review_elem in soup.find_all("div", {"data-hook": "review"}):
                if len(reviews) >= limit:
                    break

                # 标题
                title = ""
                title_elem = review_elem.find("a", {"data-hook": "review-title"})
                if title_elem:
                    # 移除内部嵌套的星级span
                    for span in title_elem.find_all("span", class_="a-icon-alt"):
                        span.decompose()
                    title = title_elem.get_text(strip=True)

                # 评分
                rating = ""
                rating_elem = review_elem.find("i", {"data-hook": "review-star-rating"})
                if rating_elem:
                    match = re.search(r'(\d)', rating_elem.get_text())
                    if match:
                        rating = match.group(1)

                # 内容
                body = ""
                body_elem = review_elem.find("span", {"data-hook": "review-body"})
                if body_elem:
                    body = body_elem.get_text(strip=True)

                # 日期和作者
                date = ""
                author = ""
                date_elem = review_elem.find("span", {"data-hook": "review-date"})
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    date = date_text

                author_elem = review_elem.find("span", class_="a-profile-name")
                if author_elem:
                    author = author_elem.get_text(strip=True)

                # 验证购买
                verified = bool(review_elem.find("span", {"data-hook": "avp-badge"}))

                if body:  # 只保留有内容的评论
                    reviews.append({
                        "title": title,
                        "rating": rating,
                        "body": body[:500],  # 限制长度
                        "date": date,
                        "author": author,
                        "verified": verified,
                    })

            return reviews

        except Exception as e:
            print(f"      ⚠️ 评论获取失败: {e}")
            return []

    def _stars_display(self, rating_str: str) -> str:
        """生成星星显示"""
        try:
            rating = float(rating_str)
            full = int(rating)
            half = 1 if rating - full >= 0.5 else 0
            empty = 5 - full - half
            return "★" * full + ("½" if half else "") + "☆" * empty
        except:
            return "★★★★★"

    def generate_notion_html(self, product: dict, reviews: list, keyword: str, rank: int, total: int) -> str:
        """生成 Notion 风格的 HTML 报告"""

        # 处理错误情况
        if product.get("error"):
            return self._generate_error_html(product, keyword, rank, total)

        # Bullet Points HTML
        bullets_html = ""
        if product.get("bullets"):
            for bullet in product["bullets"]:
                bullets_html += f'<li class="bullet-item">{html.escape(bullet)}</li>\n'
            bullets_html = f'<ul class="bullet-list">\n{bullets_html}</ul>'
        else:
            bullets_html = '<p style="color: var(--gray-color);">暂无产品要点信息</p>'

        # Reviews HTML
        reviews_html = ""
        if reviews:
            for i, review in enumerate(reviews, 1):
                stars = self._stars_display(review.get("rating", "0"))
                verified = '<span class="verified-badge">✓ 已验证购买</span>' if review.get("verified") else ""

                reviews_html += f'''
                <div class="review-card">
                    <div class="review-header">
                        <span class="review-title">{html.escape(review.get("title", "无标题"))}</span>
                        <span class="review-stars">{stars}</span>
                    </div>
                    <div class="review-meta">
                        {html.escape(review.get("author", "匿名"))} · {html.escape(review.get("date", ""))}
                        {verified}
                    </div>
                    <div class="review-body">{html.escape(review.get("body", ""))}</div>
                </div>
                '''
        else:
            reviews_html = '<div class="callout"><span class="callout-icon">ℹ️</span><div class="callout-content">暂无评论数据</div></div>'

        # 星级显示
        rating_stars = self._stars_display(product.get("rating", "0"))
        rating_value = product.get("rating", "N/A")
        review_count = product.get("review_count", "")

        # 当前时间
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(product.get("title", "Amazon Product")[:50])}...</title>
    {NOTION_CSS}
</head>
<body>
    <div class="page">
        <!-- Page Header -->
        <header class="page-header">
            <div class="page-icon">📦</div>
            <h1 class="page-title">{html.escape(product.get("title", "未知产品"))}</h1>
            <div class="page-meta">
                <span class="tag tag-blue">#{product.get("asin", "")}</span>
                <span class="tag">#{keyword.replace(" ", "_")}</span>
                <span class="tag tag-green">#{self.marketplace_name}</span>
                <span class="tag tag-orange">第 {rank}/{total} 个</span>
            </div>
        </header>

        <hr class="divider">

        <!-- Basic Info Callout -->
        <div class="callout">
            <span class="callout-icon">📋</span>
            <div class="callout-content">
                <div class="callout-title">基本信息</div>
                <table class="info-table">
                    <tr><td>ASIN</td><td><code class="asin-badge">{product.get("asin", "")}</code></td></tr>
                    <tr><td>品牌</td><td>{html.escape(product.get("brand", "未知"))}</td></tr>
                    <tr><td>站点</td><td>{self.marketplace_name} ({self.marketplace})</td></tr>
                    <tr><td>链接</td><td><a href="{product.get("url", "")}" target="_blank" style="color: var(--accent-color);">查看商品页面</a></td></tr>
                </table>
            </div>
        </div>

        <!-- Product Image -->
        {f'<img src="{product.get("image_url", "")}" alt="Product Image" class="product-image">' if product.get("image_url") else '<div class="callout"><span class="callout-icon">🖼️</span><div class="callout-content">暂无商品图片</div></div>'}

        <!-- Price Section -->
        <section class="section">
            <h2 class="section-title"><span class="section-title-icon">💰</span> 价格</h2>
            {f'<div class="price-display"><span class="price-value">{html.escape(product.get("price", ""))}</span></div>' if product.get("price") else '<p style="color: var(--gray-color);">价格信息暂不可用</p>'}
        </section>

        <!-- Rating Section -->
        <section class="section">
            <h2 class="section-title"><span class="section-title-icon">⭐</span> 评分</h2>
            <div class="rating-display">
                <span class="stars">{rating_stars}</span>
                <span class="rating-number">{rating_value}</span>
                <span class="review-count">{html.escape(review_count)}</span>
            </div>
        </section>

        <!-- Amazon Link Button -->
        <a href="{product.get("url", "")}" class="amazon-button" target="_blank">
            🛒 在 Amazon 上查看
        </a>

        <hr class="divider">

        <!-- Bullet Points Section -->
        <section class="section">
            <h2 class="section-title"><span class="section-title-icon">✨</span> 产品要点</h2>
            {bullets_html}
        </section>

        <hr class="divider">

        <!-- Reviews Section -->
        <section class="section">
            <h2 class="section-title"><span class="section-title-icon">💬</span> 用户评论</h2>
            <p style="color: var(--gray-color); margin-bottom: 16px;">首页 {len(reviews)} 条评论</p>
            {reviews_html}
        </section>

        <hr class="divider">

        <!-- Summary Callout -->
        <div class="callout">
            <span class="callout-icon">📊</span>
            <div class="callout-content">
                <div class="callout-title">数据摘要</div>
                <table class="info-table">
                    <tr><td>搜索关键词</td><td>{html.escape(keyword)}</td></tr>
                    <tr><td>排名</td><td>第 {rank} 个 / 共 {total} 个</td></tr>
                    <tr><td>抓取时间</td><td>{now}</td></tr>
                    <tr><td>评论数量</td><td>{len(reviews)} 条</td></tr>
                </table>
            </div>
        </div>

        <!-- Footer -->
        <footer class="page-footer">
            <p>Generated by Amazon Notion Reporter • {now}</p>
        </footer>
    </div>
</body>
</html>'''

        return html_content

    def _generate_error_html(self, product: dict, keyword: str, rank: int, total: int) -> str:
        """生成错误情况的 HTML"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error - {product.get("asin", "")}</title>
    {NOTION_CSS}
</head>
<body>
    <div class="page">
        <header class="page-header">
            <div class="page-icon">❌</div>
            <h1 class="page-title">获取失败</h1>
            <div class="page-meta">
                <span class="tag">#{product.get("asin", "")}</span>
            </div>
        </header>

        <hr class="divider">

        <div class="callout">
            <span class="callout-icon">⚠️</span>
            <div class="callout-content">
                <div class="callout-title">错误信息</div>
                <p>{html.escape(product.get("error", "未知错误"))}</p>
            </div>
        </div>

        <div class="callout">
            <span class="callout-icon">🔗</span>
            <div class="callout-content">
                <div class="callout-title">商品链接</div>
                <a href="{product.get("url", "")}" target="_blank" style="color: var(--accent-color);">{product.get("url", "")}</a>
            </div>
        </div>

        <footer class="page-footer">
            <p>Generated by Amazon Notion Reporter • {now}</p>
        </footer>
    </div>
</body>
</html>'''

    def export_keyword(self, keyword: str, output_dir: str, limit: int = 10):
        """导出关键词的所有ASIN报告"""
        output_path = Path(output_dir) / keyword.replace(" ", "_")
        output_path.mkdir(parents=True, exist_ok=True)

        # 同时创建一个汇总目录
        summary_path = output_path

        print(f"\n{'='*60}")
        print(f"📦 Amazon Notion 报告生成器")
        print(f"{'='*60}")
        print(f"🔍 关键词: {keyword}")
        print(f"🌍 站点: {self.marketplace_name} ({self.marketplace})")
        print(f"📊 数量: {limit} 个 ASIN")
        print(f"📁 输出: {output_path}")
        print(f"{'='*60}\n")

        # Step 1: 搜索ASIN
        print("[Step 1/3] 搜索 ASIN...")
        asins = self.search_asins(keyword, limit)

        if not asins:
            print("❌ 未找到任何 ASIN")
            return

        # Step 2: 获取详情和评论
        print(f"\n[Step 2/3] 获取商品详情和评论...")
        all_data = []

        for i, asin in enumerate(asins, 1):
            print(f"\n  [{i}/{len(asins)}] {asin}")

            # 获取商品详情（已包含评论）
            product = self.get_product_detail(asin)

            # 从商品页提取的评论（避免访问被阻止的评论页）
            reviews = product.pop("_page_reviews", [])

            all_data.append({
                "product": product,
                "reviews": reviews,
                "rank": i,
            })

            # 延迟
            if i < len(asins):
                self._delay()

        # Step 3: 生成HTML报告
        print(f"\n[Step 3/3] 生成 Notion 风格报告...")

        for data in all_data:
            product = data["product"]
            reviews = data["reviews"]
            rank = data["rank"]

            # 生成HTML
            html_content = self.generate_notion_html(
                product, reviews, keyword, rank, len(asins)
            )

            # 保存文件
            html_file = output_path / f"{product.get('asin', f'unknown_{rank}')}.html"
            html_file.write_text(html_content, encoding="utf-8")
            print(f"  ✅ {product.get('asin', '')} → {html_file.name}")

        # 生成索引文件
        self._generate_index(all_data, keyword, output_path)

        print(f"\n{'='*60}")
        print(f"✅ 导出完成!")
        print(f"{'='*60}")
        print(f"📊 成功: {len([d for d in all_data if not d['product'].get('error')])} 个")
        print(f"❌ 失败: {len([d for d in all_data if d['product'].get('error')])} 个")
        print(f"📁 输出目录: {output_path}")
        print(f"{'='*60}\n")

    def _generate_index(self, all_data: list, keyword: str, output_path: Path):
        """生成索引页面"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        items_html = ""
        for data in all_data:
            product = data["product"]
            asin = product.get("asin", "")
            title = product.get("title", "获取失败")[:60] + "..." if product.get("title") else "获取失败"
            price = product.get("price", "-")
            rating = product.get("rating", "-")
            error = product.get("error")

            status_icon = "✅" if not error else "❌"
            link = f'<a href="{asin}.html" style="color: var(--accent-color); text-decoration: none;">{title}</a>'

            items_html += f'''
            <tr>
                <td>{status_icon}</td>
                <td><code class="asin-badge">{asin}</code></td>
                <td>{link}</td>
                <td>{html.escape(price)}</td>
                <td>{html.escape(rating)}</td>
            </tr>
            '''

        index_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(keyword)} - ASIN 报告索引</title>
    {NOTION_CSS}
    <style>
        .index-table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
        .index-table th, .index-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid var(--border-color); }}
        .index-table th {{ font-weight: 600; background: var(--code-bg); }}
        .index-table tr:hover {{ background: var(--code-bg); }}
    </style>
</head>
<body>
    <div class="page">
        <header class="page-header">
            <div class="page-icon">📊</div>
            <h1 class="page-title">{html.escape(keyword)}</h1>
            <div class="page-meta">
                <span class="tag tag-blue">{len(all_data)} 个商品</span>
                <span class="tag tag-green">{self.marketplace_name}</span>
            </div>
        </header>

        <hr class="divider">

        <div class="callout">
            <span class="callout-icon">ℹ️</span>
            <div class="callout-content">
                <div class="callout-title">报告说明</div>
                <p>点击商品标题查看详细的 Notion 风格报告，包含价格、评分、产品要点和用户评论。</p>
            </div>
        </div>

        <section class="section">
            <h2 class="section-title"><span class="section-title-icon">📋</span> 商品列表</h2>
            <table class="index-table">
                <thead>
                    <tr>
                        <th>状态</th>
                        <th>ASIN</th>
                        <th>标题</th>
                        <th>价格</th>
                        <th>评分</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>
        </section>

        <footer class="page-footer">
            <p>Generated by Amazon Notion Reporter • {now}</p>
        </footer>
    </div>
</body>
</html>'''

        index_file = output_path / "index.html"
        index_file.write_text(index_html, encoding="utf-8")
        print(f"  📑 索引页面 → index.html")


def main():
    parser = argparse.ArgumentParser(
        description="Amazon ASIN Notion 报告生成器 - 为每个ASIN生成Notion风格HTML报告"
    )
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument("-n", "--limit", type=int, default=10, help="ASIN数量 (默认: 10)")
    parser.add_argument("-m", "--marketplace", default="com",
                        choices=["com", "cn", "jp", "uk", "de"],
                        help="亚马逊站点 (默认: com)")
    parser.add_argument("-o", "--output", default="~/Desktop/amazon-notion",
                        help="输出目录 (默认: ~/Desktop/amazon-notion)")

    args = parser.parse_args()

    output_dir = os.path.expanduser(args.output)

    reporter = AmazonNotionReporter(args.marketplace)
    reporter.export_keyword(args.keyword, output_dir, args.limit)


if __name__ == "__main__":
    main()
