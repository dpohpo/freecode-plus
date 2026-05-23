---
name: videodownload
description: Universal video downloader combining Firecrawl for video URL extraction from any webpage and yt-dlp for downloading 1000+ sites. Use when user wants to download videos from webpages, social media, or streaming platforms. Triggered by "/videodownload" followed by a URL or phrases like "download video from". Supports YouTube, Vimeo, Twitter/X, Instagram, TikTok, Facebook, and direct MP4 links.
user-invocable: "true"
---

# Video Download Skill

Combines **Firecrawl** (extracts video URLs from webpages) and **yt-dlp** (downloads videos) for universal video downloading.

## Quick Start

```bash
/videodownload https://example.com/page-with-video
```

The skill will:
1. Use Firecrawl to scan the page for video URLs
2. Extract all video sources (MP4, embedded players, iframes, etc.)
3. Use yt-dlp to download found videos

## Workflow

```
Input URL
    ↓
Firecrawl Scrape (extract HTML, render JS)
    ↓
Parse Video URLs (video tags, iframe tags, anchor links with mp4)
    ↓
Filter & Deduplicate URLs
    ↓
yt-dlp Download (best quality, save as MP4)
    ↓
Output: ~/Downloads/videos/
```

## Usage Examples

### Basic Download

```bash
/videodownload https://www.youtube.com/watch?v=xxx
/videodownload https://vimeo.com/123456
/videodownload https://twitter.com/user/status/xxx
/videodownload https://some-blog.com/post-with-embedded-video
```

### With Options

```bash
# Specify output directory
/videodownload https://example.com --output ~/Downloads/

# Download best quality (default)
/videodownload https://example.com --quality best

# Download worst quality (faster)
/videodownload https://example.com --quality worst

# Download audio only
/videodownload https://example.com --audio
```

## Script

The core script `scripts/download_video.py` handles:
- Firecrawl API integration for webpage scraping
- Video URL extraction (regex + HTML parsing)
- yt-dlp download orchestration

Run directly:
```bash
python3 ~/.claude/skills/videodownload/scripts/download_video.py URL
```

## Dependencies

- `firecrawl-py` - Firecrawl Python SDK
- `yt-dlp` - Video downloader (1000+ sites)
- Firecrawl API key (set as `FIRECRAWL_API_KEY` env var)

## Installation

```bash
# Install yt-dlp
pip install yt-dlp firecrawl-py

# Or via homebrew
brew install yt-dlp
```
