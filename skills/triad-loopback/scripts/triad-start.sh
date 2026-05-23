#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CWD="$PWD"
ARGS=("$@")
for ((i = 0; i < ${#ARGS[@]}; i++)); do
  if [[ "${ARGS[$i]}" == "--cwd" && $((i + 1)) -lt ${#ARGS[@]} ]]; then
    CWD="${ARGS[$((i + 1))]}"
  fi
done

bash "$SCRIPT_DIR/triad-ensure-visible.sh" --cwd "$CWD" >/dev/null || true
exec bash "$SCRIPT_DIR/triad-send.sh" planner-to-orchestrator --title "Triad start" "$@"
