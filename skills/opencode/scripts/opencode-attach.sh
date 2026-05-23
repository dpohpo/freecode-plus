#!/usr/bin/env bash
# opencode-attach.sh - show the OpenCode interactive chat tmux session in Terminal.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  opencode-attach.sh [options]

Behavior:
  - If the OpenCode tmux chat session exists, attach/show it.
  - If it does not exist, create it with the interactive `opencode` TUI, then attach.
  - This never calls `opencode run`.

Options:
  --session NAME       tmux session name. Default: opencode-main
  --window NAME        tmux window name. Default: opencode
  --cwd PATH           Working directory for a new OpenCode TUI.
  --current-terminal   Attach in the current terminal instead of opening a new Terminal tab.
  -h, --help           Show this help.
USAGE
}

SESSION_NAME="${OPENCODE_TMUX_SESSION:-opencode-main}"
WINDOW_NAME="${OPENCODE_TMUX_WINDOW:-opencode}"
CWD="${OPENCODE_CWD:-$PWD}"
CURRENT_TERMINAL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --session)
      SESSION_NAME="${2:?--session requires a name}"
      shift 2
      ;;
    --window)
      WINDOW_NAME="${2:?--window requires a name}"
      shift 2
      ;;
    --cwd)
      CWD="${2:?--cwd requires a path}"
      shift 2
      ;;
    --current-terminal)
      CURRENT_TERMINAL=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "opencode-attach: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! command -v tmux >/dev/null 2>&1; then
  echo "opencode-attach: tmux not found" >&2
  exit 127
fi

if ! command -v opencode >/dev/null 2>&1; then
  echo "opencode-attach: opencode not found" >&2
  exit 127
fi

if [[ ! -d "$CWD" ]]; then
  echo "opencode-attach: cwd does not exist: $CWD" >&2
  exit 2
fi

if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  tmux new-session -d -s "$SESSION_NAME" -n "$WINDOW_NAME" -c "$CWD" opencode
elif ! tmux list-windows -t "$SESSION_NAME" -F '#{window_name}' | grep -Fxq "$WINDOW_NAME"; then
  tmux new-window -d -t "$SESSION_NAME" -n "$WINDOW_NAME" -c "$CWD" opencode
fi

tmux select-window -t "$SESSION_NAME:$WINDOW_NAME" >/dev/null 2>&1 || true

if [[ "$CURRENT_TERMINAL" -eq 1 ]]; then
  exec tmux attach-session -t "$SESSION_NAME"
fi

if [[ -n "$(tmux list-clients -t "$SESSION_NAME" 2>/dev/null)" ]]; then
  osascript -e 'tell application "Terminal" to activate' >/dev/null 2>&1 || true
  printf '{\n  "session_name": "%s",\n  "attached_existing_client": true\n}\n' "$SESSION_NAME"
  exit 0
fi

osascript <<APPLESCRIPT
tell application "Terminal"
  activate
  do script "tmux attach-session -t ${SESSION_NAME}"
end tell
APPLESCRIPT
