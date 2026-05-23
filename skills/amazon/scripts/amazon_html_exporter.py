#!/usr/bin/env python3
"""
Amazon ASIN HTML Exporter
搜索关键词，获取前10个ASIN，为每个ASIN生成单独的Notion风格HTML文件
"""

import argparse
import os
import re
import sys
import time
import html
from datetime import datetime
from urllib.parse import quote_plus
from pathlib import Path

import requests
from bs4 import BeautifulSoup


# Notion 风格 CSS
NOTION_CSS = """
<style>
    :root {
        --bg-color: #ffffff;
        --text-color: #37352f;
        --gray-color: #787774;
        --light-gray: #e3e2de;
        --accent-color: #2383e2;
        --star-color: #f59e0b;
        --border-color: #e9e9e7;
        --code-bg: #f7f6f3;
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, 'Apple Color Emoji', Arial, sans-serif;
        background: var(--bg-color);
        color: var(--text-color);
        line-height: 1.7;
        font-size: 16px;
    }

    .container {
        max-width: 800px;
        margin: 0 auto;
        padding: 60px 24px;
    }

    /* Header */
    .header {
        margin-bottom: 48px;
    }

    .breadcrumb {
        font-size: 14px;
        color: var(--gray-color);
        margin-bottom: 16px;
    }

    .breadcrumb a {
        color: var(--accent-color);
        text-decoration: none;
    }

    .breadcrumb a:hover {
        text-decoration: underline;
    }

    .title {
        font-size: 40px;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 16px;
        letter-spacing: -0.5px;
    }

    .meta {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        align-items: center;
        font-size: 14px;
        color: var(--gray-color);
    }

    .meta-item {
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Product Image */
    .product-image {
        width: 100%;
        max-width: 500px;
        border-radius: 4px;
        margin: 32px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    /* Price */
    .price {
        font-size: 28px;
        font-weight: 600;
        color: #b12704;
        margin: 16px 0;
    }

    /* Rating */
    .rating-section {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 16px 0;
        padding: 16px;
        background: var(--code-bg);
        border-radius: 6px;
    }

    .stars {
        color: var(--star-color);
        font-size: 20px;
        letter-spacing: 2px;
    }

    .rating-value {
        font-size: 24px;
        font-weight: 600;
    }

    .review-count {
        color: var(--accent-color);
        font-size: 14px;
    }

    /* Section */
    .section {
        margin: 40px 0;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid var(--border-color);
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .section-icon {
        font-size: 20px;
    }

    /* Bullet Points */
    .bullet-list {
        list-style: none;
        padding: 0;
    }

    .bullet-item {
        position: relative;
        padding: 12px 0 12px 28px;
        border-bottom: 1px solid var(--light-gray);
    }

    .bullet-item:last-child {
        border-bottom: none;
    }

    .bullet-item::before {
        content: "✓";
        position: absolute;
        left: 0;
        color: #22c55e;
        font-weight: bold;
    }

    /* Reviews */
    .review-card {
        padding: 20px;
        margin: 16px 0;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        background: #fafafa;
    }

    .review-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
    }

    .review-title {
        font-weight: 600;
        font-size: 16px;
        color: var(--text-color);
    }

    .review-rating {
        color: var(--star-color);
        font-size: 14px;
    }

    .review-meta {
        font-size: 12px;
        color: var(--gray-color);
        margin-bottom: 12px;
    }

    .review-verified {
        color: #22c55e;
        font-size: 12px;
    }

    .review-body {
        font-size: 14px;
        line-height: 1.6;
        color: var(--text-color);
    }

    /* ASIN Badge */
    .asin-badge {
        display: inline-block;
        padding: 4px 12px;
        background: var(--code-bg);
        border-radius: 4px;
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
        font-size: 13px;
        color: var(--gray-color);
    }

    /* Links */
    .amazon-link {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 12px 24px;
        background: linear-gradient(to bottom, #f7dfa5, #f0c14b);
        border: 1px solid #a88734;
        border-radius: 4px;
        color: #111;
        text-decoration: none;
        font-size: 14px;
        margin: 20px 0;
        transition: background 0.2s;
    }

    .amazon-link:hover {
        background: linear-gradient(to bottom, #f5d78e, #eeb933);
    }

    /* Tags */
    .tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 24px;
    }

    .tag {
        padding: 4px 12px;
        background: var(--code-bg);
        border-radius: 4px;
        font-size: 12px;
        color: var(--gray-color);
    }

    /* Footer */
    .footer {
        margin-top: 60px;
        padding-top: 24px;
        border-top: 1px solid var(--border-color);
        font-size: 12px;
        color: var(--gray-color);
        text-align: center;
    }

    /* Responsive */
    @media (max-width: 600px) {
        .container {
            padding: 24px 16px;
        }
        .title {
            font-size: 28px;
        }
        .price {
            font-size: 24px;
        }
    }
</style>
"""


class AmazonHTMLExporter:
    """Amazon ASIN HTML 导出器"""

    MARKETPLACES = {
        "com": "https://www.amazon.com",
        "cn": "https://www.amazon.cn",
        "jp": "https://www.amazon.co.jp",
        "uk": "https://www.amazon.co.uk",
        "de": "https://www.amazon.de",
    }

    def __init__(self, marketplace: str = "com"):
        self.marketplace = marketplace
        self.base_url = self.MARKETPLACES.get(marketplace, "https://www.amazon.com")
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
        print(f"  Searching: {url}")

        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                print(f"    Warning: Status {response.status_code}")
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

            print(f"    Found {len(asins)} ASINs")
            return asins

        except Exception as e:
            print(f"    Error: {e}")
            return []

    def get_product_detail(self, asin: str) -> dict:
        """获取商品详情"""
        url = f"{self.base_url}/dp/{asin}"
        print(f"  Fetching: {asin}")

        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}", "asin": asin}

            soup = BeautifulSoup(response.text, "lxml")

            # 标题
            title = ""
            title_elem = soup.find("span", id="productTitle")
            if title_elem:
                title = title_elem.get_text(strip=True)

            # 价格
            price = ""
            price_elem = soup.find("span", class_="a-price-whole")
            if price_elem:
                price = "$" + price_elem.get_text(strip=True).replace(".", "")
                fraction = soup.find("span", class_="a-price-fraction")
                if fraction:
                    price += "." + fraction.get_text(strip=True)
            else:
                price_elem = soup.find("span", class_="a-offscreen")
                if price_elem:
                    price = price_elem.get_text(strip=True)

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

            # 评论数
            review_count = ""
            review_elem = soup.find("span", {"data-hook": "total-review-count"})
            if review_elem:
                review_count = review_elem.get_text(strip=True)

            # Bullet Points
            bullets = []
            feature_bullets = soup.find("div", id="feature-bullets")
            if feature_bullets:
                for li in feature_bullets.find_all("li"):
                    text = li.get_text(strip=True)
                    if text and len(text) > 5:
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

            return {
                "asin": asin,
                "url": url,
                "title": title,
                "brand": brand,
                "price": price,
                "rating": rating,
                "review_count": review_count,
                "bullets": bullets,
                "image_url": image_url,
            }

        except Exception as e:
            return {"error": str(e), "asin": asin}

    def get_reviews(self, asin: str, limit: int = 5) -> list:
        """获取商品评论"""
        url = f"{self.base_url}/product-reviews/{asin}/?reviewerType=all_reviews&sortBy=recent"

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

                # 日期
                date = ""
                date_elem = review_elem.find("span", {"data-hook": "review-date"})
                if date_elem:
                    date = date_elem.get_text(strip=True)

                # 验证购买
                verified = bool(review_elem.find("span", {"data-hook": "avp-badge"}))

                # 作者
                author = ""
                author_elem = review_elem.find("span", class_="a-profile-name")
                if author_elem:
                    author = author_elem.get_text(strip=True)

                reviews.append({
                    "title": title,
                    "rating": rating,
                    "body": body,
                    "date": date,
                    "verified": verified,
                    "author": author,
                })

            return reviews

        except Exception as e:
            print(f"    Error fetching reviews: {e}")
            return []

    def generate_html(self, product: dict, reviews: list, keyword: str) -> str:
        """生成 Notion 风格的 HTML"""

        # 生成星星显示
        def stars_html(rating_str):
            try:
                rating = float(rating_str)
                full_stars = int(rating)
                half_star = 1 if rating - full_stars >= 0.5 else 0
                empty_stars = 5 - full_stars - half_star
                return "★" * full_stars + ("½" if half_star else "") + "☆" * empty_stars
            except:
                return "☆☆☆☆☆"

        # Bullet Points HTML
        bullets_html = ""
        if product.get("bullets"):
            for bullet in product["bullets"]:
                bullets_html += f'<li class="bullet-item">{html.escape(bullet)}</li>\n'
            bullets_html = f'<ul class="bullet-list">\n{bullets_html}</ul>'
        else:
            bullets_html = '<p style="color: var(--gray-color);">暂无产品要点</p>'

        # Reviews HTML
        reviews_html = ""
        if reviews:
            for review in reviews:
                verified_badge = '<span class="review-verified">✓ 已验证购买</span>' if review.get("verified") else ""
                stars = stars_html(review.get("rating", "0"))

                reviews_html += f'''
                <div class="review-card">
                    <div class="review-header">
                        <span class="review-title">{html.escape(review.get("title", "无标题"))}</span>
                        <span class="review-rating">{stars}</span>
                    </div>
                    <div class="review-meta">
                        {html.escape(review.get("author", "匿名"))} · {html.escape(review.get("date", ""))}
                        {verified_badge}
                    </div>
                    <div class="review-body">{html.escape(review.get("body", ""))}</div>
                </div>
                '''
        else:
            reviews_html = '<p style="color: var(--gray-color);">暂无评论</p>'

        # 星星显示
        rating_stars = stars_html(product.get("rating", "0"))

        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(product.get("title", "Amazon Product"))}</title>
    {NOTION_CSS}
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <div class="breadcrumb">
                <a href="https://www.amazon.{self.marketplace}">Amazon</a>
                › <a href="https://www.amazon.{self.marketplace}/s?k={quote_plus(keyword)}">{html.escape(keyword)}</a>
                › <span class="asin-badge">{product.get("asin", "")}</span>
            </div>

            <h1 class="title">{html.escape(product.get("title", "未知产品"))}</h1>

            <div class="meta">
                <div class="meta-item">
                    <span class="asin-badge">{product.get("asin", "")}</span>
                </div>
                {f'<div class="meta-item">🏷️ {html.escape(product.get("brand", ""))}</div>' if product.get("brand") else ''}
            </div>
        </header>

        <!-- Product Image -->
        {f'<img src="{product.get("image_url", "")}" alt="Product Image" class="product-image">' if product.get("image_url") else ''}

        <!-- Price -->
        {f'<div class="price">{html.escape(product.get("price", ""))}</div>' if product.get("price") else ''}

        <!-- Rating -->
        <div class="rating-section">
            <span class="stars">{rating_stars}</span>
            <span class="rating-value">{product.get("rating", "N/A")}</span>
            <span class="review-count">{html.escape(product.get("review_count", ""))}</span>
        </div>

        <!-- Amazon Link -->
        <a href="{product.get("url", "")}" class="amazon-link" target="_blank">
            🛒 View on Amazon
        </a>

        <!-- Bullet Points -->
        <section class="section">
            <h2 class="section-title">
                <span class="section-icon">📋</span>
                Product Features
            </h2>
            {bullets_html}
        </section>

        <!-- Reviews -->
        <section class="section">
            <h2 class="section-title">
                <span class="section-icon">💬</span>
                Customer Reviews
            </h2>
            {reviews_html}
        </section>

        <!-- Tags -->
        <div class="tags">
            <span class="tag">#{product.get("asin", "")}</span>
            <span class="tag">#{keyword.replace(" ", "_")}</span>
            <span class="tag">#Amazon</span>
        </div>

        <!-- Footer -->
        <footer class="footer">
            <p>Generated by Amazon ASIN HTML Exporter</p>
            <p>Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </footer>
    </div>
</body>
</html>'''

        return html_content

    def export_keyword(self, keyword: str, output_dir: str, limit: int = 10):
        """导出关键词的所有ASIN HTML文件"""
        output_path = Path(output_dir) / keyword.replace(" ", "_")
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*60}")
        print(f"Amazon ASIN HTML Exporter")
        print(f"Keyword: {keyword}")
        print(f"Limit: {limit} ASINs")
        print(f"Output: {output_path}")
        print(f"{'='*60}\n")

        # Step 1: 搜索ASIN
        print("[Step 1] Searching ASINs...")
        asins = self.search_asins(keyword, limit)

        if not asins:
            print("No ASINs found. Exiting.")
            return

        # Step 2: 获取详情并生成HTML
        print(f"\n[Step 2] Fetching details and generating HTML...")

        for i, asin in enumerate(asins, 1):
            print(f"\n  [{i}/{len(asins)}] {asin}")

            # 获取商品详情
            product = self.get_product_detail(asin)

            if product.get("error"):
                print(f"    Error: {product['error']}")
                continue

            # 获取评论
            self._delay()
            reviews = self.get_reviews(asin, limit=5)

            # 生成HTML
            html_content = self.generate_html(product, reviews, keyword)

            # 保存文件
            html_file = output_path / f"{asin}.html"
            html_file.write_text(html_content, encoding="utf-8")
            print(f"    Saved: {html_file}")

            # 延迟
            if i < len(asins):
                self._delay()

        print(f"\n{'='*60}")
        print(f"Export completed!")
        print(f"Total: {len(asins)} ASINs")
        print(f"Output: {output_path}")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Amazon ASIN HTML Exporter - 为每个ASIN生成Notion风格HTML文件"
    )
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument("-n", "--limit", type=int, default=10, help="ASIN数量限制 (默认: 10)")
    parser.add_argument("-m", "--marketplace", default="com",
                        choices=["com", "cn", "jp", "uk", "de"],
                        help="亚马逊站点 (默认: com)")
    parser.add_argument("-o", "--output", default="~/Desktop/amazon-html",
                        help="输出目录 (默认: ~/Desktop/amazon-html)")

    args = parser.parse_args()

    output_dir = os.path.expanduser(args.output)

    exporter = AmazonHTMLExporter(args.marketplace)
    exporter.export_keyword(args.keyword, output_dir, args.limit)


if __name__ == "__main__":
    main()
