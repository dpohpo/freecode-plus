#!/usr/bin/env python3
"""
youtube2video - YouTube视频下载工具
========================================
将YouTube视频下载到本地

使用方法:
    python3 youtube2video.py "<视频URL>"
    python3 youtube2video.py "https://www.youtube.com/watch?v=xxx"
    python3 youtube2video.py "https://youtu.be/xxx"
    python3 youtube2video.py "dQw4w9WgXcQ"  # 简写，11位视频ID

依赖安装:
    pip install yt-dlp

作者: Claude @ youtube2video skill
版本: 1.0.0
"""

import os
import re
import sys
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# 默认输出目录
DEFAULT_OUTPUT_DIR = Path.home() / "Desktop" / "video"

# ============================================================
# Step 1: URL解析
# ============================================================

def extract_youtube_id(url: str) -> str:
    """
    从URL中提取YouTube视频ID

    支持格式:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://youtube.com/shorts/VIDEO_ID
    - https://www.youtube.com/live/VIDEO_ID
    - VIDEO_ID (11位简写)
    """
    # 支持的URL模式
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/|youtube\.com/live/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError(f"无法提取YouTube视频ID: {url}")


# ============================================================
# Step 2: 文件名处理
# ============================================================

def sanitize_filename(name: str) -> str:
    """
    清理文件名，移除非法字符
    """
    # 移除或替换非法字符
    illegal_chars = r'[<>:"/\\|?*\x00-\x1f]'
    name = re.sub(illegal_chars, '_', name)
    # 移除首尾空格和点
    name = name.strip(' .')
    # 限制长度
    if len(name) > 200:
        name = name[:200]
    return name or 'untitled'


# ============================================================
# Step 3: 视频下载
# ============================================================

def get_video_info(video_id: str) -> dict:
    """
    获取视频信息
    """
    url = f"https://www.youtube.com/watch?v={video_id}"

    cmd = [
        'yt-dlp',
        '--print', '%(title)s\n%(duration_string)s\n%(resolution)s\n%(uploader)s',
        '--no-playlist',
        url
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            return {
                'title': lines[0] if len(lines) > 0 else video_id,
                'duration': lines[1] if len(lines) > 1 else 'Unknown',
                'resolution': lines[2] if len(lines) > 2 else 'Unknown',
                'uploader': lines[3] if len(lines) > 3 else 'Unknown'
            }
    except Exception as e:
        logger.warning(f"获取视频信息失败: {e}")

    return {'title': video_id, 'duration': 'Unknown', 'resolution': 'Unknown', 'uploader': 'Unknown'}


def download_video(video_id: str, output_dir: Path, quality: str = "best") -> Tuple[Path, str]:
    """
    使用yt-dlp下载YouTube视频
    返回: (视频路径, 视频标题)
    """
    url = f"https://www.youtube.com/watch?v={video_id}"

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"[yt-dlp] 正在获取视频信息: {video_id}")
    info = get_video_info(video_id)

    title = info.get('title', video_id)
    safe_title = sanitize_filename(title)

    logger.info(f"[yt-dlp] 视频标题: {title}")
    logger.info(f"[yt-dlp] 时长: {info.get('duration', 'Unknown')}")
    logger.info(f"[yt-dlp] 分辨率: {info.get('resolution', 'Unknown')}")
    logger.info(f"[yt-dlp] 上传者: {info.get('uploader', 'Unknown')}")

    # 设置输出路径模板
    output_template = str(output_dir / f"{safe_title}.%(ext)s")

    # 构建下载命令
    cmd = [
        'yt-dlp',
        '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # 优先MP4格式
        '--merge-output-format', 'mp4',  # 合并为MP4
        '-o', output_template,
        '--no-playlist',
        '--no-warnings',
        '--progress',
        url
    ]

    logger.info(f"[yt-dlp] 正在下载视频...")

    try:
        # 使用实时输出
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in process.stdout:
            print(line, end='')

        process.wait()

        if process.returncode == 0:
            # 查找下载的文件
            for ext in ['.mp4', '.webm', '.mkv']:
                video_path = output_dir / f"{safe_title}{ext}"
                if video_path.exists():
                    logger.info(f"[yt-dlp] 视频下载完成: {video_path}")
                    return video_path, safe_title

            # 如果找不到预期的文件，尝试查找任何以safe_title开头的视频文件
            for f in output_dir.iterdir():
                if f.stem.startswith(safe_title[:50]) and f.suffix in ['.mp4', '.webm', '.mkv', '.avi']:
                    logger.info(f"[yt-dlp] 视频下载完成: {f}")
                    return f, safe_title

            raise RuntimeError("下载完成但找不到视频文件")
        else:
            raise RuntimeError(f"下载失败，返回码: {process.returncode}")

    except FileNotFoundError:
        raise RuntimeError("yt-dlp 未安装，请运行: pip install yt-dlp")
    except Exception as e:
        raise RuntimeError(f"下载失败: {e}")


# ============================================================
# 主流程
# ============================================================

def main(video_url: str, output_dir: Optional[Path] = None, quality: str = "best"):
    """
    主入口函数
    """
    print("=" * 60)
    print("  youtube2video - YouTube视频下载工具")
    print("=" * 60)

    # 1. 解析URL
    print("\n[Step 1] 解析URL...")
    video_id = extract_youtube_id(video_url)
    print(f"  视频ID: {video_id}")

    # 设置输出目录
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    # 2. 下载视频
    print("\n[Step 2] 下载视频...")
    video_path, video_title = download_video(video_id, output_dir, quality)

    # 完成
    print("\n" + "=" * 60)
    print("  下载完成!")
    print("=" * 60)
    print(f"\n  输出文件:")
    print(f"    {video_path}")
    print()

    return video_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python3 youtube2video.py <视频URL>")
        print("示例:")
        print("  python3 youtube2video.py https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        print("  python3 youtube2video.py https://youtu.be/dQw4w9WgXcQ")
        print("  python3 youtube2video.py dQw4w9WgXcQ")
        sys.exit(1)

    video_url = sys.argv[1]

    try:
        main(video_url)
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"处理失败: {e}")
        sys.exit(1)
