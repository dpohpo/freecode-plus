#!/usr/bin/env bash
# opencode-main-send.sh - inject raw text into the OpenCode interactive chat pane.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  opencode-main-send.sh "raw text for OpenCode chat"
  printf 'raw text' | opencode-main-send.sh

Behavior:
  - Reuses an existing tmux session running the interactive `opencode` TUI.
  - If no session exists, opens ~/Desktop/OpenCode.app to create/show the chat.
  - Injects the payload exactly as provided into the OpenCode chat window.
  - This script does not call `opencode run`.
  - For compiled Codex -> OpenCode dialogue prompts, use opencode-send-compiled.sh.

Options:
  --dry-run          Resolve/bootstrap the target pane, but do not inject.
  --focus            Switch tmux to the target OpenCode window/pane and open Terminal if detached. Default.
  --no-focus         Do not switch tmux after sending.
  --session NAME     tmux session name. Default: opencode-main
  --window NAME      tmux window name. Default: opencode
  --cwd PATH         Working directory for a bootstrapped OpenCode TUI.
  --timeout N        Bootstrap wait seconds. Default: 20
  --submit-delay N   Seconds to wait after paste before Enter. Default: 0.15
  --enter-retries N  Enter attempts when a pasted-text composer is still visible. Default: 2
  --no-bootstrap     Fail if the target OpenCode tmux session does not exist.
  --desktop-app PATH Desktop app used when bootstrapping. Default: ~/Desktop/OpenCode.app
  --no-desktop       Bootstrap directly with tmux instead of opening the desktop app.
  --no-enter         Paste only; do not press Enter after paste.
USAGE
}

DRY_RUN=0
FOCUS="${OPENCODE_FOCUS:-1}"
BOOTSTRAP=1
USE_DESKTOP=1
PRESS_ENTER=1
SESSION_NAME="${OPENCODE_TMUX_SESSION:-opencode-main}"
WINDOW_NAME="${OPENCODE_TMUX_WINDOW:-opencode}"
CWD="${OPENCODE_CWD:-$PWD}"
TIMEOUT="${OPENCODE_TMUX_TIMEOUT:-20}"
SUBMIT_DELAY="${OPENCODE_SUBMIT_DELAY:-0.15}"
ENTER_RETRIES="${OPENCODE_ENTER_RETRIES:-2}"
DESKTOP_APP="${OPENCODE_DESKTOP_APP:-$HOME/Desktop/OpenCode.app}"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/opencode-skill"
LAUNCH_ENV="$STATE_DIR/launch.env"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --focus)
      FOCUS=1
      shift
      ;;
    --no-focus)
      FOCUS=0
      shift
      ;;
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
    --timeout)
      TIMEOUT="${2:?--timeout requires seconds}"
      shift 2
      ;;
    --submit-delay)
      SUBMIT_DELAY="${2:?--submit-delay requires seconds}"
      shift 2
      ;;
    --enter-retries)
      ENTER_RETRIES="${2:?--enter-retries requires a value}"
      shift 2
      ;;
    --no-bootstrap)
      BOOTSTRAP=0
      shift
      ;;
    --desktop-app)
      DESKTOP_APP="${2:?--desktop-app requires a path}"
      shift 2
      ;;
    --no-desktop)
      USE_DESKTOP=0
      shift
      ;;
    --no-enter)
      PRESS_ENTER=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      break
      ;;
  esac
done

if [[ $# -gt 0 ]]; then
  PROMPT="$*"
else
  if [[ -t 0 ]]; then
    usage >&2
    exit 1
  fi
  PROMPT="$(cat)"
fi

if [[ -z "${PROMPT}" ]]; then
  echo "opencode-main-send: prompt is empty" >&2
  exit 1
fi
case "$SUBMIT_DELAY" in
  ''|*[!0-9.]*)
    echo "opencode-main-send: submit delay must be numeric" >&2
    exit 2
    ;;
esac
case "$ENTER_RETRIES" in
  ''|*[!0-9]*)
    echo "opencode-main-send: enter retries must be an integer" >&2
    exit 2
    ;;
esac

if ! command -v tmux >/dev/null 2>&1; then
  echo "opencode-main-send: tmux not found" >&2
  exit 127
fi

if ! command -v opencode >/dev/null 2>&1; then
  echo "opencode-main-send: opencode not found" >&2
  exit 127
fi

if [[ ! -d "$CWD" ]]; then
  echo "opencode-main-send: cwd does not exist: $CWD" >&2
  exit 2
fi

write_launch_state() {
  mkdir -p "$STATE_DIR"
  python3 - "$LAUNCH_ENV" "$CWD" "$SESSION_NAME" "$WINDOW_NAME" <<'PY'
import shlex
import sys

path, cwd, session, window = sys.argv[1:]
with open(path, "w", encoding="utf-8") as f:
    f.write(f"OPENCODE_CWD={shlex.quote(cwd)}\n")
    f.write(f"OPENCODE_TMUX_SESSION={shlex.quote(session)}\n")
    f.write(f"OPENCODE_TMUX_WINDOW={shlex.quote(window)}\n")
PY
}

ensure_target() {
  if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    if [[ "$BOOTSTRAP" -ne 1 ]]; then
      echo "opencode-main-send: tmux session not found: $SESSION_NAME" >&2
      exit 1
    fi
    if [[ "$USE_DESKTOP" -eq 1 && -d "$DESKTOP_APP" ]]; then
      write_launch_state
      open "$DESKTOP_APP"
    else
      tmux new-session -d -s "$SESSION_NAME" -n "$WINDOW_NAME" -c "$CWD" opencode
    fi
  elif ! tmux list-windows -t "$SESSION_NAME" -F '#{window_name}' | grep -Fxq "$WINDOW_NAME"; then
    if [[ "$BOOTSTRAP" -ne 1 ]]; then
      echo "opencode-main-send: tmux window not found: $SESSION_NAME:$WINDOW_NAME" >&2
      exit 1
    fi
    tmux new-window -d -t "$SESSION_NAME" -n "$WINDOW_NAME" -c "$CWD" opencode
  fi

  local deadline=$((SECONDS + TIMEOUT))
  while (( SECONDS <= deadline )); do
    if tmux list-panes -t "$SESSION_NAME:$WINDOW_NAME" -F '#{pane_id}' >/tmp/opencode-main-pane.$$ 2>/dev/null; then
      TARGET_PANE="$(head -n 1 /tmp/opencode-main-pane.$$)"
      rm -f /tmp/opencode-main-pane.$$
      if [[ -n "$TARGET_PANE" ]]; then
        return 0
      fi
    fi
    sleep 0.2
  done
  rm -f /tmp/opencode-main-pane.$$
  echo "opencode-main-send: timed out resolving OpenCode pane" >&2
  exit 1
}

TARGET_PANE=""
ensure_target
TARGET_WINDOW="$(tmux display-message -p -t "$TARGET_PANE" '#{session_name}:#{window_index}')"

if [[ "$DRY_RUN" -eq 1 ]]; then
  printf '{\n  "session_name": "%s",\n  "target_window": "%s",\n  "target_pane": "%s",\n  "prompt_length": %s,\n  "focused": false,\n  "injected": false\n}\n' \
    "$SESSION_NAME" "$TARGET_WINDOW" "$TARGET_PANE" "${#PROMPT}"
  exit 0
fi

TMP_PROMPT_FILE="$(mktemp)"
cleanup() {
  rm -f "$TMP_PROMPT_FILE"
}
trap cleanup EXIT

printf '%s' "$PROMPT" > "$TMP_PROMPT_FILE"
tmux load-buffer "$TMP_PROMPT_FILE"
tmux paste-buffer -t "$TARGET_PANE"

if [[ "$PRESS_ENTER" -eq 1 ]]; then
  sleep "$SUBMIT_DELAY"
  tmux send-keys -t "$TARGET_PANE" Enter
  for ((attempt = 1; attempt < ENTER_RETRIES; attempt++)); do
    sleep "$SUBMIT_DELAY"
    if tmux capture-pane -pt "$TARGET_PANE" -S -8 2>/dev/null | grep -Fq '[Pasted text'; then
      tmux send-keys -t "$TARGET_PANE" Enter
    else
      break
    fi
  done
fi

if [[ "$FOCUS" -eq 1 ]]; then
  tmux select-window -t "$TARGET_WINDOW" >/dev/null 2>&1 || true
  tmux select-pane -t "$TARGET_PANE" >/dev/null 2>&1 || true
  if [[ -z "$(tmux list-clients -t "$SESSION_NAME" 2>/dev/null)" ]]; then
    osascript >/dev/null 2>&1 <<APPLESCRIPT || true
tell application "Terminal"
  activate
  do script "tmux attach-session -t ${SESSION_NAME}"
end tell
APPLESCRIPT
  else
    osascript -e 'tell application "Terminal" to activate' >/dev/null 2>&1 || true
  fi
fi

printf '{\n  "session_name": "%s",\n  "target_window": "%s",\n  "target_pane": "%s",\n  "prompt_length": %s,\n  "focused": %s,\n  "injected": true\n}\n' \
  "$SESSION_NAME" "$TARGET_WINDOW" "$TARGET_PANE" "${#PROMPT}" "$([[ "$FOCUS" -eq 1 ]] && printf true || printf false)"
