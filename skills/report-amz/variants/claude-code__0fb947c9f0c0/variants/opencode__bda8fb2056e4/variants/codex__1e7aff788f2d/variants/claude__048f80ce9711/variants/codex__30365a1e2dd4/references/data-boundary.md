# Data Boundary

`report-amz` is a composition skill, not a new crawler stack.

## Allowed For Data

- Importing and using `Amazon3CBsrCrawler` from the local `jyamzon` repo.
- Fetching Amazon public search/category/detail pages through that crawler.
- Reading crawler-produced evidence written inside the isolated run directory.
- Deriving estimates from observed crawler fields when the estimate is explicitly labeled.

## Not Allowed For Data

- `references/products.json` from `us-summer-products-research-2026`.
- Codex/Claude/freeglm conversation history.
- `us-summer-products-research-2026/scripts/live_amazon_crawl.js`.
- SellerSprite MCP/API unless the user explicitly asks for an enrichment step outside this skill.
- Handwritten product facts with no evidence row.

## Allowed For Frontend

- `us-summer-products-research-2026/scripts/render_report.js`.
- `us-summer-products-research-2026/assets/source-report.html`.
- `us-summer-products-research-2026/references/frontend-spec.md`.

## Known Limits

Public Amazon pages can usually provide title, visible price, rating, review
count, image URL, product URL, category source, rank-on-page, bullets, and
sometimes BSR text. They do not reliably provide true monthly search volume,
PPC, conversion rate, exact monthly unit sales, seller-country distribution, or
profit. The report must preserve that boundary.
