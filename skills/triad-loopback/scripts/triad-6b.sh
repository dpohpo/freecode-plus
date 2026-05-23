#!/usr/bin/env bash
# Stable 6.0b entrypoint for the Codex -> OpenCode -> freeglm loop.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRAIN_SCRIPTS="/Volumes/金阳/brain/scripts"

usage() {
  cat <<'USAGE'
Usage:
  triad-6b.sh ensure [options]
  triad-6b.sh loop [options] "task"
  triad-6b.sh start [options] "task"
  triad-6b.sh p2o|o2e|e2o|o2p [route options] "message"
  triad-6b.sh verify [options]
  triad-6b.sh status
  triad-6b.sh install

Subcommands:
  ensure    Open/reuse visible OpenCode and freeglm lanes.
  loop      Start a full triad loop from Codex to OpenCode.
  start     Alias for loop.
  p2o       Codex Planner -> OpenCode Orchestrator.
  o2e       OpenCode Orchestrator -> CCGLM/freeglm Executor.
  e2o       CCGLM/freeglm Executor -> OpenCode Orchestrator.
  o2p       OpenCode Orchestrator -> Codex Planner.
  verify    Check wrappers, lane bootstrap, and Enter submit behavior.
  status    Show recent triad events.
  install   Install /Volumes brain wrappers for this script set.

Common options:
  --cwd PATH       Working directory context. Default: current directory.
  --run-id ID      Run id. Generated for loop/start if omitted.
  --title TEXT     Loop title. Default: 6.0b triad loop.
  --focus          Focus destination windows. Default.
  --no-focus       Background delivery where supported.
USAGE
}

run_id() {
  date '+LOOP-%Y%m%d-%H%M%S'
}

json_line() {
  python3 - "$@" <<'PY'
import json
import sys
print(json.dumps(sys.argv[1:], ensure_ascii=False))
PY
}

require_file() {
  local path="$1"
  if [[ ! -x "$path" ]]; then
    echo "triad-6b: missing executable: $path" >&2
    return 1
  fi
}

install_wrapper() {
  local name="$1"
  local target="$2"
  local dest="$BRAIN_SCRIPTS/$name"
  mkdir -p "$BRAIN_SCRIPTS"
  cat > "$dest" <<EOF
#!/usr/bin/env bash
set -euo pipefail
exec bash $target "\$@"
EOF
  chmod 700 "$dest"
  printf '%s\n' "$dest"
}

install_wrappers() {
  install_wrapper triad-6b.sh "$SCRIPT_DIR/triad-6b.sh"
  install_wrapper triad-loop.sh "$SCRIPT_DIR/triad-6b.sh loop"
  install_wrapper triad-send.sh "$SCRIPT_DIR/triad-send.sh"
  install_wrapper triad-start.sh "$SCRIPT_DIR/triad-start.sh"
  install_wrapper triad-ensure-visible.sh "$SCRIPT_DIR/triad-ensure-visible.sh"
  install_wrapper triad-status.sh "$SCRIPT_DIR/triad-status.sh"
  install_wrapper triad-planner-to-orchestrator.sh "$SCRIPT_DIR/triad-planner-to-orchestrator.sh"
  install_wrapper opencode-to-glm.sh "$SCRIPT_DIR/opencode-to-glm.sh"
  install_wrapper triad-orchestrator-to-executor.sh "$SCRIPT_DIR/triad-orchestrator-to-executor.sh"
  install_wrapper triad-executor-to-orchestrator.sh "$SCRIPT_DIR/triad-executor-to-orchestrator.sh"
  install_wrapper triad-orchestrator-to-planner.sh "$SCRIPT_DIR/triad-orchestrator-to-planner.sh"
}

parse_loop_args() {
  CWD="$PWD"
  RUN_ID=""
  TITLE="6.0b triad loop"
  FOCUS=1
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --cwd)
        CWD="${2:?--cwd requires a path}"
        shift 2
        ;;
      --run-id)
        RUN_ID="${2:?--run-id requires an id}"
        shift 2
        ;;
      --title)
        TITLE="${2:?--title requires text}"
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
  elif [[ -t 0 ]]; then
    MESSAGE="Run a minimal 6.0b loop: Codex -> OpenCode -> CCGLM/freeglm -> OpenCode -> Codex. Do not edit files unless explicitly requested. Report verification and blockers."
  else
    MESSAGE="$(cat)"
  fi

  if [[ -z "${MESSAGE//[[:space:]]/}" ]]; then
    echo "triad-6b loop: empty task" >&2
    exit 2
  fi
  if [[ -z "$RUN_ID" ]]; then
    RUN_ID="$(run_id)"
  fi
}

loop_start() {
  parse_loop_args "$@"
  if [[ ! -d "$CWD" ]]; then
    echo "triad-6b loop: cwd does not exist: $CWD" >&2
    exit 2
  fi

  ENSURE_ARGS=(--cwd "$CWD")
  SEND_ARGS=(--run-id "$RUN_ID" --cwd "$CWD" --title "$TITLE")
  if [[ "$FOCUS" -eq 1 ]]; then
    ENSURE_ARGS+=(--focus)
    SEND_ARGS+=(--focus)
  else
    ENSURE_ARGS+=(--no-focus)
    SEND_ARGS+=(--no-focus)
  fi

  bash "$SCRIPT_DIR/triad-ensure-visible.sh" "${ENSURE_ARGS[@]}" >/dev/null
  bash "$SCRIPT_DIR/triad-send.sh" planner-to-orchestrator "${SEND_ARGS[@]}" "$MESSAGE"
}

verify() {
  CWD="$PWD"
  FOCUS=0
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
      -h|--help)
        usage
        exit 0
        ;;
      *)
        echo "triad-6b verify: unknown option: $1" >&2
        exit 2
        ;;
    esac
  done

  local failures=0
  require_file "$SCRIPT_DIR/triad-send.sh" || failures=$((failures + 1))
  require_file "$SCRIPT_DIR/triad-ensure-visible.sh" || failures=$((failures + 1))
  require_file "$SCRIPT_DIR/opencode-to-glm.sh" || failures=$((failures + 1))
  require_file "/Volumes/金阳/brain/scripts/ccglm-main-send.sh" || failures=$((failures + 1))
  require_file "/Volumes/金阳/brain/scripts/opencode-main-send.sh" || failures=$((failures + 1))
  require_file "/Volumes/金阳/brain/scripts/codex-send.sh" || failures=$((failures + 1))

  if ! grep -Fq 'write text "" newline true' /Users/poincare/.codex/skills/ccglm/scripts/ccglm-iterm-send.sh; then
    echo "triad-6b verify: ccglm iTerm sender is missing session-level Enter submit" >&2
    failures=$((failures + 1))
  fi
  if ! grep -Fq 'opencode-to-glm.sh' "$SCRIPT_DIR/triad-send.sh"; then
    echo "triad-6b verify: planner envelope does not point OpenCode at opencode-to-glm.sh" >&2
    failures=$((failures + 1))
  fi

  ENSURE_ARGS=(--cwd "$CWD")
  if [[ "$FOCUS" -eq 1 ]]; then
    ENSURE_ARGS+=(--focus)
  else
    ENSURE_ARGS+=(--no-focus)
  fi
  bash "$SCRIPT_DIR/triad-ensure-visible.sh" "${ENSURE_ARGS[@]}"

  bash /Volumes/金阳/brain/scripts/opencode-main-send.sh --dry-run --no-focus --cwd "$CWD" "__triad_probe__"
  bash /Volumes/金阳/brain/scripts/ccglm-main-send.sh --dry-run --no-focus --cwd "$CWD" "__triad_probe__"
  bash /Volumes/金阳/brain/scripts/codex-send.sh --desktop --dry-run "__triad_probe__"

  if [[ "$failures" -ne 0 ]]; then
    echo "triad-6b verify: failed checks: $failures" >&2
    exit 1
  fi

  printf '{"ok":true,"scripted":"6.0b","cwd":%s,"default_executor":"freeglm","default_legacy_yqhsq":false}\n' \
    "$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1], ensure_ascii=False))' "$CWD")"
}

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 2
fi

COMMAND="$1"
shift

case "$COMMAND" in
  ensure)
    exec bash "$SCRIPT_DIR/triad-ensure-visible.sh" "$@"
    ;;
  loop|start)
    loop_start "$@"
    ;;
  p2o)
    exec bash "$SCRIPT_DIR/triad-send.sh" planner-to-orchestrator "$@"
    ;;
  o2e|glm)
    exec bash "$SCRIPT_DIR/opencode-to-glm.sh" "$@"
    ;;
  e2o)
    exec bash "$SCRIPT_DIR/triad-send.sh" executor-to-orchestrator "$@"
    ;;
  o2p)
    exec bash "$SCRIPT_DIR/triad-send.sh" orchestrator-to-planner "$@"
    ;;
  send)
    exec bash "$SCRIPT_DIR/triad-send.sh" "$@"
    ;;
  verify|doctor)
    verify "$@"
    ;;
  status)
    exec bash "$SCRIPT_DIR/triad-status.sh" "$@"
    ;;
  install)
    install_wrappers
    ;;
  -h|--help)
    usage
    ;;
  *)
    echo "triad-6b: unknown command: $COMMAND" >&2
    usage >&2
    exit 2
    ;;
esac
