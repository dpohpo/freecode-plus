# Data Contract

The report is only "the same file" when product rows follow the original `const P` shape. The UI is generic, but the visible card quality depends on the data fields below.

## Product Row Shape

Required display fields:

- `id`: numeric sequence.
- `cat`: one of `sports`, `water`, `garden`, `party`, `ball`, `toy`, `apparel`, `electronics`, `pet`, `home`.
- `name`: short display name with Chinese in parentheses, for example `Yoga Mat (瑜伽垫)`.
- `en`: Amazon-style English title/subtitle.
- `price`: current representative sale price, numeric USD.
- `range`: visible market price range, for example `$13.99-$29.99`.
- `rating`: numeric star rating.
- `reviews`: total review count.
- `bsr`: BSR/category rank text.
- `kw`: top five English keywords.
- `sv`: parallel monthly search volume estimates for `kw`.
- `cost`: estimated 1688/unit sourcing cost in USD.
- `fba`: estimated FBA fee in USD.
- `refRate`: referral commission percent, usually `15`.
- `sales`: estimated monthly units.
- `revenue`: estimated monthly revenue.
- `revGrowth`: annual or seasonal growth percent.
- `sellers`: approximate active seller count.
- `amazSelf`: boolean Amazon self-operated flag.
- `season`: short seasonality text.
- `peakMon`: peak month text.
- `imgs`: listing image count.
- `aplus`: boolean A+ page flag.
- `video`: boolean product video flag.
- `pains`: up to five review pain points in Chinese.
- `improve`: Chinese differentiation opportunity, usually joined with `+`.
- `tags`: any of `hot`, `new`, `trend`.

Archived field:

- `margin` exists in the original data but is not used by `renderCard`. Preserve it if present; otherwise the normalizer derives it from unit economics.

## Source Alignment

The original report mixes observed marketplace facts and model estimates. Keep that boundary explicit:

- Observed or externally collected: product title, visible category/rank, rating, reviews, image count, A+ flag, video flag, Amazon self-operated signal, common keywords.
- Estimated/modelled: search volumes, monthly sales, monthly revenue, 1688 cost, FBA fee, referral fee, growth, seller count, pain point summary, differentiation idea.
- If a value is unknown, prefer a conservative placeholder such as `待验证` for text and `0` only when the field is not critical. For ideal reports, do not leave core economics or demand fields at `0`.

## Category Mapping

Incoming Chinese category labels should normalize to:

- `运动健身` / `户外运动健身` -> `sports`
- `游泳水上` / `游泳和水上用品` -> `water`
- `园艺工具` / `庭院和园艺工具` -> `garden`
- `派对用品` / `派对和季节性用品` -> `party`
- `球类运动` -> `ball`
- `玩具` / `玩具和益智` -> `toy`
- `服饰配件` / `户外服饰配件` -> `apparel`
- `户外电子` / `户外电子/小工具` -> `electronics`
- `宠物用品` / `宠物用品(非食品)` -> `pet`
- `家居装饰` / `家居个护` -> `home`

## Normalization Script

Use `scripts/normalize_products.js` when rows come from another scraper, spreadsheet export, or agent output:

```bash
/Users/poincare/.codex/skills/us-summer-products-research-2026/scripts/normalize_products.js \
  --input /absolute/path/raw-products.json \
  --out /tmp/products.normalized.json \
  --strict
```

Supported inputs:

- JSON array.
- JSON object with `products` or `rows`.
- UTF-8 CSV with headers.

Accepted aliases include Chinese headers such as `产品名称`, `英文标题`, `售价`, `价格区间`, `评分`, `评论数`, `1688采购`, `FBA配送费`, `月销量`, `月销售额`, `需求趋势`, `峰值月份`, `核心痛点`, `差异化机会`, and `标签`.

For keywords/search volumes, either provide arrays `kw` and `sv`, delimited strings, or paired columns:

```text
kw1, sv1, kw2, sv2, kw3, sv3, kw4, sv4, kw5, sv5
关键词1, 搜索量1, ...
```

Delimited list fields support `|`, comma, Chinese comma, semicolon, Chinese semicolon, or newline.

## Ideal Data Quality

Use this checklist before rendering a final report:

- Every product has five keywords and five matching search volume values.
- Every product has at least three pain points and one concrete improvement path.
- `price`, `cost`, `fba`, `sales`, and `revenue` are non-zero.
- `tags` are used sparingly: `hot` for high demand, `new` for emerging/easier-entry ideas, `trend` for clear trend or evergreen velocity.
- `range` uses visible USD format and not raw numeric intervals.
- `name` stays compact; long explanatory text belongs in `en`, `pains`, or `improve`.

## End-To-End Rendering

```bash
SKILL=/Users/poincare/.codex/skills/us-summer-products-research-2026
$SKILL/scripts/normalize_products.js --input raw.csv --out /tmp/products.json --strict
$SKILL/scripts/render_report.js --data /tmp/products.json --out /Users/poincare/Desktop/us-summer-products-research-2026-new.html --force-render
```

The final visible result should match the original card structure, labels, colors, and interactions even when the product list changes.
