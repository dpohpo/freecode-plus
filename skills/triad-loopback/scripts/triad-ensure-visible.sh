#!/usr/bin/env bash
# Ensure the local 6.0b triad lanes are present and visible.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  triad-ensure-visible.sh [options]

Options:
  --cwd PATH       Working directory for newly bootstrapped lanes. Default: current directory.
  --focus         Start/resolve lanes and pull terminal windows forward. Default.
  --no-focus      Start/resolve lanes without pulling terminal windows forward.
  --with-cc       Also check the legacy Claude Code/yqhsq lane. Default: off.
  --no-opencode   Do not check the OpenCode lane.
  --no-ccglm      Do not check the CCGLM/freeglm lane.
  -h, --help      Show this help.
USAGE
}

CWD="$PWD"
FOCUS=1
CHECK_CC=0
CHECK_OPENCODE=1
CHECK_CCGLM=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cwd)
      CWD="${2:?--cwd requires a path}"
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
    --with-cc)
      CHECK_CC=1
      shift
      ;;
    --no-opencode)
      CHECK_OPENCODE=0
      shift
      ;;
    --no-ccglm)
      CHECK_CCGLM=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "triad-ensure-visible: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ! -d "$CWD" ]]; then
  echo "triad-ensure-visible: cwd does not exist: $CWD" >&2
  exit 2
fi

RESULTS="$(mktemp)"
cleanup() {
  rm -f "$RESULTS"
}
trap cleanup EXIT

record() {
  local lane="$1"
  local status="$2"
  local detail="${3:-}"
  local rc="${4:-0}"
  local detail_b64
  detail_b64="$(printf '%s' "$detail" | base64 | tr -d '\n')"
  printf '%s\t%s\t%s\t%s\n' "$lane" "$status" "$rc" "$detail_b64" >> "$RESULTS"
}

run_lane() {
  local lane="$1"
  shift
  local output
  if output="$("$@" 2>&1)"; then
    record "$lane" "ok" "$output" 0
  else
    local rc=$?
    record "$lane" "error" "$output" "$rc"
  fi
}

focus_tmux_session() {
  local session="$1"
  tmux select-window -t "$session" >/dev/null 2>&1 || true
  if [[ -z "$(tmux list-clients -t "$session" 2>/dev/null)" ]]; then
    osascript >/dev/null 2>&1 <<APPLESCRIPT || true
tell application "iTerm2"
  activate
  create window with default profile command "tmux attach-session -t ${session}"
end tell
APPLESCRIPT
  else
    osascript -e 'tell application "iTerm2" to activate' >/dev/null 2>&1 || true
  fi
}

if [[ "$CHECK_CCGLM" -eq 1 ]]; then
  CCGLM_ARGS=(--start-only --cwd "$CWD")
  if [[ "$FOCUS" -eq 1 ]]; then
    CCGLM_ARGS+=(--focus)
  else
    CCGLM_ARGS+=(--no-focus)
  fi
  run_lane "ccglm" bash /Volumes/金阳/brain/scripts/ccglm-main-send.sh "${CCGLM_ARGS[@]}"
fi

if [[ "$CHECK_OPENCODE" -eq 1 ]]; then
  if [[ "$FOCUS" -eq 1 ]]; then
    run_lane "opencode" bash /Volumes/金阳/brain/scripts/opencode-attach.sh --cwd "$CWD"
  else
    run_lane "opencode" bash /Volumes/金阳/brain/scripts/opencode-main-send.sh --dry-run --no-focus --cwd "$CWD" "__triad_probe__"
  fi
fi

if [[ "$CHECK_CC" -eq 1 ]]; then
  if tmux has-session -t 1 2>/dev/null; then
    if [[ "$FOCUS" -eq 1 ]]; then
      focus_tmux_session "1"
    fi
    if tmux capture-pane -pt 1:1 -S -30 2>/dev/null | grep -Fq "does not have access to Claude Code"; then
      record "claude-code" "blocked" "Claude Code lane exists, but account access is blocked; run /login in the visible cc lane." 0
    else
      record "claude-code" "ok" "Claude Code tmux session 1 exists." 0
    fi
  else
    run_lane "claude-code" bash /Volumes/金阳/brain/scripts/tmux-opus-yqhsq.sh
  fi
fi

python3 - "$RESULTS" "$CWD" <<'PY'
import base64
import json
import sys
from pathlib import Path

rows = []
for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    lane, status, rc, detail_b64 = line.split("\t", 3)
    detail = base64.b64decode(detail_b64).decode("utf-8", errors="replace")
    rows.append({"lane": lane, "status": status, "exit_code": int(rc), "detail": detail})

print(json.dumps({"cwd": sys.argv[2], "lanes": rows}, ensure_ascii=False, indent=2))
PY
