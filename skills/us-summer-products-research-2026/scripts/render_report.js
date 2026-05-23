#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

function readArgs() {
  const args = {};
  for (let i = 2; i < process.argv.length; i++) {
    const token = process.argv[i];
    if (!token.startsWith("--")) continue;
    const key = token.slice(2);
    const val = process.argv[i + 1] && !process.argv[i + 1].startsWith("--") ? process.argv[++i] : true;
    args[key] = val;
  }
  return args;
}

function jsLiteral(value) {
  return JSON.stringify(value, null, 2).replace(/<\/script/gi, "<\\/script");
}

function validateProducts(products) {
  if (!Array.isArray(products) || products.length === 0) throw new Error("data must be a non-empty product array");
  const required = [
    "id", "cat", "name", "en", "price", "range", "rating", "reviews", "bsr",
    "kw", "sv", "cost", "fba", "refRate", "sales", "revenue", "season",
    "peakMon", "pains", "improve", "tags",
  ];
  const missing = [];
  for (const [idx, p] of products.entries()) {
    for (const field of required) if (!(field in p)) missing.push(`row ${idx + 1}: ${field}`);
    if (Array.isArray(p.kw) && Array.isArray(p.sv) && p.kw.length !== p.sv.length) {
      missing.push(`row ${idx + 1}: kw and sv length mismatch`);
    }
  }
  if (missing.length) throw new Error(`product data validation failed:\n${missing.slice(0, 40).join("\n")}`);
}

const args = readArgs();
const skillDir = path.resolve(__dirname, "..");
const sourcePath = path.resolve(args.source || path.join(skillDir, "assets/source-report.html"));
const dataPath = args.data ? path.resolve(args.data) : path.join(skillDir, "references/products.json");
const outPath = path.resolve(args.out || path.join(process.cwd(), "us-summer-products-research-2026.html"));

fs.mkdirSync(path.dirname(outPath), { recursive: true });

if (!args.data && !args["force-render"]) {
  fs.copyFileSync(sourcePath, outPath);
  console.log(`Copied byte-for-byte source report: ${outPath}`);
  process.exit(0);
}

const html = fs.readFileSync(sourcePath, "utf8");
const products = JSON.parse(fs.readFileSync(dataPath, "utf8"));
validateProducts(products);

let rendered = html.replace(
  /const P=\[[\s\S]*?\n\];\n\n\/\/ ===== RENDER =====/,
  `const P=${jsLiteral(products)};\n\n// ===== RENDER =====`,
);
rendered = rendered.replace(
  /<div class="n" id="totalCount">.*?<\/div>/,
  `<div class="n" id="totalCount">${products.length}</div>`,
);
fs.writeFileSync(outPath, rendered, "utf8");
console.log(`Rendered report: ${outPath}`);
