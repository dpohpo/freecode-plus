# SellerSprite Official Docs Index

Official sources:

- API overview: https://open.sellersprite.com/api
- MCP access: https://open.sellersprite.com/mcp/16
- Codex setup: https://open.sellersprite.com/mcp/40
- Token and `returnFields`: https://open.sellersprite.com/mcp/46
- Appendix: https://open.sellersprite.com/appendix

Core rules verified from the official docs:

- API gateway is `https://api.sellersprite.com`.
- MCP endpoint is `https://mcp.sellersprite.com/mcp` with `secret-key` in headers, or URL direct form `https://mcp.sellersprite.com/mcp?secret-key=...`.
- API headers include `secret-key`, `Content-Type: application/json;charset=utf-8`, and `x-request-id` as a unique request identifier.
- Common response envelope is `code`, `message`, `data`.
- Same query condition only supports TOP 2K records; split by ranking, BSR, search volume, sales, or other documented ranges when pulling more.
- MCP supports `returnFields` to reduce returned fields; use comma-separated official return-field names only.

## MCP Tool Pages

| MCP code | Name | Method | Official doc | API URL |
|---|---|---:|---|---|
| `competitor_lookup` | 查竞品 | POST | https://open.sellersprite.com/api/1 | `https://api.sellersprite.com/v1/product/competitor-lookup` |
| `product_research` | 选产品 | POST | https://open.sellersprite.com/api/2 | `https://api.sellersprite.com/v1/product/research` |
| `product_node` | 查产品类目 | GET | https://open.sellersprite.com/api/9 | `https://api.sellersprite.com/v1/product/node` |
| `asin_detail` | ASIN 详情 | GET | https://open.sellersprite.com/api/3 | `https://api.sellersprite.com/v1/asin/{marketplace}/{asin}` |
| `asin_coupon_trend` | ASIN优惠趋势 | GET | https://open.sellersprite.com/api/56 | `https://api.sellersprite.com/v1/asin/{marketplace}/{asin}/coupon-trend` |
| `asin_detail_with_coupon_trend` | ASIN详情及优惠趋势 | GET | https://open.sellersprite.com/api/57 | `https://api.sellersprite.com/v1/asin/{marketplace}/{asin}/with-coupon-trend` |
| `asin_prediction` | ASIN 销量预测 | GET | https://open.sellersprite.com/api/27 | `https://api.sellersprite.com/v1/sales/prediction/asin` |
| `bsr_prediction` | BSR销量预测 | GET | https://open.sellersprite.com/api/26 | `https://api.sellersprite.com/v1/sales/prediction/bsr` |
| `traffic_keyword` | 关键词反查(流量词列表) | POST | https://open.sellersprite.com/api/14 | `https://api.sellersprite.com/v1/traffic/keyword` |
| `keepa_info` | 商品趋势详情(keepa) | GET | https://open.sellersprite.com/api/22 | `https://api.sellersprite.com/v1/keepa/{marketplace}/{asin}` |
| `keyword_research` | 关键词选品 | POST | https://open.sellersprite.com/api/10 | `https://api.sellersprite.com/v1/keyword-research` |
| `keyword_research_trends` | 关键词选品-趋势数据 | POST | https://open.sellersprite.com/api/11 | `https://api.sellersprite.com/v1/keyword-research/trends` |
| `keyword_miner` | 关键词挖掘 | POST | https://open.sellersprite.com/api/6 | `https://api.sellersprite.com/v1/keyword/miner` |
| `traffic_extend` | 拓展流量词 | POST | https://open.sellersprite.com/api/46 | `https://api.sellersprite.com/v1/traffic/extend` |
| `aba_research_weekly` | ABA 数据选品-按周 | POST | https://open.sellersprite.com/api/19 | `https://api.sellersprite.com/v1/aba/research/weekly` |
| `aba_research_monthly` | ABA 数据选品-按月 | POST | https://open.sellersprite.com/api/20 | `https://api.sellersprite.com/v1/aba/research/monthly` |
| `aba_research_trend` | ABA 数据选品-关键词趋势 | POST | https://open.sellersprite.com/api/60 | `https://api.sellersprite.com/v1/aba/research/trends` |
| `google_trend` | 谷歌趋势 | GET | https://open.sellersprite.com/api/12 | `https://api.sellersprite.com/v1/google/trends` |
| `keyword_order` | 出单词反查 | POST | https://open.sellersprite.com/api/24 | `https://api.sellersprite.com/v1/keyword-order` |
| `traffic_listing` | 关联流量列表 | POST | https://open.sellersprite.com/api/16 | `https://api.sellersprite.com/v1/traffic/listing/page` |
| `traffic_keyword_stat` | 流量词统计 | GET | https://open.sellersprite.com/api/13 | `https://api.sellersprite.com/v1/traffic/keyword/stat/{marketplace}/{asin}` |
| `traffic_listing_stat` | 关联流量统计 | GET | https://open.sellersprite.com/api/15 | `https://api.sellersprite.com/v1/traffic/listing/stat/{marketplace}/{asin}` |
| `traffic_source` | 查流量来源(关键词流向) | POST | https://open.sellersprite.com/api/17 | `https://api.sellersprite.com/v1/traffic/source` |
| `market_research` | 选市场列表 | POST | https://open.sellersprite.com/api/29 | `https://api.sellersprite.com/v1/market/research` |
| `market_research_statistics` | 选市场-统计 | POST | https://open.sellersprite.com/api/30 | `https://api.sellersprite.com/v1/market/statistics` |
| `market_product_concentration` | 选市场-商品集中度 | POST | https://open.sellersprite.com/api/31 | `https://api.sellersprite.com/v1/market/goods` |
| `market_brand_concentration` | 选市场-品牌集中度 | POST | https://open.sellersprite.com/api/32 | `https://api.sellersprite.com/v1/market/brand` |
| `market_seller_country_distribution` | 选市场-卖家所属地分布 | POST | https://open.sellersprite.com/api/35 | `https://api.sellersprite.com/v1/market/seller/location` |
| `market_seller_concentration` | 选市场-卖家集中度 | POST | https://open.sellersprite.com/api/33 | `https://api.sellersprite.com/v1/market/seller` |
| `market_seller_type_concentration` | 选市场-卖家类型分布 | POST | https://open.sellersprite.com/api/34 | `https://api.sellersprite.com/v1/market/seller/type` |
| `market_product_demand_trend` | 选市场-商品需求趋势 | POST | https://open.sellersprite.com/api/36 | `https://api.sellersprite.com/v1/market/performance` |
| `market_listing_date_distribution` | 选市场-上架时间分布 | POST | https://open.sellersprite.com/api/37 | `https://api.sellersprite.com/v1/market/shelf/time` |
| `market_listing_trend_distribution` | 选市场-上架趋势分布 | POST | https://open.sellersprite.com/api/38 | `https://api.sellersprite.com/v1/market/shelf/trend` |
| `market_ratings_count_distribution` | 选市场-评分数分布 | POST | https://open.sellersprite.com/api/39 | `https://api.sellersprite.com/v1/market/ratings` |
| `market_rating_distribution` | 选市场-评分值分布 | POST | https://open.sellersprite.com/api/40 | `https://api.sellersprite.com/v1/market/rating` |
| `market_price_distribution` | 选市场-价格分布 | POST | https://open.sellersprite.com/api/41 | `https://api.sellersprite.com/v1/market/price` |
| `market_ebc_distribution` | 选市场-A+视频分布 | POST | https://open.sellersprite.com/api/42 | `https://api.sellersprite.com/v1/market/ebc` |
| `review` | 查评论 | POST | https://open.sellersprite.com/api/25 | `https://api.sellersprite.com/v1/review` |

## Non-MCP API Pages

These are official API pages, but the official index does not show an MCP code for them:

| Name | Method | Official doc | API URL |
|---|---:|---|---|
| 图片文字识别 | POST | https://open.sellersprite.com/api/44 | `https://api.sellersprite.com/v1/ocr` |
| 全球商标库-数据范围 | GET | https://open.sellersprite.com/api/50 | `https://api.sellersprite.com/v1/global/brand/range` |
| 全球商标库-详情 | GET | https://open.sellersprite.com/api/49 | `https://api.sellersprite.com/v1/global/brand/detail` |
| 全球商标库-列表 | POST | https://open.sellersprite.com/api/48 | `https://api.sellersprite.com/v1/global/brand/list` |
| 全球商标库-统计 | POST | https://open.sellersprite.com/api/47 | `https://api.sellersprite.com/v1/global/brand/stats` |
