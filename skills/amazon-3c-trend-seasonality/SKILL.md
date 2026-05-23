---
name: amazon-3c-trend-seasonality
description: Analyzes Google Trends and SellerSprite trend data for Amazon 3C product keywords, including 3-year monthly seasonality and launch timing. Use when the task asks for Google Trend, seasonal demand, 起量月份, 淡旺季, or trend validation for a 3C product.
---

# 3C Trend Seasonality

## Official Data Rule

Use SellerSprite MCP tool `google_trend`. Before calling, verify the current official parameters with:

```bash
python3 /Users/poincare/.codex/skills/sellerspirite/scripts/fetch_official_doc.py --tool google_trend
```

Known official request fields: `marketplace` required, `keyword`, `googleProp`, `monthly`.

## Workflow

1. For each keyword, call `google_trend` with `marketplace`, `keyword`, `monthly:true`, and documented `googleProp` value (`web` or `shoppingCart`) only if desired.
2. Keep raw response fields: `marketplace`, `keyword`, `link`, `items.time`, `items.value`.
3. Convert `items.time` to month. Analyze at least the latest 36 monthly points; if fewer exist, mark the result as insufficient.
4. Classify pattern:
   - Seasonal: same 2-4 months repeat as peaks in at least 2 of 3 years.
   - Rising: rolling 12-month average up by more than 15% year over year.
   - Declining: rolling 12-month average down by more than 15% year over year.
   - Stable: no repeated peak and year-over-year movement within +/-15%.
   - Spike-risk: one peak month is more than 2.5x median and not repeated.
5. Convert pattern into launch timing:
   - Launch listing and inventory 60-90 days before recurring peak.
   - Avoid buying inventory immediately after a one-off spike.

## Interpretation Discipline

Google Trends values are normalized 0-100 relative interest, not absolute search volume. Always pair this skill with `amazon-3c-keyword-opportunity` before estimating market size.

## Output Fields

`keyword`, `marketplace`, `googleProp`, `monthsCovered`, `peakMonths`, `rampMonths`, `declineMonths`, `seasonalityClass`, `trendClass`, `launchWindow`, `riskNote`, `sourceLink`.
