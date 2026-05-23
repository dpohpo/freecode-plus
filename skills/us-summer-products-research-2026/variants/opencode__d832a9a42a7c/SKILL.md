---
name: us-summer-products-research-2026
description: Generates the exact single-file HTML format and report-ready product data model of the US summer products selection report, including Chinese labels, cards, filters, expand/collapse interactions, category schema, economics fields, keyword fields, pain points, and differentiation notes. Use when the user mentions us-summer-products-research-2026, 美国夏季热销产品调研报告, summer products report, or asks to output the same product-selection HTML/data format.
---

# US Summer Products Research 2026

Use this skill to reproduce the user's Desktop report format and run fresh Amazon
summer product research. For weak or slow agents such as free-code/freeglm, do
not manually reason through the HTML, CSS, or product rows. Run the 6.0b script
and report the JSON output.

```text
/Users/poincare/Desktop/us-summer-products-research-2026.html
```

The report format is a standalone UTF-8 HTML file with embedded CSS, embedded
JavaScript, and inline product data. Research data must come from the live
Amazon crawler, not from Codex history or the archived template product JSON.

## 6.0b Quick Start

Install the browser runtime once if Playwright is missing:

```bash
/Users/poincare/.config/opencode/skills/us-summer-products-research-2026/scripts/us_summer_6b.sh install-deps
```

Primary live-crawl command for free-code/OpenCode/Claude Code/Codex:

```bash
/Volumes/金阳/brain/scripts/us-summer-products-research-2026.sh \
  --out /Users/poincare/Desktop/us-summer-products-research-2026-live-amazon.html \
  --min-price 10 --max-price 40 --target 60
```

If the global wrapper is unavailable, run the local skill runner:

```bash
/Users/poincare/.config/opencode/skills/us-summer-products-research-2026/scripts/us_summer_6b.sh run \
  --out /Users/poincare/Desktop/us-summer-products-research-2026-live-amazon.html \
  --min-price 10 --max-price 40 --target 60
```

Verify the whole skill before reporting success:

```bash
/Users/poincare/.config/opencode/skills/us-summer-products-research-2026/scripts/us_summer_6b.sh verify
```

The live crawler writes `amazon-live-raw.json`, `amazon-live-evidence.jsonl`,
`products.normalized.json`, and `summary.json` under `--out-dir`.

Expected live success facts:

```json
{"products":">= target unless Amazon blocked","badPrice":0,"source":"amazon_live_playwright"}
```

## 6.0b Rules

- Default `run` must crawl Amazon pages with Playwright on every execution.
- Do not use `references/products.json` or Codex conversation history as market data.
- `demo-run` is only for formatting regression tests, not product research.
- Do not ask the model to invent products interactively.
- Do not ask the model to rewrite HTML by hand.
- Do not call web search or SellerSprite unless the user explicitly asks for a fresh data refresh.
- Do not change CSS, labels, category keys, or product data shape.
- Do not continue if `badPrice` or `incomplete` is non-zero.
- Use `references/6b-contract.md` as the weak-model command contract.

## Assets

- Exact source template: `assets/source-report.html`
- Archived template product data, format only: `references/products.json`
- Extracted category and tag counts: `references/categories.json`
- Data schema and normalization rules: `references/data-spec.md`
- Weak-model command contract: `references/6b-contract.md`
- Full machine-readable frontend inventory: `references/frontend-inventory.json`
- Human-readable frontend contract: `references/frontend-spec.md`
- 6.0b runner: `scripts/us_summer_6b.sh`
- Live Amazon crawler: `scripts/live_amazon_crawl.js`
- Data normalizer: `scripts/normalize_products.js`
- Legacy static demo data builder: `scripts/build_us_summer_lowrisk_2026_data.js`
- Legacy one-command report runner: `scripts/make_lowrisk_report.sh`
- Generator: `scripts/render_report.js`
- Analyzer/refresher: `scripts/analyze_frontend.js`

## Script Subcommands

Use these instead of manual handling:

```bash
SKILL=/Users/poincare/.config/opencode/skills/us-summer-products-research-2026
$SKILL/scripts/us_summer_6b.sh install-deps
$SKILL/scripts/us_summer_6b.sh run --out /Users/poincare/Desktop/us-summer-products-research-2026-live-amazon.html --min-price 10 --max-price 40 --target 60
$SKILL/scripts/us_summer_6b.sh demo-run --out /tmp/us-summer-products-demo.html
$SKILL/scripts/us_summer_6b.sh copy-original --out /Users/poincare/Desktop/us-summer-products-research-2026-copy.html
$SKILL/scripts/us_summer_6b.sh normalize-render --input /absolute/path/raw-products.json --out /Users/poincare/Desktop/us-summer-products-research-2026-new.html
$SKILL/scripts/us_summer_6b.sh render-data --data /absolute/path/products.normalized.json --out /Users/poincare/Desktop/us-summer-products-research-2026-new.html
$SKILL/scripts/us_summer_6b.sh install-all
```

`install-all` syncs this skill into Codex, Claude Code, OpenCode/free-code, and
the global wrapper at `/Volumes/金阳/brain/scripts/us-summer-products-research-2026.sh`.

## Output Contract

Preserve these unless the user explicitly asks to change them:

- Single `.html` file.
- Chinese interface labels.
- Header gradient, stat cards, pill filters, search box, category sections, card grid, expandable detail panels, profit bar, footer.
- Product data embedded as `const P=[...]`.
- Functions: `filterCat`, `searchProducts`, `toggleDetail`, `toggleCat`, `renderProducts`, `renderCard`, `formatNum`.
- Category order comes from first appearance in product data.
- Product count is set from `P.length` at runtime.

## Data Contract

The ideal result uses the same data shape as the original `const P` array. Each product row must keep these fields:

```text
id, cat, name, en, price, range, rating, reviews, bsr,
kw, sv, cost, fba, refRate, sales, revenue, revGrowth,
sellers, amazSelf, season, peakMon, imgs, aplus, video,
pains, improve, tags, margin
```

Rules:

- `kw` and `sv` are parallel arrays; show the first five keyword/search-volume pairs.
- Amazon crawl does not provide true keyword search volume; keep unknown volumes as `0` unless separately enriched.
- `tags` supports `hot`, `new`, `trend`; `tag-warn` style exists but the source data does not use it.
- `improve` must render as text. If raw data contains multiple ideas, join them with `+`.
- `cat` should match an existing key in the category maps unless the user wants a new category.
- `margin` exists in the source data but is not rendered; preserve it if present.
- Use `references/data-spec.md` before creating or transforming product rows.
- Use `scripts/normalize_products.js` when source data comes from another scraper, spreadsheet export, or agent.

## Frontend Reference

Before modifying the template, read `references/frontend-spec.md`. If exact CSS selectors, event handlers, labels, or category counts matter, inspect `references/frontend-inventory.json` instead of guessing.

## Validation

Run the combined verifier before reporting completion:

```bash
/Users/poincare/.config/opencode/skills/us-summer-products-research-2026/scripts/us_summer_6b.sh verify
```

`verify` checks script syntax, source-template copy, demo rendering, and live
crawler dry-run. It does not claim Amazon live success. For final research, run
`run` and report the output path, product count, raw evidence path, `badPrice`,
`incomplete`, and any Amazon block/captcha failures from `summary.json`.
