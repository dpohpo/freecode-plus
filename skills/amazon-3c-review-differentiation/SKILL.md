---
name: amazon-3c-review-differentiation
description: Finds 3C product differentiation opportunities from SellerSprite review, ASIN detail, listing quality, ratings, Q&A, SKU, and feature-gap signals. Use when analyzing reviews, complaints, LQS, improvement opportunities, product upgrade ideas, or whether a 3C candidate can be differentiated.
---

# 3C Review Differentiation

## Official Data Rule

Validate these tools before use:

```bash
python3 /Users/poincare/.codex/skills/sellerspirite/scripts/fetch_official_doc.py --tool asin_detail_with_coupon_trend
python3 /Users/poincare/.codex/skills/sellerspirite/scripts/fetch_official_doc.py --tool review
```

Known `review` request fields: `marketplace`, `asin`, `starList`, `typeList`, `page`, `size`; maximum `size` is 10 in the official docs.

## Workflow

1. Use `asin_detail_with_coupon_trend` for top 3-5 competitor ASINs only.
2. Pull fields: `asin.title`, `asin.features`, `asin.overviews`, `asin.price`, `asin.rating`, `asin.ratings`, `asin.reviews`, `asin.questions`, `asin.lqs`, `asin.variationList`, `asin.skuList`, `asin.coupon`.
3. Use `review` for 1-3 star reviews first: `starList:[1,2,3]`, then page through only enough examples to identify repeated pain points.
4. Extract recurring complaint themes: compatibility, durability, heat, cable length, port count, fit, adhesive, noise, firmware/app, packaging, instructions.
5. Convert themes into testable differentiation hypotheses: feature, bundle, material, instruction, compatibility table, QA process, warranty, listing education.
6. Reject if complaints imply unavoidable product physics, high defect rate, or certification issues.

## Output Fields

`asin`, `complaintTheme`, `frequencyEvidence`, `differentiationIdea`, `buyerBenefit`, `sourcingRequirement`, `listingRequirement`, `riskClass`, `testPlan`.
