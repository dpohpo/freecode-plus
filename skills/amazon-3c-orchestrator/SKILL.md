---
name: amazon-3c-orchestrator
description: Orchestrates MECE Amazon 3C product-selection research across trend, market, keyword, competition, profit, compliance, review, traffic, and workbook skills. Use when the user asks for Amazon 3C/consumer electronics product research, 数码3C选品, or a full feasibility workflow before SellerSprite MCP execution.
---

# Amazon 3C Orchestrator

## Goal

Turn a broad 3C idea into a ranked shortlist with evidence, not a one-off hot-product guess.

Default assumptions unless user says otherwise: Amazon US, private-label or light customization, avoid heavy certification burden, target small/standard-size products, preserve all raw data locally.

## Premise Check

- 3C is not one category. Split into accessories, chargers/cables, holders/mounts, smart peripherals, storage, audio, gaming, photo/video, and replacement parts.
- 3C demand can be real while the product is still bad because certification, battery, IP, defect rate, return rate, or ad cost can destroy margin.
- If no exact keyword/product is given, start with seed clusters, not MCP calls: phone stand, USB-C hub, cable organizer, laptop stand, webcam light, controller accessory, tablet mount, SSD case, camera mount, desk charging station.

## MECE Data Model

1. Demand and growth: search volume, purchases, units, revenue, growth rates.
2. Seasonality and timing: Google Trends monthly pattern, Amazon keyword trend, market cycle.
3. Supply and competition: products, brands, sellers, concentration, review moat, Amazon self-operated share.
4. Unit economics: price, FBA fee, weight, package size, gross margin, ad cost pressure.
5. Compliance and operational risk: battery, wireless, adapter/charger, child use, IP/patent, return and defect risk.
6. Differentiation: review complaints, low LQS, feature gaps, SKU gaps, bundle gaps.
7. Traffic entry: reverse keywords, related traffic, PPC bid, click concentration, ad/natural ratio.
8. Portfolio expansion: adjacent accessories, frequently bought together, vertical line extension.
9. Data governance: raw MCP response, normalized tables, scoring, source and timestamp.

## Minimal MCP Sequence

Run broad-to-narrow. Do not call expensive/detail tools until a candidate survives earlier gates.

1. Seed trend: `google_trend` for each seed keyword with `monthly:true`; classify 36+ month seasonality.
2. Keyword screen: `keyword_research` for surviving seed clusters; use `returnFields` with demand, competition, CPC, concentration, and brand fields.
3. Product screen: `product_research` for keyword/category candidates; pull top 100 only, with `returnFields` for ASIN, price, units, revenue, ratings, rating, BSR, profit, FBA, weight, dimensions, LQS, sellers, fulfillment, brand.
4. Category validation: `product_node` if node IDs are unclear, then `market_research` for finalist node paths.
5. Competition detail: only for final nodes call `market_product_concentration`; only for finalist ASINs call `traffic_keyword`, `asin_detail_with_coupon_trend`, and `review`.
6. Expansion: call `traffic_listing` only after a winning ASIN cluster exists.

## Scoring

Use a 100-point score:

- Demand 20
- Growth and seasonality timing 15
- Competition openness 20
- Profit/logistics 15
- Compliance/risk 15
- Differentiation/traffic angle 15

Reject regardless of score if compliance, IP, or defect risk is not controllable.

## Output

Use `amazon-3c-data-workbook` to create or update the Excel workbook. Every conclusion must reference the sheet, row, and source MCP/tool call.
