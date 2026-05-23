#!/usr/bin/env bash
# codex-chat.sh — 向 Codex 桌面应用发送消息（6.0b）
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  codex-chat.sh "message" [--no-enter]
  printf 'message' | codex-chat.sh [--no-enter]
USAGE
}

NO_ENTER=0
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-enter)
      NO_ENTER=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      ARGS+=("$1")
      shift
      ;;
  esac
done

if [[ "${#ARGS[@]}" -gt 0 ]]; then
  MSG="${ARGS[*]}"
else
  if [[ -t 0 ]]; then
    usage >&2
    exit 1
  fi
  MSG="$(cat)"
fi

if [[ -z "${MSG//[[:space:]]/}" ]]; then
  echo "codex-chat: message is empty" >&2
  exit 1
fi

if ! pgrep -x "Codex" >/dev/null 2>&1; then
  echo "codex-chat: Codex is not running" >&2
  exit 1
fi

SAVED_CLIPBOARD="$(pbpaste 2>/dev/null || true)"
restore_clipboard() {
  printf '%s' "$SAVED_CLIPBOARD" | pbcopy 2>/dev/null || true
}
trap restore_clipboard EXIT

printf '%s' "$MSG" | pbcopy

if [[ "$NO_ENTER" -eq 1 ]]; then
  osascript <<'APPLESCRIPT'
tell application "Codex" to activate
delay 0.4
tell application "System Events"
  tell process "Codex"
    set frontmost to true
    delay 0.2
    keystroke "v" using command down
  end tell
end tell
APPLESCRIPT
else
  osascript <<'APPLESCRIPT'
tell application "Codex" to activate
delay 0.4
tell application "System Events"
  tell process "Codex"
    set frontmost to true
    delay 0.2
    keystroke "v" using command down
    delay 0.2
    key code 36
  end tell
end tell
APPLESCRIPT
fi

sleep 0.3
printf '{\n  "target": "Codex",\n  "prompt_length": %s,\n  "injected": true,\n  "submitted": %s\n}\n' \
  "${#MSG}" "$([[ "$NO_ENTER" -eq 1 ]] && printf false || printf true)"
