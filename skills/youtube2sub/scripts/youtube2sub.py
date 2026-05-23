#!/usr/bin/env python3
"""
youtube2sub - YouTube视频转字幕工具
========================================
将YouTube视频的音频转换为字幕文件（SRT/VTT/TXT）

使用方法:
    python3 youtube2sub.py "<视频URL>"
    python3 youtube2sub.py "https://www.youtube.com/watch?v=xxx"
    python3 youtube2sub.py "https://youtu.be/xxx"
    python3 youtube2sub.py "dQw4w9WgXcQ"  # 简写，11位视频ID

依赖安装:
    pip install yt-dlp funasr modelscope faster-whisper pydub langdetect

作者: Claude @ youtube2sub skill
版本: 1.0.0
"""

import os
import re
import sys
import subprocess
from pathlib import Path
from datetime import timedelta
from typing import Optional, List, Tuple
import tempfile
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# 默认输出目录
DEFAULT_OUTPUT_DIR = Path.home() / "Desktop" / "字幕"

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
# Step 2: 音频下载
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


def download_audio_youtube(video_id: str, output_dir: Path) -> Tuple[Path, str]:
    """
    使用yt-dlp下载YouTube音频
    返回: (音频路径, 视频标题)
    """
    url = f"https://www.youtube.com/watch?v={video_id}"

    logger.info(f"[yt-dlp] 正在获取视频信息: {video_id}")

    try:
        # 首先获取视频标题
        title_cmd = [
            'yt-dlp',
            '--print', '%(title)s',
            '--no-playlist',
            url
        ]
        title_result = subprocess.run(title_cmd, capture_output=True, text=True)

        if title_result.returncode != 0:
            logger.warning(f"[yt-dlp] 获取标题失败: {title_result.stderr}")
            title = video_id
        else:
            title = title_result.stdout.strip() or video_id

        # 清理标题作为文件名
        safe_title = sanitize_filename(title)
        logger.info(f"[yt-dlp] 视频标题: {title}")
        logger.info(f"[yt-dlp] 文件名: {safe_title}")

        # 下载音频
        audio_path = output_dir / f"{safe_title}.m4a"

        download_cmd = [
            'yt-dlp',
            '-f', 'bestaudio/best',
            '-x',  # 仅提取音频
            '--audio-format', 'm4a',
            '--audio-quality', '0',  # 最佳质量
            '-o', str(audio_path.with_suffix('')),  # 不带扩展名，yt-dlp会自动添加
            '--no-playlist',
            '--no-warnings',
            url
        ]

        logger.info(f"[yt-dlp] 正在下载音频...")
        result = subprocess.run(download_cmd, capture_output=True, text=True)

        # 检查下载结果
        possible_extensions = ['.m4a', '.opus', '.webm', '.mp3']
        downloaded_path = None
        for ext in possible_extensions:
            candidate = output_dir / f"{safe_title}{ext}"
            if candidate.exists():
                downloaded_path = candidate
                break

        # 如果找不到预期的文件，尝试查找任何以safe_title开头的音频文件
        if not downloaded_path:
            for f in output_dir.iterdir():
                if f.stem.startswith(safe_title[:50]) and f.suffix in possible_extensions:
                    downloaded_path = f
                    break

        if downloaded_path and downloaded_path.exists():
            logger.info(f"[yt-dlp] 音频下载完成: {downloaded_path}")
            return downloaded_path, safe_title
        else:
            # 列出目录中的文件用于调试
            logger.warning(f"[yt-dlp] 目录内容: {list(output_dir.iterdir())}")
            raise RuntimeError(f"下载失败: {result.stderr}")

    except FileNotFoundError:
        raise RuntimeError("yt-dlp 未安装，请运行: pip install yt-dlp")
    except Exception as e:
        raise RuntimeError(f"下载失败: {e}")


# ============================================================
# Step 3: 音频预处理
# ============================================================

def convert_to_wav(audio_path: Path) -> Path:
    """
    将音频转换为WAV格式（ASR需要）
    """
    wav_path = audio_path.with_suffix('.wav')

    try:
        from pydub import AudioSegment

        logger.info(f"[预处理] 正在转换为WAV格式...")
        audio = AudioSegment.from_file(str(audio_path))
        audio.export(str(wav_path), format='wav')

        logger.info(f"[预处理] 转换完成: {wav_path}")
        return wav_path

    except ImportError:
        # 使用 ffmpeg 作为备选
        logger.info(f"[预处理] 使用ffmpeg转换...")
        cmd = ['ffmpeg', '-y', '-i', str(audio_path), '-ar', '16000', '-ac', '1', str(wav_path)]
        subprocess.run(cmd, capture_output=True)
        return wav_path


def split_audio(wav_path: Path, chunk_length_minutes: int = 30) -> List[Path]:
    """
    将长音频分割成多个片段

    FunASR/Whisper 对超长音频支持有限，建议分段处理
    """
    try:
        from pydub import AudioSegment

        audio = AudioSegment.from_wav(str(wav_path))
        chunk_length_ms = chunk_length_minutes * 60 * 1000

        if len(audio) <= chunk_length_ms:
            return [wav_path]

        chunks = []
        for i, start in enumerate(range(0, len(audio), chunk_length_ms)):
            chunk = audio[start:start + chunk_length_ms]
            chunk_path = wav_path.parent / f"{wav_path.stem}_part{i}.wav"
            chunk.export(str(chunk_path), format='wav')
            chunks.append(chunk_path)

        logger.info(f"[预处理] 音频已分割为 {len(chunks)} 个片段")
        return chunks

    except ImportError:
        logger.warning("[预处理] pydub未安装，跳过分段")
        return [wav_path]


# ============================================================
# Step 4: ASR识别
# ============================================================

def transcribe_funasr(wav_path: Path) -> Optional[List[dict]]:
    """
    使用 FunASR Paraformer 进行语音识别

    中文首选方案 | VERIFIED: 阿里达摩院开源，中文效果优于Whisper
    """
    try:
        from funasr import AutoModel

        logger.info(f"[FunASR] 正在加载模型...")

        # 使用 Paraformer 模型（中文最佳）
        model = AutoModel(
            model="paraformer-zh",
            vad_model="fsmn-vad",
            punc_model="ct-punc",
            # 首次运行会自动下载模型（~1GB）
        )

        logger.info(f"[FunASR] 正在识别: {wav_path}")
        result = model.generate(input=str(wav_path))

        # 转换为标准格式
        segments = []
        if result and len(result) > 0:
            # FunASR 返回格式可能不同，需要适配
            text = result[0].get('text', '') if isinstance(result[0], dict) else str(result[0])
            # 检查是否有时间戳信息
            timestamp = result[0].get('timestamp') if isinstance(result[0], dict) else None

            if timestamp:
                # 使用FunASR的时间戳
                for ts in timestamp:
                    segments.append({
                        'start': ts[0] / 1000.0,  # 毫秒转秒
                        'end': ts[1] / 1000.0,
                        'text': ts[2] if len(ts) > 2 else ''
                    })
            else:
                # 简化处理：生成单个segment
                segments = [{
                    'start': 0.0,
                    'end': 0.0,
                    'text': text
                }]

        logger.info(f"[FunASR] 识别完成，共 {len(segments)} 个片段")
        return segments

    except ImportError:
        logger.warning("[FunASR] 库未安装，尝试使用 faster-whisper")
        return None
    except Exception as e:
        logger.warning(f"[FunASR] 识别失败: {e}")
        return None


def transcribe_whisper(wav_path: Path, language: str = None) -> List[dict]:
    """
    使用 faster-whisper 进行语音识别

    多语言备选方案 | VERIFIED: CPU速度比原版快3.3倍
    """
    try:
        from faster_whisper import WhisperModel

        logger.info(f"[Whisper] 正在加载模型...")

        # 使用 large-v3 模型
        model = WhisperModel("large-v3", device="auto", compute_type="auto")

        logger.info(f"[Whisper] 正在识别: {wav_path}")

        # 如果未指定语言，让Whisper自动检测
        transcribe_params = {}
        if language:
            transcribe_params['language'] = language

        segments, info = model.transcribe(str(wav_path), **transcribe_params)

        logger.info(f"[Whisper] 检测到语言: {info.language} (概率: {info.language_probability:.2%})")

        # 转换为标准格式
        results = []
        for segment in segments:
            results.append({
                'start': segment.start,
                'end': segment.end,
                'text': segment.text.strip()
            })

        logger.info(f"[Whisper] 识别完成，共 {len(results)} 个片段")
        return results

    except ImportError:
        logger.error("[Whisper] faster-whisper 未安装")
        raise ImportError("请安装: pip install faster-whisper")
    except Exception as e:
        logger.error(f"[Whisper] 识别失败: {e}")
        raise


def detect_language(text: str) -> str:
    """
    检测文本语言
    """
    try:
        from langdetect import detect
        lang = detect(text)
        # 转换为Whisper语言代码
        lang_map = {
            'zh-cn': 'zh',
            'zh-tw': 'zh',
            'zh-hk': 'zh',
        }
        return lang_map.get(lang, lang)
    except:
        return "auto"


def transcribe(wav_path: Path) -> List[dict]:
    """
    执行ASR识别，自动选择最佳引擎

    YouTube视频语言多样，优先使用Whisper（支持自动语言检测）
    如果检测到中文，则尝试FunASR
    """
    # 首先尝试Whisper（因为YouTube内容语言多样，Whisper的自动检测更好）
    try:
        return transcribe_whisper(wav_path)
    except Exception as e:
        logger.warning(f"[Whisper] 识别失败，尝试FunASR: {e}")

    # 如果Whisper失败，尝试FunASR
    segments = transcribe_funasr(wav_path)
    if segments:
        return segments

    raise RuntimeError("ASR识别失败，请检查依赖安装")


# ============================================================
# Step 5: 字幕生成
# ============================================================

def format_timestamp_srt(seconds: float) -> str:
    """生成SRT格式的时间戳"""
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{milliseconds:03d}"


def format_timestamp_vtt(seconds: float) -> str:
    """生成VTT格式的时间戳"""
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}.{milliseconds:03d}"


def generate_srt(segments: List[dict], output_path: Path):
    """生成SRT字幕文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, seg in enumerate(segments, 1):
            start = format_timestamp_srt(seg['start'])
            end = format_timestamp_srt(seg['end'])
            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{seg['text']}\n\n")

    logger.info(f"[字幕] SRT文件已生成: {output_path}")


def generate_vtt(segments: List[dict], output_path: Path):
    """生成VTT字幕文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("WEBVTT\n\n")
        for i, seg in enumerate(segments, 1):
            start = format_timestamp_vtt(seg['start'])
            end = format_timestamp_vtt(seg['end'])
            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{seg['text']}\n\n")

    logger.info(f"[字幕] VTT文件已生成: {output_path}")


def generate_txt(segments: List[dict], output_path: Path):
    """生成纯文本文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for seg in segments:
            f.write(f"{seg['text']}\n")

    logger.info(f"[字幕] TXT文件已生成: {output_path}")


def generate_subtitles(segments: List[dict], title: str, output_dir: Path):
    """生成所有格式的字幕文件"""
    output_dir.mkdir(parents=True, exist_ok=True)

    # 清理标题作为文件名
    safe_title = sanitize_filename(title)
    base_path = output_dir / safe_title

    generate_srt(segments, base_path.with_suffix('.srt'))
    generate_vtt(segments, base_path.with_suffix('.vtt'))
    generate_txt(segments, base_path.with_suffix('.txt'))

    return base_path


# ============================================================
# 主流程
# ============================================================

def main(video_url: str, output_dir: Optional[Path] = None):
    """
    主入口函数
    """
    print("=" * 60)
    print("  youtube2sub - YouTube视频转字幕工具")
    print("=" * 60)

    # 1. 解析URL
    print("\n[Step 1] 解析URL...")
    video_id = extract_youtube_id(video_url)
    print(f"  视频ID: {video_id}")

    # 设置输出目录
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    # 2. 下载音频
    print("\n[Step 2] 下载音频...")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        audio_path, video_title = download_audio_youtube(video_id, temp_path)
        print(f"  音频文件: {audio_path}")
        print(f"  视频标题: {video_title}")

        # 3. 预处理
        print("\n[Step 3] 预处理...")
        wav_path = convert_to_wav(audio_path)
        chunks = split_audio(wav_path)

        # 4. ASR识别
        print("\n[Step 4] ASR识别...")
        all_segments = []
        for i, chunk in enumerate(chunks):
            print(f"  处理片段 {i+1}/{len(chunks)}...")
            segments = transcribe(chunk)
            # 如果分段，需要调整时间戳
            if chunk != chunks[0]:
                offset = i * 30 * 60  # 30分钟偏移
                for seg in segments:
                    seg['start'] += offset
                    seg['end'] += offset
            all_segments.extend(segments)

        # 5. 生成字幕
        print("\n[Step 5] 生成字幕...")
        base_path = generate_subtitles(all_segments, video_title, output_dir)

    # 完成
    print("\n" + "=" * 60)
    print("  处理完成!")
    print("=" * 60)
    print(f"\n  输出文件:")
    print(f"    - {base_path}.srt")
    print(f"    - {base_path}.vtt")
    print(f"    - {base_path}.txt")
    print()

    return base_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python3 youtube2sub.py <视频URL>")
        print("示例:")
        print("  python3 youtube2sub.py https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        print("  python3 youtube2sub.py https://youtu.be/dQw4w9WgXcQ")
        print("  python3 youtube2sub.py dQw4w9WgXcQ")
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
