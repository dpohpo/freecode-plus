---
name: amazon-3c-traffic-expansion
description: Maps 3C traffic entry and expansion opportunities using SellerSprite reverse ASIN keywords, related traffic, and bundle/adjacent-product signals. Use when analyzing traffic_keyword, traffic_listing, related products, FBT, bundles, vertical expansion, or non-search traffic for 3C products.
---

# 3C Traffic Expansion

## Official Data Rule

Validate tools before use:

```bash
python3 /Users/poincare/.codex/skills/sellerspirite/scripts/fetch_official_doc.py --tool traffic_keyword
python3 /Users/poincare/.codex/skills/sellerspirite/scripts/fetch_official_doc.py --tool traffic_listing
```

Do not invent `relations` values for `traffic_listing`; use only values documented in the SellerSprite appendix or active MCP schema.

## Workflow

1. Start with winner or competitor ASINs from product research.
2. Use `traffic_keyword` to identify search entry:
   - return fields: `items.keyword,items.searches,items.products,items.purchases,items.purchaseRate,items.bid,items.rankPosition,items.latest30daysAds,items.supplyDemandRatio,items.trafficPercentage,items.naturalRatio,items.adRatio`.
3. Classify traffic:
   - Search-led: many keywords with natural ranking and purchase intent.
   - Ad-led: high ad ratio and many advertisers.
   - Long-tail-led: many small but high-conversion phrases.
4. Use `traffic_listing` only for finalist ASINs to find related-product/bundle opportunities.
5. Translate into expansion:
   - bundle pack
   - accessory companion
   - replacement part
   - compatibility variant
   - premium/pro version

## Output Fields

`sourceAsin`, `keyword`, `searches`, `purchases`, `purchaseRate`, `rankPosition`, `bid`, `trafficPercentage`, `naturalRatio`, `adRatio`, `relatedAsin`, `expansionType`, `action`.
