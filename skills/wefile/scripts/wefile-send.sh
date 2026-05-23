#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  wefile-send.sh [--recipient NAME] [--skip-search] [--dry-run] FILE

Send FILE to WeChat's File Transfer chat on this Mac.

Defaults:
  recipient: File Transfer

Notes:
  - WeChat must be logged in.
  - macOS Accessibility permission must allow Terminal/iTerm/node to control the UI.
  - The script uses GUI automation and will overwrite the clipboard while it runs.
USAGE
}

recipient="File Transfer"
skip_search=0
dry_run=0
file=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --recipient)
      [[ $# -ge 2 ]] || { echo "Missing value for --recipient" >&2; exit 2; }
      recipient="$2"
      shift 2
      ;;
    --skip-search)
      skip_search=1
      shift
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      file="$1"
      shift
      ;;
  esac
done

if [[ -z "$file" && $# -gt 0 ]]; then
  file="$1"
fi

if [[ -z "$file" ]]; then
  usage >&2
  exit 2
fi

if [[ ! -f "$file" ]]; then
  echo "File not found: $file" >&2
  exit 1
fi

file_dir="$(cd "$(dirname "$file")" && pwd -P)"
file_base="$(basename "$file")"
file_path="$file_dir/$file_base"

if ! command -v osascript >/dev/null 2>&1; then
  echo "osascript is required on macOS." >&2
  exit 1
fi

if command -v cliclick >/dev/null 2>&1; then
  cliclick_bin="$(command -v cliclick)"
elif [[ -x /opt/homebrew/bin/cliclick ]]; then
  cliclick_bin="/opt/homebrew/bin/cliclick"
else
  echo "cliclick is required. Install with: brew install cliclick" >&2
  exit 1
fi

if [[ "$dry_run" -eq 1 ]]; then
  echo "Would send: $file_path"
  echo "Recipient: $recipient"
  echo "Search: $([[ "$skip_search" -eq 1 ]] && echo skipped || echo enabled)"
  echo "cliclick: $cliclick_bin"
  exit 0
fi

echo "Opening WeChat..."
open -a WeChat
sleep 0.8

if [[ "$skip_search" -eq 0 ]]; then
  echo "Selecting recipient: $recipient"
  printf '%s' "$recipient" | pbcopy
  osascript <<'APPLESCRIPT'
tell application "WeChat" to activate
delay 0.3
tell application "System Events"
  key code 53
  delay 0.1
  keystroke "f" using command down
  delay 0.25
  keystroke "v" using command down
  delay 0.8
  key code 36
  delay 0.5
  key code 53
end tell
APPLESCRIPT
  sleep 0.4
fi

bounds="$(
  osascript <<'APPLESCRIPT'
tell application "WeChat" to activate
delay 0.2
tell application "System Events"
  tell process "WeChat"
    set frontmost to true
    set w to window 1
    set p to position of w
    set s to size of w
    return (item 1 of p as text) & "," & (item 2 of p as text) & "," & (item 1 of s as text) & "," & (item 2 of s as text)
  end tell
end tell
APPLESCRIPT
)"

IFS=',' read -r wx wy ww wh <<<"$bounds"
attach_x=$((wx + 403))
attach_y=$((wy + wh - 34))

echo "Opening file picker..."
"$cliclick_bin" "c:${attach_x},${attach_y}"
sleep 0.9

echo "Choosing file: $file_path"
printf '%s' "$file_path" | pbcopy
osascript <<'APPLESCRIPT'
tell application "System Events"
  keystroke "g" using {command down, shift down}
  delay 0.35
  keystroke "v" using command down
  delay 0.25
  key code 36
  delay 0.9
  key code 36
  delay 1.0
  key code 36
end tell
APPLESCRIPT

echo "Requested WeChat transfer: $file_path"

