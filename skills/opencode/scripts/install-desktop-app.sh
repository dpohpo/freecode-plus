#!/usr/bin/env bash
# install-desktop-app.sh - build ~/Desktop/OpenCode.app as a tmux-backed launcher.
set -euo pipefail

APP_PATH="${1:-$HOME/Desktop/OpenCode.app}"
DEFAULT_CWD="${OPENCODE_DEFAULT_CWD:-$HOME/Documents/New project 2}"
ATTACH_SCRIPT="/Volumes/金阳/brain/scripts/opencode-attach.sh"

mkdir -p "$(dirname "$APP_PATH")"
rm -rf "$APP_PATH"

APPLESCRIPT="$(mktemp)"
cleanup() {
  rm -f "$APPLESCRIPT"
}
trap cleanup EXIT

python3 - "$APPLESCRIPT" "$DEFAULT_CWD" "$ATTACH_SCRIPT" <<'PY'
import json
import shlex
import sys

out, default_cwd, attach_script = sys.argv[1:]
shell = f'''
STATE="$HOME/.local/state/opencode-skill/launch.env"
OPENCODE_CWD={shlex.quote(default_cwd)}
OPENCODE_TMUX_SESSION="${{OPENCODE_TMUX_SESSION:-opencode-main}}"
OPENCODE_TMUX_WINDOW="${{OPENCODE_TMUX_WINDOW:-opencode}}"
if [ -f "$STATE" ]; then
  . "$STATE"
fi
exec bash {shlex.quote(attach_script)} \\
  --current-terminal \\
  --session "$OPENCODE_TMUX_SESSION" \\
  --window "$OPENCODE_TMUX_WINDOW" \\
  --cwd "$OPENCODE_CWD"
'''.strip()
command = "bash -lc " + shlex.quote(shell)
with open(out, "w", encoding="utf-8") as f:
    f.write('tell application "Terminal"\n')
    f.write('  activate\n')
    f.write(f'  do script {json.dumps(command, ensure_ascii=False)}\n')
    f.write('end tell\n')
PY

osacompile -o "$APP_PATH" "$APPLESCRIPT"
printf '%s\n' "$APP_PATH"
