# Doubao Voice Team - 闪电说的 × 豆包集成

## 任务目标
将闪电说的 (Shandianshuo) 的语音对话接入 Doubao Voice Daemon (`Developer/doubao-voice/doubao_voice.py`)，实现：
1. Shandianshuo 语音 → Doubao Voice ASR → LLM → TTS 全链路
2. 利用 Doubao Voice 已有的优化（SileroVAD、回声消除、语音指纹等）
3. 替换 Shandianshuo 的外部 LLM 调用为本地 Doubao Voice pipeline

## 团队角色分工

### Agent 1: `arch` - 架构师
- 负责整体方案设计
- 定义 Shandianshuo ↔ Doubao Voice 的接口协议
- 设计 IPC 机制（Unix socket / HTTP / FIFO）
- 评估各方案的优缺点，输出架构决策文档

### Agent 2: `api` - API 工程师
- 负责 Doubao Voice HTTP API 封装（如需要）
- 设计 Shandianshuo 插件接口
- 编写 `doubao_plugin.py` Shandianshuo 插件代码

### Agent 3: `vad` - VAD/音频工程师
- 负责音频管道优化
- 对接 SileroVAD 与 Shandianshuo 的音频捕获
- 验证 ASR 流式输入质量

### Agent 4: `tts` - TTS/播放工程师
- 负责 TTS 合成与音频播放
- 对接 volcengine TTS 与 Shandianshuo 音频输出
- 实现回声消除（麦克风静音策略）

### Agent 5: `test` - 测试工程师
- 负责端到端测试用例设计
- 验证 ASR→LLM→TTS 全链路
- 测试延迟、可靠性、错误恢复

## 技术约束
- 优先复用 `Developer/doubao-voice/doubao_voice.py` 已有代码
- Shandianshuo 插件用 Python 编写
- IPC 优先 Unix domain socket，避免网络开销
- 保持 闪电说的 原有 UX

## 通信
通过 hcom team 消息传递进展：
- arch 输出架构方案后 → 发给 api/vad/tts/test
- 各 agent 完成模块后 → 报告给 arch
- test 验证通过 → arch 确认最终交付
