#!/usr/bin/env bash
# OpenCode -> CCGLM/freeglm handoff with the stable iTerm transport.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'USAGE'
Usage:
  opencode-to-glm.sh --run-id ID --cwd PATH "executor task"
  printf 'executor task' | opencode-to-glm.sh --run-id ID --cwd PATH

Behavior:
  - Wraps the OpenCode -> CCGLM loopback route.
  - Reuses the existing iTerm/freeglm lane; does not pass --new-window.
  - Uses the ccglm iTerm sender that submits pasted-text composers with session-level Enter.
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

exec bash "$SCRIPT_DIR/triad-orchestrator-to-executor.sh" "$@"
