---
name: sellerspirite
description: Use SellerSprite Open API/MCP for Amazon product, keyword, traffic, ASIN, review, and market research with official parameters only. Use when the user says $sellerspirite, $sellersprite, 卖家精灵, SellerSprite MCP/API, Amazon 选品, product_research, keyword_research, traffic_keyword, or asks to query SellerSprite data without inventing fields.
---

# SellerSprite

## Hard Rule

Never invent SellerSprite tool names, request parameters, enum values, or return fields. Before calling MCP/API, verify every field against either:

1. The active MCP tool schema, if the SellerSprite MCP server is connected.
2. The official docs at `https://open.sellersprite.com/api` and the exact tool page in [references/official-docs-index.md](references/official-docs-index.md).
3. A fresh scrape from [scripts/fetch_official_doc.py](scripts/fetch_official_doc.py).

If a needed parameter is not documented, do not use it. Ask for a different filter or explain the closest documented alternative.

## Official Endpoints

- MCP endpoint: `https://mcp.sellersprite.com/mcp`
- MCP auth header: `secret-key: <Your Secret>`
- API gateway: `https://api.sellersprite.com`
- API headers: `secret-key`, `Content-Type: application/json;charset=utf-8`, optional `x-request-id`

## Workflow

1. Map the user goal to an official tool in [references/official-docs-index.md](references/official-docs-index.md). For broad Amazon 选品, start with `product_research`, `market_research`, `keyword_research`, and supporting ASIN/traffic tools as needed.
2. Fetch the official tool page before composing parameters:
   ```bash
   python3 /Users/poincare/.codex/skills/sellerspirite/scripts/fetch_official_doc.py --tool product_research
   ```
3. Build the MCP/API input using exact documented parameter names and casing, usually camelCase such as `minUnits`, `maxRatings`, `nodeIdPath`, `returnFields`. Do not convert to guessed snake_case unless the CLI help explicitly shows CLI flags.
4. Validate any planned JSON input before calling:
   ```bash
   python3 /Users/poincare/.codex/skills/sellerspirite/scripts/fetch_official_doc.py --tool product_research --validate-json '{"marketplace":"US","keyword":"earbuds","minUnits":300}'
   ```
5. Use `returnFields` for MCP calls when large responses are expected. Only include fields that are present in the official return-parameter table; comma-separate them, e.g. `asin,title,price,units,revenue,rating,ratings,bsr`.
6. Preserve documented limits. The API overview says the same query condition can fetch only TOP 2K records; split by rank, BSR, search volume, sales, or other documented filters when more coverage is needed.

## Parameter Discipline

- Required fields marked `✓` must be present.
- For `GET` docs with path placeholders such as `{marketplace}` and `{asin}`, pass those exact documented fields to MCP, or substitute them in the API URL when calling HTTP directly.
- For nested parameters such as `order.field` and `order.desc`, keep them under the documented parent object.
- If docs and examples disagree, prefer the request-parameter table and note the discrepancy.
- Marketplace and appendix-linked enum values must be checked in the official appendix or the active tool schema before use.

## Sources To Check

- API overview: `https://open.sellersprite.com/api`
- Tool index and docs: [references/official-docs-index.md](references/official-docs-index.md)
- MCP setup: `https://open.sellersprite.com/mcp/16`
- Codex setup: `https://open.sellersprite.com/mcp/40`
- Token/`returnFields`: `https://open.sellersprite.com/mcp/46`
- Appendix: `https://open.sellersprite.com/appendix`
