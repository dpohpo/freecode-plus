#!/usr/bin/env bash
# Fast raw send to the interactive OpenCode chat window.
set -euo pipefail

exec bash /Users/poincare/.codex/skills/opencode/scripts/opencode-main-send.sh "$@"
