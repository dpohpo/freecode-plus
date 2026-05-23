---
name: amazon-3c-keyword-opportunity
description: Scores Amazon 3C keyword opportunities using SellerSprite keyword research, demand, purchase, supply-demand, PPC, and click concentration fields. Use when analyzing 3C keywords, 长尾词, keyword_research, search demand, purchase rate, CPC, or keyword competition.
---

# 3C Keyword Opportunity

## Official Data Rule

Use SellerSprite MCP tool `keyword_research`; verify fields first:

```bash
python3 /Users/poincare/.codex/skills/sellerspirite/scripts/fetch_official_doc.py --tool keyword_research
```

Known official request fields include `marketplace`, `month`, `departments`, `keywords`, `minSearches`, `maxSearches`, `minProducts`, `maxProducts`, `minPurchases`, `minPurchaseRate`, `withYearlyGrowth`, `minSearchNearlyCr`, `marketPeriod`, `minAvgPrice`, `maxAvgPrice`, `minBid`, `maxBid`, `minAraClickRate`, `maxAraClickRate`, `minSupplyDemandRatio`, `minWordCount`, `page`, `size`, and `order`.

## Workflow

1. Query seed and long-tail clusters, not just head words.
2. Use `size:15` because official docs limit `keyword_research` page size to 15.
3. Use return fields: `keywords,searches,purchases,purchaseRate,products,supplyDemandRatio,growth,searchMonthlyCr,searchNearlyCr,avgPrice,avgRatings,avgRating,bid,bidMin,bidMax,araClickRate,araShareRate,titleDensityExact,marketPeriod,hasBrandWord,keywordCn`.
4. Classify each keyword:
   - Demand: searches and purchases.
   - Conversion: purchaseRate.
   - Supply gap: supplyDemandRatio and products.
   - Ad pressure: bid/avgPrice and araClickRate.
   - Entry path: long-tail if word count >= 3 and purchaseRate is acceptable.
5. Reject if `hasBrandWord` is true unless the plan is accessory-compatible and non-infringing.

## Output Fields

`keyword`, `keywordCn`, `searches`, `purchases`, `purchaseRate`, `products`, `supplyDemandRatio`, `avgPrice`, `bid`, `trafficCostRatio`, `araClickRate`, `titleDensityExact`, `marketPeriod`, `keywordClass`, `riskNote`.
