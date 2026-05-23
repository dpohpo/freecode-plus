# 6.0b Contract

The weak/slow-agent contract is: do not reason through the report manually and
do not reuse historical product data. Run the live crawler, then report the JSON
plus output path.

## Install Browser Runtime

Run once if Playwright is missing:

```bash
/Users/poincare/.config/opencode/skills/us-summer-products-research-2026/scripts/us_summer_6b.sh install-deps
```

## Primary Command

```bash
/Volumes/金阳/brain/scripts/us-summer-products-research-2026.sh \
  --out /Users/poincare/Desktop/us-summer-products-research-2026-live-amazon.html \
  --min-price 10 --max-price 40 --target 60
```

## Local Skill Command

```bash
./scripts/us_summer_6b.sh run \
  --out /Users/poincare/Desktop/us-summer-products-research-2026-live-amazon.html \
  --min-price 10 --max-price 40 --target 60
```

## Validation Command

```bash
./scripts/us_summer_6b.sh verify
```

## Expected Success JSON

```json
{
  "products": 60,
  "badPrice": 0,
  "source": "amazon_live_playwright"
}
```

Live runs also write `amazon-live-raw.json`, `amazon-live-evidence.jsonl`,
`products.normalized.json`, and `summary.json` under `--out-dir`.

## Do Not

- Do not use `references/products.json` as product research data.
- Do not use Codex or Claude conversation history as a data source.
- Do not submit `demo-run` output as final research.
- Do not ask the model to invent products interactively.
- Do not ask the model to rewrite HTML by hand.
- Do not call web search or SellerSprite unless the user explicitly asks for a fresh data refresh.
- Do not change CSS, labels, category keys, or the product data shape.
- Do not continue if `badPrice` or `incomplete` is non-zero.

## Subcommands

- `run`: live Amazon Playwright crawl plus render.
- `demo-run`: deterministic static demo only, not market research.
- `install-deps`: install Playwright runtime.
- `copy-original`: byte-for-byte source template copy.
- `normalize-render --input raw.json`: convert raw JSON/CSV rows and render.
- `render-data --data products.json`: render normalized rows.
- `verify`: syntax checks, template copy check, demo render, live crawler dry-run.
- `install-all`: sync skill copies into Codex, Claude Code, and OpenCode/free-code.
