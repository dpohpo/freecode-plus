#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const Module = require("module");

function readArgs() {
  const out = {};
  for (let i = 2; i < process.argv.length; i++) {
    const token = process.argv[i];
    if (!token.startsWith("--")) continue;
    const key = token.slice(2);
    const val = process.argv[i + 1] && !process.argv[i + 1].startsWith("--") ? process.argv[++i] : true;
    out[key] = val;
  }
  return out;
}

const args = readArgs();
const skillDir = path.resolve(__dirname, "..");
const outDir = path.resolve(args["out-dir"] || "/Users/poincare/Documents/amazon/outputs/us_summer_live_amazon");
const target = Number(args.target || 60);
const minPrice = Number(args["min-price"] || 10);
const maxPrice = Number(args["max-price"] || 40);
const maxDetails = Number(args["max-details"] || target);
const searchPages = Number(args["search-pages"] || 1);
const delayMs = Number(args["delay-ms"] || 1200);
const timeoutMs = Number(args.timeout || 45000);
const observedAt = new Date().toISOString();

const defaultSeeds = [
  ["water", "beach chair towel cover", "沙滩椅毛巾套"],
  ["water", "sand free beach blanket", "防沙沙滩毯"],
  ["water", "waterproof phone pouch", "手机防水袋"],
  ["water", "dry bag 10l", "防水收纳袋"],
  ["water", "swim goggles adult", "成人泳镜"],
  ["sports", "cooling towel", "冰凉运动毛巾"],
  ["sports", "pickleball paddle cover", "匹克球拍套"],
  ["sports", "agility cones set", "训练标志碟"],
  ["sports", "jump rope mat", "跳绳垫"],
  ["sports", "resistance bands fabric", "布面弹力带"],
  ["garden", "garden hose nozzle", "花园水管喷头"],
  ["garden", "garden kneeler pad", "园艺跪垫"],
  ["garden", "rose pruning gloves", "玫瑰修剪手套"],
  ["garden", "patio umbrella cover", "庭院伞套"],
  ["garden", "garden tool bag", "园艺工具包"],
  ["party", "picnic blanket waterproof", "防水野餐毯"],
  ["party", "outdoor tablecloth waterproof", "户外桌布"],
  ["party", "cooler tote bag", "软体冰包"],
  ["party", "mesh food covers", "户外食物罩"],
  ["party", "utensil caddy outdoor", "户外餐具收纳盒"],
  ["ball", "cornhole bags", "玉米洞沙包"],
  ["ball", "pickleball balls outdoor", "户外匹克球"],
  ["ball", "beach volleyball", "沙滩排球"],
  ["ball", "ball storage mesh bag", "球类收纳网袋"],
  ["ball", "ball pump kit", "球类打气筒"],
  ["toy", "ladder toss game", "梯球游戏"],
  ["toy", "ring toss game outdoor", "户外套圈游戏"],
  ["toy", "yard dice set", "庭院骰子"],
  ["toy", "beach paddle ball set", "沙滩拍球套装"],
  ["toy", "portable scoreboard", "便携计分板"],
  ["apparel", "wide brim sun hat", "宽檐遮阳帽"],
  ["apparel", "water shoes women", "女式涉水鞋"],
  ["apparel", "cooling neck gaiter", "冰感脖套"],
  ["apparel", "beach sarong cover up", "沙滩围巾"],
  ["apparel", "sun visor hat", "空顶遮阳帽"],
  ["electronics", "travel cable organizer", "数码旅行收纳包"],
  ["electronics", "phone sun shade", "手机遮阳罩"],
  ["electronics", "water bottle sling", "水壶斜挎包"],
  ["electronics", "waterproof luggage tags", "防水行李牌"],
  ["electronics", "backpack rain cover", "背包防雨罩"],
  ["pet", "dog cooling mat", "狗狗凉垫"],
  ["pet", "dog car seat cover", "宠物车垫"],
  ["pet", "dog life jacket", "狗狗救生衣"],
  ["pet", "pet travel towel", "宠物速干毛巾"],
  ["pet", "dog car door protector", "车门防抓垫"],
  ["home", "outdoor rug waterproof", "户外地毯"],
  ["home", "outdoor pillow covers", "户外抱枕套"],
  ["home", "patio furniture cover", "庭院家具罩"],
  ["home", "outdoor cushion covers", "户外坐垫套"],
  ["home", "hammock straps", "吊床绑带"],
];

const blockedTitleWords = [
  "seed", "seeds", "liquid", "spray", "lotion", "oil", "gel", "cream", "drink",
  "juice", "fertilizer", "pesticide", "repellent", "insecticide", "bait", "knife",
  "weapon", "gun", "battery", "power bank", "lithium", "sofa", "couch", "mattress",
  "gazebo", "pool pump", "chemical", "weed killer", "fireworks",
];

function loadSeeds() {
  if (!args["seed-file"]) return defaultSeeds.map(([cat, q, zh]) => ({ cat, q, zh }));
  const file = path.resolve(args["seed-file"]);
  const raw = JSON.parse(fs.readFileSync(file, "utf8"));
  return raw.map((x) => Array.isArray(x) ? { cat: x[0], q: x[1], zh: x[2] || x[1] } : x);
}

function requireFrom(root, name) {
  return Module.createRequire(path.join(root, "package.json"))(name);
}

function loadPlaywright() {
  const roots = [
    process.env.PLAYWRIGHT_NODE_ROOT,
    path.join(skillDir, ".runtime"),
    "/Users/poincare/.codex/skills/us-summer-products-research-2026/.runtime",
    "/Users/poincare/.config/opencode/skills/us-summer-products-research-2026/.runtime",
    "/Users/poincare/.claude/skills/us-summer-products-research-2026/.runtime",
    process.cwd(),
  ].filter(Boolean);
  for (const root of roots) {
    try {
      return requireFrom(root, "playwright");
    } catch (_) {}
  }
  throw new Error([
    "Playwright is required for live Amazon crawling.",
    "Install once:",
    `  npm install --prefix ${path.join(skillDir, ".runtime")} playwright`,
    `  npx --prefix ${path.join(skillDir, ".runtime")} playwright install chromium`,
  ].join("\n"));
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function parseMoney(text) {
  if (!text) return 0;
  const m = String(text).replace(/,/g, "").match(/\$?\s*(\d+(?:\.\d{1,2})?)/);
  return m ? Number(m[1]) : 0;
}

function parseIntText(text) {
  if (!text) return 0;
  const m = String(text).replace(/,/g, "").match(/(\d+)/);
  return m ? Number(m[1]) : 0;
}

function parseRating(text) {
  if (!text) return 0;
  const m = String(text).match(/([0-5](?:\.\d)?)/);
  return m ? Number(m[1]) : 0;
}

function titleAllowed(title) {
  const s = String(title || "").toLowerCase();
  return s && !blockedTitleWords.some((w) => s.includes(w));
}

function amazonSearchUrl(keyword, page) {
  const p36 = `${Math.round(minPrice * 100)}-${Math.round(maxPrice * 100)}`;
  const u = new URL("https://www.amazon.com/s");
  u.searchParams.set("k", keyword);
  u.searchParams.set("rh", `p_36:${p36}`);
  if (page > 1) u.searchParams.set("page", String(page));
  return u.toString();
}

async function assertUsablePage(page, context) {
  const text = await page.locator("body").innerText({ timeout: 5000 }).catch(() => "");
  if (/validateCaptcha|Enter the characters you see below|Sorry, we just need to make sure|Robot Check/i.test(text)) {
    throw new Error(`Amazon bot/captcha block while loading ${context}`);
  }
}

async function extractSearchRows(page, seed, pageNo) {
  return page.$$eval("[data-component-type='s-search-result']", (cards, meta) => {
    const money = (text) => {
      const m = String(text || "").replace(/,/g, "").match(/\$?\s*(\d+(?:\.\d{1,2})?)/);
      return m ? Number(m[1]) : 0;
    };
    return cards.map((el, idx) => {
      const text = (sel) => el.querySelector(sel)?.textContent?.trim() || "";
      const href = el.querySelector("h2 a, a.a-link-normal.s-no-outline")?.getAttribute("href") || "";
      const priceText = text(".a-price .a-offscreen") || text(".a-color-base .a-offscreen");
      const ratingText = text(".a-icon-alt");
      const reviewText = text("a[href*='customerReviews'] span, span[aria-label$='ratings']");
      const title = text("h2 span") || text("h2");
      return {
        asin: el.getAttribute("data-asin") || "",
        title,
        price: money(priceText),
        priceText,
        ratingText,
        reviewText,
        rating: Number((ratingText.match(/([0-5](?:\.\d)?)/) || [])[1] || 0),
        reviews: Number((reviewText.replace(/,/g, "").match(/(\d+)/) || [])[1] || 0),
        url: href ? new URL(href, "https://www.amazon.com").toString() : "",
        image: el.querySelector("img.s-image")?.getAttribute("src") || "",
        searchKeyword: meta.keyword,
        cat: meta.cat,
        zh: meta.zh,
        searchPage: meta.pageNo,
        searchRank: (meta.pageNo - 1) * 48 + idx + 1,
      };
    });
  }, { keyword: seed.q, cat: seed.cat, zh: seed.zh, pageNo });
}

async function extractDetail(page, row) {
  if (!row.url) return {};
  await page.goto(row.url, { waitUntil: "domcontentloaded", timeout: timeoutMs });
  await assertUsablePage(page, row.url);
  await page.waitForTimeout(600);
  const bodyText = await page.locator("body").innerText({ timeout: 8000 }).catch(() => "");
  const detail = await page.evaluate(() => {
    const text = (sel) => document.querySelector(sel)?.textContent?.trim() || "";
    const exists = (sel) => Boolean(document.querySelector(sel));
    const price = text("#corePrice_feature_div .a-offscreen") || text(".a-price .a-offscreen");
    const sellerText = text("#merchant-info") || text("#tabular-buybox .tabular-buybox-text");
    return {
      title: text("#productTitle"),
      priceText: price,
      ratingText: text("#acrPopover .a-icon-alt") || text(".reviewCountTextLinkedHistogram .a-icon-alt"),
      reviewsText: text("#acrCustomerReviewText"),
      sellerText,
      imageCount: document.querySelectorAll("#altImages img").length,
      hasAplus: exists("#aplus, #aplus_feature_div"),
      hasVideo: exists("[data-video-url], #videoBlock, .vse-video-content"),
      availability: text("#availability"),
    };
  });
  const rankMatch = bodyText.match(/Best Sellers Rank\s*#?\s*([\d,]+)\s+in\s+([^\n#(]+)/i);
  detail.bsr = rankMatch ? `#${rankMatch[1]} in ${rankMatch[2].trim()}` : "";
  detail.bsrNumber = rankMatch ? parseIntText(rankMatch[1]) : 0;
  detail.price = parseMoney(detail.priceText) || row.price;
  detail.rating = parseRating(detail.ratingText) || row.rating;
  detail.reviews = parseIntText(detail.reviewsText) || row.reviews;
  detail.amazonSelf = /sold by amazon\.com|ships from amazon\.com/i.test(detail.sellerText);
  return detail;
}

function estimateSales(row, detail) {
  const rank = detail.bsrNumber || row.searchRank * 900;
  const reviewSignal = Math.min(12000, Math.max(200, Math.round((detail.reviews || row.reviews || 0) * 0.08)));
  const rankSignal = Math.max(80, Math.round(180000 / Math.sqrt(Math.max(rank, 1))));
  return Math.max(60, Math.round((reviewSignal + rankSignal) / 2));
}

function toProduct(row, detail, id) {
  const price = detail.price || row.price;
  const sales = estimateSales(row, detail);
  const cost = Math.round(price * 0.28 * 100) / 100;
  const fba = Math.round(Math.max(3.19, Math.min(8.99, price * 0.16)) * 100) / 100;
  const refRate = 15;
  const refFee = price * refRate / 100;
  const margin = Math.round((price - cost - fba - refFee - cost * 0.15) / price * 100);
  const keyword = row.searchKeyword;
  return {
    id,
    cat: row.cat,
    name: `${row.zh} (${keyword})`,
    en: (detail.title || row.title).slice(0, 150),
    price,
    range: `$${minPrice.toFixed(2)}-$${maxPrice.toFixed(2)}`,
    rating: detail.rating || row.rating,
    reviews: detail.reviews || row.reviews,
    bsr: detail.bsr || `Amazon search rank ${row.searchRank} for "${keyword}"`,
    kw: [keyword, `${keyword} amazon`, `${keyword} for summer`, `outdoor ${keyword}`, `${keyword} ${new Date().getFullYear()}`],
    sv: [0, 0, 0, 0, 0],
    cost,
    fba,
    refRate,
    margin,
    sales,
    revenue: Math.round(price * sales),
    revGrowth: 0,
    sellers: 0,
    amazSelf: Boolean(detail.amazonSelf),
    season: "Amazon live crawl summer candidate; demand trend requires separate Google Trends validation",
    peakMon: "5-8月待交叉验证",
    imgs: detail.imageCount || 0,
    aplus: Boolean(detail.hasAplus),
    video: Boolean(detail.hasVideo),
    pains: ["评论痛点需二次抓取评论验证", "价格带需持续监控", "同款竞争需人工复核"],
    improve: "基于实时页面先做价格/评分/评论/BSR筛选+后续补充评论痛点和供应链报价",
    tags: ["trend"],
    evidence: {
      observedAt,
      source: "amazon_live_playwright",
      asin: row.asin,
      url: row.url,
      searchKeyword: keyword,
      searchRank: row.searchRank,
      detailCaptured: Boolean(detail.title || detail.bsr || detail.price),
    },
  };
}

async function main() {
  fs.mkdirSync(outDir, { recursive: true });
  if (args["dry-run"]) {
    const seeds = loadSeeds();
    fs.writeFileSync(path.join(outDir, "seed-plan.json"), JSON.stringify({ observedAt, minPrice, maxPrice, target, seeds }, null, 2));
    console.log(JSON.stringify({ ok: true, dryRun: true, outDir, seeds: seeds.length, minPrice, maxPrice, target }, null, 2));
    return;
  }

  const { chromium } = loadPlaywright();
  const seeds = loadSeeds();
  const browser = await chromium.launch({
    headless: args.headful ? false : true,
    args: ["--disable-blink-features=AutomationControlled", "--no-sandbox"],
  });
  const context = await browser.newContext({
    locale: "en-US",
    timezoneId: "America/Los_Angeles",
    viewport: { width: 1365, height: 900 },
    userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
  });
  const page = await context.newPage();
  const detailPage = await context.newPage();
  const raw = [];
  const byAsin = new Map();
  const failures = [];

  try {
    for (const seed of seeds) {
      for (let p = 1; p <= searchPages; p++) {
        const url = amazonSearchUrl(seed.q, p);
        try {
          await page.goto(url, { waitUntil: "domcontentloaded", timeout: timeoutMs });
          await assertUsablePage(page, url);
          await page.waitForTimeout(800);
          const rows = await extractSearchRows(page, seed, p);
          raw.push(...rows.map((x) => ({ ...x, searchUrl: url, observedAt })));
          for (const row of rows) {
            if (!row.asin || byAsin.has(row.asin)) continue;
            if (row.price < minPrice || row.price > maxPrice) continue;
            if (!titleAllowed(row.title)) continue;
            if (!row.rating || !row.reviews) continue;
            byAsin.set(row.asin, { ...row, searchUrl: url, observedAt });
            if (byAsin.size >= target) break;
          }
        } catch (error) {
          failures.push({ seed: seed.q, page: p, url, error: error.message });
        }
        if (byAsin.size >= target) break;
        await sleep(delayMs);
      }
      if (byAsin.size >= target) break;
    }

    const selected = Array.from(byAsin.values()).slice(0, target);
    const details = [];
    for (const row of selected.slice(0, maxDetails)) {
      try {
        const detail = await extractDetail(detailPage, row);
        details.push({ asin: row.asin, url: row.url, observedAt, detail });
      } catch (error) {
        failures.push({ asin: row.asin, url: row.url, error: error.message });
        details.push({ asin: row.asin, url: row.url, observedAt, detail: {} });
      }
      await sleep(delayMs);
    }
    const detailByAsin = new Map(details.map((d) => [d.asin, d.detail || {}]));
    const products = selected.map((row, i) => toProduct(row, detailByAsin.get(row.asin) || {}, i + 1));

    fs.writeFileSync(path.join(outDir, "amazon-live-raw.json"), JSON.stringify({ observedAt, minPrice, maxPrice, raw, selected, details, failures }, null, 2));
    fs.writeFileSync(path.join(outDir, "amazon-live-evidence.jsonl"), products.map((p) => JSON.stringify(p.evidence)).join("\n") + "\n");
    fs.writeFileSync(path.join(outDir, "products.normalized.json"), JSON.stringify(products, null, 2));
    fs.writeFileSync(path.join(outDir, "summary.json"), JSON.stringify({
      observedAt,
      sourceBoundary: "Amazon pages crawled live with Playwright. Sales, sourcing cost, FBA fee, revenue, growth, seller count, trend volume, pain points, and differentiation remain estimates/placeholders unless enriched by separate evidence.",
      minPrice,
      maxPrice,
      target,
      rawCards: raw.length,
      selectedProducts: selected.length,
      detailPagesAttempted: Math.min(selected.length, maxDetails),
      products: products.length,
      failures,
    }, null, 2));
    console.log(JSON.stringify({ ok: true, outDir, products: products.length, rawCards: raw.length, failures: failures.length, observedAt }, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});
