#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/scripts/resolve-bun.sh"
BUN_BIN="$(resolve_bun_bin)"

exec "$BUN_BIN" run "$ROOT/src/entrypoints/cli.tsx" "$@"
