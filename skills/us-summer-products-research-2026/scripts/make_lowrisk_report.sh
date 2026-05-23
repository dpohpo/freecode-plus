#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_HTML="/Users/poincare/Desktop/us-summer-products-research-2026-lowrisk-amazon.html"
OUT_DIR="/Users/poincare/Documents/amazon/outputs/us_summer_lowrisk_2026"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out)
      OUT_HTML="$2"
      shift 2
      ;;
    --out-dir)
      OUT_DIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

node "$SKILL_DIR/scripts/build_us_summer_lowrisk_2026_data.js" --out-dir "$OUT_DIR"
node "$SKILL_DIR/scripts/normalize_products.js" \
  --input "$OUT_DIR/raw-products.json" \
  --out "$OUT_DIR/products.normalized.json" \
  --strict
node "$SKILL_DIR/scripts/render_report.js" \
  --data "$OUT_DIR/products.normalized.json" \
  --out "$OUT_HTML" \
  --force-render

HTML_PATH="$OUT_HTML" DATA_DIR="$OUT_DIR" node <<'NODE'
const fs = require("fs");
const vm = require("vm");
const htmlPath = process.env.HTML_PATH;
const html = fs.readFileSync(htmlPath, "utf8");
const products = vm.runInNewContext(html.match(/const P=(\[[\s\S]*?\]);\n\n\/\/ ===== RENDER =====/)[1]);
const cats = {};
for (const p of products) cats[p.cat] = (cats[p.cat] || 0) + 1;
const badPrice = products.filter((p) => p.price < 10 || p.price > 40).length;
const incomplete = products.filter((p) => !p.sales || !p.revenue || !p.cost || !p.fba || !p.kw?.length || !p.pains?.length).length;
console.log(JSON.stringify({
  html: htmlPath,
  dataDir: process.env.DATA_DIR,
  products: products.length,
  categories: cats,
  badPrice,
  incomplete
}, null, 2));
NODE
