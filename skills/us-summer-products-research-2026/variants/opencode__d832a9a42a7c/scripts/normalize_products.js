#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

function args() {
  const out = {};
  for (let i = 2; i < process.argv.length; i++) {
    const t = process.argv[i];
    if (!t.startsWith("--")) continue;
    out[t.slice(2)] = process.argv[i + 1] && !process.argv[i + 1].startsWith("--") ? process.argv[++i] : true;
  }
  return out;
}

const A = args();
if (!A.input || !A.out) {
  console.error("Usage: normalize_products.js --input raw.json|raw.csv --out products.json [--strict]");
  process.exit(2);
}

function parseCsv(text) {
  const rows = [];
  let row = [], cell = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i], next = text[i + 1];
    if (q && ch === '"' && next === '"') { cell += '"'; i++; continue; }
    if (ch === '"') { q = !q; continue; }
    if (!q && ch === ",") { row.push(cell); cell = ""; continue; }
    if (!q && (ch === "\n" || ch === "\r")) {
      if (ch === "\r" && next === "\n") i++;
      row.push(cell); rows.push(row); row = []; cell = ""; continue;
    }
    cell += ch;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  const headers = rows.shift().map((h) => h.trim());
  return rows.filter((r) => r.some((x) => x.trim())).map((r) =>
    Object.fromEntries(headers.map((h, i) => [h, r[i] == null ? "" : r[i].trim()])));
}

function readRows(file) {
  const text = fs.readFileSync(file, "utf8");
  if (/\.csv$/i.test(file)) return parseCsv(text);
  const raw = JSON.parse(text);
  if (Array.isArray(raw)) return raw;
  if (Array.isArray(raw.products)) return raw.products;
  if (Array.isArray(raw.rows)) return raw.rows;
  throw new Error("JSON input must be an array or contain products/rows array");
}

const pick = (r, names) => {
  for (const name of names) if (r[name] !== undefined && r[name] !== "") return r[name];
  return undefined;
};
const splitList = (v) => {
  if (Array.isArray(v)) return v.map(String).map((x) => x.trim()).filter(Boolean);
  if (v == null || v === "") return [];
  return String(v).split(/\s*(?:\||;|；|,|，|\n)\s*/).map((x) => x.trim()).filter(Boolean);
};
const num = (v, fallback = undefined) => {
  if (typeof v === "number") return Number.isFinite(v) ? v : fallback;
  if (v == null || v === "") return fallback;
  const n = Number(String(v).replace(/[$,%\s,]/g, ""));
  return Number.isFinite(n) ? n : fallback;
};
const bool = (v, fallback = false) => {
  if (typeof v === "boolean") return v;
  if (v == null || v === "") return fallback;
  return /^(true|yes|y|1|是|有|✅|amazon|自营)$/i.test(String(v).trim());
};

const aliases = {
  id: ["id", "序号", "编号"],
  cat: ["cat", "category_key", "品类键", "类目键", "category", "品类"],
  name: ["name", "产品名称", "中文名称", "产品"],
  en: ["en", "english", "英文标题", "英文名", "amazon_title", "Amazon标题"],
  price: ["price", "售价", "sale_price", "amazon_price"],
  range: ["range", "价格区间", "price_range"],
  rating: ["rating", "评分", "星级"],
  reviews: ["reviews", "评论数", "review_count"],
  bsr: ["bsr", "BSR", "排名", "best_seller_rank"],
  cost: ["cost", "1688采购", "采购价", "1688_cost"],
  fba: ["fba", "FBA配送费", "fba_fee"],
  refRate: ["refRate", "佣金率", "referral_rate"],
  sales: ["sales", "月销量", "monthly_sales"],
  revenue: ["revenue", "月销售额", "monthly_revenue"],
  revGrowth: ["revGrowth", "年增速", "growth", "yoy_growth"],
  sellers: ["sellers", "卖家数", "seller_count"],
  amazSelf: ["amazSelf", "Amazon自营", "amazon_self"],
  season: ["season", "需求趋势", "seasonality"],
  peakMon: ["peakMon", "峰值月份", "peak_months"],
  imgs: ["imgs", "图片数量", "image_count"],
  aplus: ["aplus", "A+页面", "a_plus"],
  video: ["video", "产品视频", "has_video"],
  improve: ["improve", "差异化机会", "改进机会"],
  tags: ["tags", "标签"],
  kw: ["kw", "keywords", "核心关键词"],
  sv: ["sv", "search_volumes", "搜索量"],
  pains: ["pains", "pain_points", "核心痛点", "差评痛点"],
};

const catMap = {
  "运动健身": "sports", "户外运动健身": "sports", sports: "sports",
  "游泳水上": "water", "游泳和水上用品": "water", water: "water",
  "园艺工具": "garden", "庭院和园艺工具": "garden", garden: "garden",
  "派对用品": "party", "派对和季节性用品": "party", party: "party",
  "球类运动": "ball", ball: "ball",
  "玩具": "toy", "玩具和益智": "toy", toy: "toy",
  "服饰配件": "apparel", "户外服饰配件": "apparel", apparel: "apparel",
  "户外电子": "electronics", "户外电子/小工具": "electronics", electronics: "electronics",
  "宠物用品": "pet", "宠物用品(非食品)": "pet", pet: "pet",
  "家居装饰": "home", "家居个护": "home", home: "home",
};

function kwArray(row) {
  const direct = splitList(pick(row, aliases.kw));
  if (direct.length) return direct.slice(0, 5);
  return [1, 2, 3, 4, 5].map((i) => pick(row, [`kw${i}`, `关键词${i}`, `keyword${i}`]))
    .filter((x) => x !== undefined && x !== "").map(String).slice(0, 5);
}

function svArray(row) {
  const direct = splitList(pick(row, aliases.sv)).map((x) => num(x, 0));
  if (direct.length) return direct.slice(0, 5);
  return [1, 2, 3, 4, 5].map((i) => num(pick(row, [`sv${i}`, `搜索量${i}`, `search_volume${i}`]), 0)).slice(0, 5);
}

function normalize(row, i) {
  const price = num(pick(row, aliases.price), 0);
  const cost = num(pick(row, aliases.cost), 0);
  const fba = num(pick(row, aliases.fba), 0);
  const refRate = num(pick(row, aliases.refRate), 15);
  const sales = num(pick(row, aliases.sales), 0);
  const revenue = num(pick(row, aliases.revenue), Math.round(price * sales));
  const refFee = price * refRate / 100;
  const profitRate = price ? Math.round((price - cost - fba - refFee - cost * 0.15) / price * 100) : 0;
  const catRaw = String(pick(row, aliases.cat) || "").trim();
  const kws = kwArray(row);
  const svs = svArray(row);
  while (svs.length < kws.length) svs.push(0);
  return {
    id: num(pick(row, aliases.id), i + 1),
    cat: catMap[catRaw] || catRaw,
    name: String(pick(row, aliases.name) || "").trim(),
    en: String(pick(row, aliases.en) || "").trim(),
    price,
    range: String(pick(row, aliases.range) || `$${price.toFixed(2)}-$${price.toFixed(2)}`).trim(),
    rating: num(pick(row, aliases.rating), 0),
    reviews: num(pick(row, aliases.reviews), 0),
    bsr: String(pick(row, aliases.bsr) || "-").trim(),
    kw: kws,
    sv: svs,
    cost,
    fba,
    refRate,
    margin: num(row.margin, profitRate),
    sales,
    revenue,
    revGrowth: num(pick(row, aliases.revGrowth), 0),
    sellers: num(pick(row, aliases.sellers), 0),
    amazSelf: bool(pick(row, aliases.amazSelf), false),
    season: String(pick(row, aliases.season) || "待验证").trim(),
    peakMon: String(pick(row, aliases.peakMon) || "待验证").trim(),
    imgs: num(pick(row, aliases.imgs), 0),
    aplus: bool(pick(row, aliases.aplus), false),
    video: bool(pick(row, aliases.video), false),
    pains: splitList(pick(row, aliases.pains)).slice(0, 5),
    improve: splitList(pick(row, aliases.improve)).join("+") || String(pick(row, aliases.improve) || "").trim(),
    tags: splitList(pick(row, aliases.tags)).map((t) => ({ HOT: "hot", NEW: "new", "趋势": "trend" }[t] || t.toLowerCase())).filter(Boolean),
  };
}

const rows = readRows(path.resolve(A.input));
const products = rows.map(normalize);
const errors = [];
for (const p of products) {
  for (const f of ["cat", "name", "en", "price", "rating", "reviews", "cost", "fba", "sales", "revenue"]) {
    if (p[f] === "" || p[f] === 0) errors.push(`${p.id} ${p.name || "(unnamed)"} missing/zero ${f}`);
  }
  if (!p.kw.length) errors.push(`${p.id} ${p.name || "(unnamed)"} missing kw`);
  if (!p.pains.length) errors.push(`${p.id} ${p.name || "(unnamed)"} missing pains`);
  if (!p.improve) errors.push(`${p.id} ${p.name || "(unnamed)"} missing improve`);
}
if (errors.length && A.strict) {
  console.error(errors.slice(0, 80).join("\n"));
  process.exit(1);
}

fs.mkdirSync(path.dirname(path.resolve(A.out)), { recursive: true });
fs.writeFileSync(path.resolve(A.out), JSON.stringify(products, null, 2));
console.log(JSON.stringify({ inputRows: rows.length, products: products.length, warnings: errors.length, out: path.resolve(A.out) }, null, 2));
