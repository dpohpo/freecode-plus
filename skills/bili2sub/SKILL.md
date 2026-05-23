---
name: bili2sub
description: Bilibili视频转字幕工具 — 下载任意B站视频音频并转换为多格式字幕(SRT/VTT/TXT)
user-invocable: "true"
---

> **反幻觉铁律（全局生效 | 详见 ~/.claude/CLAUDE.md）**
> 1.诚信：不知道就说不知道，不编造 2.实事求是：证明之前保持怀疑，自证无效 3.98%门槛：置信度<98%禁止确定性语气 4.失效条件必标：技术声明必须标注何时不生效 5.代码交付：所有外部API/命令/配置必须验证真实性，未验证标注 UNVERIFIED | 豁免：仅用户主动声明时可跳过

你现在进入 **BILI2SUB 模式** — Bilibili视频转字幕工具。

## 功能概述

| 功能 | 说明 |
|------|------|
| 视频下载 | 从Bilibili下载任意视频的音频轨道 |
| 语音识别 | FunASR(中文优先) / faster-whisper(多语言) |
| 字幕输出 | 同时生成 SRT + VTT + TXT 三种格式 |
| 自动分段 | 超长视频自动分段处理 |

## 使用方法

```
/bili2sub <视频URL>
/bili2sub https://www.bilibili.com/video/BVxxx
/bili2sub BV1xx  # 简写，自动补全URL
```

## 输出位置

```
~/Desktop/字幕/{BV号}.srt
~/Desktop/字幕/{BV号}.vtt
~/Desktop/字幕/{BV号}.txt
```

## 执行流程

```
┌─────────────────────────────────────────────────────────┐
│ 1. URL解析                                              │
│    提取BV号/AV号 → 验证URL有效性                         │
├─────────────────────────────────────────────────────────┤
│ 2. 音频下载                                             │
│    bilibili-api-python → 失败则fallback到yt-dlp         │
├─────────────────────────────────────────────────────────┤
│ 3. ASR识别                                              │
│    中文 → FunASR Paraformer                             │
│    其他语言 → faster-whisper large-v3                   │
│    超长视频 → 自动分段处理                               │
├─────────────────────────────────────────────────────────┤
│ 4. 字幕生成                                             │
│    添加时间戳 → 句子分段 → 生成SRT/VTT/TXT              │
└─────────────────────────────────────────────────────────┘
```

## 技术选型

| 模块 | 首选 | 备选 | 状态 |
|------|------|------|------|
| 视频下载 | bilibili-api-python | yt-dlp | VERIFIED |
| ASR引擎 | FunASR Paraformer | faster-whisper | VERIFIED |
| 音频处理 | pydub + ffmpeg | - | VERIFIED |

## 依赖安装

```bash
pip install bilibili-api-python funasr modelscope faster-whisper pydub
```

## 已知限制

| 限制 | 说明 |
|------|------|
| 会员内容 | 无法下载会员专享视频 |
| 登录态 | 部分视频需要Cookie |
| 区域限制 | 港澳台番剧可能无法访问 |
| ASR准确率 | 噪音大、方言重时下降 |
| 首次运行 | FunASR需下载模型(~1GB) |

## 脚本位置

```
~/.claude/skills/bili2sub/scripts/bili2sub.py
```

## 调用方式

```bash
python3 ~/.claude/skills/bili2sub/scripts/bili2sub.py "<视频URL>"
```

---

$ARGUMENTS
