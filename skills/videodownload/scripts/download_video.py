#!/usr/bin/env python3
"""
Video Download Script - Firecrawl + yt-dlp Combination

Extracts video URLs from webpages using Firecrawl, then downloads with yt-dlp.

Usage:
    python3 download_video.py <URL> [--output DIR] [--quality best|worst] [--audio]

Examples:
    python3 download_video.py https://www.youtube.com/watch?v=xxx
    python3 download_video.py https://example.com --output ~/Downloads/
    python3 download_video.py https://example.com --audio
"""

import os
import re
import sys
import argparse
import subprocess
from pathlib import Path
from urllib.parse import urlparse, urljoin

try:
    from firecrawl import FirecrawlApp
except ImportError:
    print("Installing firecrawl-py...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "firecrawl-py", "-q"])
    from firecrawl import FirecrawlApp


def extract_video_urls_from_html(html: str, base_url: str) -> list[str]:
    """Extract video URLs from HTML content."""
    urls = set()

    # 1. <video> tag src attributes
    video_pattern = r'<video[^>]*>\s*<source[^>]*src=["\']([^"\']+)["\']'
    urls.update(re.findall(video_pattern, html, re.IGNORECASE))

    # 2. <video> tag direct src
    video_src_pattern = r'<video[^>]*src=["\']([^"\']+)["\']'
    urls.update(re.findall(video_src_pattern, html, re.IGNORECASE))

    # 3. <iframe> embed URLs (YouTube, Vimeo, etc.)
    iframe_pattern = r'<iframe[^>]*src=["\']([^"\']+)["\']'
    iframe_urls = re.findall(iframe_pattern, html, re.IGNORECASE)

    # 4. Direct .mp4, .webm, .mov, .avi links
    video_extensions = r'(https?://[^\s"\'<>]+\.(?:mp4|webm|mov|avi|mkv|flv|m4v)(?:\?[^\s"\'<>]*)?)'
    urls.update(re.findall(video_extensions, html, re.IGNORECASE))

    # Filter and clean URLs
    clean_urls = []
    for url in list(urls) + iframe_urls:
        url = url.strip()
        if not url or url.startswith('data:'):
            continue

        # Skip ads/tracking
        if any(x in url.lower() for x in ['ad.doubleclick', 'google_ads', 'analytics']):
            continue

        # Convert relative URLs to absolute
        if url.startswith('//'):
            url = 'https:' + url
        elif url.startswith('/'):
            url = urljoin(base_url, url)

        clean_urls.append(url)

    return clean_urls


def scrape_with_firecrawl(url: str, api_key: str = None) -> dict:
    """Scrape webpage using Firecrawl."""
    if api_key:
        app = FirecrawlApp(api_key=api_key)
    else:
        app = FirecrawlApp()

    result = app.scrape_url(
        url,
        params={'formats': ['markdown', 'html', 'extract']}
    )
    return result


def extract_urls_ytdlp_fallback(url: str) -> list[str]:
    """
    Fallback: Use yt-dlp --list-formats to extract URLs.
    This works for many sites without needing Firecrawl.
    """
    try:
        result = subprocess.run(
            ['yt-dlp', '--list-formats', '--skip-download', url],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            # yt-dlp recognizes this URL, return it
            return [url]
    except Exception:
        pass
    return []


def download_video_with_ytdlp(url: str, output_dir: str = None, quality: str = "best", audio_only: bool = False) -> bool:
    """Download video using yt-dlp."""
    output_dir = output_dir or os.path.expanduser("~/Downloads/videos")
    os.makedirs(output_dir, exist_ok=True)

    cmd = ['yt-dlp', '-o', f'{output_dir}/%(title)s.%(ext)s']

    # Quality options
    if audio_only:
        cmd.extend(['-x', '--audio-format', 'mp3'])
        cmd.extend(['--audio-quality', '0'])
    elif quality == "best":
        cmd.extend(['-f', 'bestvideo+bestaudio/best'])
    elif quality == "worst":
        cmd.extend(['-f', 'worst'])
    else:
        cmd.extend(['-f', quality])

    # Other options
    cmd.extend(['--no-playlist', '--concurrent-fragments', '4'])

    cmd.append(url)

    print(f"Downloading: {url}")
    print(f"Output: {output_dir}")

    result = subprocess.run(cmd)
    return result.returncode == 0


def is_video_platform(url: str) -> bool:
    """Check if URL is a known video platform."""
    domains = [
        'youtube.com', 'youtu.be',
        'vimeo.com',
        'dailymotion.com',
        'twitch.tv',
        'twitter.com', 'x.com',
        'tiktok.com',
        'instagram.com',
        'facebook.com',
        'facebook.com/watch',
        'streamable.com',
        'reddit.com',
    ]
    parsed = urlparse(url)
    return any(domain in parsed.netloc.lower() for domain in domains)


def main():
    parser = argparse.ArgumentParser(description='Download videos from webpages')
    parser.add_argument('url', help='URL of the page with video')
    parser.add_argument('--output', '-o', help='Output directory')
    parser.add_argument('--quality', '-q', choices=['best', 'worst'], default='best', help='Video quality')
    parser.add_argument('--audio', '-a', action='store_true', help='Download audio only')
    parser.add_argument('--firecrawl-key', help='Firecrawl API key (or set FIRECRAWL_API_KEY env var)')

    args = parser.parse_args()

    url = args.url
    output_dir = args.output
    quality = args.quality
    audio_only = args.audio

    # Get Firecrawl API key
    api_key = args.firecrawl_key or os.environ.get('FIRECRAWL_API_KEY')

    video_urls = []

    # Strategy 1: Direct yt-dlp for known platforms (faster)
    if is_video_platform(url):
        print(f"Detected known video platform, using yt-dlp directly...")
        video_urls = [url]

    # Strategy 2: Firecrawl scraping for general webpages
    elif api_key:
        print(f"Scraping webpage with Firecrawl...")
        try:
            scrape_result = scrape_with_firecrawl(url, api_key)
            html = scrape_result.get('html', '')

            if html:
                video_urls = extract_video_urls_from_html(html, url)
                print(f"Found {len(video_urls)} video URLs")
        except Exception as e:
            print(f"Firecrawl error: {e}")
            print("Falling back to yt-dlp direct...")
            video_urls = extract_urls_ytdlp_fallback(url)

    # Strategy 3: Fallback to yt-dlp list-formats
    else:
        print("No Firecrawl API key provided, trying yt-dlp direct...")
        video_urls = extract_urls_ytdlp_fallback(url)

    # Deduplicate while preserving order
    seen = set()
    unique_urls = []
    for u in video_urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)

    print(f"Total unique URLs to download: {len(unique_urls)}")

    # Download each URL
    success_count = 0
    for i, video_url in enumerate(unique_urls, 1):
        print(f"\n[{i}/{len(unique_urls)}] Processing: {video_url[:80]}...")
        if download_video_with_ytdlp(video_url, output_dir, quality, audio_only):
            success_count += 1
        else:
            print(f"Failed to download: {video_url[:80]}")

    print(f"\n✅ Successfully downloaded {success_count}/{len(unique_urls)} videos")


if __name__ == "__main__":
    main()
