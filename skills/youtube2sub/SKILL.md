---
name: youtube2sub
description: YouTube视频转字幕工具 — 下载任意YouTube视频音频并转换为多格式字幕(SRT/VTT/TXT)
user-invocable: "true"
---

> **反幻觉铁律（全局生效 | 详见 ~/.claude/CLAUDE.md）**
> 1.诚信：不知道就说不知道，不编造 2.实事求是：证明之前保持怀疑，自证无效 3.98%门槛：置信度<98%禁止确定性语气 4.失效条件必标：技术声明必须标注何时不生效 5.代码交付：所有外部API/命令/配置必须验证真实性，未验证标注 UNVERIFIED | 豁免：仅用户主动声明时可跳过

你现在进入 **YOUTUBE2SUB 模式** — YouTube视频转字幕工具。

## 功能概述

| 功能 | 说明 |
|------|------|
| 视频下载 | 从YouTube下载任意视频的音频轨道 |
| 语音识别 | FunASR(中文优先) / faster-whisper(多语言) |
| 字幕输出 | 同时生成 SRT + VTT + TXT 三种格式 |
| 自动分段 | 超长视频自动分段处理 |

## 使用方法

```
/youtube2sub <视频URL>
/youtube2sub https://www.youtube.com/watch?v=xxx
/youtube2sub https://youtu.be/xxx
/youtube2sub https://youtube.com/shorts/xxx
/youtube2sub dQw4w9WgXcQ  # 简写，11位视频ID
```

## 输出位置

```
~/Desktop/字幕/{视频标题}.srt
~/Desktop/字幕/{视频标题}.vtt
~/Desktop/字幕/{视频标题}.txt
```

## 执行流程

```
┌─────────────────────────────────────────────────────────┐
│ 1. URL解析                                              │
│    提取YouTube视频ID (11位) → 验证URL有效性              │
├─────────────────────────────────────────────────────────┤
│ 2. 音频下载                                             │
│    yt-dlp → 获取视频标题 → 下载最佳音频格式              │
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

| 模块 | 方案 | 状态 |
|------|------|------|
| 视频下载 | yt-dlp | VERIFIED (v2026.2.4) |
| ASR引擎 | FunASR Paraformer / faster-whisper | VERIFIED |
| 音频处理 | pydub + ffmpeg | VERIFIED |

## 依赖安装

```bash
pip install yt-dlp funasr modelscope faster-whisper pydub langdetect
```

## 已知限制

| 限制 | 说明 |
|------|------|
| 区域限制 | 部分视频有地区限制，可能无法下载 |
| 会员内容 | YouTube Premium专享内容无法下载 |
| 直播流 | 需要等待直播结束才能下载 |
| 私享视频 | 无法访问私享/未列出视频 |
| ASR准确率 | 噪音大、方言重时下降 |
| 首次运行 | FunASR需下载模型(~1GB) |

## 脚本位置

```
~/.claude/skills/youtube2sub/scripts/youtube2sub.py
```

## 调用方式

```bash
python3 ~/.claude/skills/youtube2sub/scripts/youtube2sub.py "<视频URL>"
```

---

$ARGUMENTS
