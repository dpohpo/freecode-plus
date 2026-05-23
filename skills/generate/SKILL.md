# Chinese Realtime Voice Chat Skill

实时中文语音对话技能 - 本地部署版

## 概述

此技能启用实时中文双向语音对话，完全本地运行，无需云端 API。

## 技术架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   麦克风     │ ──▶ │  STT (中文)  │ ──▶ │   Claude    │
│             │     │ Whisper.cpp │     │   (LLM)     │
└─────────────┘     └─────────────┘     └─────────────┘
                                             │
                                             ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   扬声器    │ ◀── │ TTS (中文)  │ ◀── │   回复文本   │
│             │     │ Qwen3-TTS   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

## 服务配置 Schema

### STT (语音转文字)

```yaml
stt:
  name: Whisper.cpp Server
  port: 2022
  endpoint: http://127.0.0.1:2022/v1/audio/transcriptions
  model: base
  language: zh
  response_format: json
  latency: ~150ms (with Core ML)
  features:
    - 中文语音识别
    - 流式处理
    - Core ML 加速
```

### TTS (文字转语音)

```yaml
tts:
  name: Qwen3-TTS 0.6B CustomVoice
  port: 8888
  endpoint: http://127.0.0.1:8888/v1/audio/speech
  model: tts-1
  voices:
    - vivian    # 明亮年轻女声 (中文)
    - serena    # 温柔女声 (中文)
    - uncle_fu  # 沉稳男声 (中文)
    - dylan     # 北京男声 (北京话)
    - eric      # 成都男声 (四川话)
    - ryan      # 动感男声 (英文)
    - aiden     # 阳光男声 (英文)
  default_voice: vivian
  sample_rate: 24000
  latency: ~3-5s (M4 Mac)
```

## 环境配置

### 文件位置

```yaml
paths:
  qwen3_tts_root: ~/qwen3-tts
  models_dir: ~/qwen3-tts/models
  server_script: ~/qwen3-tts/qwen_tts_server.py
  chat_script: ~/qwen3-tts/voice_chat.py
  voicemode_config: ~/.voicemode/voicemode.env
```

### 环境变量 (~/.voicemode/voicemode.env)

```bash
# STT 配置
STT_ENDPOINTS=http://127.0.0.1:2022/v1
VOICEMODE_WHISPER_LANGUAGE=zh
VOICEMODE_WHISPER_MODEL=base

# TTS 配置
TTS_ENDPOINTS=http://127.0.0.1:8888/v1
TTS_MODEL=tts-1
TTS_VOICE=vivian

# 优先本地服务
PREFER_LOCAL=true
```

## 启动命令

### 启动 Qwen3-TTS 服务器

```bash
cd ~/qwen3-tts && source venv/bin/activate
python qwen_tts_server.py
# 服务运行在 http://0.0.0.0:8888
```

### 启动实时对话

```bash
cd ~/qwen3-tts && source venv/bin/activate
python voice_chat.py
```

### 后台运行

```bash
# 启动 TTS 服务 (后台)
cd ~/qwen3-tts && source venv/bin/activate
nohup python qwen_tts_server.py > qwen_tts_server.log 2>&1 &

# 检查服务状态
curl http://127.0.0.1:8888/health
```

## API 调用示例

### STT 调用 (cURL)

```bash
curl -X POST http://127.0.0.1:2022/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "model=base" \
  -F "language=zh" \
  -F "response_format=json"
```

### TTS 调用 (cURL)

```bash
curl -X POST http://127.0.0.1:8888/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "你好，这是测试语音", "voice": "vivian"}' \
  -o output.wav
```

### Python 调用

```python
import requests

# STT
def stt(audio_path):
    with open(audio_path, 'rb') as f:
        response = requests.post(
            "http://127.0.0.1:2022/v1/audio/transcriptions",
            files={'file': f},
            data={'model': 'base', 'language': 'zh'}
        )
    return response.json().get('text', '')

# TTS
def tts(text, voice='vivian'):
    response = requests.post(
        "http://127.0.0.1:8888/v1/audio/speech",
        json={"input": text, "voice": voice}
    )
    return response.content  # WAV audio bytes
```

## 服务健康检查

```bash
# 检查 STT
curl http://127.0.0.1:2022/

# 检查 TTS
curl http://127.0.0.1:8888/health
```

## 故障排除

### STT 无法识别中文

确保请求中包含 `language=zh` 参数：
```bash
-F "language=zh"
```

### TTS 服务未启动

```bash
# 检查进程
ps aux | grep qwen_tts_server

# 查看日志
tail -f ~/qwen3-tts/qwen_tts_server.log

# 重启服务
pkill -f qwen_tts_server
cd ~/qwen3-tts && source venv/bin/activate
python qwen_tts_server.py
```

### M4 Mac 性能优化

- 使用 0.6B 模型而非 1.7B
- 确保使用 MPS 后端
- 关闭其他 GPU 密集应用

## 依赖

```yaml
dependencies:
  python: ">=3.10"
  packages:
    - torch
    - transformers
    - accelerate
    - qwen-tts
    - pyaudio
    - requests
    - soundfile
    - fastapi
    - uvicorn
  system:
    - portaudio (brew install portaudio)
```

## 版本信息

```yaml
version: 1.0.0
created: 2026-02-12
author: Claude
components:
  stt: Whisper.cpp (base model, Core ML enabled)
  tts: Qwen3-TTS-12Hz-0.6B-CustomVoice
  platform: macOS (Apple Silicon M4)
```
