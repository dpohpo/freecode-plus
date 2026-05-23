#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JYAMZON_REPO_DEFAULT="/Users/poincare/Documents/amazon"
US_SKILL_DEFAULT="/Users/poincare/.codex/skills/us-summer-products-research-2026"
BACKUP_ROOT_DEFAULT="/Users/poincare/Documents/amazon/outputs/report_amz_codex_backup"
CLAUDE_SKILL="/Users/poincare/.claude/skills/report-amz"
OPENCODE_SKILL="/Users/poincare/.config/opencode/skills/report-amz"
CODEX_SKILL="/Users/poincare/.codex/skills/report-amz"
GLOBAL_WRAPPER="/Volumes/金阳/brain/scripts/report-amz.sh"

usage() {
  cat <<'EOF'
report-amz: jyamzon data acquisition + us-summer frontend renderer.

Usage:
  report_amz.sh [--target N] [--min-price N] [--max-price N] [--out-dir DIR] [--desktop-name NAME]
                [--mode search|new-releases] [--search-timeout N] [--timeout N]
  report_amz.sh --dry-run
  report_amz.sh --verify
  report_amz.sh --install-all

Defaults:
  backup root: /Users/poincare/Documents/amazon/outputs/report_amz_codex_backup
  data:        jyamzon crawler only
  frontend:    us-summer-products-research-2026 render_report.js only
EOF
}

die() {
  echo "ERROR: $*" >&2
  exit 1
}

timestamp() {
  date +"%Y%m%d_%H%M%S"
}

RUN_ID="run_$(timestamp)_$$"
BACKUP_ROOT="$BACKUP_ROOT_DEFAULT"
OUT_DIR=""
HTML=""
DESKTOP_NAME=""
JYAMZON_REPO="$JYAMZON_REPO_DEFAULT"
US_SKILL="$US_SKILL_DEFAULT"
TARGET=60
MIN_PRICE=30
MAX_PRICE=60
MAX_PAGES=80
MAX_DETAILS=0
SLEEP=0.35
TIMEOUT=15
SEARCH_TIMEOUT=6
MAX_PRODUCTS_PER_SEED=2
SEED_FILE=""
MODE="search"
DRY_RUN=0
VERIFY=0
INSTALL_ALL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --backup-root) BACKUP_ROOT="$2"; shift 2 ;;
    --out-dir) OUT_DIR="$2"; shift 2 ;;
    --html) HTML="$2"; shift 2 ;;
    --desktop-name) DESKTOP_NAME="$2"; shift 2 ;;
    --jyamzon-repo) JYAMZON_REPO="$2"; shift 2 ;;
    --us-skill) US_SKILL="$2"; shift 2 ;;
    --target) TARGET="$2"; shift 2 ;;
    --min-price) MIN_PRICE="$2"; shift 2 ;;
    --max-price) MAX_PRICE="$2"; shift 2 ;;
    --max-pages) MAX_PAGES="$2"; shift 2 ;;
    --max-details) MAX_DETAILS="$2"; shift 2 ;;
    --sleep) SLEEP="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    --search-timeout) SEARCH_TIMEOUT="$2"; shift 2 ;;
    --max-products-per-seed) MAX_PRODUCTS_PER_SEED="$2"; shift 2 ;;
    --seed-file) SEED_FILE="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --verify) VERIFY=1; shift ;;
    --install-all) INSTALL_ALL=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

if [[ -z "$OUT_DIR" ]]; then
  OUT_DIR="$BACKUP_ROOT/$RUN_ID"
fi
if [[ -z "$HTML" ]]; then
  HTML="$OUT_DIR/report.html"
fi

sync_to() {
  local target="$1"
  mkdir -p "$(dirname "$target")"
  if [[ "$(cd "$SKILL_DIR" && pwd)" == "$(mkdir -p "$target" && cd "$target" && pwd)" ]]; then
    return 0
  fi
  rm -rf "$target"
  mkdir -p "$target"
  (cd "$SKILL_DIR" && tar cf - .) | (cd "$target" && tar xf -)
  chmod +x "$target"/scripts/* 2>/dev/null || true
}

rewrite_skill_paths() {
  local target="$1"
  if [[ -f "$target/SKILL.md" ]]; then
    perl -0pi -e "s#/Users/poincare/\\.(?:codex|claude)/skills/report-amz#$target#g; s#/Users/poincare/\\.config/opencode/skills/report-amz#$target#g" "$target/SKILL.md"
  fi
}

install_all() {
  sync_to "$CODEX_SKILL"
  sync_to "$CLAUDE_SKILL"
  sync_to "$OPENCODE_SKILL"
  rewrite_skill_paths "$CODEX_SKILL"
  rewrite_skill_paths "$CLAUDE_SKILL"
  rewrite_skill_paths "$OPENCODE_SKILL"
  mkdir -p "$(dirname "$GLOBAL_WRAPPER")"
  python3 - "$GLOBAL_WRAPPER" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
path.write_text("""#!/usr/bin/env bash
set -euo pipefail
for skill_dir in \
  "/Users/poincare/.config/opencode/skills/report-amz" \
  "/Users/poincare/.claude/skills/report-amz" \
  "/Users/poincare/.codex/skills/report-amz"; do
  if [[ -x "$skill_dir/scripts/report_amz.sh" ]]; then
    exec "$skill_dir/scripts/report_amz.sh" "$@"
  fi
done
echo "ERROR: report-amz skill not installed" >&2
exit 1
""", encoding="utf-8")
PY
  chmod +x "$GLOBAL_WRAPPER"
  echo "{\"ok\":true,\"codex\":\"$CODEX_SKILL\",\"claude\":\"$CLAUDE_SKILL\",\"opencode\":\"$OPENCODE_SKILL\",\"wrapper\":\"$GLOBAL_WRAPPER\"}"
}

verify() {
  python3 -m py_compile "$SKILL_DIR/scripts/build_report_amz_data.py"
  [[ -f "$JYAMZON_REPO/scripts/crawl_amazon_3c_bsr_new_releases.py" ]] || die "jyamzon crawler missing: $JYAMZON_REPO"
  [[ -x "$US_SKILL/scripts/render_report.js" || -f "$US_SKILL/scripts/render_report.js" ]] || die "us renderer missing: $US_SKILL"
  "$SKILL_DIR/scripts/build_report_amz_data.py" --dry-run --jyamzon-repo "$JYAMZON_REPO" --out-dir "/tmp/report-amz-verify-$USER"
  node --check "$US_SKILL/scripts/render_report.js"
  echo "{\"ok\":true,\"data\":\"jyamzon\",\"frontend\":\"us-summer-products-research-2026\",\"dryRun\":true}"
}

if [[ "$INSTALL_ALL" -eq 1 ]]; then
  install_all
  exit 0
fi

if [[ "$VERIFY" -eq 1 ]]; then
  verify
  exit 0
fi

mkdir -p "$OUT_DIR"

if [[ "$MAX_DETAILS" -eq 0 ]]; then
  MAX_DETAILS=$(( TARGET * 6 ))
fi

build_args=(
  --jyamzon-repo "$JYAMZON_REPO"
  --out-dir "$OUT_DIR"
  --mode "$MODE"
  --target "$TARGET"
  --min-price "$MIN_PRICE"
  --max-price "$MAX_PRICE"
  --max-pages "$MAX_PAGES"
  --max-details "$MAX_DETAILS"
  --timeout "$TIMEOUT"
  --search-timeout "$SEARCH_TIMEOUT"
  --sleep "$SLEEP"
  --max-products-per-seed "$MAX_PRODUCTS_PER_SEED"
)
if [[ -n "$SEED_FILE" ]]; then build_args+=(--seed-file "$SEED_FILE"); fi
if [[ "$DRY_RUN" -eq 1 ]]; then build_args+=(--dry-run); fi

"$SKILL_DIR/scripts/build_report_amz_data.py" "${build_args[@]}"

if [[ "$DRY_RUN" -eq 1 ]]; then
  exit 0
fi

if [[ ! -s "$OUT_DIR/products.normalized.json" ]]; then
  die "no normalized products produced: $OUT_DIR/products.normalized.json"
fi

node "$US_SKILL/scripts/render_report.js" \
  --data "$OUT_DIR/products.normalized.json" \
  --out "$HTML" \
  --force-render

if [[ -n "$DESKTOP_NAME" ]]; then
  DESKTOP_DIR="/Users/poincare/Desktop/$DESKTOP_NAME"
  mkdir -p "$DESKTOP_DIR"
  cp "$HTML" "$DESKTOP_DIR/$DESKTOP_NAME.html"
  cp -R "$OUT_DIR/jyamzon_raw" "$DESKTOP_DIR/evidence"
  cp "$OUT_DIR/products.normalized.json" "$DESKTOP_DIR/products.normalized.json"
  cp "$OUT_DIR/summary.json" "$DESKTOP_DIR/summary.json"
  HTML="$DESKTOP_DIR/$DESKTOP_NAME.html"
fi

HTML_PATH="$HTML" OUT_DIR="$OUT_DIR" node <<'NODE'
const fs = require("fs");
const vm = require("vm");
const html = fs.readFileSync(process.env.HTML_PATH, "utf8");
const m = html.match(/const P=(\[[\s\S]*?\]);\n\n\/\/ ===== RENDER =====/);
if (!m) throw new Error("const P data block not found");
const products = vm.runInNewContext(m[1]);
const summary = JSON.parse(fs.readFileSync(`${process.env.OUT_DIR}/summary.json`, "utf8"));
const badPrice = products.filter((p) => p.price < summary.price_gate.min || p.price > summary.price_gate.max).length;
const incomplete = products.filter((p) => !p.price || !p.rating || !p.reviews || !p.bsr).length;
console.log(JSON.stringify({
  ok: true,
  html: process.env.HTML_PATH,
  outDir: process.env.OUT_DIR,
  products: products.length,
  rejected: summary.rejected,
  badPrice,
  incomplete,
  data: "jyamzon",
  frontend: "us-summer-products-research-2026"
}, null, 2));
NODE
