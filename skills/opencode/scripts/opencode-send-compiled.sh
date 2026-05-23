#!/usr/bin/env bash
# opencode-send-compiled.sh - compile a Codex -> OpenCode 6.0b prompt, then inject it into OpenCode chat.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'USAGE'
Usage:
  opencode-send-compiled.sh "message for OpenCode"
  printf 'message' | opencode-send-compiled.sh

Behavior:
  - Default: wrap input in a Codex -> OpenCode 6.0b dialogue contract.
  - Then inject it into the interactive OpenCode chat pane through tmux.
  - This script does not call `opencode run`.
  - If the payload starts with /, it is sent raw so slash commands survive.

Options:
  --raw              Send text directly without dialogue compilation.
  --title TEXT       Dialogue title. Default: Codex to OpenCode coordination
  --focus            Switch tmux to the OpenCode window/pane after sending. Default.
  --no-focus         Do not switch tmux after sending.
  --session NAME     tmux session name. Default: opencode-main
  --window NAME      tmux window name. Default: opencode
  --cwd PATH         Working directory for a bootstrapped OpenCode TUI.
  --timeout N        Bootstrap wait seconds. Default: 20
  --no-bootstrap     Fail if the target OpenCode tmux session does not exist.
  --desktop-app PATH Desktop app used when bootstrapping.
  --no-desktop       Bootstrap directly with tmux instead of opening the desktop app.
USAGE
}

RAW=0
TITLE="Codex to OpenCode coordination"
PASS_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --raw)
      RAW=1
      shift
      ;;
    --title)
      TITLE="${2:?--title requires text}"
      shift 2
      ;;
    --focus|--no-focus|--no-bootstrap|--no-desktop)
      PASS_ARGS+=("$1")
      shift
      ;;
    --session|--window|--cwd|--timeout|--desktop-app)
      PASS_ARGS+=("$1" "${2:?$1 requires a value}")
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

if [[ -z "${INPUT_TEXT}" ]]; then
  echo "opencode-send-compiled: message is empty" >&2
  exit 1
fi

FIRST_NONSPACE="$(printf '%s' "$INPUT_TEXT" | sed -E 's/^[[:space:]]+//' | head -c 1)"
if [[ "$RAW" -eq 1 || "$FIRST_NONSPACE" == "/" ]]; then
  bash "$SCRIPT_DIR/opencode-main-send.sh" "${PASS_ARGS[@]}" "$INPUT_TEXT"
  exit 0
fi

PROMPT="$(cat <<EOF
# 6.0b Agent Dialogue Contract

Sender: Codex
Recipient: OpenCode
Delivery: interactive OpenCode chat window via tmux
Title: ${TITLE}

## Contract

You are receiving a scripted Codex -> OpenCode coordination message. Treat this as an agent-to-agent handoff, not casual chat. Read any referenced files, verify the conclusions, challenge weak assumptions, and return concrete next actions.

## Payload From Codex

${INPUT_TEXT}

## Required Response

Return:
1. Agreement or disagreement with the Codex conclusions.
2. Priority-ordered next actions.
3. Risks or missing constraints Codex did not identify.
4. Exact files/scripts you recommend changing.
5. Any command interface you recommend for a bash-first 6.0b implementation.
EOF
)"

bash "$SCRIPT_DIR/opencode-main-send.sh" "${PASS_ARGS[@]}" "$PROMPT"
