#!/usr/bin/env bash
set -euo pipefail

DEFAULT_HTML="/Users/poincare/Desktop/us-summer-products-research-2026-live-amazon.html"
DEFAULT_OUT_DIR="/Users/poincare/Documents/amazon/outputs/us_summer_live_amazon"
CODEX_SKILL="/Users/poincare/.codex/skills/us-summer-products-research-2026"
CLAUDE_SKILL="/Users/poincare/.claude/skills/us-summer-products-research-2026"
OPENCODE_SKILL="/Users/poincare/.config/opencode/skills/us-summer-products-research-2026"
GLOBAL_WRAPPER="/Volumes/金阳/brain/scripts/us-summer-products-research-2026.sh"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

usage() {
  cat <<'EOF'
US summer products report 6.0b runner.

Commands:
  run [--out HTML] [--out-dir DIR] [--min-price N] [--max-price N] [--target N]
      Crawl live Amazon pages with Playwright, structure observed data, and render HTML.
  demo-run [--out HTML] [--out-dir DIR]
      Render the legacy deterministic demo dataset. Not valid as fresh market research.
  install-deps
      Install Playwright into the skill runtime.
  copy-original [--out HTML]
      Copy the original source report byte-for-byte.
  normalize-render --input RAW_JSON_OR_CSV [--out HTML] [--out-dir DIR]
      Normalize raw rows to the report data model, then render HTML.
  render-data --data PRODUCTS_JSON [--out HTML]
      Render HTML from already-normalized products JSON.
  verify
      Run syntax checks, byte-for-byte copy check, and low-risk report smoke test.
  install-all
      Sync this skill into Codex, Claude Code, and OpenCode/free-code skill folders.

Default final HTML:
  /Users/poincare/Desktop/us-summer-products-research-2026-live-amazon.html
EOF
}

json_quote() {
  node -e 'process.stdout.write(JSON.stringify(process.argv[1]))' "$1"
}

die() {
  echo "ERROR: $*" >&2
  exit 1
}

need_file() {
  [[ -f "$1" ]] || die "missing file: $1"
}

need_exe() {
  [[ -x "$1" ]] || die "missing executable: $1"
}

parse_run_args() {
  OUT_HTML="$DEFAULT_HTML"
  OUT_DIR="$DEFAULT_OUT_DIR"
  MIN_PRICE=10
  MAX_PRICE=40
  TARGET=60
  MAX_DETAILS="$TARGET"
  SEARCH_PAGES=1
  DELAY_MS=1200
  HEADFUL=0
  SEED_FILE=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --out) OUT_HTML="$2"; shift 2 ;;
      --out-dir) OUT_DIR="$2"; shift 2 ;;
      --min-price) MIN_PRICE="$2"; shift 2 ;;
      --max-price) MAX_PRICE="$2"; shift 2 ;;
      --target) TARGET="$2"; MAX_DETAILS="$2"; shift 2 ;;
      --max-details) MAX_DETAILS="$2"; shift 2 ;;
      --search-pages) SEARCH_PAGES="$2"; shift 2 ;;
      --delay-ms) DELAY_MS="$2"; shift 2 ;;
      --seed-file) SEED_FILE="$2"; shift 2 ;;
      --headful) HEADFUL=1; shift ;;
      *) die "unknown argument: $1" ;;
    esac
  done
}

summarize_html() {
  local html="$1"
  local data_dir="${2:-}"
  local min_price="${3:-0}"
  local max_price="${4:-999999}"
  HTML_PATH="$html" DATA_DIR="$data_dir" MIN_PRICE="$min_price" MAX_PRICE="$max_price" node <<'NODE'
const fs = require("fs");
const vm = require("vm");
const htmlPath = process.env.HTML_PATH;
const minPrice = Number(process.env.MIN_PRICE || 0);
const maxPrice = Number(process.env.MAX_PRICE || 999999);
const html = fs.readFileSync(htmlPath, "utf8");
const m = html.match(/const P=(\[[\s\S]*?\]);\n\n\/\/ ===== RENDER =====/);
if (!m) throw new Error("const P data block not found");
const products = vm.runInNewContext(m[1]);
const categories = {};
for (const p of products) categories[p.cat] = (categories[p.cat] || 0) + 1;
const badPrice = products.filter((p) => p.price < minPrice || p.price > maxPrice).length;
const incomplete = products.filter((p) => !p.sales || !p.revenue || !p.cost || !p.fba || !p.kw?.length || !p.pains?.length).length;
console.log(JSON.stringify({ html: htmlPath, dataDir: process.env.DATA_DIR || undefined, products: products.length, categories, priceGate: { minPrice, maxPrice }, badPrice, incomplete }, null, 2));
NODE
}

cmd_run() {
  parse_run_args "$@"
  need_exe "$SKILL_DIR/scripts/live_amazon_crawl.js"
  need_exe "$SKILL_DIR/scripts/render_report.js"
  crawl_args=(--out-dir "$OUT_DIR" --min-price "$MIN_PRICE" --max-price "$MAX_PRICE" --target "$TARGET" --max-details "$MAX_DETAILS" --search-pages "$SEARCH_PAGES" --delay-ms "$DELAY_MS")
  if [[ -n "$SEED_FILE" ]]; then crawl_args+=(--seed-file "$SEED_FILE"); fi
  if [[ "$HEADFUL" -eq 1 ]]; then crawl_args+=(--headful); fi
  node "$SKILL_DIR/scripts/live_amazon_crawl.js" "${crawl_args[@]}"
  node "$SKILL_DIR/scripts/render_report.js" --data "$OUT_DIR/products.normalized.json" --out "$OUT_HTML" --force-render
  summarize_html "$OUT_HTML" "$OUT_DIR" "$MIN_PRICE" "$MAX_PRICE"
}

cmd_demo_run() {
  OUT_HTML="/Users/poincare/Desktop/us-summer-products-research-2026-demo-static.html"
  OUT_DIR="/Users/poincare/Documents/amazon/outputs/us_summer_demo_static"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --out) OUT_HTML="$2"; shift 2 ;;
      --out-dir) OUT_DIR="$2"; shift 2 ;;
      *) die "unknown argument: $1" ;;
    esac
  done
  need_exe "$SKILL_DIR/scripts/build_us_summer_lowrisk_2026_data.js"
  need_exe "$SKILL_DIR/scripts/normalize_products.js"
  need_exe "$SKILL_DIR/scripts/render_report.js"
  node "$SKILL_DIR/scripts/build_us_summer_lowrisk_2026_data.js" --out-dir "$OUT_DIR"
  node "$SKILL_DIR/scripts/normalize_products.js" --input "$OUT_DIR/raw-products.json" --out "$OUT_DIR/products.normalized.json" --strict
  node "$SKILL_DIR/scripts/render_report.js" --data "$OUT_DIR/products.normalized.json" --out "$OUT_HTML" --force-render
  summarize_html "$OUT_HTML" "$OUT_DIR" 10 40
}

cmd_install_deps() {
  mkdir -p "$SKILL_DIR/.runtime"
  npm install --prefix "$SKILL_DIR/.runtime" playwright
  npx --prefix "$SKILL_DIR/.runtime" playwright install chromium
}

cmd_copy_original() {
  OUT_HTML="/Users/poincare/Desktop/us-summer-products-research-2026-copy.html"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --out) OUT_HTML="$2"; shift 2 ;;
      *) die "unknown argument: $1" ;;
    esac
  done
  node "$SKILL_DIR/scripts/render_report.js" --out "$OUT_HTML"
  cmp -s "$SKILL_DIR/assets/source-report.html" "$OUT_HTML" || die "copy did not match source template"
  summarize_html "$OUT_HTML" "" 0 999999
}

cmd_render_data() {
  OUT_HTML="$DEFAULT_HTML"
  DATA=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --data) DATA="$2"; shift 2 ;;
      --out) OUT_HTML="$2"; shift 2 ;;
      *) die "unknown argument: $1" ;;
    esac
  done
  [[ -n "$DATA" ]] || die "--data is required"
  need_file "$DATA"
  node "$SKILL_DIR/scripts/render_report.js" --data "$DATA" --out "$OUT_HTML" --force-render
  summarize_html "$OUT_HTML" "$(dirname "$DATA")" 0 999999
}

cmd_normalize_render() {
  OUT_HTML="$DEFAULT_HTML"
  OUT_DIR="$DEFAULT_OUT_DIR"
  INPUT=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --input) INPUT="$2"; shift 2 ;;
      --out) OUT_HTML="$2"; shift 2 ;;
      --out-dir) OUT_DIR="$2"; shift 2 ;;
      *) die "unknown argument: $1" ;;
    esac
  done
  [[ -n "$INPUT" ]] || die "--input is required"
  need_file "$INPUT"
  mkdir -p "$OUT_DIR"
  node "$SKILL_DIR/scripts/normalize_products.js" --input "$INPUT" --out "$OUT_DIR/products.normalized.json" --strict
  node "$SKILL_DIR/scripts/render_report.js" --data "$OUT_DIR/products.normalized.json" --out "$OUT_HTML" --force-render
  summarize_html "$OUT_HTML" "$OUT_DIR" 0 999999
}

cmd_verify() {
  node --check "$SKILL_DIR/scripts/render_report.js"
  node --check "$SKILL_DIR/scripts/analyze_frontend.js"
  node --check "$SKILL_DIR/scripts/normalize_products.js"
  node --check "$SKILL_DIR/scripts/build_us_summer_lowrisk_2026_data.js"
  node --check "$SKILL_DIR/scripts/live_amazon_crawl.js"
  local tmp_html="/tmp/us-summer-products-6b-copy.html"
  local tmp_run_html="/tmp/us-summer-products-6b-run.html"
  local tmp_data="/tmp/us-summer-products-6b-data"
  node "$SKILL_DIR/scripts/render_report.js" --out "$tmp_html"
  cmp -s "$SKILL_DIR/assets/source-report.html" "$tmp_html" || die "copy verification failed"
  node "$SKILL_DIR/scripts/live_amazon_crawl.js" --dry-run --out-dir "$tmp_data" --target 3 --min-price 10 --max-price 40 >/tmp/us-summer-products-6b-live-dry-run.log
  cmd_demo_run --out "$tmp_run_html" --out-dir "$tmp_data/demo-static" >/tmp/us-summer-products-6b-run.log
  HTML_PATH="$tmp_run_html" node <<'NODE'
const fs = require("fs");
const vm = require("vm");
const html = fs.readFileSync(process.env.HTML_PATH, "utf8");
const m = html.match(/const P=(\[[\s\S]*?\]);\n\n\/\/ ===== RENDER =====/);
if (!m) throw new Error("const P data block not found");
const products = vm.runInNewContext(m[1]);
const categories = {};
for (const p of products) categories[p.cat] = (categories[p.cat] || 0) + 1;
const badPrice = products.filter((p) => p.price < 10 || p.price > 40).length;
const incomplete = products.filter((p) => !p.sales || !p.revenue || !p.cost || !p.fba || !p.kw?.length || !p.pains?.length).length;
if (products.length !== 110) throw new Error(`expected 110 products, got ${products.length}`);
if (Object.keys(categories).length !== 10) throw new Error(`expected 10 categories, got ${Object.keys(categories).length}`);
for (const [cat, count] of Object.entries(categories)) {
  if (count !== 11) throw new Error(`expected 11 products in ${cat}, got ${count}`);
}
  if (badPrice !== 0) throw new Error(`badPrice=${badPrice}`);
  if (incomplete !== 0) throw new Error(`incomplete=${incomplete}`);
console.log(JSON.stringify({ ok: true, html: process.env.HTML_PATH, liveCrawlerSyntax: true, liveCrawlerDryRun: true, demoProducts: products.length, categories, badPrice, incomplete }, null, 2));
NODE
}

sync_to() {
  local target="$1"
  mkdir -p "$(dirname "$target")"
  if [[ "$(cd "$SKILL_DIR" && pwd)" == "$(mkdir -p "$target" && cd "$target" && pwd)" ]]; then
    return 0
  fi
  rm -rf "$target"
  mkdir -p "$target"
  (cd "$SKILL_DIR" && tar cf - .) | (cd "$target" && tar xf -)
  rm -rf "$target/.runtime" "$target/node_modules"
  chmod +x "$target"/scripts/* 2>/dev/null || true
}

rewrite_skill_paths() {
  local target="$1"
  local escaped
  escaped="$(printf '%s\n' "$target" | sed 's/[\/&]/\\&/g')"
  if [[ -f "$target/SKILL.md" ]]; then
    perl -0pi -e "s#/Users/poincare/\\.(?:codex|claude)/skills/us-summer-products-research-2026#$target#g; s#/Users/poincare/\\.config/opencode/skills/us-summer-products-research-2026#$target#g" "$target/SKILL.md"
  fi
}

cmd_install_all() {
  sync_to "$CODEX_SKILL"
  sync_to "$CLAUDE_SKILL"
  sync_to "$OPENCODE_SKILL"
  rewrite_skill_paths "$CODEX_SKILL"
  rewrite_skill_paths "$CLAUDE_SKILL"
  rewrite_skill_paths "$OPENCODE_SKILL"
  mkdir -p "$(dirname "$GLOBAL_WRAPPER")"
  cat >"$GLOBAL_WRAPPER" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
for skill_dir in \
  "/Users/poincare/.config/opencode/skills/us-summer-products-research-2026" \
  "/Users/poincare/.claude/skills/us-summer-products-research-2026" \
  "/Users/poincare/.codex/skills/us-summer-products-research-2026"; do
  if [[ -x "$skill_dir/scripts/us_summer_6b.sh" ]]; then
    exec "$skill_dir/scripts/us_summer_6b.sh" run "$@"
  fi
done
echo "ERROR: us-summer-products-research-2026 skill not installed" >&2
exit 1
EOF
  chmod +x "$GLOBAL_WRAPPER"
  echo "{\"ok\":true,\"codex\":\"$CODEX_SKILL\",\"claude\":\"$CLAUDE_SKILL\",\"opencode\":\"$OPENCODE_SKILL\",\"wrapper\":\"$GLOBAL_WRAPPER\"}"
}

cmd="${1:-run}"
if [[ $# -gt 0 ]]; then shift; fi
case "$cmd" in
  run|report) cmd_run "$@" ;;
  demo-run|demo) cmd_demo_run "$@" ;;
  install-deps) cmd_install_deps "$@" ;;
  copy-original|copy) cmd_copy_original "$@" ;;
  normalize-render) cmd_normalize_render "$@" ;;
  render-data) cmd_render_data "$@" ;;
  verify) cmd_verify "$@" ;;
  install-all) cmd_install_all "$@" ;;
  help|-h|--help) usage ;;
  *) die "unknown command: $cmd" ;;
esac
