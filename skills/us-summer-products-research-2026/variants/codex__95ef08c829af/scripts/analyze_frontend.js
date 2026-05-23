#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const vm = require("vm");

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : fallback;
}

const skillDir = path.resolve(__dirname, "..");
const sourcePath = path.resolve(arg("source", path.join(skillDir, "assets/source-report.html")));
const outDir = path.resolve(arg("out-dir", path.join(skillDir, "references")));
const html = fs.readFileSync(sourcePath, "utf8");

function mustMatch(re, label) {
  const m = html.match(re);
  if (!m) throw new Error(`${label} not found in ${sourcePath}`);
  return m;
}

const productBlock = mustMatch(/const P=\[([\s\S]*?)\n\];\n\n\/\/ ===== RENDER =====/, "product block")[1];
const products = vm.runInNewContext(`[${productBlock}\n]`);
const style = mustMatch(/<style>([\s\S]*?)<\/style>/, "style block")[1];
const script = mustMatch(/<script>([\s\S]*?)<\/script>/, "script block")[1];

const selectors = [...style.matchAll(/(?:^|\})([^{}]+)\{/g)]
  .map((m) => m[1].trim())
  .filter(Boolean);
const cssVariables = {};
const root = style.match(/:root\{([^}]*)\}/);
if (root) {
  for (const part of root[1].split(";")) {
    const [k, v] = part.split(":");
    if (k && v) cssVariables[k.trim()] = v.trim();
  }
}

const classUses = {};
for (const m of html.matchAll(/class="([^"]+)"/g)) {
  for (const cls of m[1].split(/\s+/)) classUses[cls] = (classUses[cls] || 0) + 1;
}

const inlineEvents = [...html.matchAll(/\s(on\w+)="([^"]+)"/g)].map((m) => ({
  event: m[1],
  handler: m[2],
}));

const functions = [...script.matchAll(/function\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)/g)].map((m) => ({
  name: m[1],
  args: m[2].split(",").map((x) => x.trim()).filter(Boolean),
}));

const categories = [...new Set(products.map((p) => p.cat))];
const categoryCounts = Object.fromEntries(
  categories.map((cat) => [cat, products.filter((p) => p.cat === cat).length]),
);
const tagCounts = {};
for (const p of products) for (const t of p.tags || []) tagCounts[t] = (tagCounts[t] || 0) + 1;

const fields = [...new Set(products.flatMap((p) => Object.keys(p)))].sort();
const labels = {
  header: {
    title: html.match(/<h1>(.*?)<\/h1>/)?.[1] || "",
    subtitle: html.match(/<div class="sub">(.*?)<\/div>/)?.[1] || "",
    date: html.match(/<div class="date">(.*?)<\/div>/)?.[1] || "",
  },
  stats: [...html.matchAll(/<div class="stat-card"><div class="n"[^>]*>(.*?)<\/div><div class="l">(.*?)<\/div><\/div>/g)]
    .map((m) => ({ value: m[1], label: m[2] })),
  filters: [...html.matchAll(/<button[^>]*onclick="filterCat\('([^']+)',this\)"[^>]*>(.*?)<\/button>/g)]
    .map((m) => ({ cat: m[1], label: m[2] })),
  searchPlaceholder: html.match(/<input class="search-box" placeholder="([^"]+)"/)?.[1] || "",
  detailSections: [...script.matchAll(/<h4>(.*?)<\/h4>/g)].map((m) => m[1]),
  footer: [...html.matchAll(/<div class="footer">([\s\S]*?)<\/div>/g)][0]?.[1]
    .match(/<p[^>]*>(.*?)<\/p>/g)
    ?.map((p) => p.replace(/<[^>]+>/g, "")) || [],
};

const inventory = {
  source: sourcePath,
  analyzedAt: new Date().toISOString(),
  html: {
    title: html.match(/<title>(.*?)<\/title>/)?.[1] || "",
    lang: html.match(/<html lang="([^"]+)"/)?.[1] || "",
    staticLineCount: html.split(/\r?\n/).length,
  },
  data: {
    productCount: products.length,
    categories,
    categoryCounts,
    tagCounts,
    fields,
  },
  css: {
    variables: cssVariables,
    selectorCount: selectors.length,
    selectors,
    classUses,
  },
  events: inlineEvents,
  functions,
  labels,
};

fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(path.join(outDir, "products.json"), JSON.stringify(products, null, 2));
fs.writeFileSync(path.join(outDir, "frontend-inventory.json"), JSON.stringify(inventory, null, 2));
fs.writeFileSync(
  path.join(outDir, "categories.json"),
  JSON.stringify({ categories, categoryCounts, tagCounts }, null, 2),
);
console.log(JSON.stringify({
  products: products.length,
  categories: categoryCounts,
  tags: tagCounts,
  selectors: selectors.length,
  events: inlineEvents.length,
  outDir,
}, null, 2));
