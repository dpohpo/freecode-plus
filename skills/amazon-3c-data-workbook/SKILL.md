---
name: amazon-3c-data-workbook
description: Defines local Excel storage, raw-response preservation, normalized tables, scoring sheets, and audit trails for Amazon 3C SellerSprite research. Use when saving SellerSprite MCP data, creating Excel workbooks, exporting product research, or making a reusable local analysis dataset.
---

# 3C Data Workbook

## Goal

Every MCP/API result must be reusable later. Store raw data, normalized rows, scoring, source URLs, run IDs, and assumptions in a local Excel workbook plus raw JSON files.

## Folder Convention

Inside the active project, use:

```text
data/amazon_3c/
  raw/YYYY-MM-DD/<run_id>/<tool>_<keyword_or_asin>.json
  processed/YYYY-MM-DD/<run_id>/*.csv
  amazon_3c_selection_workbook.xlsx
```

## Workbook Sheets

1. `README`: project scope, marketplace, run ID, assumptions, decision threshold.
2. `Sources`: every MCP call, official doc URL, parameter JSON, timestamp, raw file path.
3. `Trend_Seasonality`: Google Trends monthly data and classification.
4. `Keyword_Opportunity`: keyword metrics and keyword score.
5. `Product_Screen`: product-level product_research rows.
6. `Market_Capacity`: category/node market_research rows.
7. `Competition`: moat/concentration and attackability rows.
8. `Profit_Logistics`: unit economics and physical feasibility.
9. `Compliance_Risk`: risk flags and document requirements.
10. `Review_Differentiation`: complaint themes and improvement hypotheses.
11. `Traffic_Expansion`: reverse keywords, related products, bundle ideas.
12. `Scorecard`: final weighted score and decision.

## Minimum Columns

Every data sheet must include: `run_id`, `marketplace`, `source_tool`, `source_url`, `source_doc`, `queried_at`, and the entity key (`keyword`, `asin`, or `nodeIdPath`).

## Scoring Logic

Keep scoring formulas visible and editable. Never hardcode final scores without showing the component inputs.

Default reject states:

- `Compliance_Risk.riskClass = red`
- no 36-month trend data and the product is seasonal
- product has no clear differentiation hypothesis
- estimated economics cannot absorb FBA, PPC, returns, and defect replacement

## Output

At the end of a research run, save the workbook path and a one-page decision summary with accepted, watchlist, and rejected candidates.
