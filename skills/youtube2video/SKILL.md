---
name: youtube2video
description: YouTube视频下载工具 — 下载任意YouTube视频到本地，支持多种分辨率和格式
user-invocable: "true"
---

> **反幻觉铁律（全局生效 | 详见 ~/.claude/CLAUDE.md）**
> 1.诚信：不知道就说不知道，不编造 2.实事求是：证明之前保持怀疑，自证无效 3.98%门槛：置信度<98%禁止确定性语气 4.失效条件必标：技术声明必须标注何时不生效 5.代码交付：所有外部API/命令/配置必须验证真实性，未验证标注 UNVERIFIED | 豁免：仅用户主动声明时可跳过

你现在进入 **YOUTUBE2VIDEO 模式** — YouTube视频下载工具。

## 功能概述

| 功能 | 说明 |
|------|------|
| 视频下载 | 从YouTube下载视频，自动选择最佳质量 |
| 格式支持 | MP4/WebM/MKV 等主流格式 |
| 分辨率 | 支持 4K/1080p/720p/480p 等多种分辨率 |
| 元数据 | 保留视频标题、描述、缩略图等信息 |

## 使用方法

```
/youtube2video <视频URL>
/youtube2video https://www.youtube.com/watch?v=xxx
/youtube2video https://youtu.be/xxx
/youtube2video https://youtube.com/shorts/xxx
/youtube2video dQw4w9WgXcQ  # 简写，11位视频ID
```

## 输出位置

```
~/Desktop/video/{视频标题}.mp4
```

## 执行流程

```
┌─────────────────────────────────────────────────────────┐
│ 1. URL解析                                              │
│    提取YouTube视频ID (11位) → 验证URL有效性              │
├─────────────────────────────────────────────────────────┤
│ 2. 获取视频信息                                         │
│    yt-dlp → 获取标题/分辨率/格式信息                     │
├─────────────────────────────────────────────────────────┤
│ 3. 下载视频                                             │
│    最佳质量 → 合并视频+音频 → 保存到目标目录             │
└─────────────────────────────────────────────────────────┘
```

## 技术选型

| 模块 | 方案 | 状态 |
|------|------|------|
| 视频下载 | yt-dlp | VERIFIED (v2026.2.4) |
| 格式转换 | ffmpeg (yt-dlp内置) | VERIFIED |

## 依赖安装

```bash
pip install yt-dlp
# 可选：安装ffmpeg以获得更好的格式支持
brew install ffmpeg  # macOS
```

## 已知限制

| 限制 | 说明 |
|------|------|
| 区域限制 | 部分视频有地区限制，可能无法下载 |
| 会员内容 | YouTube Premium专享内容无法下载 |
| 直播流 | 需要等待直播结束才能下载 |
| 私享视频 | 无法访问私享/未列出视频 |
| 版权视频 | 部分版权视频可能无法下载 |

## 脚本位置

```
~/.claude/skills/youtube2video/scripts/youtube2video.py
```

## 调用方式

```bash
python3 ~/.claude/skills/youtube2video/scripts/youtube2video.py "<视频URL>"
```

---

$ARGUMENTS
