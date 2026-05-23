#!/usr/bin/env python3
"""Build report-ready product JSON using jyamzon crawler code only."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from bs4 import BeautifulSoup


DEFAULT_JYAMZON_REPO = Path("/Users/poincare/Documents/amazon")
BASE = "https://www.amazon.com"

SEARCH_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Upgrade-Insecure-Requests": "1",
}

NEW_RELEASES_SEEDS = [
    ("sporting-goods", "Sports & Outdoors", "运动户外"),
    ("lawn-garden", "Patio Lawn & Garden", "庭院花园"),
    ("home-garden", "Home & Kitchen", "家居厨房"),
    ("toys-and-games", "Toys & Games", "玩具游戏"),
    ("pet-supplies", "Pet Supplies", "宠物用品"),
    ("fashion", "Clothing & Accessories", "服饰配件"),
    ("hi", "Tools & Home Improvement", "家装工具"),
    ("automotive", "Automotive", "汽配用品"),
    ("baby-products", "Baby", "母婴用品"),
    ("beauty", "Beauty & Personal Care", "美妆个护"),
    ("hpc", "Health & Household", "健康家居"),
    ("office-products", "Office Products", "办公用品"),
    ("grocery", "Gourmet Food", "食品饮料"),
    ("kitchen", "Kitchen & Dining", "厨房餐厅"),
    ("garden", "Garden & Outdoor", "花园户外"),
]


DEFAULT_SEEDS = [
    ("water", "beach chair towel cover", "沙滩椅毛巾套"),
    ("water", "sand free beach blanket", "防沙沙滩毯"),
    ("water", "pool float adult", "成人泳池浮排"),
    ("water", "pool lounge float", "泳池躺椅浮床"),
    ("water", "inflatable pool float chair", "充气泳池浮椅"),
    ("water", "beach umbrella", "沙滩伞"),
    ("water", "beach tent sun shelter", "沙滩遮阳帐"),
    ("water", "beach canopy tent", "沙滩天幕帐"),
    ("water", "snorkel mask adult", "成人浮潜面罩"),
    ("water", "dry bag 10l", "防水收纳袋"),
    ("water", "swim goggles adult", "成人泳镜"),
    ("sports", "cooling towel", "冰凉运动毛巾"),
    ("sports", "pickleball paddle cover", "匹克球拍套"),
    ("sports", "pickleball paddle set", "匹克球拍套装"),
    ("sports", "agility cones set", "训练标志碟"),
    ("sports", "jump rope mat", "跳绳垫"),
    ("sports", "pop up soccer goal", "折叠足球门"),
    ("sports", "golf chipping net", "高尔夫切杆网"),
    ("sports", "portable basketball hoop", "便携篮球架"),
    ("garden", "garden hose nozzle", "花园水管喷头"),
    ("garden", "expandable garden hose 100 ft", "伸缩水管100英尺"),
    ("garden", "garden hose reel", "花园水管收纳架"),
    ("garden", "garden kneeler pad", "园艺跪垫"),
    ("garden", "rose pruning gloves", "玫瑰修剪手套"),
    ("garden", "patio umbrella cover", "庭院伞套"),
    ("garden", "patio umbrella base", "庭院伞底座"),
    ("garden", "garden tool set", "园艺工具套装"),
    ("garden", "outdoor solar garden lights", "户外太阳能庭院灯"),
    ("party", "picnic blanket waterproof", "防水野餐毯"),
    ("party", "outdoor tablecloth waterproof", "户外桌布"),
    ("party", "cooler tote bag", "软体冰包"),
    ("party", "backpack cooler", "背包冰包"),
    ("party", "picnic basket", "野餐篮"),
    ("party", "folding camping table", "折叠露营桌"),
    ("party", "camping chair", "露营椅"),
    ("party", "mesh food covers", "户外食物罩"),
    ("ball", "cornhole bags", "玉米洞沙包"),
    ("ball", "cornhole board set", "玉米洞板套装"),
    ("ball", "pickleball balls outdoor", "户外匹克球"),
    ("ball", "beach volleyball", "沙滩排球"),
    ("ball", "bocce ball set", "地滚球套装"),
    ("ball", "ladder toss balls", "梯球沙包球"),
    ("ball", "ball storage mesh bag", "球类收纳网袋"),
    ("toy", "ladder toss game", "梯球游戏"),
    ("toy", "ring toss game outdoor", "户外套圈游戏"),
    ("toy", "yard dice set", "庭院骰子"),
    ("toy", "beach paddle ball set", "沙滩拍球套装"),
    ("toy", "outdoor game set", "户外游戏套装"),
    ("toy", "giant yard pong", "庭院投杯游戏"),
    ("toy", "kids sprinkler toy", "儿童喷水玩具"),
    ("apparel", "wide brim sun hat", "宽檐遮阳帽"),
    ("apparel", "water shoes women", "女式涉水鞋"),
    ("apparel", "cooling neck gaiter", "冰感脖套"),
    ("apparel", "sun visor hat", "空顶遮阳帽"),
    ("apparel", "beach tote bag large", "大号沙滩包"),
    ("apparel", "straw beach bag", "草编沙滩包"),
    ("apparel", "beach cover up women", "女士沙滩罩衫"),
    ("electronics", "travel cable organizer", "数码旅行收纳包"),
    ("electronics", "phone sun shade", "手机遮阳罩"),
    ("electronics", "water bottle sling", "水壶斜挎包"),
    ("electronics", "backpack rain cover", "背包防雨罩"),
    ("electronics", "portable neck fan", "便携挂脖风扇"),
    ("electronics", "camping lantern rechargeable", "充电露营灯"),
    ("electronics", "outdoor bluetooth speaker waterproof", "户外防水音箱"),
    ("pet", "dog cooling mat", "狗狗凉垫"),
    ("pet", "dog car seat cover", "宠物车垫"),
    ("pet", "dog life jacket", "狗狗救生衣"),
    ("pet", "pet travel towel", "宠物速干毛巾"),
    ("pet", "dog cooling vest", "狗狗降温背心"),
    ("pet", "dog pool float", "狗狗泳池浮床"),
    ("pet", "dog travel bag", "宠物旅行包"),
    ("pet", "portable dog water bottle large", "大号便携狗水杯"),
    ("home", "outdoor rug waterproof", "户外地毯"),
    ("home", "outdoor pillow covers", "户外抱枕套"),
    ("home", "patio furniture cover", "庭院家具罩"),
    ("home", "outdoor cushion covers", "户外坐垫套"),
    ("home", "patio chair covers", "庭院椅套"),
    ("home", "outdoor patio curtains", "户外庭院窗帘"),
    ("home", "small deck box", "小型庭院储物箱"),
    ("home", "hammock with stand", "带支架吊床"),
    ("home", "hammock straps", "吊床绑带"),
]

BLOCKED_TERMS = {
    "liquid", "lotion", "gel", "cream", "drink", "juice",
    "seed", "seeds", "fertilizer", "pesticide", "repellent", "insecticide",
    "bait", "knife", "weapon", "gun", "battery", "lithium", "power bank",
    "sofa", "couch", "mattress", "gazebo", "pool pump", "chemical",
    "weed killer", "fireworks", "food", "supplement",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build report-amz data using jyamzon crawler code.")
    parser.add_argument("--jyamzon-repo", default=str(DEFAULT_JYAMZON_REPO))
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--target", type=int, default=60)
    parser.add_argument("--min-price", type=float, default=30)
    parser.add_argument("--max-price", type=float, default=60)
    parser.add_argument("--max-pages", type=int, default=80)
    parser.add_argument("--max-details", type=int, default=80)
    parser.add_argument("--max-candidates-per-seed", type=int, default=0)
    parser.add_argument("--max-products-per-seed", type=int, default=2)
    parser.add_argument("--max-products-per-brand", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--search-timeout", type=int, default=6)
    parser.add_argument("--sleep", type=float, default=0.35)
    parser.add_argument("--detail-retries", type=int, default=2)
    parser.add_argument("--retry-sleep", type=float, default=1.5)
    parser.add_argument("--seed-file")
    parser.add_argument("--candidate-file")
    parser.add_argument("--existing-details-file")
    parser.add_argument("--mode", choices=["search", "new-releases"], default="search",
                        help="Data source: keyword search or New Releases category pages")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_jyamzon(repo: Path):
    script = repo / "scripts" / "crawl_amazon_3c_bsr_new_releases.py"
    if not script.exists():
        raise FileNotFoundError(f"jyamzon crawler script not found: {script}")
    spec = importlib.util.spec_from_file_location("report_amz_jyamzon_base", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load jyamzon crawler script: {script}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_crawler(jy: Any, timeout: int, sleep: float, use_env_proxy: bool = False) -> Any:
    try:
        return jy.Amazon3CBsrCrawler(timeout=timeout, sleep=sleep, use_env_proxy=use_env_proxy)
    except TypeError:
        crawler = jy.Amazon3CBsrCrawler(timeout=timeout, sleep=sleep)
        if hasattr(crawler, "session"):
            crawler.session.trust_env = use_env_proxy
        return crawler


def configure_search_crawler(crawler: Any) -> Any:
    if hasattr(crawler, "session"):
        crawler.session.headers.update(SEARCH_HEADERS)
    return crawler


def load_seeds(seed_file: str | None) -> list[dict[str, str]]:
    if not seed_file:
        return [{"cat": cat, "query": q, "zh": zh} for cat, q, zh in DEFAULT_SEEDS]
    raw = json.loads(Path(seed_file).read_text(encoding="utf-8"))
    seeds: list[dict[str, str]] = []
    for item in raw:
        if isinstance(item, list):
            seeds.append({"cat": item[0], "query": item[1], "zh": item[2] if len(item) > 2 else item[1]})
        else:
            seeds.append({"cat": item["cat"], "query": item["query"], "zh": item.get("zh", item["query"])})
    return seeds


def search_url(query: str, min_price: float, max_price: float, page: int) -> str:
    price_gate = f"{round(min_price * 100)}-{round(max_price * 100)}"
    url = f"{BASE}/gp/aw/s?k={quote_plus(query)}&rh=p_36:{price_gate}"
    if page > 1:
        url += f"&page={page}"
    return url


def new_releases_url(slug: str, page: int) -> str:
    url = f"{BASE}/gp/new-releases/{slug}"
    if page > 1:
        url += f"?pg={page}"
    return url


def load_existing_details(path: str | None) -> dict[str, dict[str, Any]]:
    if not path:
        return {}
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    details: dict[str, dict[str, Any]] = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        asin = str(item.get("asin") or "")
        detail = item.get("detail") if isinstance(item.get("detail"), dict) else item
        if asin and isinstance(detail, dict):
            details[asin] = detail
    return details


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def first_text(root: Any, selectors: list[str]) -> str:
    for selector in selectors:
        el = root.select_one(selector)
        if not el:
            continue
        text = clean_text(el.get_text(" ", strip=True) or el.get("aria-label", "") or el.get("title", ""))
        if text:
            return text
    return ""


def extract_rating_text(text: str) -> str:
    match = re.search(r"([0-5](?:\.\d+)?)", str(text or ""))
    return match.group(1) if match else ""


def extract_count_text(text: str) -> str:
    match = re.search(r"([\d,.]+)\s*([Kk])?", str(text or ""))
    if not match:
        return ""
    value = match.group(1).replace(",", "")
    if match.group(2):
        try:
            return str(int(float(value) * 1000))
        except ValueError:
            return ""
    return value.split(".", 1)[0]


def useful_image_src(src: str) -> bool:
    lower = src.lower()
    return bool(src) and "grey-pixel" not in lower and not lower.endswith(".svg")


def search_card_hints(html: str) -> dict[str, dict[str, Any]]:
    """Recover triage fields from Amazon search result cards.

    Detail pages can occasionally return HTTP 200 pages with no product body.
    Search result cards are lower fidelity, but enough for this report's public
    crawler boundary when title/price/rating/reviews/image are visible.
    """
    soup = BeautifulSoup(html, "html.parser")
    hints: dict[str, dict[str, Any]] = {}
    for card in soup.select("[data-asin]"):
        asin = str(card.get("data-asin") or "").strip()
        if not re.fullmatch(r"[A-Z0-9]{10}", asin):
            continue
        title = first_text(card, [
            "h2 a span",
            "h2 span",
            "span.a-text-normal",
            ".a-size-base-plus.a-color-base.a-text-normal",
            ".a-size-medium.a-color-base.a-text-normal",
            "[data-cy='title-recipe'] span",
        ])
        if not title:
            link_texts = [
                clean_text(a.get_text(" ", strip=True))
                for a in card.find_all("a", href=True)
                if len(clean_text(a.get_text(" ", strip=True))) > 24
            ]
            if link_texts:
                title = max(link_texts, key=len)
        image_url = ""
        for img in card.find_all("img"):
            src = clean_text(img.get("src"))
            if useful_image_src(src):
                image_url = src
                break
        price = first_text(card, [".a-price .a-offscreen", ".a-color-base .a-offscreen"])
        rating = extract_rating_text(first_text(card, [".a-icon-alt", "span[aria-label*='out of 5']"]))
        review_count = ""
        for selector in [
            "a[href*='customerReviews'] span.a-size-base",
            "a[href*='product-reviews'] span.a-size-base",
            "a[href*='reviews'] span.a-size-base",
            "span[aria-label*='ratings']",
            "span[aria-label*='reviews']",
            ".s-underline-text",
        ]:
            el = card.select_one(selector)
            if not el:
                continue
            text = clean_text(el.get("aria-label", "") or el.get_text(" ", strip=True))
            if "out of 5" in text.lower():
                continue
            review_count = extract_count_text(text)
            if review_count:
                break
        if not review_count:
            review_count = extract_count_text(first_text(card, ["a[aria-label*='stars']", "span[aria-label*='stars']"]))
        if not review_count:
            paren = re.search(r"\(([\d,.]+\s*[Kk]?)\)", card.get_text(" ", strip=True))
            if paren:
                review_count = extract_count_text(paren.group(1))
        link = card.select_one("h2 a[href]")
        product_url = ""
        if link and link.get("href"):
            href = str(link.get("href"))
            product_url = href if href.startswith("http") else f"{BASE}{href}"
        candidate = {
            "title": title,
            "price": price,
            "rating": rating,
            "review_count": review_count,
            "image_url": image_url,
            "product_url": product_url,
            "fallback_source": "search_card",
        }
        existing = hints.get(asin, {})
        candidate_score = sum(bool(candidate.get(key)) for key in ["title", "price", "rating", "review_count", "image_url"])
        existing_score = sum(bool(existing.get(key)) for key in ["title", "price", "rating", "review_count", "image_url"])
        if candidate_score > existing_score:
            hints[asin] = candidate
    return hints


def parse_search_result(crawler: Any, jy: Any, seed: dict[str, str], url: str, html: str) -> tuple[list[str], dict[str, dict[str, Any]]]:
    if not html:
        return [], {}
    task = jy.CategoryTask("Amazon Search", seed["cat"], seed["query"], url, 0)
    asins, _children = crawler.parse_category_page(task, html)
    hints = search_card_hints(html)
    hinted = [asin for asin in asins if hints.get(asin, {}).get("title")]
    rest = [asin for asin in asins if asin not in set(hinted)]
    return hinted + rest, hints


def should_try_proxy_fallback(status: str, asins: list[str], hints: dict[str, dict[str, Any]]) -> bool:
    if status in {"captcha", "robot_check"}:
        return False
    if status != "ok":
        return True
    return not asins and not hints


def detail_quality_score(detail: dict[str, Any]) -> int:
    return sum(
        [
            bool(detail.get("title")),
            bool(parse_price(detail.get("price"))),
            bool(parse_rating(detail.get("rating"))),
            bool(parse_int(detail.get("review_count"))),
            bool(detail.get("image_url")),
        ]
    )


def detail_complete(detail: dict[str, Any]) -> bool:
    return bool(
        detail.get("title")
        and parse_price(detail.get("price"))
        and parse_rating(detail.get("rating"))
        and parse_int(detail.get("review_count"))
    )


def clone_crawler(crawler: Any) -> Any:
    return crawler.__class__(timeout=getattr(crawler, "timeout", 15), sleep=getattr(crawler, "sleep", 0.35))


def extract_detail_with_retry(crawler: Any, asin: str, existing: dict[str, Any], retries: int, retry_sleep: float) -> tuple[dict[str, Any], int]:
    if detail_complete(existing):
        return existing, 0
    best = existing if existing else {}
    attempts = max(1, retries + 1)
    for attempt in range(1, attempts + 1):
        active_crawler = crawler if attempt == 1 else clone_crawler(crawler)
        detail = active_crawler.extract_product_detail(asin)
        if detail.get("title") or not best:
            best = detail
        if detail_complete(detail):
            return detail, attempt
        time.sleep(retry_sleep * attempt)
    return best, attempts


def merge_detail_with_search_card(row: dict[str, Any], detail: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    merged = dict(detail)
    used = False
    for key in ["title", "price", "rating", "review_count", "image_url", "product_url"]:
        if not merged.get(key) and row.get(key):
            merged[key] = row.get(key)
            used = True
    if used:
        merged["fallback_source"] = row.get("fallback_source", "search_card")
        if merged.get("detail_error") == "missing_title" and merged.get("title"):
            merged["detail_error"] = ""
    return merged, used


def search_card_detail(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "asin": row.get("asin", ""),
        "product_url": row.get("product_url") or f"{BASE}/dp/{row.get('asin', '')}",
        "detail_status": "search_card_complete",
        "title": row.get("title", ""),
        "brand": row.get("brand", ""),
        "price": row.get("price", ""),
        "rating": row.get("rating", ""),
        "review_count": row.get("review_count", ""),
        "bullet_points": [],
        "image_url": row.get("image_url", ""),
        "bsr_text": "",
        "detail_error": "",
        "fallback_source": row.get("fallback_source", "search_card"),
    }


def detail_failure_reason(detail: dict[str, Any]) -> str:
    if detail_complete(detail):
        return "complete"
    status = str(detail.get("detail_status") or "")
    error = str(detail.get("detail_error") or "")
    if status in {"captcha", "robot_check", "continue_shopping", "sign_in_page"}:
        return status
    if error:
        return error.split(":", 1)[0]
    if not detail.get("title"):
        return "missing_title"
    missing = []
    if not parse_price(detail.get("price")):
        missing.append("price")
    if not parse_rating(detail.get("rating")):
        missing.append("rating")
    if not parse_int(detail.get("review_count")):
        missing.append("review_count")
    return "missing_" + "_".join(missing) if missing else "incomplete"


def parse_price(value: Any) -> float:
    text = str(value or "").replace(",", "")
    match = re.search(r"(\d+(?:\.\d{1,2})?)", text)
    return float(match.group(1)) if match else 0.0


def parse_int(value: Any) -> int:
    text = str(value or "").replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)\s*([Kk])?", text)
    if not match:
        return 0
    number = float(match.group(1))
    if match.group(2):
        number *= 1000
    return int(number)


def parse_rating(value: Any) -> float:
    text = str(value or "")
    match = re.search(r"([0-5](?:\.\d+)?)", text)
    return float(match.group(1)) if match else 0.0


def clean_brand(value: Any) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    text = re.sub(r"^visit the\s+", "", text, flags=re.I)
    text = re.sub(r"\s+store$", "", text, flags=re.I)
    return text.strip() or "Amazon seller"


VARIANT_WORDS = {
    "black", "white", "gray", "grey", "blue", "green", "red", "pink", "purple",
    "yellow", "orange", "brown", "beige", "navy", "aqua", "teal", "clear",
    "small", "medium", "large", "xl", "xxl", "pack", "pcs", "piece", "pieces",
    "set", "size", "inch", "inches", "ft", "feet", "cm", "mm", "oz", "lb", "lbs",
}


def title_signature(title: str, brand: str) -> str:
    text = re.sub(r"\b\d+(?:\.\d+)?\s*(?:x|in|inch|inches|ft|feet|cm|mm|oz|lb|lbs|pack|pcs|piece|pieces)\b", " ", title.lower())
    text = re.sub(r"[^a-z0-9]+", " ", text)
    tokens = []
    for token in text.split():
        if token in VARIANT_WORDS or token.isdigit():
            continue
        tokens.append(token)
    return f"{clean_brand(brand).lower()}|" + " ".join(tokens[:14])


def product_name(row: dict[str, Any], detail: dict[str, Any]) -> str:
    query = row.get("query", "")
    zh = row.get("zh", query)
    brand = clean_brand(detail.get("brand"))
    title = str(detail.get("title") or "")
    words = re.sub(r"[^A-Za-z0-9]+", " ", title).strip().split()
    short = " ".join(words[:5])
    if brand != "Amazon seller":
        return f"{zh} | {brand}"
    if short:
        return f"{zh} | {short}"
    return f"{zh} ({query})"


def allowed_text(title: str, category: str) -> tuple[bool, str]:
    blob = f"{title} {category}".lower()
    for term in sorted(BLOCKED_TERMS):
        if term in blob:
            return False, f"blocked_term:{term}"
    return True, ""


def estimate_sales(review_count: int, rank_on_page: int) -> int:
    review_signal = min(9000, max(100, round(review_count * 0.07)))
    rank_signal = max(80, round(2600 / math.sqrt(max(rank_on_page, 1))))
    return max(60, round((review_signal + rank_signal) / 2))


def product_row(row: dict[str, Any], detail: dict[str, Any], idx: int, min_price: float, max_price: float) -> dict[str, Any]:
    title = detail.get("title") or row.get("title") or row.get("asin", "")
    price = parse_price(detail.get("price")) or parse_price(row.get("price"))
    rating = parse_rating(detail.get("rating")) or parse_rating(row.get("rating"))
    reviews = parse_int(detail.get("review_count")) or parse_int(row.get("review_count"))
    sales = estimate_sales(reviews, int(row.get("rank_on_page", 1) or 1))
    cost = round(price * 0.30, 2)
    fba = round(max(3.19, min(9.5, price * 0.16)), 2)
    ref_rate = 15
    margin = round((price - cost - fba - price * ref_rate / 100 - cost * 0.15) / price * 100) if price else 0
    query = row.get("query", "")
    bullets = [row.get(f"bullet_{i}", "") for i in range(1, 6)]
    bullets = [x for x in bullets if x] or detail.get("bullet_points", []) or []
    return {
        "id": idx,
        "cat": row.get("cat", "home"),
        "name": product_name(row, detail),
        "en": title[:150],
        "price": price,
        "range": f"${min_price:.2f}-${max_price:.2f}",
        "rating": rating,
        "reviews": reviews,
        "bsr": detail.get("bsr_text") or f"Amazon rank {row.get('rank_on_page')} for {query}",
        "kw": [query, f"{query} amazon", f"{query} summer", f"outdoor {query}", f"{query} {datetime.now().year}"],
        "sv": [0, 0, 0, 0, 0],
        "cost": cost,
        "fba": fba,
        "refRate": ref_rate,
        "margin": margin,
        "sales": sales,
        "revenue": round(price * sales),
        "revGrowth": 0,
        "sellers": 0,
        "amazSelf": False,
        "season": "夏季候选；需求强度来自 jyamzon 抓取的 Amazon 搜索/排名信号，趋势需另行验证",
        "peakMon": "5-8月待验证",
        "imgs": 1 if detail.get("image_url") else 0,
        "aplus": False,
        "video": False,
        "pains": ["公开页面未抓评论正文", "同质化竞争需复核", "价格和BSR需持续监控"],
        "improve": "基于公开页面标题/五点做差异化+补充评论抓取+供应链报价复核",
        "tags": ["trend"],
        "evidence": {
            "source": "jyamzon",
            "asin": row.get("asin", ""),
            "product_url": detail.get("product_url") or f"{BASE}/dp/{row.get('asin', '')}",
            "category_url": row.get("category_url", ""),
            "search_url": row.get("search_url", ""),
            "observed_at": row.get("observed_at", ""),
            "rank_on_page": row.get("rank_on_page", ""),
        },
        "bullet_points": bullets,
    }


def main() -> int:
    args = parse_args()
    repo = Path(args.jyamzon_repo).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    raw_dir = out_dir / "jyamzon_raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    seeds = load_seeds(args.seed_file)
    is_new_releases = args.mode == "new-releases"
    if is_new_releases and not args.seed_file:
        seeds = [{"cat": slug, "query": slug, "zh": zh} for slug, _en, zh in NEW_RELEASES_SEEDS]
    observed_at = datetime.now(timezone.utc).isoformat()

    if args.dry_run:
        write_json(out_dir / "seed-plan.json", {"observed_at": observed_at, "repo": str(repo), "seeds": seeds, "mode": args.mode})
        print(json.dumps({"ok": True, "dry_run": True, "out_dir": str(out_dir), "seeds": len(seeds), "mode": args.mode}, ensure_ascii=False, indent=2))
        return 0

    jy = load_jyamzon(repo)
    if is_new_releases:
        search_crawler = make_crawler(jy, timeout=args.search_timeout, sleep=args.sleep)
        proxy_search_crawler = make_crawler(jy, timeout=args.search_timeout, sleep=args.sleep, use_env_proxy=True)
    else:
        search_crawler = configure_search_crawler(make_crawler(jy, timeout=args.search_timeout, sleep=args.sleep))
        proxy_search_crawler = configure_search_crawler(make_crawler(jy, timeout=args.search_timeout, sleep=args.sleep, use_env_proxy=True))
    detail_crawler = make_crawler(jy, timeout=args.timeout, sleep=args.sleep)
    proxy_detail_crawler = make_crawler(jy, timeout=args.timeout, sleep=args.sleep, use_env_proxy=True)
    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    pages: list[dict[str, Any]] = []
    seen: set[str] = set()

    if args.candidate_file:
        selected = json.loads(Path(args.candidate_file).read_text(encoding="utf-8"))
        selected = [row for row in selected if isinstance(row, dict) and row.get("asin")]
        per_seed_candidate_cap = 0
        pages.append({
            "source": "candidate_file",
            "path": str(Path(args.candidate_file).expanduser().resolve()),
            "asin_count": len(selected),
            "observed_at": observed_at,
        })
    else:
        max_candidates = min(args.max_details, max(args.target * (20 if is_new_releases else 3), args.target))
        per_seed_candidate_cap = args.max_candidates_per_seed
        if per_seed_candidate_cap <= 0:
            per_seed_candidate_cap = max(3, math.ceil(max_candidates / max(len(seeds), 1)))
        seed_candidate_counts: Counter[str] = Counter()

        for page_num in range(1, args.max_pages + 1):
            if len(selected) >= max_candidates:
                break
            active_seed_count = 0
            for seed in seeds:
                if len(selected) >= max_candidates:
                    break
                seed_key = seed["query"]
                if seed_candidate_counts[seed_key] >= per_seed_candidate_cap:
                    continue
                active_seed_count += 1
                if is_new_releases:
                    url = new_releases_url(seed["query"], page_num)
                else:
                    url = search_url(seed["query"], args.min_price, args.max_price, page_num)
                html, status = search_crawler.fetch(url)
                asins, hints = parse_search_result(search_crawler, jy, seed, url, html)
                fetch_mode = "direct"
                if should_try_proxy_fallback(status, asins, hints):
                    proxy_html, proxy_status = proxy_search_crawler.fetch(url)
                    proxy_asins, proxy_hints = parse_search_result(proxy_search_crawler, jy, seed, url, proxy_html)
                    if len(proxy_asins) > len(asins) or (
                        status != "ok" and proxy_status == "ok"
                    ) or (not hints and proxy_hints):
                        html, status = proxy_html, proxy_status
                        asins, hints = proxy_asins, proxy_hints
                        fetch_mode = "env_proxy_fallback"
                pages.append({
                    "seed": seed,
                    "url": url,
                    "status": status,
                    "fetch_mode": fetch_mode,
                    "asin_count": len(asins),
                    "card_hint_count": len(hints),
                    "observed_at": observed_at,
                })
                if status in {"captcha", "robot_check"}:
                    rejected.append({"seed": seed, "url": url, "reject_reason": status})
                    continue
                for rank, asin in enumerate(asins, start=1):
                    if len(selected) >= max_candidates or seed_candidate_counts[seed_key] >= per_seed_candidate_cap:
                        break
                    if asin in seen:
                        continue
                    seen.add(asin)
                    seed_candidate_counts[seed_key] += 1
                    hint = hints.get(asin, {})
                    selected.append({
                        **seed,
                        **hint,
                        "asin": asin,
                        "rank_on_page": rank,
                        "category_url": url,
                        "search_url": url,
                        "observed_at": observed_at,
                    })
                if len(pages) % 10 == 0:
                    write_json(raw_dir / "search_pages.partial.json", pages)
                    write_json(raw_dir / "candidate_asins.partial.json", selected)
                    print(
                        f"Search pages {len(pages)}; candidates={len(selected)}; last_status={status}",
                        flush=True,
                    )
                time.sleep(args.sleep)
            if active_seed_count == 0:
                break

    details: list[dict[str, Any]] = []
    products: list[dict[str, Any]] = []
    product_seed_counts: Counter[str] = Counter()
    product_brand_counts: Counter[str] = Counter()
    product_signatures: set[str] = set()
    existing_details = load_existing_details(args.existing_details_file)
    detail_retry_counts: Counter[str] = Counter()
    raw_detail_failure_counts: Counter[str] = Counter()
    final_detail_failure_counts: Counter[str] = Counter()
    search_card_fallback_count = 0
    search_card_only_count = 0
    price_pre_filter_count = 0
    for row in selected[: args.max_details]:
        # Price pre-filter: skip detail fetch when search card price is clearly out of range
        # This is critical for new-releases mode where URL-level price filter is unavailable
        if is_new_releases:
            card_hint_price = parse_price(row.get("price"))
            if card_hint_price > 0 and (card_hint_price < args.min_price or card_hint_price > args.max_price):
                rejected.append({**row, "reject_reason": f"price_pre_filter:{card_hint_price}"})
                price_pre_filter_count += 1
                continue
        card_detail = search_card_detail(row)
        if detail_complete(card_detail):
            detail = card_detail
            retry_count = 0
            search_card_only_count += 1
        else:
            detail, retry_count = extract_detail_with_retry(
                detail_crawler,
                row["asin"],
                existing_details.get(row["asin"], {}),
                args.detail_retries,
                args.retry_sleep,
            )
            detail_fetch_mode = "direct"
            if not detail_complete(detail):
                proxy_detail, proxy_retry_count = extract_detail_with_retry(
                    proxy_detail_crawler,
                    row["asin"],
                    {},
                    args.detail_retries,
                    args.retry_sleep,
                )
                if detail_quality_score(proxy_detail) > detail_quality_score(detail):
                    detail = proxy_detail
                    retry_count = f"{retry_count}+proxy:{proxy_retry_count}"
                    detail_fetch_mode = "env_proxy_fallback"
        if detail.get("detail_status") == "search_card_complete":
            detail_fetch_mode = "search_card"
        detail_retry_counts[str(retry_count)] += 1
        raw_detail_failure_counts[detail_failure_reason(detail)] += 1
        merged_detail, used_search_card_fallback = merge_detail_with_search_card(row, detail)
        final_detail_failure_counts[detail_failure_reason(merged_detail)] += 1
        if used_search_card_fallback:
            search_card_fallback_count += 1
        detail_record = {
            "asin": row["asin"],
            "detail": detail,
            "merged_detail": merged_detail if used_search_card_fallback else {},
            "used_search_card_fallback": used_search_card_fallback,
            "detail_fetch_mode": detail_fetch_mode,
            "observed_at": observed_at,
            "retry_count": retry_count,
        }
        details.append(detail_record)
        if len(details) % 10 == 0:
            write_json(raw_dir / "details.partial.json", details)
            write_json(raw_dir / "rejected.partial.json", rejected)
            print(
                f"Details {len(details)}; products={len(products)}; rejected={len(rejected)}; pre_filter={price_pre_filter_count}; sc_only={search_card_only_count}",
                flush=True,
            )
        price = parse_price(merged_detail.get("price"))
        rating = parse_rating(merged_detail.get("rating"))
        reviews = parse_int(merged_detail.get("review_count"))
        allowed, reason = allowed_text(merged_detail.get("title", ""), row.get("query", ""))
        if not merged_detail.get("title"):
            rejected.append({**row, "reject_reason": merged_detail.get("detail_error") or "missing_title"})
            continue
        seed_key = row.get("query", "")
        brand_name = clean_brand(merged_detail.get("brand"))
        brand_key = "" if brand_name.lower() == "amazon seller" else brand_name.lower()
        signature = title_signature(merged_detail.get("title", ""), merged_detail.get("brand", ""))
        if product_seed_counts[seed_key] >= args.max_products_per_seed:
            rejected.append({**row, "reject_reason": f"seed_product_cap:{args.max_products_per_seed}", "detail": merged_detail})
            continue
        if brand_key and product_brand_counts[brand_key] >= args.max_products_per_brand:
            rejected.append({**row, "reject_reason": f"brand_product_cap:{args.max_products_per_brand}", "detail": merged_detail})
            continue
        if signature in product_signatures:
            rejected.append({**row, "reject_reason": "duplicate_title_family", "detail": merged_detail})
            continue
        if price < args.min_price or price > args.max_price:
            rejected.append({**row, "reject_reason": f"price_out_of_range:{price}", "detail": merged_detail})
            continue
        if not allowed:
            rejected.append({**row, "reject_reason": reason, "detail": merged_detail})
            continue
        if not rating or not reviews:
            rejected.append({**row, "reject_reason": "missing_rating_or_reviews", "detail": merged_detail})
            continue
        products.append(product_row(row, merged_detail, len(products) + 1, args.min_price, args.max_price))
        product_seed_counts[seed_key] += 1
        product_brand_counts[brand_key] += 1
        product_signatures.add(signature)
        if len(products) >= args.target:
            break
        time.sleep(args.sleep)

    write_json(raw_dir / "search_pages.json", pages)
    write_json(raw_dir / "candidate_asins.json", selected)
    write_json(raw_dir / "details.json", details)
    write_json(raw_dir / "rejected.json", rejected)
    write_json(out_dir / "products.normalized.json", products)
    evidence_lines = [json.dumps(product["evidence"], ensure_ascii=False) for product in products]
    (raw_dir / "evidence.jsonl").write_text("\n".join(evidence_lines) + ("\n" if evidence_lines else ""), encoding="utf-8")
    summary = {
        "ok": True,
        "mode": args.mode,
        "source": "jyamzon",
        "frontend": "us-summer-products-research-2026",
        "observed_at": observed_at,
        "jyamzon_repo": str(repo),
        "out_dir": str(out_dir),
        "target": args.target,
        "products": len(products),
        "candidate_asins": len(selected),
        "rejected": len(rejected),
        "search_pages": len(pages),
        "seed_count": len(seeds),
        "seed_candidate_cap": per_seed_candidate_cap,
        "search_timeout": args.search_timeout,
        "detail_timeout": args.timeout,
        "detail_retry_counts": dict(detail_retry_counts),
        "search_fetch_modes": dict(Counter(page.get("fetch_mode", "unknown") for page in pages)),
        "detail_fetch_modes": dict(Counter(item.get("detail_fetch_mode", "unknown") for item in details)),
        "raw_detail_failure_reasons": dict(raw_detail_failure_counts),
        "final_detail_failure_reasons": dict(final_detail_failure_counts),
        "search_card_fallback_count": search_card_fallback_count,
        "search_card_only_count": search_card_only_count,
        "price_pre_filter_count": price_pre_filter_count,
        "category_counts": dict(Counter(product.get("cat", "") for product in products)),
        "query_counts": dict(Counter(product.get("kw", [""])[0] for product in products)),
        "reject_reasons": dict(Counter(str(item.get("reject_reason", "unknown")).split(":")[0] for item in rejected)),
        "price_gate": {"min": args.min_price, "max": args.max_price},
        "data_boundary": "Amazon public pages via jyamzon crawler. Search volume, sales, revenue, sourcing cost, FBA, seller count, trend and pain points are estimates or placeholders unless separately enriched.",
    }
    write_json(out_dir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if products else 2


if __name__ == "__main__":
    raise SystemExit(main())
