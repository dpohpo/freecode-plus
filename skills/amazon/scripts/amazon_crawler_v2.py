#!/usr/bin/env python3
"""
Amazon Deep Crawler V2 - 基于 exotic-amazon/PulsarRPA 策略优化
使用 undetected-chromedriver 实现反检测 + 人类行为模拟

关键技术策略（从 exotic-amazon 学习）：
1. 真实浏览器环境（非 requests）
2. WebDriver 隐身（undetected-chromedriver）
3. 人类行为模拟（随机延迟、页面滚动）
4. 隐私上下文管理（独立会话）
5. RPA 交互（点击、滚动、等待动态加载）
"""

import argparse
import csv
import os
import re
import sys
import time
import json
import random
from datetime import datetime
from urllib.parse import quote_plus, urljoin
from typing import Optional, List, Dict

# 反检测浏览器
try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False
    print("Warning: undetected-chromedriver not installed. Install with:")
    print("  pip3 install undetected-chromedriver --break-system-packages")


class HumanBehaviorSimulator:
    """人类行为模拟器 - 模拟真实用户行为模式"""

    @staticmethod
    def random_delay(min_sec: float = 1.0, max_sec: float = 3.0, context: str = ""):
        """智能随机延迟 - 不同场景使用不同延迟范围"""
        delays = {
            "page_load": (2.0, 5.0),      # 页面加载
            "click": (0.5, 1.5),          # 点击后
            "scroll": (0.3, 1.0),         # 滚动
            "typing": (0.1, 0.3),         # 输入
            "navigation": (3.0, 7.0),     # 页面导航
            "review_page": (2.0, 4.0),    # 评论页
        }
        if context in delays:
            min_sec, max_sec = delays[context]
        time.sleep(random.uniform(min_sec, max_sec))

    @staticmethod
    def human_scroll(driver, scroll_times: int = 3):
        """模拟人类滚动行为"""
        for i in range(scroll_times):
            # 随机滚动距离
            scroll_amount = random.randint(300, 800)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.3, 0.8))

        # 偶尔回滚一点
        if random.random() > 0.7:
            driver.execute_script(f"window.scrollBy(0, -{random.randint(100, 300)});")
            time.sleep(random.uniform(0.2, 0.5))

    @staticmethod
    def human_click(driver, element):
        """模拟人类点击行为"""
        # 先移动到元素
        actions = ActionChains(driver)
        actions.move_to_element(element)
        # 随机偏移
        actions.move_by_offset(random.randint(-5, 5), random.randint(-5, 5))
        time.sleep(random.uniform(0.1, 0.3))
        actions.click()
        actions.perform()

    @staticmethod
    def move_mouse_randomly(driver):
        """随机移动鼠标"""
        try:
            actions = ActionChains(driver)
            actions.move_by_offset(random.randint(-50, 50), random.randint(-50, 50))
            actions.perform()
        except:
            pass


class AmazonCrawlerV2:
    """Amazon 深度爬虫 V2 - 反检测版本"""

    MARKETPLACES = {
        "com": "https://www.amazon.com",
        "cn": "https://www.amazon.cn",
        "jp": "https://www.amazon.co.jp",
        "uk": "https://www.amazon.co.uk",
        "de": "https://www.amazon.de",
    }

    def __init__(self, marketplace: str = "com", headless: bool = True):
        if not UC_AVAILABLE:
            raise ImportError("undetected-chromedriver is required. Install with: pip3 install undetected-chromedriver")

        self.base_url = self.MARKETPLACES.get(marketplace, "https://www.amazon.com")
        self.headless = headless
        self.driver = None
        self.products = []
        self.reviews_data = {}
        self.human = HumanBehaviorSimulator()

    def _create_driver(self):
        """创建反检测浏览器"""
        options = uc.ChromeOptions()

        if self.headless:
            # 注意：PulsarRPA 指出 headless 模式可被检测
            # 但为了实用性我们仍提供此选项
            options.add_argument('--headless=new')

        # 基础反检测配置
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')

        # 随机窗口大小（更像真实用户）
        width = random.randint(1200, 1400)
        height = random.randint(800, 1000)
        options.add_argument(f'--window-size={width},{height}')

        # 禁用不必要的功能
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-notifications')

        # 创建驱动
        self.driver = uc.Chrome(options=options, version_main=None)

        # 设置页面加载超时
        self.driver.set_page_load_timeout(60)
        self.driver.implicitly_wait(10)

        return self.driver

    def _close_driver(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

    def _safe_get(self, url: str, max_retries: int = 3) -> bool:
        """安全访问页面，带重试"""
        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                self.human.random_delay(context="page_load")

                # 检查是否被重定向到验证页面
                if "captcha" in self.driver.current_url.lower() or \
                   "signin" in self.driver.current_url.lower():
                    print(f"    Warning: Redirected to {self.driver.current_url}")
                    self.human.random_delay(5.0, 10.0)
                    continue

                return True

            except Exception as e:
                print(f"    Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    self.human.random_delay(5.0, 10.0)

        return False

    def search(self, keyword: str, pages: int = 3) -> List[str]:
        """搜索关键词，返回所有 ASIN 列表"""
        all_asins = []
        asin_pattern = re.compile(r'^[A-Z0-9]{10}$')

        for page in range(1, pages + 1):
            url = f"{self.base_url}/s?k={quote_plus(keyword)}&page={page}"
            print(f"  Searching page {page}/{pages}: {url}")

            if not self._safe_get(url):
                continue

            # 模拟人类滚动
            self.human.human_scroll(self.driver, scroll_times=2)

            # 获取页面源码
            page_source = self.driver.page_source

            # 从 data-asin 属性提取
            asin_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-asin]")

            page_asins = []
            for elem in asin_elements:
                try:
                    asin = elem.get_attribute("data-asin")
                    if asin and asin_pattern.match(asin) and asin not in all_asins:
                        all_asins.append(asin)
                        page_asins.append(asin)
                except:
                    continue

            print(f"    Found {len(page_asins)} new ASINs (total: {len(all_asins)})")

            if page < pages:
                self.human.random_delay(context="navigation")

        return all_asins

    def get_product_detail(self, asin: str) -> Optional[Dict]:
        """获取商品详情页信息"""
        url = f"{self.base_url}/dp/{asin}"
        print(f"  Fetching product: {asin}")

        if not self._safe_get(url):
            return None

        # 模拟人类浏览行为
        self.human.human_scroll(self.driver, scroll_times=3)

        try:
            product = {"asin": asin, "url": url}

            # 标题
            try:
                title_elem = self.driver.find_element(By.ID, "productTitle")
                product["title"] = title_elem.text.strip()
            except:
                product["title"] = ""

            # 价格
            try:
                # 尝试多种价格选择器
                price_selectors = [
                    ".a-price-whole",
                    ".a-price .a-offscreen",
                    "#priceblock_ourprice",
                    "#priceblock_dealprice",
                    "#priceblock_saleprice",
                    ".a-price-range .a-offscreen",
                ]
                for selector in price_selectors:
                    try:
                        price_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        product["price"] = price_elem.text.strip()
                        break
                    except:
                        continue
                if "price" not in product:
                    product["price"] = ""
            except:
                product["price"] = ""

            # 评分
            try:
                rating_selectors = [
                    "[data-hook='rating-average']",
                    ".a-icon-star .a-icon-alt",
                    "#acrPopover .a-icon-alt",
                ]
                for selector in rating_selectors:
                    try:
                        rating_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        match = re.search(r'([\d.]+)', rating_elem.get_attribute("innerText") or rating_elem.text)
                        if match:
                            product["rating"] = match.group(1)
                            break
                    except:
                        continue
                if "rating" not in product:
                    product["rating"] = ""
            except:
                product["rating"] = ""

            # 评论数
            try:
                review_elem = self.driver.find_element(By.ID, "acrCustomerReviewText")
                match = re.search(r'([\d,]+)', review_elem.text)
                product["review_count"] = match.group(1) if match else ""
            except:
                product["review_count"] = ""

            # Bullet Points
            product["bullet_points"] = []
            try:
                feature_bullets = self.driver.find_element(By.ID, "feature-bullets")
                bullet_items = feature_bullets.find_elements(By.TAG_NAME, "li")
                for li in bullet_items:
                    text = li.text.strip()
                    if text and len(text) > 5:
                        product["bullet_points"].append(text)
            except:
                # 备用选择器
                try:
                    bullet_ul = self.driver.find_elements(By.CSS_SELECTOR, ".a-unordered-list.a-vertical")
                    for ul in bullet_ul:
                        items = ul.find_elements(By.TAG_NAME, "li")
                        texts = [li.text.strip() for li in items if li.text.strip() and len(li.text.strip()) > 5]
                        if len(texts) >= 3:
                            product["bullet_points"] = texts
                            break
                except:
                    pass

            # 主图
            try:
                img_selectors = [
                    "#landingImage",
                    "#imgBlkFront",
                    "[data-old-hires]",
                ]
                for selector in img_selectors:
                    try:
                        img_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        product["image_url"] = (
                            img_elem.get_attribute("data-old-hires") or
                            img_elem.get_attribute("src") or ""
                        )
                        if product["image_url"]:
                            break
                    except:
                        continue
                if "image_url" not in product:
                    product["image_url"] = ""
            except:
                product["image_url"] = ""

            # 品牌
            try:
                brand_elem = self.driver.find_element(By.ID, "bylineInfo")
                product["brand"] = brand_elem.text.strip()
            except:
                product["brand"] = ""

            # BSR
            try:
                bsr_elem = self.driver.find_element(By.ID, "SalesRank")
                match = re.search(r'#([\d,]+)', bsr_elem.text)
                product["bsr"] = match.group(1) if match else ""
            except:
                product["bsr"] = ""

            return product

        except Exception as e:
            print(f"    Error fetching product: {e}")
            return None

    def get_negative_reviews(self, asin: str, max_reviews: int = 30) -> List[Dict]:
        """获取差评（1-2星）- 使用 RPA 交互"""
        reviews = []

        # 方式1：直接访问差评页面
        review_url = f"{self.base_url}/product-reviews/{asin}/"
        params = "?reviewerType=all_reviews&filterByStar=one_star,two_star&sortBy=recent"

        print(f"  Fetching negative reviews: {asin}")

        if not self._safe_get(review_url + params):
            return reviews

        # 等待评论加载
        self.human.random_delay(context="review_page")
        self.human.human_scroll(self.driver, scroll_times=2)

        max_pages = (max_reviews // 10) + 1  # 每页约10条评论

        for page in range(max_pages):
            if len(reviews) >= max_reviews:
                break

            try:
                # 等待评论元素出现
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-hook='review']"))
                )

                review_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-hook='review']")

                for review_elem in review_elements:
                    if len(reviews) >= max_reviews:
                        break

                    try:
                        review = {"asin": asin}

                        # 评分
                        try:
                            rating_elem = review_elem.find_element(By.CSS_SELECTOR, "[data-hook='review-star-rating']")
                            match = re.search(r'(\d)', rating_elem.text)
                            rating = match.group(1) if match else ""
                            # 只保留1-2星
                            if rating not in ["1", "2"]:
                                continue
                            review["rating"] = rating
                        except:
                            continue

                        # 标题
                        try:
                            title_elem = review_elem.find_element(By.CSS_SELECTOR, "[data-hook='review-title']")
                            review["title"] = title_elem.text.strip()
                        except:
                            review["title"] = ""

                        # 内容
                        try:
                            body_elem = review_elem.find_element(By.CSS_SELECTOR, "[data-hook='review-body']")
                            review["body"] = body_elem.text.strip()
                        except:
                            review["body"] = ""

                        # 日期
                        try:
                            date_elem = review_elem.find_element(By.CSS_SELECTOR, "[data-hook='review-date']")
                            review["date"] = date_elem.text.strip()
                        except:
                            review["date"] = ""

                        # 验证购买
                        try:
                            review_elem.find_element(By.CSS_SELECTOR, "[data-hook='avp-badge']")
                            review["verified"] = True
                        except:
                            review["verified"] = False

                        # 有用数
                        try:
                            helpful_elem = review_elem.find_element(By.CSS_SELECTOR, "[data-hook='helpful-vote-statement']")
                            match = re.search(r'(\d+)', helpful_elem.text)
                            review["helpful"] = match.group(1) if match else "0"
                        except:
                            review["helpful"] = "0"

                        # 去重
                        if review["body"] and review not in reviews:
                            reviews.append(review)

                    except Exception as e:
                        continue

                # 尝试点击下一页
                if len(reviews) < max_reviews and page < max_pages - 1:
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, ".a-pagination .a-last a")
                        if next_button:
                            self.human.human_click(self.driver, next_button)
                            self.human.random_delay(context="review_page")
                            self.human.human_scroll(self.driver, scroll_times=1)
                    except:
                        break  # 没有下一页

            except TimeoutException:
                print(f"    Timeout waiting for reviews")
                break
            except Exception as e:
                print(f"    Error fetching reviews: {e}")
                break

        print(f"    Found {len(reviews)} negative reviews")
        return reviews[:max_reviews]

    def download_image(self, asin: str, image_url: str, output_dir: str) -> Optional[str]:
        """下载商品图片"""
        if not image_url:
            return None

        try:
            import requests
            response = requests.get(image_url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            })
            if response.status_code == 200:
                img_path = os.path.join(output_dir, f"{asin}.jpg")
                with open(img_path, "wb") as f:
                    f.write(response.content)
                return img_path
        except Exception as e:
            print(f"    Error downloading image: {e}")

        return None

    def crawl(self, keyword: str, pages: int = 3, max_reviews: int = 30,
              output_dir: str = None) -> Dict:
        """完整爬取流程"""
        if output_dir is None:
            output_dir = os.path.expanduser("~/Desktop/amazon")

        os.makedirs(output_dir, exist_ok=True)

        print(f"\n{'='*60}")
        print(f"Amazon Deep Crawler V2 (Anti-Detection)")
        print(f"Keyword: {keyword}")
        print(f"Pages: {pages}")
        print(f"Max reviews per product: {max_reviews}")
        print(f"Output: {output_dir}")
        print(f"{'='*60}\n")

        try:
            # 创建浏览器
            print("[Init] Creating anti-detection browser...")
            self._create_driver()
            print("  Browser created successfully\n")

            # Step 1: 搜索获取 ASIN
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

                self.human.random_delay(context="navigation")

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

                self.human.random_delay(context="navigation")

            total_reviews = sum(len(r) for r in all_reviews.values())
            print(f"Total negative reviews collected: {total_reviews}\n")

            # Step 4: 保存数据
            print("[Step 4] Saving data...")
            self._save_data(products, all_reviews, output_dir)

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

        finally:
            self._close_driver()

    def _save_data(self, products: List[Dict], reviews: Dict, output_dir: str):
        """保存数据到文件"""
        # 保存商品 CSV
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

        # 保存完整 JSON
        json_path = os.path.join(output_dir, "products.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"  Products JSON: {json_path}")

        # 保存差评
        reviews_path = os.path.join(output_dir, "negative_reviews.json")
        with open(reviews_path, "w", encoding="utf-8") as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2)
        print(f"  Reviews JSON: {reviews_path}")

        # 保存差评 CSV
        reviews_csv_path = os.path.join(output_dir, "negative_reviews.csv")
        with open(reviews_csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["asin", "rating", "title", "body", "date", "verified", "helpful"])
            writer.writeheader()
            for asin, review_list in reviews.items():
                for r in review_list:
                    writer.writerow(r)
        print(f"  Reviews CSV: {reviews_csv_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Amazon Deep Crawler V2 - Anti-Detection Version"
    )
    parser.add_argument("keyword", help="Search keyword")
    parser.add_argument("-p", "--pages", type=int, default=3, help="Pages to crawl (default: 3)")
    parser.add_argument("-r", "--max-reviews", type=int, default=30,
                        help="Max negative reviews per product (default: 30)")
    parser.add_argument("-m", "--marketplace", default="com",
                        choices=["com", "cn", "jp", "uk", "de"],
                        help="Amazon marketplace (default: com)")
    parser.add_argument("-o", "--output", help="Output directory")
    parser.add_argument("--no-headless", action="store_true",
                        help="Run browser in visible mode (for debugging)")

    args = parser.parse_args()

    if not UC_AVAILABLE:
        print("Error: undetected-chromedriver is required!")
        print("Install with: pip3 install undetected-chromedriver --break-system-packages")
        sys.exit(1)

    crawler = AmazonCrawlerV2(
        marketplace=args.marketplace,
        headless=not args.no_headless
    )
    crawler.crawl(
        keyword=args.keyword,
        pages=args.pages,
        max_reviews=args.max_reviews,
        output_dir=args.output
    )


if __name__ == "__main__":
    main()
