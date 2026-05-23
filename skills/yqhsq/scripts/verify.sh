#!/usr/bin/env bash
# 用法: bash verify.sh
# 一气化三清 · 七神验证器
# 输出 JSON，exit 0=全通过，exit 1=异常
set -euo pipefail

WINDOW_NAME="五神"
EXPECTED_PANES=7
STATE_DIR="${HOME}/.brain/yqhsq"
HEALTH_FILE="${HOME}/.brain/shared_memory/recent/cc_agent_health.json"

pid_alive() {
    local pid_file="$1"
    local pid=""
    [[ -f "$pid_file" ]] || return 1
    pid="$(cat "$pid_file" 2>/dev/null || true)"
    [[ -n "$pid" ]] || return 1
    kill -0 "$pid" 2>/dev/null
}

# P1: 检查限定到五神 window
if ! tmux list-windows -a -F '#{window_name}' 2>/dev/null | grep -q "^${WINDOW_NAME}$"; then
    echo '{"tmux_started":false,"panes":0,"claude_alive":0,"status":"not_found"}'
    exit 1
fi

# 获取 session:window 目标
WIN_TARGET=$(tmux list-windows -a -F '#{window_name}:#{session_name}:#{window_index}' \
    | grep "^${WINDOW_NAME}:" | head -1 | cut -d: -f2-3)

# 检查 pane 数
PANE_COUNT=$(tmux list-panes -t "$WIN_TARGET" 2>/dev/null | wc -l | tr -d ' ')

# 检查 agent 是否真实可协作：
# 只看到名字不够，必须同时满足 hooks_bound/process_bound/session_id，
# 否则只是 hcom 预注册占位，太一无法可靠分派任务。
AGENTS=("taiyi" "yuanshi" "lingbao" "daode" "guanmiao" "siguo" "xuanshu")
HCOM_JSON="$(hcom list --json 2>/dev/null || true)"
HCOM_SUMMARY="$(
    YQHSQ_VERIFY_AGENTS="${AGENTS[*]}" \
    YQHSQ_HCOM_JSON="$HCOM_JSON" \
    python3 - <<'PY'
import json
import os

wanted = os.environ["YQHSQ_VERIFY_AGENTS"].split()
rows = {}
for line in os.environ.get("YQHSQ_HCOM_JSON", "").splitlines():
    try:
        row = json.loads(line)
    except json.JSONDecodeError:
        continue
    name = row.get("name")
    if name in wanted:
        rows[name] = row

ready = 0
unready = []
for name in wanted:
    row = rows.get(name)
    if not row:
        unready.append(f"{name}:missing")
        continue
    status_ok = row.get("status") in {"active", "listening"}
    hooks_ok = bool(row.get("hooks_bound"))
    process_ok = bool(row.get("process_bound"))
    session_ok = bool(row.get("session_id"))
    if status_ok and hooks_ok and process_ok and session_ok:
        ready += 1
    else:
        reasons = []
        if not status_ok:
            reasons.append(f"status={row.get('status')}")
        if not hooks_ok:
            reasons.append("hooks_bound=false")
        if not process_ok:
            reasons.append("process_bound=false")
        if not session_ok:
            reasons.append("session_id=null")
        unready.append(f"{name}:{'+'.join(reasons)}")

print(f"{ready}|{','.join(unready)}")
PY
)"
CLAUDE_ALIVE="${HCOM_SUMMARY%%|*}"
HCOM_UNREADY="${HCOM_SUMMARY#*|}"

# 判定状态
ERROR_WATCH_ALIVE=false
CODEX_DETECTOR_ALIVE=false
AGENT_HEALTH_FRESH=false
pid_alive "$STATE_DIR/cc-error-watch.pid" && ERROR_WATCH_ALIVE=true
pid_alive "$STATE_DIR/codex-detector.pid" && CODEX_DETECTOR_ALIVE=true
if [[ -f "$HEALTH_FILE" ]]; then
    NOW_EPOCH="$(date +%s)"
    HEALTH_MTIME="$(stat -f %m "$HEALTH_FILE" 2>/dev/null || echo 0)"
    if [[ "$HEALTH_MTIME" -gt 0 && $((NOW_EPOCH - HEALTH_MTIME)) -le 900 ]]; then
        AGENT_HEALTH_FRESH=true
    fi
fi

if [[ "$PANE_COUNT" -ge "$EXPECTED_PANES" && "$CLAUDE_ALIVE" -ge "$EXPECTED_PANES" ]]; then
    STATUS="ok"
    EXIT=0
elif [[ "$PANE_COUNT" -ge "$EXPECTED_PANES" ]]; then
    STATUS="partial"
    EXIT=1
else
    STATUS="failed"
    EXIT=1
fi

echo "{\"tmux_started\":true,\"panes\":${PANE_COUNT},\"claude_alive\":${CLAUDE_ALIVE},\"hcom_unready\":\"${HCOM_UNREADY}\",\"error_watch_alive\":${ERROR_WATCH_ALIVE},\"codex_detector_alive\":${CODEX_DETECTOR_ALIVE},\"agent_health_fresh\":${AGENT_HEALTH_FRESH},\"status\":\"${STATUS}\"}"
exit $EXIT
