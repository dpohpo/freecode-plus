# Frontend Contract

Source analyzed:

```text
/Users/poincare/Desktop/us-summer-products-research-2026.html
```

Current extracted inventory:

- 108 products.
- 10 category directions.
- 60 CSS selectors/rules recorded in `frontend-inventory.json`.
- 14 inline event declarations.
- 28 product data fields.

## Static Labels

Document:

- `<html lang="zh-CN">`
- `<title>`: `美国夏季热销产品调研报告 2026 — 100+产品运营数据`
- Header H1: `美国夏季热销产品调研报告`
- Subtitle: `100+ 产品运营数据卡 | 适合中国跨境出口`
- Date/source line: `调研日期: 2026年5月 | 数据来源: Amazon Best Sellers 实时采集 + 运营数据模型`

Stats bar:

- `产品总数`: initialized as `108`, then overwritten by `P.length`.
- `品类方向`: `10`
- `数据维度/产品`: `12`
- `Amazon类目`: `8`

Filter labels and category keys:

- `all`: `全部`
- `sports`: `运动健身`
- `water`: `游泳水上`
- `garden`: `园艺工具`
- `party`: `派对用品`
- `ball`: `球类运动`
- `toy`: `玩具`
- `apparel`: `服饰配件`
- `electronics`: `户外电子`
- `pet`: `宠物用品`
- `home`: `家居装饰`

Search input:

- Placeholder: `搜索产品名称...`

Rendered category names:

- `sports`: `户外运动健身`, icon `🏃`
- `water`: `游泳和水上用品`, icon `🏊`
- `garden`: `庭院和园艺工具`, icon `🌿`
- `party`: `派对和季节性用品`, icon `🎉`
- `ball`: `球类运动`, icon `🎾`
- `toy`: `玩具和益智`, icon `🧸`
- `apparel`: `户外服饰配件`, icon `🕶️`
- `electronics`: `户外电子/小工具`, icon `⚡`
- `pet`: `宠物用品(非食品)`, icon `🐕`
- `home`: `家居个护`, icon `🏠`

Detail panel section labels:

- `💰 利润核算`
- `📊 销售估算`
- `⭐ 评论分析`
- `🔑 核心关键词 & 搜索量`
- `📅 季节性`
- `📋 Listing质量`
- `⚠️ 核心痛点(差评分析)`
- `💡 差异化机会`

Footer:

- `美国夏季热销产品调研报告 | 2026年5月 | 100+产品运营数据卡`
- `数据来源: Amazon.com Best Sellers | 成本数据基于1688行业均价 | 利润模型含15%佣金+标准FBA费`
- `标注 "估算" 的数据建议用 Jungle Scout / Helium 10 / 卖家精灵 进一步验证`

## Data Counts

Category product counts:

- `sports`: 14
- `water`: 12
- `garden`: 11
- `party`: 9
- `ball`: 10
- `toy`: 9
- `apparel`: 13
- `electronics`: 9
- `pet`: 9
- `home`: 12

Tag counts in source data:

- `hot`: 37
- `trend`: 64
- `new`: 26

Tag rendering:

- `hot` -> label `HOT`, class `tag tag-hot`
- `new` -> label `NEW`, class `tag tag-new`
- `trend` -> label `趋势`, class `tag tag-trend`
- Any unknown tag renders its raw value with `tag-${value}`.
- `tag-warn` is styled but not used by current product data.

## Click And Input Behavior

Inline filter buttons:

- `onclick="filterCat('all',this)"`
- `onclick="filterCat('sports',this)"`
- `onclick="filterCat('water',this)"`
- `onclick="filterCat('garden',this)"`
- `onclick="filterCat('party',this)"`
- `onclick="filterCat('ball',this)"`
- `onclick="filterCat('toy',this)"`
- `onclick="filterCat('apparel',this)"`
- `onclick="filterCat('electronics',this)"`
- `onclick="filterCat('pet',this)"`
- `onclick="filterCat('home',this)"`

Dynamic render events:

- Category header uses `onclick="toggleCat('${cat}')"` and toggles the corresponding product grid between `display:grid` and `display:none`.
- Product card header uses `onclick="toggleDetail(${p.id})"` and toggles `.p-detail.show`.
- Search input uses `oninput="searchProducts(this.value)"`; it lowercases the query and checks `data-name` and `data-en` only.

Function side effects:

- `filterCat(cat, btn)`: removes `.active` from all filter buttons, adds `.active` to clicked button, shows matching `.cat-section` blocks.
- `searchProducts(q)`: sets each `.p-card` to `display:block` or `display:none`.
- `toggleDetail(id)`: toggles `show` class on `#d-${id}`.
- `toggleCat(cat)`: toggles category grid display and arrow text `▼` / `▶`.
- `renderProducts()`: writes all category sections to `#content`.
- `renderCard(p)`: computes fees, margin display, tag labels, keywords, pains, and all product card HTML.
- `formatNum(n)`: formats `>=1,000,000` as `M`, `>=1,000` as `K`, otherwise raw integer string.

## CSS Tokens

Root variables:

```css
--primary:#1a73e8;
--primary-light:#e8f0fe;
--success:#34a853;
--warning:#fbbc04;
--danger:#ea4335;
--gray-50:#f8f9fa;
--gray-100:#f1f3f4;
--gray-200:#e8eaed;
--gray-600:#5f6368;
--gray-800:#3c4043;
--shadow:0 1px 3px rgba(0,0,0,.12);
--radius:10px;
```

Other literal colors/effects:

- Header gradient: `linear-gradient(135deg,#1a73e8,#0d47a1)`
- Hover card shadow: `0 4px 12px rgba(0,0,0,.15)`
- `tag-hot`: background `#fce8e6`, color `var(--danger)`
- `tag-new`: background `#e6f4ea`, color `var(--success)`
- `tag-trend`: background `var(--primary-light)`, color `var(--primary)`
- `tag-warn`: background `#fff3e0`, color `#e65100`
- `seg-cost`: `#9e9e9e`
- `seg-fba`: `#ff9800`
- `seg-ref`: `#f44336`
- `opp-text`: color `#2e7d32`, background `#e8f5e9`

## Selector Inventory

Preserve these selectors unless redesign is explicitly requested:

```text
:root
*
body
.header
.header h1
.header .sub
.header .date
.container
.stats-bar
.stat-card
.stat-card .n
.stat-card .l
.filter-bar
.filter-bar button
.filter-bar button.active,.filter-bar button:hover
.search-box
.search-box:focus
.cat-section
.cat-header
.cat-header h2
.cat-header .count
.cat-header .toggle
.product-grid
.p-card
.p-card:hover
.p-card-header
.p-card-header .name
.p-card-header .price
.p-card-meta
.p-card-meta span
.p-card-meta .stars
.p-card-tags
.tag
.tag-hot
.tag-new
.tag-trend
.tag-warn
.p-detail
.p-detail.show
.p-detail h4
.p-detail h4:first-child
.d-grid
.d-grid .dl
.d-grid .dv
.d-grid-3
.d-grid-3 .dl
.d-grid-3 .dv
.profit-bar
.profit-bar .seg
.seg-cost
.seg-fba
.seg-ref
.seg-profit
.pain-list
.pain-list li
.opp-text
.footer
@media(max-width:768px)
@media .product-grid
@media .d-grid,.d-grid-3
@media .search-box
```

## Layout Rules

- Page background is `var(--gray-50)`.
- Main container max width is `1280px`; horizontal padding is `16px`.
- Stats use responsive grid: `repeat(auto-fit,minmax(160px,1fr))`.
- Product grid uses `repeat(auto-fill,minmax(360px,1fr))`.
- Mobile breakpoint is `768px`: product grid becomes one column, detail grids become one column, search input becomes full width.
- Cards use `border-radius:10px`, white background, shadow, and hover shadow.
- Product card header has `border-left:4px solid var(--primary)` and is clickable.
- Detail panel starts hidden with `display:none`; `.show` changes it to `display:block`.

## Calculated Fields

In `renderCard(p)`:

- Referral fee: `price * refRate / 100`.
- Head freight/other estimate: `cost * 0.15`.
- Total cost: `cost + fba + referral fee + cost * 0.15`.
- Profit: `price - total cost`.
- Profit rate: `profit / price * 100`.
- Profit bar widths: purchase cost %, FBA %, referral %, remaining profit %.
- Monthly new reviews estimate: `reviews * 0.005`.
- Daily sales estimate: `sales / 30`.
- Annual revenue estimate: `revenue * 12`.
