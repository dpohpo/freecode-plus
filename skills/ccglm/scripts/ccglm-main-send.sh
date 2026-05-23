#!/usr/bin/env bash
# Raw send to the managed CCGLM/freeglm executor lane.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "${CCGLM_TRANSPORT:-iterm}" == "iterm" ]]; then
  exec bash "$SCRIPT_DIR/ccglm-iterm-send.sh" "$@"
fi

usage() {
  cat <<'USAGE'
Usage:
  ccglm-main-send.sh [options] "message"
  printf 'message' | ccglm-main-send.sh [options]

Options:
  --start-only          Ensure the ccglm tmux lane exists, but send nothing.
  --dry-run             Resolve/start target and print JSON without sending.
  --no-start            With --dry-run, do not create a missing lane.
  --cwd PATH            Working directory for first startup. Default: current directory.
  --session NAME        tmux session name. Default: ccglm-main.
  --window NAME         tmux window name. Default: ccglm.
  --startup-delay N     Seconds to wait after starting freeglm. Default: 6.
  --submit-delay N      Seconds to wait after paste before Enter. Default: 0.2.
  --enter-retries N     Enter attempts when a pasted-text composer is still visible. Default: 2.
  --focus               Open or activate iTerm2 attached to the lane after sending. Default.
  --no-focus            Do not focus.
  --no-enter            Paste only; do not press Enter.
  -h, --help            Show this help.
USAGE
}

SESSION_NAME="${CCGLM_SESSION:-ccglm-main}"
WINDOW_NAME="${CCGLM_WINDOW:-ccglm}"
START_CMD="${CCGLM_START_CMD:-freeglm}"
CWD="$PWD"
STARTUP_DELAY="${CCGLM_STARTUP_DELAY:-6}"
SUBMIT_DELAY="${CCGLM_SUBMIT_DELAY:-0.2}"
ENTER_RETRIES="${CCGLM_ENTER_RETRIES:-2}"
DRY_RUN=0
NO_START=0
START_ONLY=0
FOCUS="${CCGLM_FOCUS:-1}"
SEND_ENTER=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --start-only)
      START_ONLY=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --no-start)
      NO_START=1
      shift
      ;;
    --cwd)
      CWD="${2:?--cwd requires a path}"
      shift 2
      ;;
    --session)
      SESSION_NAME="${2:?--session requires a name}"
      shift 2
      ;;
    --window)
      WINDOW_NAME="${2:?--window requires a name}"
      shift 2
      ;;
    --startup-delay)
      STARTUP_DELAY="${2:?--startup-delay requires a value}"
      shift 2
      ;;
    --submit-delay)
      SUBMIT_DELAY="${2:?--submit-delay requires a value}"
      shift 2
      ;;
    --enter-retries)
      ENTER_RETRIES="${2:?--enter-retries requires a value}"
      shift 2
      ;;
    --focus)
      FOCUS=1
      shift
      ;;
    --no-focus)
      FOCUS=0
      shift
      ;;
    --no-enter)
      SEND_ENTER=0
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

case "$STARTUP_DELAY" in
  ''|*[!0-9.]*)
    echo "startup delay must be numeric" >&2
    exit 2
    ;;
esac
case "$SUBMIT_DELAY" in
  ''|*[!0-9.]*)
    echo "submit delay must be numeric" >&2
    exit 2
    ;;
esac
case "$ENTER_RETRIES" in
  ''|*[!0-9]*)
    echo "enter retries must be an integer" >&2
    exit 2
    ;;
esac

if [[ "$START_ONLY" -eq 0 ]]; then
  if [[ $# -gt 0 ]]; then
    PROMPT="$*"
  else
    if [[ -t 0 ]]; then
      usage >&2
      exit 2
    fi
    PROMPT="$(cat)"
  fi
  if [[ -z "${PROMPT//[[:space:]]/}" ]]; then
    echo "prompt is empty" >&2
    exit 2
  fi
else
  PROMPT=""
fi

STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/ccglm"
EVENTS="$STATE_DIR/events.jsonl"
mkdir -p "$STATE_DIR"

json_escape() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'
}

log_event() {
  local status="$1"
  CCGLM_EVENTS="$EVENTS" \
  CCGLM_STATUS="$status" \
  CCGLM_SESSION="$SESSION_NAME" \
  CCGLM_WINDOW="$WINDOW_NAME" \
  python3 - <<'PY'
import json
import os
from datetime import datetime, timezone
from pathlib import Path

event = {
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "status": os.environ["CCGLM_STATUS"],
    "session": os.environ["CCGLM_SESSION"],
    "window": os.environ["CCGLM_WINDOW"],
}
path = Path(os.environ["CCGLM_EVENTS"])
with path.open("a", encoding="utf-8") as f:
    f.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
PY
}

window_exists() {
  tmux list-windows -t "$SESSION_NAME" -F '#{window_name}' 2>/dev/null | awk -v w="$WINDOW_NAME" '$0 == w { found=1 } END { exit(found ? 0 : 1) }'
}

start_shell_command() {
  python3 - "${SHELL:-/bin/zsh}" "$START_CMD" <<'PY'
import shlex
import sys

shell, start_cmd = sys.argv[1:]
inner = f"""
{shlex.quote(shell)} -lic {shlex.quote(start_cmd)}
ccglm_exit_status=$?
printf '\\n[ccglm] startup command exited with status %s\\n' "$ccglm_exit_status"
printf '[ccglm] keeping this tmux lane open so the iTerm2 window does not flash-close.\\n'
printf '[ccglm] fix the startup command or rerun ccglm-main-send after resolving the issue.\\n'
printf '[ccglm] type exit or press Ctrl-D to close this diagnostic shell.\\n\\n'
exec {shlex.quote(shell)} -li
""".strip()
print(f"exec {shlex.quote(shell)} -lic {shlex.quote(inner)}")
PY
}

target_pane() {
  tmux list-panes -t "$SESSION_NAME" -F '#{window_name} #{pane_id}' 2>/dev/null \
  | awk -v w="$WINDOW_NAME" '$1 == w { print $2; exit }'
}

composer_still_pasted() {
  tmux capture-pane -pt "$TARGET_PANE" -S -8 2>/dev/null | grep -Fq '[Pasted text'
}

ensure_lane() {
  local created=0
  if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    if [[ "$NO_START" -eq 1 ]]; then
      return 1
    fi
    tmux new-session -d -s "$SESSION_NAME" -n "$WINDOW_NAME" -c "$CWD" "$(start_shell_command)"
    created=1
  elif ! window_exists; then
    if [[ "$NO_START" -eq 1 ]]; then
      return 1
    fi
    tmux new-window -d -t "$SESSION_NAME" -n "$WINDOW_NAME" -c "$CWD" "$(start_shell_command)"
    created=1
  fi

  if [[ "$created" -eq 1 ]]; then
    log_event "start"
    sleep "$STARTUP_DELAY"
    if [[ -z "$(target_pane || true)" ]]; then
      log_event "start_failed"
      return 1
    fi
  fi
  return 0
}

if ! ensure_lane; then
  printf '{\n  "session_name": %s,\n  "window_name": %s,\n  "target_pane": null,\n  "exists": false,\n  "injected": false\n}\n' \
    "$(printf '%s' "$SESSION_NAME" | json_escape)" \
    "$(printf '%s' "$WINDOW_NAME" | json_escape)"
  exit 1
fi

TARGET_PANE="$(target_pane)"
if [[ -z "$TARGET_PANE" ]]; then
  echo "failed to resolve ccglm pane" >&2
  tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} #{window_name} #{pane_id} #{pane_current_command} #{pane_title}' >&2 || true
  exit 1
fi
TARGET_WINDOW="$(tmux display-message -p -t "$TARGET_PANE" '#{session_name}:#{window_index}')"

focus_lane() {
  tmux select-window -t "$TARGET_WINDOW" >/dev/null 2>&1 || true
  tmux select-pane -t "$TARGET_PANE" >/dev/null 2>&1 || true
  if [[ -z "$(tmux list-clients -t "$SESSION_NAME" 2>/dev/null)" ]]; then
    ATTACH_COMMAND="$(
      python3 - "$SESSION_NAME" <<'PY'
import shlex
import sys

session = sys.argv[1]
script = (
    f"tmux attach-session -t {shlex.quote(session)} || "
    "{ echo '[ccglm] tmux attach failed; the session may have exited before attach.'; "
    'exec "${SHELL:-/bin/zsh}" -l; }'
)
print("bash -lc " + shlex.quote(script))
PY
    )"
    osascript >/dev/null 2>&1 <<APPLESCRIPT || true
tell application "iTerm2"
  activate
  create window with default profile command "${ATTACH_COMMAND}"
end tell
APPLESCRIPT
  else
    osascript -e 'tell application "iTerm2" to activate' >/dev/null 2>&1 || true
  fi
}

if [[ "$DRY_RUN" -eq 1 || "$START_ONLY" -eq 1 ]]; then
  DID_FOCUS=0
  if [[ "$DRY_RUN" -eq 0 && "$START_ONLY" -eq 1 && "$FOCUS" -eq 1 ]]; then
    focus_lane
    DID_FOCUS=1
  fi
  printf '{\n  "session_name": %s,\n  "target_window": %s,\n  "target_pane": %s,\n  "prompt_length": %s,\n  "focused": %s,\n  "injected": false\n}\n' \
    "$(printf '%s' "$SESSION_NAME" | json_escape)" \
    "$(printf '%s' "$TARGET_WINDOW" | json_escape)" \
    "$(printf '%s' "$TARGET_PANE" | json_escape)" \
    "${#PROMPT}" \
    "$([[ "$DID_FOCUS" -eq 1 ]] && printf true || printf false)"
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
if [[ "$SEND_ENTER" -eq 1 ]]; then
  sleep "$SUBMIT_DELAY"
  tmux send-keys -t "$TARGET_PANE" Enter
  for ((attempt = 1; attempt < ENTER_RETRIES; attempt++)); do
    sleep "$SUBMIT_DELAY"
    if composer_still_pasted; then
      tmux send-keys -t "$TARGET_PANE" Enter
    else
      break
    fi
  done
fi
log_event "send"

if [[ "$FOCUS" -eq 1 ]]; then
  focus_lane
fi

printf '{\n  "session_name": %s,\n  "target_window": %s,\n  "target_pane": %s,\n  "prompt_length": %s,\n  "focused": %s,\n  "injected": true\n}\n' \
  "$(printf '%s' "$SESSION_NAME" | json_escape)" \
  "$(printf '%s' "$TARGET_WINDOW" | json_escape)" \
  "$(printf '%s' "$TARGET_PANE" | json_escape)" \
  "${#PROMPT}" \
  "$([[ "$FOCUS" -eq 1 ]] && printf true || printf false)"
