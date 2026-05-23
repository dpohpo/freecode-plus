#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/Users/poincare/.codex/skills/ccglm"

usage() {
  cat <<'EOF'
Usage:
  bash ccglm.sh "message for CCGLM main executor (compiled route)"
  printf 'message' | bash ccglm.sh

Behavior:
  - Default: compile a small CCGLM executor contract, then inject it into freeglm.
  - For exact raw text, use `bash ccglm-main-send.sh "message"` or pass `--raw`.
  - If payload starts with `/`, sends raw so slash commands work.

Options:
  --raw                  Send text directly without compilation.
  --focus                Focus the target tmux window/pane. Default.
  --no-focus             Do not focus after sending.
  --cwd PATH             Startup/context cwd. Default: current directory.
EOF
}

RAW=0
FOCUS="${CCGLM_FOCUS:-1}"
CWD="$PWD"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --raw)
      RAW=1
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
    --cwd)
      CWD="${2:?--cwd requires a path}"
      shift 2
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
  INPUT_TEXT="$*"
else
  if [[ -t 0 ]]; then
    usage >&2
    exit 1
  fi
  INPUT_TEXT="$(cat)"
fi

if [[ -z "${INPUT_TEXT//[[:space:]]/}" ]]; then
  echo "message is empty" >&2
  exit 1
fi

FIRST_NONSPACE="$(printf '%s' "$INPUT_TEXT" | sed -E 's/^[[:space:]]+//' | head -c 1)"
FOCUS_ARGS=()
if [[ "$FOCUS" -eq 1 ]]; then
  FOCUS_ARGS+=(--focus)
else
  FOCUS_ARGS+=(--no-focus)
fi

if [[ "$RAW" -eq 1 || "$FIRST_NONSPACE" == "/" ]]; then
  exec bash "$ROOT_DIR/scripts/ccglm-main-send.sh" "${FOCUS_ARGS[@]}" --cwd "$CWD" "$INPUT_TEXT"
fi

PROMPT="$(
  CCGLM_SIGNATURE="${CCGLM_SENDER_SIGNATURE:-/codex}" \
  CCGLM_CWD="$CWD" \
  CCGLM_TASK="$INPUT_TEXT" \
  python3 - <<'PY'
import os

print(f"""{os.environ['CCGLM_SIGNATURE']}
CCGLM_EXECUTOR_V1
cwd: {os.environ['CCGLM_CWD']}

from: OpenCode/Codex coordination layer
to: CCGLM (Executor)

task:
{os.environ['CCGLM_TASK']}

rules:
- You are the executor lane started by freeglm.
- Sign reports with $ccglm.
- If a TRIAD_LOOPBACK_V1 envelope is present, follow its loopback_required script exactly.
- Report changed files/actions, verification, blockers, and next requested action.
""")
PY
)"

exec bash "$ROOT_DIR/scripts/ccglm-main-send.sh" "${FOCUS_ARGS[@]}" --cwd "$CWD" "$PROMPT"
