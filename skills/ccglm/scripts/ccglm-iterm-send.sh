#!/usr/bin/env bash
# Direct iTerm2 transport for the CCGLM/freeglm executor lane.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ccglm-iterm-send.sh [options] "message"
  printf 'message' | ccglm-iterm-send.sh [options]

Options:
  --start-only          Ensure the iTerm freeglm lane exists, but send nothing.
  --dry-run             Print resolved target metadata without sending.
  --no-start            With --dry-run, do not create a missing lane.
  --cwd PATH            Working directory before starting freeglm. Default: current directory.
  --session NAME        iTerm session name. Default: ccglm-iterm.
  --window NAME         Accepted for compatibility; not used by iTerm transport.
  --startup-delay N     Seconds to wait after typing freeglm. Default: 6.
  --focus               Activate iTerm2. Default.
  --no-focus            Do not explicitly activate iTerm2 after delivery.
  --no-enter            Paste only; do not press Enter.
  --enter-retries N     TTY carriage-return attempts after writing. Default: 2.
  --new-window          Always create a fresh iTerm window/session.
  -h, --help            Show this help.
USAGE
}

SESSION_NAME="${CCGLM_ITERM_SESSION:-ccglm-iterm}"
WINDOW_NAME="${CCGLM_WINDOW:-ccglm}"
START_CMD="${CCGLM_START_CMD:-freeglm}"
CWD="$PWD"
STARTUP_DELAY="${CCGLM_STARTUP_DELAY:-6}"
DRY_RUN=0
NO_START=0
START_ONLY=0
FOCUS="${CCGLM_FOCUS:-1}"
SEND_ENTER=1
ENTER_RETRIES="${CCGLM_ENTER_RETRIES:-2}"
NEW_WINDOW=0

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
    --enter-retries)
      ENTER_RETRIES="${2:?--enter-retries requires a value}"
      shift 2
      ;;
    --new-window)
      NEW_WINDOW=1
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
case "$ENTER_RETRIES" in
  ''|*[!0-9]*)
    echo "enter retries must be an integer" >&2
    exit 2
    ;;
esac

if [[ ! -d "$CWD" ]]; then
  echo "cwd does not exist: $CWD" >&2
  exit 2
fi

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
LOCK_DIR="$STATE_DIR/iterm.lock.d"
LOCK_TIMEOUT="${CCGLM_ITERM_LOCK_TIMEOUT:-120}"
LOCK_HELD=0
STATE_KEY="$(
  python3 - "$SESSION_NAME" <<'PY'
import re
import sys
print(re.sub(r"[^A-Za-z0-9_.-]+", "_", sys.argv[1]).strip("_") or "default")
PY
)"
ITERM_STATE="$STATE_DIR/iterm-$STATE_KEY.json"
PREVIOUS_TTY="$(
  python3 - "$ITERM_STATE" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
if not path.exists():
    raise SystemExit(0)
try:
    print((json.loads(path.read_text(encoding="utf-8")).get("tty") or "").strip())
except Exception:
    pass
PY
)"
TRUSTED_PREVIOUS_TTY="$(
  python3 - "$ITERM_STATE" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
if not path.exists():
    print("0")
    raise SystemExit(0)
try:
    data = json.loads(path.read_text(encoding="utf-8"))
    print("1" if data.get("trusted_tty") is True else "0")
except Exception:
    print("0")
PY
)"

PROMPT_FILE="$(mktemp)"
cleanup() {
  rm -f "$PROMPT_FILE"
  if [[ "$LOCK_HELD" -eq 1 ]]; then
    rm -rf "$LOCK_DIR"
  fi
}
trap cleanup EXIT
printf '%s' "$PROMPT" > "$PROMPT_FILE"

acquire_iterm_lock() {
  case "$LOCK_TIMEOUT" in
    ''|*[!0-9]*)
      echo "lock timeout must be an integer number of seconds" >&2
      exit 2
      ;;
  esac

  local start now holder
  start="$(date +%s)"
  while ! mkdir "$LOCK_DIR" 2>/dev/null; do
    holder=""
    if [[ -f "$LOCK_DIR/pid" ]]; then
      holder="$(cat "$LOCK_DIR/pid" 2>/dev/null || true)"
    fi
    if [[ -z "$holder" ]]; then
      rm -rf "$LOCK_DIR"
      continue
    fi
    if [[ -n "$holder" ]] && ! kill -0 "$holder" 2>/dev/null; then
      rm -rf "$LOCK_DIR"
      continue
    fi
    now="$(date +%s)"
    if (( now - start >= LOCK_TIMEOUT )); then
      echo "timed out waiting for ccglm iTerm lock: $LOCK_DIR" >&2
      exit 1
    fi
    sleep 0.2
  done
  LOCK_HELD=1
  printf '%s\n' "$$" > "$LOCK_DIR/pid"
}

log_event() {
  local status="$1"
  CCGLM_EVENTS="$EVENTS" \
  CCGLM_STATUS="$status" \
  CCGLM_SESSION="$SESSION_NAME" \
  CCGLM_WINDOW="$WINDOW_NAME" \
  CCGLM_TRANSPORT="iterm" \
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
    "transport": os.environ["CCGLM_TRANSPORT"],
}
path = Path(os.environ["CCGLM_EVENTS"])
with path.open("a", encoding="utf-8") as f:
    f.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
PY
}

if [[ "$DRY_RUN" -eq 1 && "$NO_START" -eq 1 ]]; then
  printf '{\n  "transport": "iterm",\n  "session_name": "%s",\n  "prompt_length": %s,\n  "focused": false,\n  "injected": false,\n  "started": false\n}\n' "$SESSION_NAME" "${#PROMPT}"
  exit 0
fi

acquire_iterm_lock

OSASCRIPT_OUTPUT="$(
  /usr/bin/osascript - "$PROMPT_FILE" "$SESSION_NAME" "$PREVIOUS_TTY" "$TRUSTED_PREVIOUS_TTY" "$CWD" "$START_CMD" "$STARTUP_DELAY" "$FOCUS" "$SEND_ENTER" "$NEW_WINDOW" "$DRY_RUN" "$START_ONLY" <<'APPLESCRIPT'
on boolText(v)
  if v then
    return "true"
  end if
  return "false"
end boolText

on sessionNameMatches(sessionText, sessionName)
  if sessionText is sessionName then
    return true
  end if
  if sessionText starts with (sessionName & " ") then
    return true
  end if
  if sessionText contains sessionName then
    return true
  end if
  return false
end sessionNameMatches

on listContains(valuesList, needle)
  repeat with itemValue in valuesList
    if (itemValue as text) is needle then
      return true
    end if
  end repeat
  return false
end listContains

on currentWindowIds()
  set idsList to {}
  tell application "iTerm"
    repeat with w in windows
      try
        copy ((id of w) as text) to end of idsList
      end try
    end repeat
  end tell
  return idsList
end currentWindowIds

on findNewWindow(beforeIds)
  tell application "iTerm"
    repeat with w in windows
      try
        set windowId to ((id of w) as text)
        if not my listContains(beforeIds, windowId) then
          return w
        end if
      end try
    end repeat
  end tell
  return missing value
end findNewWindow

on findSessionByIdentity(sessionName, targetTty, allowTtyFallback)
  set fallbackSession to missing value
  tell application "iTerm"
    repeat with w in windows
      repeat with t in tabs of w
        repeat with s in sessions of t
          try
            set sessionText to (name of s) as text
            set sessionTty to (tty of s) as text
            if my sessionNameMatches(sessionText, sessionName) then
              if targetTty is "" or sessionTty is targetTty then
                return s
              end if
              if fallbackSession is missing value then
                set fallbackSession to s
              end if
            else if allowTtyFallback and targetTty is not "" and sessionTty is targetTty then
              return s
            end if
          end try
        end repeat
      end repeat
    end repeat
  end tell
  if fallbackSession is not missing value then
    return fallbackSession
  end if
  return missing value
end findSessionByIdentity

on run argv
  set promptPath to item 1 of argv
  set sessionName to item 2 of argv
  set previousTty to item 3 of argv
  set allowTtyFallback to (item 4 of argv) is "1"
  set cwdPath to item 5 of argv
  set startCmd to item 6 of argv
  set startupDelay to (item 7 of argv) as real
  set shouldFocus to (item 8 of argv) is "1"
  set shouldEnter to (item 9 of argv) is "1"
  set forceNewWindow to (item 10 of argv) is "1"
  set isDryRun to (item 11 of argv) is "1"
  set isStartOnly to (item 12 of argv) is "1"
  if isStartOnly then
    set promptText to ""
  else
    set promptText to read (POSIX file promptPath) as «class utf8»
  end if
  set startedNew to false
  set beforeWindowIds to my currentWindowIds()

  tell application "iTerm"
    if shouldFocus then activate

    if forceNewWindow then
      set targetSession to missing value
    else
      set targetSession to my findSessionByIdentity(sessionName, previousTty, allowTtyFallback)
    end if

    if targetSession is missing value then
      if isDryRun then
        return sessionName & (ASCII character 9) & "" & (ASCII character 9) & "false" & (ASCII character 9) & "false" & (ASCII character 9) & "false"
      end if

      create window with default profile
      set startedNew to true
      delay 0.5
      set targetWindow to my findNewWindow(beforeWindowIds)
      if targetWindow is missing value then
        set targetWindow to current window
      end if
      tell targetWindow
        select
        set targetSession to current session
        try
          set name of targetSession to sessionName
        end try
        tell targetSession
          write text "cd " & quoted form of cwdPath newline true
          delay 0.2
          write text startCmd newline true
          delay startupDelay
        end tell
        try
          set name of targetSession to sessionName
        end try
      end tell
    else
      if shouldFocus then
        try
          select (window of (tab of targetSession))
        end try
      end if
    end if

    try
      set targetTty to (tty of targetSession) as text
    on error
      set targetTty to ""
    end try

    if isDryRun then
      return sessionName & (ASCII character 9) & targetTty & (ASCII character 9) & "true" & (ASCII character 9) & my boolText(startedNew) & (ASCII character 9) & "false"
    end if

    if not isStartOnly then
      tell targetSession
        write text promptText newline false
      end tell
    end if

    return sessionName & (ASCII character 9) & targetTty & (ASCII character 9) & "true" & (ASCII character 9) & my boolText(startedNew) & (ASCII character 9) & my boolText(not isStartOnly)
  end tell
end run
APPLESCRIPT
)"

OUTPUT_JSON="$(
  OSASCRIPT_OUTPUT="$OSASCRIPT_OUTPUT" python3 - "$ITERM_STATE" <<'PY'
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

state_path = Path(sys.argv[1])
raw = os.environ["OSASCRIPT_OUTPUT"]
parts = raw.split("\t")
if len(parts) != 5:
    raise SystemExit(f"unexpected osascript output: {raw!r}")
session_name, tty, exists, started, injected = parts
payload = {
    "transport": "iterm",
    "session_name": session_name,
    "tty": tty,
    "exists": exists == "true",
    "started": started == "true",
    "injected": injected == "true",
}
if payload.get("exists") and payload.get("tty"):
    state_path.write_text(
        json.dumps(
            {
                "session_name": payload.get("session_name"),
                "tty": payload.get("tty"),
                "state_version": 2,
                "trusted_tty": True,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
print(json.dumps(payload, ensure_ascii=False))
PY
)"

if [[ "$SEND_ENTER" -eq 1 && "$START_ONLY" -eq 0 && "$DRY_RUN" -eq 0 ]]; then
  TARGET_TTY="$(OUTPUT_JSON="$OUTPUT_JSON" python3 - <<'PY'
import json
import os
print(json.loads(os.environ["OUTPUT_JSON"]).get("tty", ""))
PY
)"
  if [[ -n "$TARGET_TTY" ]]; then
    /usr/bin/osascript - "$TARGET_TTY" "$ENTER_RETRIES" <<'APPLESCRIPT' >/dev/null
on run argv
  set targetTty to item 1 of argv
  set retryCount to (item 2 of argv) as integer
  tell application "iTerm"
    repeat with attempt from 1 to retryCount
      repeat with w in windows
        repeat with t in tabs of w
          repeat with s in sessions of t
            try
              if ((tty of s) as text) is targetTty then
                tell s to write text "" newline true
                delay 0.2
                exit repeat
              end if
            end try
          end repeat
        end repeat
      end repeat
    end repeat
  end tell
end run
APPLESCRIPT
  fi
fi

if [[ "$START_ONLY" -eq 1 ]]; then
  log_event "start"
elif [[ "$DRY_RUN" -eq 0 ]]; then
  log_event "send"
fi

printf '%s\n' "$OUTPUT_JSON" | python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=2))'
