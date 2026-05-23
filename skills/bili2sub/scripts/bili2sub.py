#!/usr/bin/env python3
"""
bili2sub - Bilibili视频转字幕工具
========================================
将Bilibili视频的音频转换为字幕文件（SRT/VTT/TXT）

使用方法:
    python3 bili2sub.py "<视频URL>"
    python3 bili2sub.py "https://www.bilibili.com/video/BV1xx"
    python3 bili2sub.py "BV1xx"  # 简写

依赖安装:
    pip install bilibili-api-python funasr modelscope faster-whisper pydub langdetect

作者: Claude @ bili2sub skill
版本: 1.0.0
"""

import os
import re
import sys
import json
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

def extract_bvid(url: str) -> str:
    """
    从URL或简写中提取BV号或AV号

    支持格式:
    - https://www.bilibili.com/video/BV1xx...
    - https://b23.tv/BV1xx...
    - BV1xx... (简写)
    - av123456 (AV号)
    """
    # 提取BV号（注意：BV号大小写敏感，不能转换）
    bv_match = re.search(r'(BV[\w]+)', url)
    if bv_match:
        return bv_match.group(1)  # 保持原始大小写

    # 提取AV号
    av_match = re.search(r'av(\d+)', url, re.IGNORECASE)
    if av_match:
        return f"av{av_match.group(1)}"

    # 如果输入本身就是BV号（保持原始大小写）
    if url.startswith('BV') and len(url) >= 10:
        return url  # 保持原始大小写

    raise ValueError(f"无法从URL中提取视频ID: {url}")


# ============================================================
# Step 2: 音频下载
# ============================================================

def download_audio_bilibili_api(bvid: str, output_dir: Path) -> Optional[Path]:
    """
    使用 bilibili-api-python 下载音频

    VERIFIED: Nemo2011/bilibili-api 活跃维护中
    """
    try:
        from bilibili_api import video, sync

        logger.info(f"[bilibili-api] 正在获取视频信息: {bvid}")

        # 创建视频对象
        if bvid.upper().startswith('BV'):
            v = video.Video(bvid=bvid)
        else:
            # AV号转换
            aid = int(bvid.replace('av', ''))
            v = video.Video(aid=aid)

        # 获取视频信息
        info = sync(v.get_info())
        title = info.get('title', bvid)
        logger.info(f"[bilibili-api] 视频标题: {title}")

        # 获取音频流URL
        audio_url = sync(v.get_audio_url())

        if not audio_url:
            logger.warning("[bilibili-api] 未找到音频流")
            return None

        # 下载音频
        audio_path = output_dir / f"{bvid}.m4a"
        logger.info(f"[bilibili-api] 正在下载音频...")

        import requests
        headers = {
            'Referer': 'https://www.bilibili.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        response = requests.get(audio_url, headers=headers, stream=True)
        response.raise_for_status()

        with open(audio_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"[bilibili-api] 音频下载完成: {audio_path}")
        return audio_path

    except ImportError:
        logger.warning("[bilibili-api] 库未安装，跳过")
        return None
    except Exception as e:
        logger.warning(f"[bilibili-api] 下载失败: {e}")
        return None


def download_audio_ytdlp(bvid: str, output_dir: Path) -> Optional[Path]:
    """
    使用 yt-dlp 作为备选方案下载音频

    已知问题: 2025.9.26版本后Bilibili支持不稳定
    建议: 使用最新版本 yt-dlp -U
    """
    try:
        url = f"https://www.bilibili.com/video/{bvid}"
        audio_path = output_dir / f"{bvid}.m4a"

        logger.info(f"[yt-dlp] 正在下载音频: {bvid}")

        cmd = [
            'yt-dlp',
            '-f', 'bestaudio',
            '-x',  # 仅提取音频
            '--audio-format', 'm4a',
            '-o', str(audio_path.with_suffix('')),
            '--no-playlist',
            url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0 and audio_path.exists():
            logger.info(f"[yt-dlp] 音频下载完成: {audio_path}")
            return audio_path
        else:
            logger.warning(f"[yt-dlp] 下载失败: {result.stderr}")
            return None

    except FileNotFoundError:
        logger.warning("[yt-dlp] 未安装，跳过")
        return None
    except Exception as e:
        logger.warning(f"[yt-dlp] 下载失败: {e}")
        return None


def download_audio(bvid: str, temp_dir: Path) -> Path:
    """
    下载音频文件，使用多工具fallback机制
    """
    # 首先尝试 bilibili-api
    audio_path = download_audio_bilibili_api(bvid, temp_dir)

    # 失败则尝试 yt-dlp
    if not audio_path:
        audio_path = download_audio_ytdlp(bvid, temp_dir)

    if not audio_path:
        raise RuntimeError(f"无法下载音频，请检查: 1) 视频URL是否正确 2) 是否需要登录 3) 是否为会员专享内容")

    return audio_path


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

def transcribe_funasr(wav_path: Path) -> List[dict]:
    """
    使用 FunASR Paraformer 进行语音识别

    中文首选方案 | VERIFIED: 阿里达摩院开源，中文效果优于Whisper
    """
    try:
        from funasr import AutoModel
        from modelscope.hub.snapshot_download import snapshot_download

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
            text = result[0].get('text', '')
            # 简化处理：生成单个segment
            # TODO: 使用FunASR的时间戳功能
            segments = [{
                'start': 0.0,
                'end': 0.0,  # 需要后续处理
                'text': text
            }]

        logger.info(f"[FunASR] 识别完成，共 {len(text)} 字")
        return segments

    except ImportError:
        logger.warning("[FunASR] 库未安装，尝试使用 faster-whisper")
        return None
    except Exception as e:
        logger.warning(f"[FunASR] 识别失败: {e}")
        return None


def transcribe_whisper(wav_path: Path, language: str = "zh") -> List[dict]:
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
        segments, info = model.transcribe(str(wav_path), language=language)

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


def detect_language(wav_path: Path) -> str:
    """
    检测音频语言
    """
    # 简化实现：默认中文
    # TODO: 使用 langdetect 或 whisper 的语言检测功能
    return "zh"


def transcribe(wav_path: Path) -> List[dict]:
    """
    执行ASR识别，自动选择最佳引擎
    """
    language = detect_language(wav_path)

    # 中文优先使用 FunASR
    if language == "zh":
        segments = transcribe_funasr(wav_path)
        if segments:
            return segments

    # 备选使用 faster-whisper
    return transcribe_whisper(wav_path, language)


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


def generate_subtitles(segments: List[dict], bvid: str, output_dir: Path):
    """生成所有格式的字幕文件"""
    output_dir.mkdir(parents=True, exist_ok=True)

    base_path = output_dir / bvid

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
    print("  bili2sub - Bilibili视频转字幕工具")
    print("=" * 60)

    # 1. 解析URL
    print("\n[Step 1] 解析URL...")
    bvid = extract_bvid(video_url)
    print(f"  视频ID: {bvid}")

    # 设置输出目录
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    # 2. 下载音频
    print("\n[Step 2] 下载音频...")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        audio_path = download_audio(bvid, temp_path)
        print(f"  音频文件: {audio_path}")

        # 3. 预处理
        print("\n[Step 3] 预处理...")
        wav_path = convert_to_wav(audio_path)
        chunks = split_audio(wav_path)

        # 4. ASR识别
        print("\n[Step 4] ASR识别...")
        all_segments = []
        for chunk in chunks:
            segments = transcribe(chunk)
            # 如果分段，需要调整时间戳
            if chunk != chunks[0]:
                offset = chunks.index(chunk) * 30 * 60  # 30分钟偏移
                for seg in segments:
                    seg['start'] += offset
                    seg['end'] += offset
            all_segments.extend(segments)

        # 5. 生成字幕
        print("\n[Step 5] 生成字幕...")
        base_path = generate_subtitles(all_segments, bvid, output_dir)

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
        print("使用方法: python3 bili2sub.py <视频URL>")
        print("示例: python3 bili2sub.py https://www.bilibili.com/video/BV1xx")
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
