#!/usr/bin/env bash

resolve_bun_bin() {
  if [[ -n "${BUN_BIN:-}" ]]; then
    if [[ -x "$BUN_BIN" ]]; then
      printf '%s\n' "$BUN_BIN"
      return 0
    fi
    echo "BUN_BIN is set but not executable: $BUN_BIN" >&2
    return 1
  fi

  if command -v bun >/dev/null 2>&1; then
    command -v bun
    return 0
  fi

  local candidate
  for candidate in \
    "$HOME/.bun/bin/bun" \
    "/tmp/freecode-bun-download/bun-darwin-aarch64/bun" \
    "/tmp/freecode-bun-download/bun-linux-x64/bun"; do
    if [[ -x "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  echo "bun not found. Install Bun or set BUN_BIN=/absolute/path/to/bun." >&2
  return 1
}
