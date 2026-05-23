---
name: amazon-3c-profit-logistics
description: Screens Amazon 3C candidates for price, gross profit, FBA fee, weight, dimension, packaging, and cash-flow feasibility using SellerSprite official product fields. Use when evaluating margin, logistics, FBA cost, weight, size, inventory risk, or 3C cash-flow feasibility.
---

# 3C Profit Logistics

## Official Data Rule

Use `product_research` for first-pass economics; verify official fields first:

```bash
python3 /Users/poincare/.codex/skills/sellerspirite/scripts/fetch_official_doc.py --tool product_research
```

Relevant official fields: `price`, `profit`, `fba`, `weight`, `dimension`, `pkgWeight`, `pkgDimensions`, `dimensionsType`, `pkgDimensionType`, `units`, `revenue`, `fulfillment`, `deliveryPrice`.

## Workflow

1. Pull only economic/logistics return fields for candidates.
2. Classify price bands:
   - Low risk: $15-$50 unless 3C compliance or ad cost demands higher margin.
   - Caution: below $10 requires very high volume and low support cost.
   - Caution: above $80 needs stronger brand trust and return-control evidence.
3. Check physical feasibility:
   - Prefer small/standard-size accessories.
   - Penalize heavy, fragile, battery-heavy, plug-in, heat-generating, or high-return electronics.
4. Estimate ad pressure from `amazon-3c-keyword-opportunity`: `bid / avgPrice`.
5. Reject if gross margin cannot absorb FBA fee, referral fee, PPC, returns, replacement, and inspection.

## Output Fields

`asin`, `price`, `profit`, `fba`, `weight`, `pkgWeight`, `dimension`, `pkgDimensions`, `units`, `revenue`, `fulfillment`, `trafficCostRatio`, `logisticsClass`, `marginClass`, `cashFlowNote`.
