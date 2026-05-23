#!/usr/bin/env bash
# Legacy alias: compiled Codex -> OpenCode chat-window delivery.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$SCRIPT_DIR/opencode-send-compiled.sh" "$@"
