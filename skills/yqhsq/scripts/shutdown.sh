#!/usr/bin/env bash
# 用法: bash shutdown.sh [--force]
# 一气化三清 · 五神关闭器
# P0: 只关闭五神 window，绝不杀其他 session
set -euo pipefail

WINDOW_NAME="五神"
FORCE=false
STATE_DIR="${HOME}/.brain/yqhsq"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --force) FORCE=true; shift ;;
        *) shift ;;
    esac
done

stop_sidecar() {
    local pid_file="$1"
    local pid=""
    [[ -f "$pid_file" ]] || return 0
    pid="$(cat "$pid_file" 2>/dev/null || true)"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null || true
    fi
    rm -f "$pid_file"
}

# 找五神 window
if ! tmux list-windows -a -F '#{window_name}' 2>/dev/null | grep -q "^${WINDOW_NAME}$"; then
    echo '{"status":"not_found","message":"五神未运行"}'
    exit 0
fi

WIN_TARGET=$(tmux list-windows -a -F '#{window_name}:#{session_name}:#{window_index}' \
    | grep "^${WINDOW_NAME}:" | head -1 | cut -d: -f2-3)

if [[ "$FORCE" != "true" ]]; then
    # 优雅关闭: 向每个 pane 发 /exit
    PANE_COUNT=$(tmux list-panes -t "$WIN_TARGET" 2>/dev/null | wc -l | tr -d ' ')
    for i in $(seq $((PANE_COUNT - 1)) -1 0); do
        tmux send-keys -t "$WIN_TARGET.$i" "/exit" C-m 2>/dev/null || true
    done
    sleep 5
fi

# 只关闭五神 window（P0: 绝不 kill-session）
if tmux list-windows -a -F '#{window_name}' 2>/dev/null | grep -q "^${WINDOW_NAME}$"; then
    tmux kill-window -t "$WIN_TARGET"
fi

stop_sidecar "$STATE_DIR/cc-error-watch.pid"
stop_sidecar "$STATE_DIR/codex-detector.pid"

echo '{"status":"closed","message":"五神已关闭"}'
exit 0
