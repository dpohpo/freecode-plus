---
name: amazon-3c-competition-moat
description: Assesses Amazon 3C competitive barriers using SellerSprite product, market concentration, review moat, brand concentration, seller count, and Amazon self-operated signals. Use when evaluating competition, monopoly, review barriers, new brand entry, or whether a 3C niche is attackable.
---

# 3C Competition Moat

## Official Data Rule

Validate every tool before use:

```bash
python3 /Users/poincare/.codex/skills/sellerspirite/scripts/fetch_official_doc.py --tool product_research
python3 /Users/poincare/.codex/skills/sellerspirite/scripts/fetch_official_doc.py --tool market_product_concentration
```

Use `market_product_concentration` only for finalist node paths because it requires `marketplace` and `nodeIdPath`.

## Workflow

1. Start with `product_research` for top products in the niche.
2. Use return fields: `asin,title,brand,price,units,revenue,bsr,ratings,rating,ratingsCv,availableDate,fulfillment,variations,sellers,sellerName,sellerNation,lqs,badge,nodeIdPath,nodeLabelPath`.
3. Compute:
   - Review moat: median and top-10 `ratings`; count products with `ratings < 100`.
   - New entrant signal: products with recent `availableDate` and meaningful `units`.
   - Brand moat: top brands repeated across rows.
   - Seller openness: more third-party sellers and fewer Amazon-owned rows is usually better.
   - Listing weakness: high sales with low `lqs` or low `rating`.
4. For finalist categories, call `market_product_concentration` and inspect `totalUnitsRatio` / `totalRevenueRatio`.
5. Classify:
   - Open: dispersed sales, several low-review sellers, weak LQS.
   - Contested: demand exists but top brands/reviews dominate.
   - Avoid: Amazon/major brand dominance, extreme review moat, or concentrated revenue.

## Output Fields

`asin`, `brand`, `sellerName`, `units`, `revenue`, `ratings`, `rating`, `availableDate`, `lqs`, `sellers`, `fulfillment`, `topShare`, `reviewMoatClass`, `brandMoatClass`, `attackability`.
