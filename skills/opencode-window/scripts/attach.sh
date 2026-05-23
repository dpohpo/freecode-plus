#!/usr/bin/env bash
# Show the interactive OpenCode chat window.
set -euo pipefail

exec bash /Users/poincare/.codex/skills/opencode/scripts/opencode-attach.sh "$@"
