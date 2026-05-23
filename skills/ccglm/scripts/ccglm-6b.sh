#!/usr/bin/env bash
# Stable 6.0b entrypoint for one or more CCGLM/freeglm iTerm lanes.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRAIN_SCRIPTS="/Volumes/金阳/brain/scripts"

usage() {
  cat <<'USAGE'
Usage:
  ccglm-6b.sh start-lanes [options]
  ccglm-6b.sh amazon-selection [options]
  ccglm-6b.sh verify [options]
  ccglm-6b.sh install

Subcommands:
  start-lanes       Start any number of named freeglm lanes and send a 6.0b bootstrap prompt.
  amazon-selection  Start the default Amazon product-selection pair: orchestrator/小o and executor/小e.
  verify            Check the ccglm sender and this scripted entrypoint.
  install           Install /Volumes brain wrappers for this script set.

start-lanes options:
  --cwd PATH            Working directory context. Default: current directory.
  --task TEXT           Shared task context sent to every lane.
  --lane NAME:SHORT:ROLE
                        Add a lane. Repeat this option for any number of lanes.
  --focus              Focus destination windows. Default.
  --no-focus           Background delivery where supported.
  --startup-delay N    Seconds to wait after starting freeglm. Default: CCGLM_STARTUP_DELAY or 6.

If no --lane is provided, start-lanes uses the same defaults as amazon-selection.
USAGE
}

json_string() {
  python3 -c 'import json,sys; print(json.dumps(sys.argv[1], ensure_ascii=False))' "$1"
}

install_wrapper() {
  local name="$1"
  local command="$2"
  local dest="$BRAIN_SCRIPTS/$name"
  mkdir -p "$BRAIN_SCRIPTS"
  cat > "$dest" <<EOF
#!/usr/bin/env bash
set -euo pipefail
exec bash $command "\$@"
EOF
  chmod 700 "$dest"
  printf '%s\n' "$dest"
}

install_wrappers() {
  install_wrapper ccglm-6b.sh "$SCRIPT_DIR/ccglm-6b.sh"
  install_wrapper ccglm-lanes.sh "$SCRIPT_DIR/ccglm-6b.sh start-lanes"
}

default_lanes() {
  LANES+=("orchestrator:小o:orchestrator/小o，负责统筹亚马逊选品任务、拆解流程、明确需要的数据、安排 executor 执行、汇总判断并输出最终选品结论。")
  LANES+=("executor:小e:executor/小e，负责按 orchestrator/小o 的拆解执行具体调研、数据整理、竞品分析、机会判断和风险核查。")
}

parse_lane() {
  python3 - "$1" <<'PY'
import sys

spec = sys.argv[1]
parts = spec.split(":", 2)
if len(parts) != 3 or not all(part.strip() for part in parts):
    raise SystemExit("lane must use NAME:SHORT:ROLE")
print("\t".join(part.strip() for part in parts))
PY
}

build_prompt() {
  LANE_NAME="$1" SHORT_NAME="$2" ROLE_TEXT="$3" TASK_TEXT="$4" CWD_TEXT="$5" python3 - <<'PY'
import os

lane = os.environ["LANE_NAME"]
short = os.environ["SHORT_NAME"]
role = os.environ["ROLE_TEXT"]
task = os.environ["TASK_TEXT"]
cwd = os.environ["CWD_TEXT"]

print(f"""/codex
CCGLM_LANE_BOOTSTRAP_V1
scripted: 6.0b
cwd: {cwd}

from: Codex 6.0b bootstrap
to: {lane} ({short})

identity:
- Your stable lane name is {lane}.
- Your short name is {short}.

task:
{task}

role:
{role}

rules:
- You are a separate freeglm lane started by ccglm-6b.sh.
- Treat other named lanes as collaborators, not as your own internal thoughts.
- Do not fabricate Amazon marketplace data, sales, rank, pricing, or competitor facts.
- If current marketplace research is required, state what data/tooling is needed or cite the source you actually used.
- Keep outputs actionable: findings, assumptions, risks, blockers, and next requested action.
- If a TRIAD_LOOPBACK_V1 envelope appears later, follow its loopback_required script exactly.
""")
PY
}

parse_start_lanes_args() {
  CWD="$PWD"
  TASK="执行一个亚马逊的选品任务。"
  FOCUS=1
  STARTUP_DELAY="${CCGLM_STARTUP_DELAY:-6}"
  LANES=()

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --cwd)
        CWD="${2:?--cwd requires a path}"
        shift 2
        ;;
      --task)
        TASK="${2:?--task requires text}"
        shift 2
        ;;
      --lane)
        LANES+=("${2:?--lane requires NAME:SHORT:ROLE}")
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
      --startup-delay)
        STARTUP_DELAY="${2:?--startup-delay requires a value}"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        echo "ccglm-6b start-lanes: unknown option: $1" >&2
        usage >&2
        exit 2
        ;;
    esac
  done

  if [[ ! -d "$CWD" ]]; then
    echo "ccglm-6b start-lanes: cwd does not exist: $CWD" >&2
    exit 2
  fi
  case "$STARTUP_DELAY" in
    ''|*[!0-9.]*)
      echo "ccglm-6b start-lanes: startup delay must be numeric" >&2
      exit 2
      ;;
  esac
  if [[ "${#LANES[@]}" -eq 0 ]]; then
    default_lanes
  fi
}

record_lane() {
  local results="$1"
  local lane="$2"
  local short="$3"
  local role="$4"
  local status="$5"
  local rc="$6"
  local detail="$7"
  local role_b64 detail_b64
  role_b64="$(printf '%s' "$role" | base64 | tr -d '\n')"
  detail_b64="$(printf '%s' "$detail" | base64 | tr -d '\n')"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$lane" "$short" "$status" "$rc" "$role_b64" "$detail_b64" >> "$results"
}

emit_results() {
  python3 - "$1" "$CWD" "$TASK" <<'PY'
import base64
import json
import sys
from pathlib import Path

rows = []
ttys = []
ok = True
for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    lane, short, status, rc, role_b64, detail_b64 = line.split("\t", 5)
    detail = base64.b64decode(detail_b64).decode("utf-8", errors="replace")
    parsed = None
    try:
        parsed = json.loads(detail)
    except Exception:
        ok = False
    tty = parsed.get("tty") if isinstance(parsed, dict) else None
    if tty:
        ttys.append(tty)
    if status != "ok":
        ok = False
    rows.append(
        {
            "lane": lane,
            "short_name": short,
            "status": status,
            "exit_code": int(rc),
            "tty": tty,
            "detail": parsed if parsed is not None else detail,
        }
    )

distinct_ttys = len(ttys) == len(set(ttys))
if ttys and not distinct_ttys:
    ok = False

print(
    json.dumps(
        {
            "ok": ok,
            "scripted": "6.0b",
            "cwd": sys.argv[2],
            "task": sys.argv[3],
            "lane_count": len(rows),
            "distinct_ttys": distinct_ttys,
            "lanes": rows,
        },
        ensure_ascii=False,
        indent=2,
    )
)
if not ok:
    raise SystemExit(1)
PY
}

start_lanes() {
  parse_start_lanes_args "$@"

  local results
  results="$(mktemp)"

  local focus_args=()
  if [[ "$FOCUS" -eq 1 ]]; then
    focus_args+=(--focus)
  else
    focus_args+=(--no-focus)
  fi

  local spec lane short role prompt output rc
  for spec in "${LANES[@]}"; do
    IFS=$'\t' read -r lane short role < <(parse_lane "$spec")
    prompt="$(build_prompt "$lane" "$short" "$role" "$TASK" "$CWD")"
    if output="$(bash "$SCRIPT_DIR/ccglm-main-send.sh" --cwd "$CWD" --session "$lane" --new-window --startup-delay "$STARTUP_DELAY" "${focus_args[@]}" "$prompt" 2>&1)"; then
      record_lane "$results" "$lane" "$short" "$role" "ok" 0 "$output"
    else
      rc=$?
      record_lane "$results" "$lane" "$short" "$role" "error" "$rc" "$output"
    fi
  done

  local emit_rc=0
  emit_results "$results" || emit_rc=$?
  rm -f "$results"
  return "$emit_rc"
}

amazon_selection() {
  start_lanes "$@"
}

verify() {
  local failures=0
  [[ -x "$SCRIPT_DIR/ccglm-main-send.sh" ]] || { echo "ccglm-6b verify: missing ccglm-main-send.sh" >&2; failures=$((failures + 1)); }
  [[ -x "$SCRIPT_DIR/ccglm-iterm-send.sh" ]] || { echo "ccglm-6b verify: missing ccglm-iterm-send.sh" >&2; failures=$((failures + 1)); }
  grep -Fq 'acquire_iterm_lock' "$SCRIPT_DIR/ccglm-iterm-send.sh" || { echo "ccglm-6b verify: iTerm sender lock missing" >&2; failures=$((failures + 1)); }
  grep -Fq 'findNewWindow(beforeWindowIds)' "$SCRIPT_DIR/ccglm-iterm-send.sh" || { echo "ccglm-6b verify: stable new-window target missing" >&2; failures=$((failures + 1)); }
  bash -n "$SCRIPT_DIR/ccglm-iterm-send.sh" || failures=$((failures + 1))
  bash -n "$SCRIPT_DIR/ccglm-main-send.sh" || failures=$((failures + 1))
  bash -n "$0" || failures=$((failures + 1))

  if [[ "$failures" -ne 0 ]]; then
    echo "ccglm-6b verify: failed checks: $failures" >&2
    exit 1
  fi

  printf '{"ok":true,"scripted":"6.0b","sender_lock":true,"stable_new_window":true}\n'
}

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 2
fi

COMMAND="$1"
shift

case "$COMMAND" in
  start-lanes|lanes)
    start_lanes "$@"
    ;;
  amazon-selection|amazon)
    amazon_selection "$@"
    ;;
  verify|doctor)
    verify "$@"
    ;;
  install)
    install_wrappers
    ;;
  -h|--help)
    usage
    ;;
  *)
    echo "ccglm-6b: unknown command: $COMMAND" >&2
    usage >&2
    exit 2
    ;;
esac
