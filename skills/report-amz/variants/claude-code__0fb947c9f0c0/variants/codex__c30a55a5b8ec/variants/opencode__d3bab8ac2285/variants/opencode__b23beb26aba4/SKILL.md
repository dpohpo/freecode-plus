---
name: report-amz
description: Builds Amazon research HTML reports by using jyamzon for every data-acquisition step and the US Summer Products Research 2026 frontend only for rendering. Use when the user says /report-amz, asks to combine /jyamzon crawler data with /us-summer-products-research-2026 HTML, or wants crawler-backed Amazon product reports without SellerSprite MCP.
---

# Report AMZ

Use this skill to create Amazon product-selection reports with a hard separation:

- Data acquisition: only `jyamzon` public Amazon crawler code.
- Frontend: only `us-summer-products-research-2026` HTML renderer/template.
- No Codex history, static product JSON, SellerSprite MCP, or the `us` live crawler may be used as product data.

## Quick Start

Default output is an isolated backup run directory so it will not conflict with
freecode/OpenCode runs:

```bash
/Users/poincare/.config/opencode/skills/report-amz/scripts/report_amz.sh \
  --target 60 --min-price 30 --max-price 60
```

The default detail budget is `target * 6`. If an Amazon search-result card
already exposes title, price, rating, review count, and image, the report can
use that same live public-page evidence directly; otherwise product detail
fields fall back to visible search-card fields when detail pages return HTTP
200 but parse as empty. This keeps report generation complete without
reclassifying soft detail misses as captcha/robot blocks.
Search pages use a shorter timeout than detail pages and write partial
`search_pages.partial.json`, `candidate_asins.partial.json`, and
`details.partial.json` files so slow Amazon responses are auditable while a run
is still active.

For the user's requested Desktop report folder:

```bash
/Users/poincare/.config/opencode/skills/report-amz/scripts/report_amz.sh \
  --target 60 --min-price 30 --max-price 60 \
  --desktop-name "夏季产品市场调研30美元以上产品"
```

## Output

Each run creates a unique directory:

```text
/Users/poincare/Documents/amazon/outputs/report_amz_codex_backup/run_<timestamp>_<pid>/
```

Inside it:

- `jyamzon_raw/search_pages.json`: search/category page evidence.
- `jyamzon_raw/details.json`: detail-page evidence.
- `jyamzon_raw/rejected.json`: excluded ASINs with reasons.
- `products.normalized.json`: data shaped for the `us` frontend.
- `report.html`: final rendered single-file HTML.
- `summary.json`: counts, gates, warnings, and source boundary.
  It also separates raw detail-page failure reasons from final failure reasons
  after search-card fallback.

If `--desktop-name` is used, the final HTML and evidence folder are copied into:

```text
/Users/poincare/Desktop/<desktop-name>/
```

## Commands

```bash
SKILL=/Users/poincare/.config/opencode/skills/report-amz
$SKILL/scripts/report_amz.sh --dry-run
$SKILL/scripts/report_amz.sh --target 10 --min-price 30 --max-price 60
$SKILL/scripts/report_amz.sh --mode new-releases --target 60 --min-price 30 --max-price 60
$SKILL/scripts/report_amz.sh --target 60 --min-price 30 --max-price 60 --max-pages 120 --max-details 80
$SKILL/scripts/report_amz.sh --install-all
```

## Modes

- `search` (default): Keyword search via `jyamzon` category crawler. Uses `DEFAULT_SEEDS` or `--seed-file`.
- `new-releases`: Crawl Amazon New Releases (`/gp/new-releases/`) category pages. Uses built-in `NEW_RELEASES_SEEDS` covering Sports & Outdoors, Patio Lawn & Garden, Home & Kitchen, Toys & Games, Pet Supplies, Fashion, Tools, Automotive, Baby, Beauty, Health, Office, and Grocery. No URL-level price filter — price filtering happens during detail processing, so `max_candidates` is set to `target * 8`.

### New Releases Usage

```bash
/Users/poincare/.config/opencode/skills/report-amz/scripts/report_amz.sh \
  --mode new-releases --target 60 --min-price 30 --max-price 60 \
  --desktop-name "亚马逊新品榜夏季产品调研"
```

## Rules

- All network fetches must go through `jyamzon`'s `Amazon3CBsrCrawler`.
- The script may import `jyamzon` crawler classes, but must not write into the shared `jyamzon` repo's `data/` or `outputs/` directories.
- Use `us-summer-products-research-2026/scripts/render_report.js` only after `products.normalized.json` has been created from jyamzon evidence.
- Do not call any `us-summer-products-research-2026/scripts/us_summer_6b.sh run`; that would use the `us` data crawler and violate this skill.
- Public Amazon pages do not prove search volume, true sales, PPC, or conversion. Keep those fields as estimates or `0` and preserve the boundary in `summary.json`.
- Stop or report blockers when Amazon returns captcha/robot pages; do not silently substitute archived data.

## Deduplication

- **Same product, different variant (color/size/pack) MUST be treated as duplicates.** The `title_signature()` function strips variant words (colors, sizes, pack counts, dimensions) and matches on brand + first 14 meaningful title tokens. Products with matching signatures are rejected with reason `duplicate_title_family`.
- **Each seed (keyword or category) contributes at most `--max-products-per-seed` (default 2) products.**  
- **Each brand contributes at most `--max-products-per-brand` (default 3) products.**
- These rules prevent the same product appearing multiple times in the final HTML report, even if crawled from different search queries or categories.

## Validation

Before reporting completion:

```bash
/Users/poincare/.config/opencode/skills/report-amz/scripts/report_amz.sh --verify
```

For a live smoke test:

```bash
/Users/poincare/.config/opencode/skills/report-amz/scripts/report_amz.sh \
  --target 2 --min-price 30 --max-price 60 --max-pages 4 --max-details 2
```

Report the final HTML path, run directory, product count, rejected count, and any captcha/block failures.
