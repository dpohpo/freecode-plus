#!/bin/bash
#
# 实时中文语音对话启动脚本
# 

set -e

echo "=========================================="
echo "  实时中文语音对话"
echo "=========================================="
echo ""

# 检查 STT 服务
echo "检查 STT 服务 (Whisper.cpp)..."
if curl -s http://127.0.0.1:2022/ > /dev/null 2>&1; then
    echo "✓ STT 服务运行中"
else
    echo "✗ STT 服务未运行"
    echo "  请确保 Whisper.cpp 服务在端口 2022 运行"
    exit 1
fi

# 检查/启动 TTS 服务
echo ""
echo "检查 TTS 服务 (Qwen3-TTS)..."
if curl -s http://127.0.0.1:8888/health > /dev/null 2>&1; then
    echo "✓ TTS 服务运行中"
else
    echo "启动 Qwen3-TTS 服务..."
    cd ~/qwen3-tts
    source venv/bin/activate
    nohup python qwen_tts_server.py > qwen_tts_server.log 2>&1 &
    echo "等待服务启动..."
    sleep 15
    if curl -s http://127.0.0.1:8888/health > /dev/null 2>&1; then
        echo "✓ TTS 服务启动成功"
    else
        echo "✗ TTS 服务启动失败，请检查日志:"
        echo "  tail -f ~/qwen3-tts/qwen_tts_server.log"
        exit 1
    fi
fi

echo ""
echo "启动实时对话..."
echo "提示: 说 '再见' 可以退出"
echo ""

cd ~/qwen3-tts
source venv/bin/activate
python voice_chat.py
