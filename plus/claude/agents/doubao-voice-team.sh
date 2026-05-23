#!/bin/bash
# doubao-voice-team.sh - 启动 5 个 Opus Agent 处理 Doubao Voice 集成
# 用法: ./doubao-voice-team.sh [session-name]
set -e

SESSION="${1:-dvteam}"
AGENT_DIR="$HOME/.claude/agents/doubao-voice-team"

mkdir -p "$AGENT_DIR"

# 项目上下文
PROJECT_DIR="$HOME/Developer/doubao-voice"

echo "=== Doubao Voice Team ==="
echo "Session: $SESSION"

# ---------- Agent 1: arch - 架构师 ----------
ARCH_PROMPT="你想成为架构师。你的任务：设计 闪电说的(Shandianshuo) macOS 桌面语音助手 与 豆包Voice Daemon 的集成架构。

## 背景
- 闪电说的 (Shandianshuo)：macOS 桌面语音助手，通过 bigmodel.cn 调用 LLM（智谱glm-5、MiniMax-M2.5、火山引擎doubao-seed）。有麦克风音频捕获、LLM 对话、TTS 播放能力。
- 豆包Voice Daemon：~/Developer/doubao-voice/doubao_voice.py，完整 ASR→LLM→TTS pipeline（火山引擎ASR WebSocket + LLM + TTS HTTP），包含 SileroVAD、语音指纹、回声消除等优化。
- Shandianshuo 日志显示它最近在用 volcengine doubao-seed 模型，但直接调 bigmodel.cn（报错了）。

## 你的任务
1. 搜索 Shandianshuo 的插件机制/API 文档（如果有）
2. 设计 Shandianshuo ↔ Doubao Voice 的集成方案
3. 关键问题：
   - Shandianshuo 如何使用 Doubao Voice 的 ASR？
   - 如何用 Doubao Voice 替换 Shandianshuo 的 LLM 后端？
   - IPC 方式选择（Unix socket / HTTP / FIFO）？
   - 如何复用 Doubao Voice 的 VAD 和回声消除？

## 输出
1. 推荐架构方案（含理由）
2. 实施步骤
3. 需要 Shandianshuo 提供的接口列表

## 完成后
通过 hcom send 向 api、vad、tts、test 发消息告知你的架构决策。
"

echo "$ARCH_PROMPT" > "$AGENT_DIR/arch-prompt.txt"

# ---------- Agent 2: api - API 工程师 ----------
API_PROMPT="你想成为 API 工程师。你负责实现 Shandianshuo × Doubao Voice 集成的 API 层。

## 当前状态
等待 arch 架构师发消息告知架构决策。

## Doubao Voice HTTP/TTS 实现（参考）
运行：head -350 ~/Developer/doubao-voice/doubao_voice.py | tail -100

## 环境变量配置
运行：grep -v '^#' ~/Developer/doubao-voice/.env 2>/dev/null | grep '=' | head -20

## 你的任务
等收到 arch 的 hcom 消息后：
1. 如果架构是 HTTP API → 为 Doubao Voice 添加 HTTP 服务接口
2. 如果架构是 Unix socket → 实现 socket wrapper
3. 编写 Shandianshuo 插件文件（参考其插件文档）

## 等待方式
先用 hcom listen 等待 arch 消息。收到后开始实现。

## 完成后
hcom send arch 报告完成状态。"
echo "$API_PROMPT" > "$AGENT_DIR/api-prompt.txt"

# ---------- Agent 3: vad - VAD/音频工程师 ----------
VAD_PROMPT="你想成为 VAD/音频工程师。你负责音频管道（麦克风→VAD→ASR）的集成。

## Doubao Voice VAD 实现
运行：grep -A 70 'class SmartVAD' ~/Developer/doubao-voice/doubao_voice.py
运行：grep -A 50 'class ASRWarmer' ~/Developer/doubao-voice/doubao_voice.py

## 你的任务
1. 分析 Doubao Voice 的 SileroVAD 实现（基于 ONNX）
2. 分析 ASR Warmer（连接预热）机制
3. 设计 Shandianshuo 音频流 → Doubao Voice ASR WebSocket 的接入方案
4. 评估预触发缓冲（400ms ring buffer）的必要性

## 完成后
hcom send arch \"VAD方案已完成：<简要描述>\"
hcom send test \"VAD集成方案：<详细说明>\"
"
echo "$VAD_PROMPT" > "$AGENT_DIR/vad-prompt.txt"

# ---------- Agent 4: tts - TTS/播放工程师 ----------
TTS_PROMPT="你想成为 TTS/播放工程师。你负责 TTS 合成与音频播放的集成。

## Doubao Voice TTS 实现
运行：grep -A 20 'async def volcengine_tts' ~/Developer/doubao-voice/doubao_voice.py
运行：grep -A 15 '_play_pcm' ~/Developer/doubao-voice/doubao_voice.py
运行：grep 'tts_playing\|tts_playing' ~/Developer/doubao-voice/doubao_voice.py
运行：grep 'DEFAULT_VOICE' ~/Developer/doubao-voice/doubao_voice.py

## 你的任务
1. 分析 TTS HTTP API 调用（volcengine TTS）
2. 设计 Shandianshuo 接收 TTS PCM 流的方案
3. 实现回声消除的麦克风静音策略（tts_playing 标志）
4. 评估句级 TTS pipeline 是否需要适配

## 完成后
hcom send arch \"TTS方案已完成：<简要描述>\"
hcom send test \"TTS集成方案：<详细说明>\"
"
echo "$TTS_PROMPT" > "$AGENT_DIR/tts-prompt.txt"

# ---------- Agent 5: test - 测试工程师 ----------
TEST_PROMPT="你想成为测试工程师。你负责设计端到端测试方案。

## Doubao Voice 架构
Mic → SmartVAD(SileroVAD) → ASR(WebSocket) → LLM(volcenginesdkarkruntime) → TTS(HTTP) → Speaker
                                             ↑ voice fingerprint (optional)

## 你的任务
等待 vad 和 tts agent 的 hcom 消息后，设计测试用例：
- TC1: 语音识别准确性
- TC2: LLM 对话响应
- TC3: TTS 合成质量
- TC4: 全链路延迟测试
- TC5: 错误恢复（网络断开、API 超时）
- TC6: 回声消除效果
- TC7: 并发对话

先用 hcom listen 等待 vad 和 tts 的消息。

## 完成后
hcom send arch \"测试方案已完成：<简要描述>\"
"
echo "$TEST_PROMPT" > "$AGENT_DIR/test-prompt.txt"

# ---------- 创建 tmux session ----------
# 如果已存在，先杀死
tmux kill-session -t "$SESSION" 2>/dev/null || true

# 创建 session（后台）
tmux new-session -d -s "$SESSION"

# Window 1: arch
echo "[1/5] Launching arch (架构师)..."
tmux new-window -t "$SESSION" -n "01-arch"
tmux send-keys -t "$SESSION:01-arch" \
  "claude --model opus --name arch --system-prompt-file $AGENT_DIR/arch-prompt.txt --no-session-persistence" C-m

sleep 3

# Window 2: api
echo "[2/5] Launching api (API工程师)..."
tmux new-window -t "$SESSION" -n "02-api"
tmux send-keys -t "$SESSION:02-api" \
  "claude --model opus --name api --system-prompt-file $AGENT_DIR/api-prompt.txt --no-session-persistence" C-m

sleep 2

# Window 3: vad
echo "[3/5] Launching vad (VAD/音频工程师)..."
tmux new-window -t "$SESSION" -n "03-vad"
tmux send-keys -t "$SESSION:03-vad" \
  "claude --model opus --name vad --system-prompt-file $AGENT_DIR/vad-prompt.txt --no-session-persistence" C-m

sleep 2

# Window 4: tts
echo "[4/5] Launching tts (TTS/播放工程师)..."
tmux new-window -t "$SESSION" -n "04-tts"
tmux send-keys -t "$SESSION:04-tts" \
  "claude --model opus --name tts --system-prompt-file $AGENT_DIR/tts-prompt.txt --no-session-persistence" C-m

sleep 2

# Window 5: test
echo "[5/5] Launching test (测试工程师)..."
tmux new-window -t "$SESSION" -n "05-test"
tmux send-keys -t "$SESSION:05-test" \
  "claude --model opus --name test --system-prompt-file $AGENT_DIR/test-prompt.txt --no-session-persistence" C-m

sleep 1

# ---------- 完成 ----------
echo ""
echo "=== All 5 agents launched ==="
echo ""
echo "Attach with: tmux attach -t $SESSION"
echo ""
echo "Windows:"
tmux list-windows -t "$SESSION"
echo ""
echo "Team:"
echo "  01-arch  - 架构师 (设计集成方案)"
echo "  02-api   - API工程师 (实现API/插件)"
echo "  03-vad   - VAD/音频工程师 (音频管道)"
echo "  04-tts   - TTS/播放工程师 (TTS和播放)"
echo "  05-test  - 测试工程师 (端到端测试)"
echo ""
echo "Prompts saved to: $AGENT_DIR/"
