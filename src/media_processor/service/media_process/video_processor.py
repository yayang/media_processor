import datetime
import os
import subprocess
import time
from pathlib import Path

from media_processor.constant.constant import (
    VIDEO_CRF_DEFAULT,
    VIDEO_PRESET_DEFAULT,
    VIDEO_AUDIO_BITRATE,
)

"""
先合并, 后压缩
全局码率分配 (Bitrate Efficiency): 
视频编码器 (Encoder) 如果能看到完整的长视频，它能更智能地分配比特率。
比如，前5分钟是静态画面（少给点数据），后5分钟是剧烈运动（多给点数据）。
如果分开压缩，每一段都只能基于局部优化，合并后的整体积往往比"一次性压缩"要大，或者画质不均匀。

压缩: 使用 H.264 编码，CRF=28 (数值越大文件越小，画质越差，23是默认，28是比较明显的压缩)
分辨率限制: 根据用户选择, 限制最大宽度为 720p 或 1080p
"""

from enum import Enum


class VideoResolution(Enum):
    P720 = "720p"
    P1080 = "1080p"


# --- 封装好的工具函数 ---


def run_ffmpeg(cmd, use_gpu):
    try:
        # -loglevel error: 保持清爽
        # -stats: 显示进度条
        #         但日志高概率卡死Pycharm的UI
        #         如果是在系统Terminal执行 python3 batch_runner.py , 可以加上-stats
        # full_cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-stats"] + cmd
        full_cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + cmd
        mode_str = "GPU (VideoToolbox)" if use_gpu else "CPU (libx264)"
        print(f"🚀 Running FFmpeg [{mode_str}]...")
        subprocess.run(full_cmd, check=True)
    except subprocess.CalledProcessError:
        print(f"\n❌ FFmpeg process failed.")
        raise


def process_video(
    input_path,
    output_path,
    use_gpu=False,
    resolution: VideoResolution = VideoResolution.P720,
    delete_source=False,
    compatibility_mode=False,
    embed_subtitles=False,
    remove_subtitle=False,
    test_mode=False,
):
    """Transcodes a single video file.

    Args:
        input_path (Path): Path to the source video file.
        output_path (Path): Path to the destination video file.
        use_gpu (bool): Whether to use GPU acceleration.
        resolution (VideoResolution): Target resolution.
        delete_source (bool): Whether to delete the source file after success.
        compatibility_mode (bool): Whether to enable compatibility mode for older devices.
    """
    input_path = Path(input_path).resolve()
    output_path = Path(output_path).resolve()

    if output_path.exists():
        print(f"⏭️  Skipping (Exists): {output_path.name}")
        return

    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"🎬 Processing Video: {input_path.name}")
    print(f"   Input:  {input_path}")
    print(f"   Output: {output_path}")
    if compatibility_mode:
        print(
            f"   Mode:   🛡️ Compatibility Mode Enabled (Deinterlace, YUV420P, High@4.1)"
        )

    # 1. 构建 Filter Chain
    filters = []

    # (A) Deinterlacing (仅在兼容模式下)
    # yadif=1:-1:0 -> 启用 bob 去隔行 (1), 自动检测 (-1), 总是输出一帧 (0)
    # 这对老电视播放 1080i 隔行视频非常重要，防止拉丝。
    if compatibility_mode:
        filters.append("yadif=1:-1:0")

    # (B) Scaling - 强制截断为偶数，防止硬件对齐错误
    scale_filter = "scale='trunc(min(1280,iw)/2)*2:trunc(ih/2)*2'"
    if resolution == VideoResolution.P1080:
        scale_filter = "scale='trunc(min(1920,iw)/2)*2:trunc(ih/2)*2'"
    filters.append(scale_filter)

    # 组合滤见链: "filter1,filter2"
    vf_chain = ",".join(filters)

    # --- 1. Subtitle Detection ---
    # Try to find a subtitle file with the same name
    possible_subs = [input_path.with_suffix(ext) for ext in [".srt", ".ass", ".vtt"]]
    sub_path = next((p for p in possible_subs if p.exists()), None)

    if sub_path:
        print(f"   Subtitle: {sub_path.name} (Embedding as soft-sub)")

        # Validation
        supported_extensions = [".mp4", ".mov", ".m4v", ".mkv"]
        if output_path.suffix.lower() not in supported_extensions:
            print(
                f"❌ Error: Target Container '{output_path.suffix}' does not support subtitle embedding. Skipping subtitle."
            )
            # We don't return here, we just unset sub_path so it continues without subtitle
            sub_path = None

    # --- 2. Build FFmpeg Command ---
    # Base inputs
    cmd = ["-i", str(input_path)]

    # Add subtitle input if exists (Input #1)
    if sub_path:
        cmd.extend(["-i", str(sub_path)])

    # Map Streams
    # -map 0:v -> Select all video streams from Input #0
    # -map 0:a -> Select all audio streams from Input #0
    cmd.extend(["-map", "0:v", "-map", "0:a"])

    # Map Subtitle if exists
    # -map 1:0 -> Select the first subtitle stream from Input #1
    # -c:s mov_text -> Convert to MP4 compatible text format
    if sub_path:
        output_suffix = output_path.suffix.lower()
        if output_suffix in [".mp4", ".mov", ".m4v"]:
            sub_codec = "mov_text"
        else:
            sub_codec = "copy"

        cmd.extend(
            [
                "-map",
                "1:0",
                "-c:s",
                sub_codec,
                "-metadata:s:s:0",
                "title=默认字幕",
                "-disposition:s:0",
                "default",
            ]
        )

    # --- 3. Filters & Encoders ---
    cmd.extend(
        [
            "-vf",
            vf_chain,
            "-af",
            "aformat=channel_layouts=stereo",  # Apply stereo format to audio streams
            "-c:a",
            "aac",
            "-b:a",
            VIDEO_AUDIO_BITRATE,
        ]
    )

    # 兼容性模式全局 Flags
    if compatibility_mode:
        # -vsync cfr: 强制恒定帧率 (解决 VFR 音画同步问题)
        # -movflags +faststart: 优化 MP4 头部，利于流媒体/电视播放加载
        # -pix_fmt yuv420p: 强制 8-bit YUV420，电视解码必选 (防止 yuv444/10-bit 不兼容)
        cmd.extend(["-vsync", "cfr", "-movflags", "+faststart", "-pix_fmt", "yuv420p"])

    if use_gpu:
        cmd.extend(["-c:v", "h264_videotoolbox", "-q:v", "50"])
        # 在 VideoToolbox 中，通常通过 Profile 限制。
        if compatibility_mode:
            cmd.extend(["-profile:v", "high"])
    else:
        cmd.extend(
            [
                "-c:v",
                "libx264",
                "-crf",
                VIDEO_CRF_DEFAULT,
                "-preset",
                VIDEO_PRESET_DEFAULT,
            ]
        )
        if compatibility_mode:
            # 强制 Level 4.1 的同时，限制参考帧数量，这是电视硬解的物理上限
            cmd.extend(
                [
                    "-profile:v",
                    "high",
                    "-level",
                    "4.1",
                    "-x264-params",
                    "ref=4:bframes=3",
                ]
            )

    # Test Mode: Only process first 3 minutes (180 seconds)
    if test_mode:
        print("   🧪 Test Mode: Limiting duration to 180s")
        cmd.extend(["-t", "180"])

    # Output path
    # 使用 _processing 后缀 (如 video_processing.mp4)
    stem = output_path.stem
    suffix = output_path.suffix
    processing_output_path = output_path.with_name(f"{stem}_processing{suffix}")
    cmd.append(str(processing_output_path))

    try:
        start_time = time.time()
        run_ffmpeg(cmd, use_gpu)
        duration = time.time() - start_time

        # 重命名回正式目标名
        if processing_output_path.exists():
            processing_output_path.rename(output_path)

        file_size = output_path.stat().st_size / (1024 * 1024)
        print(
            f"✅ Done! Time: {duration:.1f}s | Size: {file_size:.2f} MB | DateTime: {datetime.datetime.now()}"
        )

        # 删除源文件 (如果配置了且新文件存在)
        if delete_source and output_path.exists():
            print(f"🗑️ Deleting source: {input_path}")
            os.remove(input_path)

        # 删除字幕文件 (如果配置了且新文件生成成功)
        if remove_subtitle and sub_path and sub_path.exists():
            print(f"🗑️ Deleting subtitle: {sub_path.name}")
            os.remove(sub_path)

    except Exception as e:
        print(f"❌ Failed to process {input_path.name}: {e}")
        # 如果失败，清理可能生成的半成品
        if processing_output_path.exists():
            os.remove(processing_output_path)
        if output_path.exists():  # 理论上这时候output_path应该还没生成，但为了保险
            os.remove(output_path)
