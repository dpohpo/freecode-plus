#!/usr/bin/env python3
"""
Amazon Deep Crawler - 爬取商品详情、差评、图片
支持多页搜索，提取完整商品信息用于分析
"""

import argparse
import csv
import os
import re
import sys
import time
import json
from datetime import datetime
from urllib.parse import quote_plus, urljoin
from typing import Optional

import requests
from bs4 import BeautifulSoup


class AmazonCrawler:
    def __init__(self, marketplace: str = "com"):
        self.marketplaces = {
            "com": "https://www.amazon.com",
            "cn": "https://www.amazon.cn",
            "jp": "https://www.amazon.co.jp",
            "uk": "https://www.amazon.co.uk",
            "de": "https://www.amazon.de",
        }
        self.base_url = self.marketplaces.get(marketplace, "https://www.amazon.com")
        self.session = self._create_session()
        self.products = []
        self.reviews_data = {}

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        })
        return session

    def _delay(self, min_sec: float = 1.5, max_sec: float = 3.0):
        """随机延迟防止被封"""
        import random
        time.sleep(random.uniform(min_sec, max_sec))

    def search(self, keyword: str, pages: int = 3) -> list[str]:
        """搜索关键词，返回所有ASIN列表"""
        all_asins = []
        asin_pattern = re.compile(r'^[A-Z0-9]{10}$')

        for page in range(1, pages + 1):
            url = f"{self.base_url}/s?k={quote_plus(keyword)}&page={page}"
            print(f"  Searching page {page}/{pages}: {url}")

            try:
                response = self.session.get(url, timeout=30)
                if response.status_code != 200:
                    print(f"    Warning: Status {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                page_asins = []

                for item in soup.find_all(attrs={"data-asin": True}):
                    asin = item.get("data-asin", "")
                    if asin and asin_pattern.match(asin) and asin not in all_asins:
                        all_asins.append(asin)
                        page_asins.append(asin)

                print(f"    Found {len(page_asins)} new ASINs (total: {len(all_asins)})")

                if page < pages:
                    self._delay()

            except Exception as e:
                print(f"    Error: {e}")

        return all_asins

    def get_product_detail(self, asin: str) -> Optional[dict]:
        """获取商品详情页信息"""
        url = f"{self.base_url}/dp/{asin}"
        print(f"  Fetching product: {asin}")

        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                print(f"    Warning: Status {response.status_code}")
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # 标题
            title = ""
            title_elem = soup.find("span", id="productTitle")
            if title_elem:
                title = title_elem.get_text(strip=True)

            # 价格
            price = ""
            price_elem = (
                soup.find("span", class_="a-price-whole") or
                soup.find("span", class_="a-offscreen") or
                soup.find("span", {"data-a-color": "price"})
            )
            if price_elem:
                price = price_elem.get_text(strip=True)

            # 评分
            rating = ""
            rating_elem = soup.find("span", {"data-hook": "rating-average"}) or \
                          soup.find("i", class_="a-icon-star") or \
                          soup.find("span", class_="a-icon-alt")
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                match = re.search(r'([\d.]+)\s*(out of|stars)', rating_text, re.I)
                if match:
                    rating = match.group(1)

            # 评论数
            review_count = ""
            review_elem = soup.find("span", {"data-hook": "total-review-count"}) or \
                          soup.find("span", id="acrCustomerReviewText")
            if review_elem:
                review_text = review_elem.get_text(strip=True)
                match = re.search(r'([\d,]+)', review_text)
                if match:
                    review_count = match.group(1)

            # Bullet Points
            bullet_points = []
            feature_bullets = soup.find("div", id="feature-bullets")
            if feature_bullets:
                for li in feature_bullets.find_all("li"):
                    text = li.get_text(strip=True)
                    if text and len(text) > 5:
                        bullet_points.append(text)

            # 如果没找到 feature-bullets，尝试其他位置
            if not bullet_points:
                for ul in soup.find_all("ul", class_="a-unordered-list"):
                    items = [li.get_text(strip=True) for li in ul.find_all("li") if li.get_text(strip=True)]
                    if len(items) >= 3:
                        bullet_points = items
                        break

            # 主图
            image_url = ""
            img_elem = soup.find("img", id="landingImage") or \
                       soup.find("img", {"data-old-hires": True})
            if img_elem:
                image_url = img_elem.get("data-old-hires") or \
                           img_elem.get("src") or ""

            # 商品描述
            description = ""
            desc_elem = soup.find("div", id="productDescription")
            if desc_elem:
                description = desc_elem.get_text(strip=True)[:500]

            # 品牌信息
            brand = ""
            brand_elem = soup.find("a", id="bylineInfo")
            if brand_elem:
                brand = brand_elem.get_text(strip=True)

            # Best Sellers Rank
            bsr = ""
            bsr_elem = soup.find("li", id="SalesRank") or \
                       soup.find("span", string=re.compile(r'Best Sellers'))
            if bsr_elem:
                bsr_text = bsr_elem.get_text(strip=True)
                match = re.search(r'#([\d,]+)', bsr_text)
                if match:
                    bsr = match.group(1)

            product = {
                "asin": asin,
                "title": title,
                "brand": brand,
                "price": price,
                "rating": rating,
                "review_count": review_count,
                "bullet_points": bullet_points,
                "description": description,
                "image_url": image_url,
                "bsr": bsr,
                "url": url
            }

            self._delay()
            return product

        except Exception as e:
            print(f"    Error fetching product: {e}")
            return None

    def get_negative_reviews(self, asin: str, max_reviews: int = 30) -> list[dict]:
        """获取差评（1-2星）"""
        reviews = []

        # 尝试获取差评页面
        for filter_type in ["negative", "one_star", "two_star"]:
            url = f"{self.base_url}/product-reviews/{asin}/"
            params = {
                "reviewerType": "all_reviews",
                "filterByStar": filter_type,
                "sortBy": "recent",
                "pageSize": "20"
            }

            print(f"  Fetching reviews ({filter_type}): {asin}")

            try:
                response = self.session.get(url, params=params, timeout=30)
                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, "html.parser")

                for review_elem in soup.find_all("div", {"data-hook": "review"}):
                    if len(reviews) >= max_reviews:
                        break

                    # 评论标题
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

                    # 只保留1-2星差评
                    if rating not in ["1", "2"]:
                        continue

                    # 评论内容
                    body = ""
                    body_elem = review_elem.find("span", {"data-hook": "review-body"})
                    if body_elem:
                        body = body_elem.get_text(strip=True)

                    # 评论日期
                    date = ""
                    date_elem = review_elem.find("span", {"data-hook": "review-date"})
                    if date_elem:
                        date = date_elem.get_text(strip=True)

                    # 验证标记
                    verified = False
                    verify_elem = review_elem.find("span", {"data-hook": "avp-badge"})
                    if verify_elem:
                        verified = True

                    # 有用数
                    helpful = ""
                    helpful_elem = review_elem.find("span", {"data-hook": "helpful-vote-statement"})
                    if helpful_elem:
                        match = re.search(r'(\d+)', helpful_elem.get_text())
                        if match:
                            helpful = match.group(1)

                    review = {
                        "asin": asin,
                        "rating": rating,
                        "title": title,
                        "body": body,
                        "date": date,
                        "verified": verified,
                        "helpful": helpful
                    }

                    # 去重
                    if review["body"] and review not in reviews:
                        reviews.append(review)

                if len(reviews) >= max_reviews:
                    break

                self._delay()

            except Exception as e:
                print(f"    Error fetching reviews: {e}")

        return reviews[:max_reviews]

    def download_image(self, asin: str, image_url: str, output_dir: str) -> Optional[str]:
        """下载商品图片"""
        if not image_url:
            return None

        try:
            response = self.session.get(image_url, timeout=15)
            if response.status_code == 200:
                img_path = os.path.join(output_dir, f"{asin}.jpg")
                with open(img_path, "wb") as f:
                    f.write(response.content)
                return img_path
        except Exception as e:
            print(f"    Error downloading image: {e}")

        return None

    def crawl(self, keyword: str, pages: int = 3, max_reviews: int = 30,
              output_dir: str = None) -> dict:
        """完整爬取流程"""
        if output_dir is None:
            output_dir = os.path.expanduser("~/Desktop/amazon")

        os.makedirs(output_dir, exist_ok=True)

        print(f"\n{'='*60}")
        print(f"Amazon Deep Crawler")
        print(f"Keyword: {keyword}")
        print(f"Pages: {pages}")
        print(f"Max reviews per product: {max_reviews}")
        print(f"Output: {output_dir}")
        print(f"{'='*60}\n")

        # Step 1: 搜索获取ASIN
        print("[Step 1] Searching for ASINs...")
        asins = self.search(keyword, pages)
        print(f"Total unique ASINs found: {len(asins)}\n")

        if not asins:
            print("No ASINs found. Exiting.")
            return {"products": [], "reviews": {}}

        # Step 2: 获取商品详情
        print(f"[Step 2] Fetching product details ({len(asins)} products)...")
        products = []
        for i, asin in enumerate(asins, 1):
            print(f"  [{i}/{len(asins)}] {asin}")
            product = self.get_product_detail(asin)
            if product:
                products.append(product)
                # 下载图片
                if product.get("image_url"):
                    self.download_image(asin, product["image_url"], output_dir)

        print(f"Successfully fetched: {len(products)} products\n")

        # Step 3: 获取差评
        print(f"[Step 3] Fetching negative reviews...")
        all_reviews = {}
        for i, product in enumerate(products, 1):
            asin = product["asin"]
            print(f"  [{i}/{len(products)}] {asin}")
            reviews = self.get_negative_reviews(asin, max_reviews)
            all_reviews[asin] = reviews
            product["negative_review_count"] = len(reviews)

        total_reviews = sum(len(r) for r in all_reviews.values())
        print(f"Total negative reviews collected: {total_reviews}\n")

        # Step 4: 保存数据
        print("[Step 4] Saving data...")

        # 保存商品CSV
        csv_path = os.path.join(output_dir, "products.csv")
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            fieldnames = ["asin", "title", "brand", "price", "rating", "review_count",
                         "negative_review_count", "bsr", "bullet_points", "url"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for p in products:
                row = {k: (v if not isinstance(v, list) else " | ".join(v))
                       for k, v in p.items() if k in fieldnames}
                writer.writerow(row)
        print(f"  Products CSV: {csv_path}")

        # 保存完整JSON
        json_path = os.path.join(output_dir, "products.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"  Products JSON: {json_path}")

        # 保存差评
        reviews_path = os.path.join(output_dir, "negative_reviews.json")
        with open(reviews_path, "w", encoding="utf-8") as f:
            json.dump(all_reviews, f, ensure_ascii=False, indent=2)
        print(f"  Reviews JSON: {reviews_path}")

        # 保存差评CSV
        reviews_csv_path = os.path.join(output_dir, "negative_reviews.csv")
        with open(reviews_csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["asin", "rating", "title", "body", "date", "verified", "helpful"])
            writer.writeheader()
            for asin, reviews in all_reviews.items():
                for r in reviews:
                    writer.writerow(r)
        print(f"  Reviews CSV: {reviews_csv_path}")

        print(f"\n{'='*60}")
        print(f"✅ Crawl completed!")
        print(f"   Products: {len(products)}")
        print(f"   Negative reviews: {total_reviews}")
        print(f"   Output directory: {output_dir}")
        print(f"{'='*60}\n")

        return {
            "products": products,
            "reviews": all_reviews,
            "output_dir": output_dir
        }


def main():
    parser = argparse.ArgumentParser(
        description="Amazon Deep Crawler - 爬取商品详情和差评"
    )
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument("-p", "--pages", type=int, default=3, help="爬取页数（默认3页）")
    parser.add_argument("-r", "--max-reviews", type=int, default=30,
                        help="每个商品最大差评数（默认30）")
    parser.add_argument("-m", "--marketplace", default="com",
                        choices=["com", "cn", "jp", "uk", "de"],
                        help="亚马逊站点（默认com）")
    parser.add_argument("-o", "--output", help="输出目录")

    args = parser.parse_args()

    crawler = AmazonCrawler(args.marketplace)
    crawler.crawl(
        keyword=args.keyword,
        pages=args.pages,
        max_reviews=args.max_reviews,
        output_dir=args.output
    )


if __name__ == "__main__":
    main()
