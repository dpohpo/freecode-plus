---
name: voice
description: 实时中文语音双向对话 — 按住 F 键说话，本地 Whisper.cpp + Qwen3-TTS
user-invocable: "true"
---

> **反幻觉铁律（全局生效 | 详见 ~/.claude/CLAUDE.md）**
> 1.诚信：不知道就说不知道，不编造 2.实事求是：证明之前保持怀疑，自证无效 3.98%门槛：置信度<98%禁止确定性语气 4.失效条件必标：技术声明必须标注何时不生效 5.代码交付：所有外部API/命令/配置必须验证真实性，未验证标注 UNVERIFIED | 豁免：仅用户主动声明时可跳过

> **编码铁律+自审清单（涉及代码时生效 | 详见 /coding）**
> 铁律：先扫描后编码 | 双轨验证(网络+执行)不可省 | 溯源到一手(官方文档/repo) | 98%才用确定语气 | 自建功能100%三轨验证 | 构建链每层VERIFIED | 失效条件必标 | 不存在要三轮证明
> 自审：所有外部声明已识别 | 所有依赖>=98%VERIFIED | 代码无未标注外部引用 | 技术声明含生效/失效/验证三元组 | 未使用should work

> **自对齐协议（全局生效 | 病毒式传染 — 所有模式/技能必须携带此段）**
> 每次执行前，用1行自检：`[ALIGN] 模式:<当前> | 任务:<描述> | 匹配:是/否 | 置信度:X%`
> 匹配=否 或 置信度<80% → 暂停，向用户建议切换模式。无模式时 → 评估是否需要模式。

你现在进入 **VOICE 模式** — 实时中文语音双向对话系统。

核心功能：**按住 F 键开始讲话，松开 F 键讲话完毕，实现与 Claude Code CLI 的实时中文语音对话。**

---

## 系统架构 Schema

```yaml
voice_system:
  type: realtime_bidirectional
  language: zh-CN
  platform: macOS (Apple Silicon)

  components:
    stt:
      name: Whisper.cpp Server
      port: 2022
      endpoint: http://127.0.0.1:2022/v1/audio/transcriptions
      model: base
      language: zh
      latency_ms: ~150
      features: [chinese_recognition, core_ml_acceleration]

    tts:
      name: Qwen3-TTS 0.6B CustomVoice
      port: 8888
      endpoint: http://127.0.0.1:8888/v1/audio/speech
      model: tts-1
      default_voice: vivian
      sample_rate: 24000
      latency_ms: ~3000

    interaction:
      mode: push_to_talk
      key: F
      action: hold_to_record
      record_duration_s: 5
```

---

## 语音角色 Schema

```yaml
voices:
  chinese:
    vivian:
      description: 明亮、略带锐利的年轻女声
      gender: female
      age: young
      native: true

    serena:
      description: 温暖、温柔的年轻女声
      gender: female
      age: young
      native: true

    uncle_fu:
      description: 沉稳、醇厚的成熟男声
      gender: male
      age: mature
      native: true

    dylan:
      description: 清朗自然的北京年轻男声
      gender: male
      age: young
      dialect: beijing
      native: true

    eric:
      description: 活泼明亮的成都男声
      gender: male
      age: young
      dialect: sichuan
      native: true

  english:
    ryan:
      description: 节奏感强的动感男声
      gender: male
      native: true

    aiden:
      description: 阳光、中音清澈的美国男声
      gender: male
      native: true

  japanese:
    ono_anna:
      description: 轻盈灵动的俏皮日语女声
      gender: female
      native: true

  korean:
    sohee:
      description: 情感丰富的温暖韩语女声
      gender: female
      native: true
```

---

## 环境配置 Schema

```yaml
paths:
  qwen3_tts_root: ~/qwen3-tts
  models_dir: ~/qwen3-tts/models
  server_script: ~/qwen3-tts/qwen_tts_server.py
  chat_script: ~/qwen3-tts/voice_chat.py
  voicemode_config: ~/.voicemode/voicemode.env
  skill_startup: ~/.claude/skills/generate/start-voice-chat.sh

env_vars:
  STT_ENDPOINTS: http://127.0.0.1:2022/v1
  TTS_ENDPOINTS: http://127.0.0.1:8888/v1
  VOICEMODE_WHISPER_LANGUAGE: zh
  VOICEMODE_WHISPER_MODEL: base
  TTS_MODEL: tts-1
  TTS_VOICE: vivian
  PREFER_LOCAL: "true"
```

---

## 交互模式 Schema

```yaml
interaction_modes:
  push_to_talk:
    description: 按住 F 键录音，松开发送
    trigger: key_hold
    key: F
    workflow:
      - action: key_press
        event: 开始录音
      - action: speaking
        event: 用户讲话
      - action: key_release
        event: 停止录音，发送 STT
      - action: stt_process
        event: Whisper.cpp 识别
      - action: llm_process
        event: Claude 处理
      - action: tts_process
        event: Qwen3-TTS 合成
      - action: audio_play
        event: 播放回复

  auto_detect:
    description: 自动检测语音端点
    trigger: vad
    vad_threshold: 0.5
    silence_duration_ms: 500
```

---

## API 调用 Schema

### STT 调用

```yaml
stt_request:
  method: POST
  url: http://127.0.0.1:2022/v1/audio/transcriptions
  headers:
    Content-Type: multipart/form-data
  body:
    file: audio.wav
    model: base
    language: zh
    response_format: json

stt_response:
  type: object
  properties:
    text:
      type: string
      description: 识别的中文文本
```

### TTS 调用

```yaml
tts_request:
  method: POST
  url: http://127.0.0.1:8888/v1/audio/speech
  headers:
    Content-Type: application/json
  body:
    input: 要合成的文本
    voice: vivian
    response_format: wav

tts_response:
  type: binary
  format: audio/wav
  sample_rate: 24000
  channels: 1
```

---

## 使用方式

### 1. 启动服务

```bash
# 一键启动
~/.claude/skills/generate/start-voice-chat.sh

# 或手动启动
cd ~/qwen3-tts && source venv/bin/activate
python voice_chat.py
```

### 2. 检查服务状态

```bash
# STT 状态
curl http://127.0.0.1:2022/

# TTS 状态
curl http://127.0.0.1:8888/health
```

### 3. Python 快速调用

```python
import requests

def stt(audio_path: str) -> str:
    """语音转文字"""
    with open(audio_path, 'rb') as f:
        r = requests.post(
            "http://127.0.0.1:2022/v1/audio/transcriptions",
            files={'file': f},
            data={'model': 'base', 'language': 'zh'}
        )
    return r.json().get('text', '')

def tts(text: str, voice: str = 'vivian') -> bytes:
    """文字转语音"""
    r = requests.post(
        "http://127.0.0.1:8888/v1/audio/speech",
        json={"input": text, "voice": voice}
    )
    return r.content
```

---

## 服务状态验证（吸收自 /bht）

```
🔍 服务健康检查
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

│ 服务        │ 端口  │ 检查命令                          │ 预期响应          │
│────────────│──────│──────────────────────────────────│──────────────────│
│ STT        │ 2022  │ curl http://127.0.0.1:2022/      │ Whisper.cpp 页面  │
│ TTS        │ 8888  │ curl http://127.0.0.1:8888/health│ {"status":"ok"}  │

六级裁决：
  ✅ VERIFIED — 服务正常响应
  ⚠️ UNVERIFIED — 服务无响应，需启动
  ❌ FAILED — 服务异常，需排查
```

---

## 故障排除 Schema

```yaml
troubleshooting:
  stt_chinese_issue:
    symptom: STT 返回英文或乱码
    cause: 未指定 language=zh 参数
    fix: 确保请求包含 -F "language=zh"

  tts_not_running:
    symptom: TTS 请求超时
    cause: Qwen3-TTS 服务未启动
    fix: |
      cd ~/qwen3-tts && source venv/bin/activate
      python qwen_tts_server.py

  slow_on_m4:
    symptom: TTS 生成速度慢
    cause: 使用 1.7B 模型或内存不足
    fix: 使用 0.6B 模型，关闭其他 GPU 应用

  port_conflict:
    symptom: 端口被占用
    cause: 其他服务占用 2022 或 8888
    fix: |
      lsof -i :2022  # 查看占用进程
      kill <PID>     # 终止进程
```

---

## 依赖 Schema

```yaml
dependencies:
  system:
    - name: portaudio
      install: brew install portaudio
    - name: sox
      install: brew install sox

  python:
    - torch>=2.0
    - transformers>=4.50
    - qwen-tts>=0.1
    - pyaudio
    - requests
    - soundfile
    - fastapi
    - uvicorn

  models:
    - name: Qwen3-TTS-Tokenizer-12Hz
      path: ~/qwen3-tts/models/Qwen3-TTS-Tokenizer-12Hz
    - name: Qwen3-TTS-12Hz-0.6B-CustomVoice
      path: ~/qwen3-tts/models/Qwen3-TTS-12Hz-0.6B-CustomVoice
```

---

## 铁律

1. **本地优先** — 优先使用本地服务，避免云端依赖
2. **中文优化** — STT 必须指定 `language=zh`
3. **按键交互** — 按住 F 录音，松开发送
4. **服务检查** — 使用前验证服务状态
5. **溯源验证** — 服务配置必须验证可用性
6. **延迟预期** — TTS 生成约 3-5 秒，需耐心等待

---

## 版本信息

```yaml
version: 2.0.0
created: 2026-02-12
enhanced_from:
  - /bht (验证机制)
  - 本地语音配置实践
components:
  stt: Whisper.cpp (base, Core ML, 中文)
  tts: Qwen3-TTS-12Hz-0.6B-CustomVoice
  platform: macOS (Apple Silicon M4)
```

---

## 最终步：知识沉淀 + 蒸馏

语音配置变更或重要发现后，判断是否存入知识库：

**存入条件**：新语音服务配置 | 故障解决方案有复用价值 | 用户要求

**执行流程：**
1. 询问用户是否存入知识库
2. 若是 → 写入 `~/.claude/knowledge/YYYY-MM-DD-voice-<关键词>.md`
3. 执行五层蒸馏
4. 蒸馏版写入 `.distilled.md`

---

现在以 VOICE 模式处理：

$ARGUMENTS
