---
name: amazon-3c-market-capacity
description: Evaluates Amazon 3C market/category capacity using SellerSprite market and product tools with official parameters. Use when analyzing market size, category opportunity, nodeIdPath, total units/revenue, 新品占比, or whether a 3C niche is large enough.
---

# 3C Market Capacity

## Official Data Rule

Use these SellerSprite MCP tools only after validating parameters:

```bash
python3 /Users/poincare/.codex/skills/sellerspirite/scripts/fetch_official_doc.py --tool product_node
python3 /Users/poincare/.codex/skills/sellerspirite/scripts/fetch_official_doc.py --tool market_research
```

## Workflow

1. Resolve category with `product_node` when the user provides a keyword but no `nodeIdPath`.
2. Call `market_research` on candidate node paths or category keywords.
3. Request minimal return fields: `marketplace,nodeId,nodeIdPath,nodeLabelPath,nodeLabelPathLocale,totalProducts,totalUnits,totalRevenue,avgUnits,avgRevenue,avgPrice,avgRatings,avgRating,avgBsr,avgProfit,returnRatio,searchToPurchaseRatio,topProducts`.
4. Screen for capacity:
   - Too small: total units/revenue cannot support the user's target order volume.
   - Too broad: total products very high and no clear sub-niche.
   - Healthy: enough revenue, multiple sellers/brands, and not dominated by one price band.
5. Pass node finalists to `amazon-3c-competition-moat` and `amazon-3c-profit-logistics`.

## 3C-Specific Notes

- Do not prefer high-revenue electronics niches automatically; many are brand-, patent-, or certification-heavy.
- Accessories and replacement parts can have lower headline revenue but better private-label feasibility.
- If `returnRatio` is high, require review analysis before passing the niche.

## Output Fields

`nodeIdPath`, `nodeLabelPath`, `totalProducts`, `totalUnits`, `totalRevenue`, `avgUnits`, `avgRevenue`, `avgPrice`, `avgRatings`, `avgRating`, `avgProfit`, `returnRatio`, `capacityClass`, `nextAction`.
