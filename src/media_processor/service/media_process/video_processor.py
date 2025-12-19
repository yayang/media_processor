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
):
    """Transcodes a single video file.

    Args:
        input_path (Path): Path to the source video file.
        output_path (Path): Path to the destination video file.
        use_gpu (bool): Whether to use GPU acceleration.
        resolution (VideoResolution): Target resolution.
        delete_source (bool): Whether to delete the source file after success.
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

    # 构建命令
    scale_filter = "scale='min(1280,iw)':-2"
    if resolution == VideoResolution.P1080:
        scale_filter = "scale='min(1920,iw)':-2"

    # 构建命令
    cmd = [
        "-i",
        str(input_path),
        "-vf",
        scale_filter,
        "-af",
        "aformat=channel_layouts=stereo",  # 自动降混多声道为双声道
        "-c:a",
        "aac",
        "-b:a",
        VIDEO_AUDIO_BITRATE,
    ]

    if use_gpu:
        cmd.extend(["-c:v", "h264_videotoolbox", "-q:v", "50"])
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

    except Exception as e:
        print(f"❌ Failed to process {input_path.name}: {e}")
        # 如果失败，清理可能生成的半成品
        if processing_output_path.exists():
            os.remove(processing_output_path)
        if output_path.exists():  # 理论上这时候output_path应该还没生成，但为了保险
            os.remove(output_path)
