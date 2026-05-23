#!/usr/bin/env bash
# 用法: bash launch.sh [--work-dir PATH]
# 一气化三清 · 七神启动器
# 创建 tmux 7-pane 布局，每个 pane 启动带专属 skill 的 claude
# 通过 hcom PTY 启动，避免 vanilla Stop hook poll 卡住前台输入。
set -euo pipefail

if [[ "${YQHSQ_ALLOW_LEGACY_HCOM:-0}" != "1" ]]; then
    cat >&2 <<'EOF'
❌ yqhsq legacy hcom/tmux launcher is disabled.

Use the Free Code official Agent Teams flow instead:
  1. TeamCreate
  2. Agent(name, team_name, prompt) for teammates
  3. SendMessage for follow-up coordination

Set YQHSQ_ALLOW_LEGACY_HCOM=1 only for manual debugging of the deprecated launcher.
EOF
    exit 2
fi

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPTS_DIR/.." && pwd)"
WORK_DIR="$(pwd)"
WINDOW_NAME="五神"
TARGET_SESSION=""
STATE_DIR="${HOME}/.brain/yqhsq"
EXPECTED_PANES=7
ENABLE_CODEX_DETECTOR="${YQHSQ_ENABLE_CODEX_WEB_DETECTOR:-0}"
YQHSQ_MODEL="${YQHSQ_MODEL:-}"
YQHSQ_SOURCE_SETTINGS="${YQHSQ_SOURCE_SETTINGS:-}"
YQHSQ_SOURCE_BARE="${YQHSQ_SOURCE_BARE:-0}"
YQHSQ_SOURCE_MODEL_ARG="${YQHSQ_SOURCE_MODEL_ARG:-}"
YQHSQ_SOURCE_TOOL="${YQHSQ_SOURCE_TOOL:-}"
YQHSQ_SOURCE_ADD_DIRS=()
YQHSQ_CONTEXT_ENV_KEYS=()

AGENTS=("taiyi" "yuanshi" "lingbao" "daode" "guanmiao" "siguo" "xuanshu")
TITLES=("太一·主持" "元始·谋" "灵宝·行" "道德·验" "观妙·观" "司过·错" "玄枢·醒")
ROLES=("Lead" "Planner" "Executor" "Critic" "Observer" "ErrorScribe" "CodexDetector")
YQHSQ_PROVIDER_ENV_KEYS=(
    "ANTHROPIC_BASE_URL"
    "ANTHROPIC_AUTH_TOKEN"
    "ANTHROPIC_API_KEY"
    "ANTHROPIC_MODEL"
    "ANTHROPIC_SMALL_FAST_MODEL"
    "ANTHROPIC_DEFAULT_OPUS_MODEL"
    "ANTHROPIC_DEFAULT_OPUS_MODEL_NAME"
    "ANTHROPIC_DEFAULT_OPUS_MODEL_DESCRIPTION"
    "ANTHROPIC_DEFAULT_SONNET_MODEL"
    "ANTHROPIC_DEFAULT_SONNET_MODEL_NAME"
    "ANTHROPIC_DEFAULT_SONNET_MODEL_DESCRIPTION"
    "ANTHROPIC_DEFAULT_HAIKU_MODEL"
    "ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME"
    "ANTHROPIC_DEFAULT_HAIKU_MODEL_DESCRIPTION"
    "ANTHROPIC_CUSTOM_MODEL_OPTION"
    "ANTHROPIC_CUSTOM_MODEL_OPTION_NAME"
    "ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION"
    "CLAUDE_CODE_SUBAGENT_MODEL"
    "CLAUDE_CODE_EFFORT_LEVEL"
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"
    "CLAUDE_CODE_TEAMMATE_COMMAND"
    "API_TIMEOUT_MS"
    "FREEGLM_TEAM_LAYOUT"
    "FREECODE_AGENT_TEAM_LAYOUT"
)

# 用于存储实际 pane ID（P1: 不硬编码 index）
PANE_IDS=()

# ── 参数解析 ─────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --work-dir) WORK_DIR="$2"; shift 2 ;;
        --model) YQHSQ_MODEL="$2"; shift 2 ;;
        --source-settings) YQHSQ_SOURCE_SETTINGS="$2"; shift 2 ;;
        --source-bare) YQHSQ_SOURCE_BARE="$2"; shift 2 ;;
        --source-tool) YQHSQ_SOURCE_TOOL="$2"; shift 2 ;;
        --source-add-dir) YQHSQ_SOURCE_ADD_DIRS+=("$2"); shift 2 ;;
        *) shift ;;
    esac
done

MODEL_CONTEXT_ENV="$(mktemp "${TMPDIR:-/tmp}/yqhsq-model-context.XXXXXX")"
MODEL_CONTEXT_ARGS=(
    --initial-model "$YQHSQ_MODEL" \
    --initial-settings "$YQHSQ_SOURCE_SETTINGS" \
    --initial-bare "$YQHSQ_SOURCE_BARE" \
    --initial-tool "$YQHSQ_SOURCE_TOOL" \
    --start-pid "$$"
)
for add_dir in "${YQHSQ_SOURCE_ADD_DIRS[@]:-}"; do
    MODEL_CONTEXT_ARGS+=(--initial-add-dir "$add_dir")
done
python3 "$SCRIPTS_DIR/resolve_model_context.py" "${MODEL_CONTEXT_ARGS[@]}" \
    >"$MODEL_CONTEXT_ENV"
# shellcheck disable=SC1090
source "$MODEL_CONTEXT_ENV"
rm -f "$MODEL_CONTEXT_ENV"

mkdir -p "$STATE_DIR"

# ── 失败清理 trap（P1: 失败时回收已创建的 pane）────────
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 && ${#PANE_IDS[@]} -gt 0 ]]; then
        echo "启动失败(exit=$exit_code)，清理已创建的 pane..."
        for pid in "${PANE_IDS[@]}"; do
            tmux kill-pane -t "$pid" 2>/dev/null || true
        done
        # 如果整个 window 空了就清理
        if [[ -n "${BASE:-}" ]]; then
            tmux kill-window -t "$BASE" 2>/dev/null || true
        fi
    fi
}
trap cleanup EXIT

# ── 环境检测 ─────────────────────────────────────────
if ! command -v tmux &>/dev/null; then
    echo "❌ tmux 未安装" >&2
    exit 1
fi

if [[ ! -d "$WORK_DIR" ]]; then
    echo "❌ 工作目录不存在: $WORK_DIR" >&2
    exit 1
fi

for name in "${AGENTS[@]}"; do
    if [[ ! -f "$SKILL_DIR/${name}.md" ]]; then
        echo "❌ 缺少 skill 文件: $SKILL_DIR/${name}.md" >&2
        exit 1
    fi
done

# ── 检测调用者是 freecode 还是 claude code ────────────
detect_invoking_tool() {
    if [[ -n "$YQHSQ_SOURCE_TOOL" ]]; then
        printf "%s" "$YQHSQ_SOURCE_TOOL"
        return 0
    fi
    local pid=$$
    while [[ $pid -gt 1 ]]; do
        local cmd
        local args
        cmd="$(ps -o comm= -p "$pid" 2>/dev/null || true)"
        args="$(ps -o args= -p "$pid" 2>/dev/null || true)"
        if [[ "$cmd" == *"free-code"* || "$cmd" == *"cli-dev"* || "$args" == *"free-code"* || "$args" == *".config/free-code"* || "$args" == *"--teammate-mode"* ]]; then
            printf "freecode"
            return 0
        fi
        pid="$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ')"
    done
    printf "claude"
}

INVOKING_TOOL="$(detect_invoking_tool)"

shell_quote() {
    printf "%s" "$1" | sed "s/'/'\\\\''/g; 1s/^/'/; \$s/\$/'/"
}

write_hcom_claude_wrapper() {
    local wrapper_path="$1"
    local exec_line="$2"
    local key=""
    local value=""
    local seen=()

    {
        echo "#!/usr/bin/env bash"
        echo "# Generated by yqhsq. Keep provider/model env aligned with the caller."
        for key in "${YQHSQ_PROVIDER_ENV_KEYS[@]}" "${YQHSQ_CONTEXT_ENV_KEYS[@]}"; do
            [[ -n "$key" ]] || continue
            if [[ " ${seen[*]:-} " == *" $key "* ]]; then
                continue
            fi
            seen+=("$key")
            if [[ "$key" == "ANTHROPIC_MODEL" && -n "$YQHSQ_MODEL" ]]; then
                value="$YQHSQ_MODEL"
            else
                value="${!key:-}"
            fi
            if [[ "$key" == "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS" && -z "$value" ]]; then
                value="1"
            fi
            if [[ "$key" == "FREEGLM_TEAM_LAYOUT" && -z "$value" ]]; then
                value="grid"
            fi
            if [[ "$key" == "FREECODE_AGENT_TEAM_LAYOUT" && -z "$value" ]]; then
                value="grid"
            fi
            if [[ -n "$value" ]]; then
                printf "export %s=%s\n" "$key" "$(shell_quote "$value")"
            fi
        done
        printf "exec %s \"\$@\"\n" "$exec_line"
    } >"$wrapper_path"
    chmod 700 "$wrapper_path"
}

prepare_hcom_claude_bin_dir() {
    local wrapper_dir="$HOME/.hcom/.tmp/bin"
    local wrapper_path="$wrapper_dir/claude"
    local exec_line=""

    # Always create a wrapper. hcom PTY/new-terminal paths do not reliably
    # inherit the caller shell env, so the wrapper pins model/provider env for
    # every yqhsq member.
    mkdir -p "$wrapper_dir"
    chmod 700 "$wrapper_dir"

    # ── freecode 模式：创建 wrapper 让 hcom 通过 tool=claude 调用 free-code ──
    if [[ "$INVOKING_TOOL" == "freecode" ]]; then
        local freecode_bin="$HOME/bin/free-code"
        if [[ ! -x "$freecode_bin" ]]; then
            echo "❌ freecode 二进制不存在: $freecode_bin" >&2
            return 1
        fi
        exec_line="$(shell_quote "$freecode_bin")"
        if [[ "$YQHSQ_SOURCE_BARE" == "1" ]]; then
            exec_line+=" --bare"
        fi
        if [[ -n "$YQHSQ_SOURCE_SETTINGS" && -f "$YQHSQ_SOURCE_SETTINGS" ]]; then
            exec_line+=" --settings $(shell_quote "$YQHSQ_SOURCE_SETTINGS")"
        fi
        for add_dir in "${YQHSQ_SOURCE_ADD_DIRS[@]:-}"; do
            if [[ -n "$add_dir" ]]; then
                exec_line+=" --add-dir $(shell_quote "$add_dir")"
            fi
        done
        exec_line+=" --teammate-mode tmux"
        write_hcom_claude_wrapper "$wrapper_path" "$exec_line"
        printf "%s" "$wrapper_dir"
        return 0
    fi

    # ── claude code 模式（原逻辑）──
    local local_bin="$HOME/.claude-cli-local/node_modules/.bin/claude"
    local local_cli="$HOME/.claude-cli-local/node_modules/@anthropic-ai/claude-code/cli.js"
    local global_cli="/opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/cli.js"
    local cli_path=""
    local path_bin=""

    if [[ -x "$local_bin" ]]; then
        exec_line="$(shell_quote "$local_bin")"
        write_hcom_claude_wrapper "$wrapper_path" "$exec_line"
        printf "%s" "$wrapper_dir"
        return 0
    fi

    path_bin="$(type -P claude || true)"
    if [[ -n "$path_bin" && -x "$path_bin" && "$path_bin" != "$wrapper_path" ]]; then
        exec_line="$(shell_quote "$path_bin")"
        write_hcom_claude_wrapper "$wrapper_path" "$exec_line"
        printf "%s" "$wrapper_dir"
        return 0
    fi

    if [[ -f "$local_cli" ]]; then
        cli_path="$local_cli"
    elif [[ -f "$global_cli" ]]; then
        cli_path="$global_cli"
    fi

    if [[ -n "$cli_path" ]]; then
        exec_line="node $(shell_quote "$cli_path")"
        write_hcom_claude_wrapper "$wrapper_path" "$exec_line"
        printf "%s" "$wrapper_dir"
        return 0
    fi

    if command -v npm &>/dev/null; then
        exec_line="npm exec --yes @anthropic-ai/claude-code --"
        write_hcom_claude_wrapper "$wrapper_path" "$exec_line"
        printf "%s" "$wrapper_dir"
        return 0
    fi

    return 1
}

CLAUDE_BIN_DIR="$(prepare_hcom_claude_bin_dir)" || {
    echo "❌ 未找到可供 hcom 使用的可执行入口 (tool=$INVOKING_TOOL)" >&2
    exit 1
}

echo "🔧 检测到调用工具: $INVOKING_TOOL → 七神将以 $INVOKING_TOOL 模式启动"
if [[ -n "$YQHSQ_MODEL" ]]; then
    echo "🔧 源模型: $YQHSQ_MODEL"
else
    echo "🔧 源模型: 未解析到显式模型，使用调用工具默认模型"
fi
if [[ -n "$YQHSQ_SOURCE_SETTINGS" ]]; then
    echo "🔧 源 settings: $YQHSQ_SOURCE_SETTINGS"
fi
if [[ ${#YQHSQ_SOURCE_ADD_DIRS[@]} -gt 0 ]]; then
    echo "🔧 源 add-dir: ${YQHSQ_SOURCE_ADD_DIRS[*]}"
fi

LAUNCH_AGENT_PY="$SCRIPTS_DIR/launch_agent.py"
if [[ ! -f "$LAUNCH_AGENT_PY" ]]; then
    echo "❌ 缺少单-agent 启动器: $LAUNCH_AGENT_PY" >&2
    exit 1
fi

# ── 场景 A: 不在 tmux 内 → 创建 session 后递归 ──────
if [[ -z "${TMUX:-}" ]]; then
    SESSION_NAME="yqhsq-$$"
    tmux new-session -d -s "$SESSION_NAME" -c "$WORK_DIR"
    RECURSIVE_CMD="bash $(shell_quote "${SCRIPTS_DIR}/launch.sh") --work-dir $(shell_quote "$WORK_DIR")"
    if [[ -n "$YQHSQ_MODEL" ]]; then
        RECURSIVE_CMD+=" --model $(shell_quote "$YQHSQ_MODEL")"
    fi
    if [[ -n "$YQHSQ_SOURCE_SETTINGS" ]]; then
        RECURSIVE_CMD+=" --source-settings $(shell_quote "$YQHSQ_SOURCE_SETTINGS")"
    fi
    if [[ -n "$YQHSQ_SOURCE_BARE" ]]; then
        RECURSIVE_CMD+=" --source-bare $(shell_quote "$YQHSQ_SOURCE_BARE")"
    fi
    if [[ -n "$YQHSQ_SOURCE_TOOL" ]]; then
        RECURSIVE_CMD+=" --source-tool $(shell_quote "$YQHSQ_SOURCE_TOOL")"
    fi
    for add_dir in "${YQHSQ_SOURCE_ADD_DIRS[@]:-}"; do
        if [[ -n "$add_dir" ]]; then
            RECURSIVE_CMD+=" --source-add-dir $(shell_quote "$add_dir")"
        fi
    done
    tmux send-keys -t "$SESSION_NAME" "$RECURSIVE_CMD" C-m
    exec tmux attach -t "$SESSION_NAME"
fi

TARGET_SESSION="$(tmux display-message -p '#S' 2>/dev/null || true)"
if [[ -z "$TARGET_SESSION" ]]; then
    echo "❌ 无法解析当前 tmux session" >&2
    exit 1
fi

# ── 幂等检测 → 自动清理重启 ─────────────────────────────
EXISTING_WINDOW_TARGET="$(tmux list-windows -a -F '#{session_name}:#{window_index} #{window_name}' 2>/dev/null \
    | awk -v session="$TARGET_SESSION" -v window="$WINDOW_NAME" '$1 ~ ("^" session ":") && $2 == window {print $1; exit}')"
if [[ -n "$EXISTING_WINDOW_TARGET" ]]; then
    echo "⚡ 检测到旧的 ${WINDOW_NAME} window，自动清理后重启..."
    bash "$SCRIPTS_DIR/shutdown.sh" --force
    sleep 2
fi

# ── 清理残留 hcom agents（防止名字冲突）────────────────
if command -v hcom &>/dev/null; then
    for name in "${AGENTS[@]}"; do
        if hcom list 2>/dev/null | grep -q "\\b${name}\\b"; then
            echo "⚡ 清理残留 agent: $name"
            hcom kill "$name" 2>/dev/null || true
        fi
    done
    sleep 1
fi

# ── hcom daemon（PTY 启动依赖 hcom）────────────────────
if ! command -v hcom &>/dev/null; then
    echo "❌ 缺少 hcom，无法启动五神 PTY 协作模式" >&2
    exit 1
fi

HAS_HCOM=false
if ! pgrep -qf "hcom daemon"; then
    hcom daemon > /dev/null 2>&1 &
fi
for _attempt in $(seq 1 10); do
    if hcom status &>/dev/null; then
        HAS_HCOM=true
        break
    fi
    sleep 0.5
done
if [[ "$HAS_HCOM" != true ]]; then
    echo "❌ hcom daemon 未就绪，无法启动五神 PTY 协作模式" >&2
    exit 1
fi

# ── 创建 tmux 布局（P1: 用 -P -F 捕获实际 pane ID）───
BASE=$(tmux new-window -P -F '#{session_name}:#{window_index}' -t "${TARGET_SESSION}:" \
    -n "$WINDOW_NAME" -c "$WORK_DIR")
# 初始 pane (pane 0) 的 ID
PANE_IDS+=("$(tmux list-panes -t "$BASE" -F '#{pane_id}' | tail -1)")
for _split in $(seq 1 $((EXPECTED_PANES - 1))); do
    PANE_IDS+=("$(tmux split-window -t "$BASE" -c "$WORK_DIR" -P -F '#{pane_id}')")
    tmux select-layout -t "$BASE" tiled >/dev/null
done

PANE_IDS=()
while IFS= read -r line; do PANE_IDS+=("$line"); done < <(tmux list-panes -t "$BASE" -F '#{pane_id}')

if [[ ${#PANE_IDS[@]} -ne "$EXPECTED_PANES" ]]; then
    echo "❌ 预期 ${EXPECTED_PANES} 个 pane，实际 ${#PANE_IDS[@]}" >&2
    exit 1
fi

# ── 每个 pane 启动 claude（PTY 模式，无 Stop hook poll 前台阻塞）──
for i in $(seq 0 $((EXPECTED_PANES - 1))); do
    PANE="${PANE_IDS[$i]}"
    NAME="${AGENTS[$i]}"
    TITLE="${TITLES[$i]}"
    ROLE="${ROLES[$i]}"
    SKILL_FILE="$SKILL_DIR/${NAME}.md"

    # 设置 pane 标题
    tmux select-pane -t "$PANE" -T "$TITLE"

    CMD="python3 '$LAUNCH_AGENT_PY'"
    CMD+=" --name '$NAME'"
    CMD+=" --title '$TITLE'"
    CMD+=" --role '$ROLE'"
    CMD+=" --skill-file '$SKILL_FILE'"
    CMD+=" --work-dir '$WORK_DIR'"
    CMD+=" --claude-bin-dir '$CLAUDE_BIN_DIR'"
    if [[ -n "$YQHSQ_MODEL" ]]; then
        CMD+=" --model '$YQHSQ_MODEL'"
    fi

    tmux send-keys -t "$PANE" "$CMD" C-m

    # 间隔启动，避免 API 压力
    sleep 1
done

start_sidecar() {
    local name="$1"
    shift
    local pid_file="$STATE_DIR/${name}.pid"
    local log_file="$STATE_DIR/${name}.log"
    local existing_pid=""
    local detached_pid=""

    if [[ -f "$pid_file" ]]; then
        existing_pid="$(cat "$pid_file" 2>/dev/null || true)"
        if [[ -n "$existing_pid" ]] && kill -0 "$existing_pid" 2>/dev/null; then
            return 0
        fi
    fi

    detached_pid="$(
        python3 - "$log_file" "$@" <<'PY'
import subprocess
import sys

log_path = sys.argv[1]
cmd = sys.argv[2:]

with open(log_path, "ab", buffering=0) as log_file:
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=log_file,
        stderr=log_file,
        start_new_session=True,
        close_fds=True,
    )

print(proc.pid)
PY
    )"

    echo "$detached_pid" >"$pid_file"
}

start_sidecar \
    "cc-error-watch" \
    python3 -u "$SCRIPTS_DIR/cc_error_watch.py" \
    --window-name "$WINDOW_NAME"

if [[ "$ENABLE_CODEX_DETECTOR" == "1" ]]; then
    start_sidecar \
        "codex-detector" \
        python3 -u "$SCRIPTS_DIR/codex_detector.py" \
        --workspace "$WORK_DIR" \
        --label "codex-login" \
        --interval 300 \
        --idle-threshold 300
fi

# ── 配置 tmux 显示 ───────────────────────────────────
tmux set-option -w -t "$BASE" pane-border-status top
tmux set-option -w -t "$BASE" pane-border-format ' #{pane_index}: #{pane_title} '
tmux select-pane -t "${PANE_IDS[0]}"

# ── 等待 claude 启动（必须完成 hcom hook 绑定）───
echo "等待 claude PTY 进程启动并完成 hcom hook 绑定..."
for _attempt in $(seq 1 30); do
    sleep 3
    VERIFY_OUTPUT="$(bash "$SCRIPTS_DIR/verify.sh" 2>/dev/null || true)"
    ALIVE="$(printf "%s" "$VERIFY_OUTPUT" | sed -n 's/.*"claude_alive":\([0-9][0-9]*\).*/\1/p')"
    STATUS="$(printf "%s" "$VERIFY_OUTPUT" | sed -n 's/.*"status":"\([^"]*\)".*/\1/p')"
    ALIVE="${ALIVE:-0}"
    STATUS="${STATUS:-unknown}"
    if [[ "$STATUS" == "ok" ]]; then
        break
    fi
    echo "  已绑定 ${ALIVE}/${EXPECTED_PANES}，等待中..."
done

# ── 验证 ─────────────────────────────────────────────
bash "$SCRIPTS_DIR/verify.sh"
