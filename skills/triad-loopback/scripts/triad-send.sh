#!/usr/bin/env bash
# triad-send.sh - 6.0b loopback router for Codex/OpenCode/CCGLM.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  triad-send.sh ROUTE [options] "message"
  printf 'message' | triad-send.sh ROUTE [options]

Routes:
  planner-to-orchestrator | p2o   Codex -> OpenCode
  orchestrator-to-executor | o2e  OpenCode -> CCGLM
  executor-to-orchestrator | e2o  CCGLM -> OpenCode
  orchestrator-to-planner | o2p   OpenCode -> Codex

Options:
  --run-id ID      Existing run id. Generated if omitted.
  --cwd PATH       Working directory context. Default: current directory.
  --title TEXT     Human title.
  --raw            Send the message without triad envelope.
  --focus          Focus destination chat where supported. Default for p2o/e2o.
  --no-focus       Send in background where supported.
  -h, --help       Show this help.
USAGE
}

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 2
fi

ROUTE="$1"
shift

case "$ROUTE" in
  p2o) ROUTE="planner-to-orchestrator" ;;
  o2e) ROUTE="orchestrator-to-executor" ;;
  e2o) ROUTE="executor-to-orchestrator" ;;
  o2p) ROUTE="orchestrator-to-planner" ;;
  -h|--help) usage; exit 0 ;;
esac

RUN_ID=""
CWD="$PWD"
TITLE="Triad loopback"
RAW=0
FOCUS=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-id)
      RUN_ID="${2:?--run-id requires an id}"
      shift 2
      ;;
    --cwd)
      CWD="${2:?--cwd requires a path}"
      shift 2
      ;;
    --title)
      TITLE="${2:?--title requires text}"
      shift 2
      ;;
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
  MESSAGE="$*"
else
  if [[ -t 0 ]]; then
    usage >&2
    exit 2
  fi
  MESSAGE="$(cat)"
fi

if [[ -z "${MESSAGE//[[:space:]]/}" ]]; then
  echo "triad-send: empty message" >&2
  exit 2
fi

if [[ -z "$RUN_ID" ]]; then
  RUN_ID="$(uuidgen 2>/dev/null || python3 -c 'import uuid; print(uuid.uuid4())')"
fi

STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/triad-loopback"
EVENTS="$STATE_DIR/events.jsonl"
mkdir -p "$STATE_DIR"

route_meta() {
  case "$ROUTE" in
    planner-to-orchestrator)
      printf '%s\n' '/codex|Codex|Planner|OpenCode|Orchestrator|$opencode|opencode-to-glm.sh'
      ;;
    orchestrator-to-executor)
      echo '$opencode|OpenCode|Orchestrator|CCGLM|Executor|$ccglm|triad-executor-to-orchestrator.sh'
      ;;
    executor-to-orchestrator)
      echo '$ccglm|CCGLM|Executor|OpenCode|Orchestrator|$opencode|triad-orchestrator-to-planner.sh'
      ;;
    orchestrator-to-planner)
      echo '$opencode|OpenCode|Orchestrator|Codex|Planner|/codex|triad-planner-to-orchestrator.sh or final user report'
      ;;
    *)
      echo "triad-send: unknown route: $ROUTE" >&2
      exit 2
      ;;
  esac
}

IFS='|' read -r SIGNATURE SENDER SENDER_ROLE RECIPIENT RECIPIENT_ROLE EXPECTED_REPLY NEXT_SCRIPT < <(route_meta)

if [[ "$RECIPIENT" == "Codex" ]]; then
  LOOP_SKILL_TRIGGER='$loop'
else
  LOOP_SKILL_TRIGGER='/loop'
fi

log_event() {
  local status="$1"
  TRIAD_EVENTS="$EVENTS" \
  TRIAD_STATUS="$status" \
  TRIAD_RUN_ID="$RUN_ID" \
  TRIAD_ROUTE="$ROUTE" \
  TRIAD_SENDER="$SENDER" \
  TRIAD_RECIPIENT="$RECIPIENT" \
  python3 - <<'PY'
import json
import os
from datetime import datetime, timezone
from pathlib import Path

path = Path(os.environ["TRIAD_EVENTS"])
event = {
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "status": os.environ["TRIAD_STATUS"],
    "run_id": os.environ["TRIAD_RUN_ID"],
    "route": os.environ["TRIAD_ROUTE"],
    "sender": os.environ["TRIAD_SENDER"],
    "recipient": os.environ["TRIAD_RECIPIENT"],
}
with path.open("a", encoding="utf-8") as f:
    f.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
PY
}

if [[ "$RAW" -eq 1 ]]; then
  PROMPT="$MESSAGE"
else
  PROMPT="$(
    TRIAD_SIGNATURE="$SIGNATURE" \
    TRIAD_RUN_ID="$RUN_ID" \
    TRIAD_ROUTE="$ROUTE" \
    TRIAD_TITLE="$TITLE" \
    TRIAD_CWD="$CWD" \
    TRIAD_SENDER="$SENDER" \
    TRIAD_SENDER_ROLE="$SENDER_ROLE" \
    TRIAD_RECIPIENT="$RECIPIENT" \
    TRIAD_RECIPIENT_ROLE="$RECIPIENT_ROLE" \
    TRIAD_EXPECTED_REPLY="$EXPECTED_REPLY" \
    TRIAD_NEXT_SCRIPT="$NEXT_SCRIPT" \
    TRIAD_LOOP_SKILL_TRIGGER="$LOOP_SKILL_TRIGGER" \
    TRIAD_MESSAGE="$MESSAGE" \
    python3 - <<'PY'
import os

print(f"""{os.environ['TRIAD_SIGNATURE']}
{os.environ['TRIAD_LOOP_SKILL_TRIGGER']}
TRIAD_LOOPBACK_V1
run_id: {os.environ['TRIAD_RUN_ID']}
route: {os.environ['TRIAD_ROUTE']}
title: {os.environ['TRIAD_TITLE']}
cwd: {os.environ['TRIAD_CWD']}

loop_skill_paths:
- Codex: /Users/poincare/.codex/skills/loop/SKILL.md
- CCGLM/Claude-compatible: /Users/poincare/.claude/skills/loop/SKILL.md
- OpenCode reference: /Users/poincare/.config/opencode/skills/loop/SKILL.md

from: {os.environ['TRIAD_SENDER']} ({os.environ['TRIAD_SENDER_ROLE']})
to: {os.environ['TRIAD_RECIPIENT']} ({os.environ['TRIAD_RECIPIENT_ROLE']})

message:
{os.environ['TRIAD_MESSAGE']}

loopback_required:
- When your part is done, report to the next responsible agent.
- Use sender signature: {os.environ['TRIAD_EXPECTED_REPLY']}
- Use script: bash /Volumes/金阳/brain/scripts/{os.environ['TRIAD_NEXT_SCRIPT']} --run-id {os.environ['TRIAD_RUN_ID']} --cwd {os.environ['TRIAD_CWD']!r} "your report"
- Include what changed, verification, blockers, and next requested action.
""")
PY
  )"
fi

log_event "send_start"

case "$ROUTE" in
  planner-to-orchestrator|executor-to-orchestrator)
    if [[ "$FOCUS" -eq 0 ]]; then
      bash /Volumes/金阳/brain/scripts/opencode-window-send.sh --no-focus --cwd "$CWD" "$PROMPT"
    else
      bash /Volumes/金阳/brain/scripts/opencode-window-send.sh --cwd "$CWD" "$PROMPT"
    fi
    ;;
  orchestrator-to-executor)
    FOCUS_ARGS=()
    if [[ "$FOCUS" -eq 1 ]]; then
      FOCUS_ARGS+=(--focus)
    else
      FOCUS_ARGS+=(--no-focus)
    fi
    bash /Volumes/金阳/brain/scripts/ccglm-main-send.sh "${FOCUS_ARGS[@]}" --cwd "$CWD" "$PROMPT"
    ;;
  orchestrator-to-planner)
    bash /Volumes/金阳/brain/scripts/codex-send.sh --desktop "$PROMPT"
    ;;
esac

log_event "send_done"

printf '{"run_id":"%s","route":"%s","sender":"%s","recipient":"%s","sent":true}\n' \
  "$RUN_ID" "$ROUTE" "$SENDER" "$RECIPIENT"
