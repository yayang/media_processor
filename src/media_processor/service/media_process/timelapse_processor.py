import subprocess
import time
from pathlib import Path
from media_processor.constant.extensions import VIDEO_EXTENSIONS
from media_processor.constant.constant import (
    TIMELAPSE_CRF,
    TIMELAPSE_PRESET,
    TIMELAPSE_FRAMERATE,
    DEFAULT_SPEED_RATIO,
)

"""
延迟摄影 (Timelapse/Hyperlapse) 的核心本质是 "抽帧" (Dropping Frames)。
20:1 的比例意味着：每 20 帧里只保留 1 帧，或者把时间戳 (PTS) 压缩到原来的 1/20。
音频处理：通常延迟摄影会直接丢弃音频 (-an)，因为加速 20 倍的声音全是尖锐的噪音，不可用。
"""


# --- 工具函数 ---


def run_ffmpeg(cmd, use_gpu):
    try:
        # -loglevel error: 保持清爽
        full_cmd = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-stats",
        ] + cmd
        # full_cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + cmd

        mode_str = "GPU" if use_gpu else "CPU"
        print(f"  🚀 Processing ({mode_str})...")
        subprocess.run(full_cmd, check=True)
    except subprocess.CalledProcessError:
        print(f"❌ FFmpeg failed.")
        # 不中断，让上层决定是否继续
        pass


def create_timelapse(video_path, output_path, speed_ratio, use_gpu):
    """Creates a timelapse video from the input video.

    Args:
        video_path (Path): Path to the input video.
        output_path (Path): Path to the output video.
        speed_ratio (int): Speed multiplier (e.g., 20 for 20x speed).
        use_gpu (bool): Whether to use GPU acceleration.
    """
    # 计算 PTS 缩放因子 (例如 20倍速 = 0.05)
    pts_multiplier = 1 / speed_ratio

    cmd = [
        "-i",
        str(video_path),
        # --- 核心滤镜 ---
        # setpts: 修改时间戳，实现加速
        "-vf",
        f"setpts={pts_multiplier}*PTS",
        # --- 丢弃音频 (延迟摄影通常不需要) ---
        "-an",
        # --- 强制帧率 ---
        # 防止加速后帧率爆炸，强制回到 30fps
        "-r",
        TIMELAPSE_FRAMERATE,
    ]

    # --- 编码器分支 ---
    if use_gpu:
        cmd.extend(
            [
                "-c:v",
                "h264_videotoolbox",
                "-q:v",
                "50",  # 硬件编码质量控制
                # "-b:v", "5000k" # 延迟摄影信息量大，如果画质不够好可以给高码率
            ]
        )
    else:
        cmd.extend(
            [
                "-c:v",
                "libx264",
                "-crf",
                TIMELAPSE_CRF,  # 延迟摄影建议画质稍微好一点 (默认28可能有点糊)
                "-preset",
                TIMELAPSE_PRESET,
            ]
        )

    cmd.append(str(output_path))

    run_ffmpeg(cmd, use_gpu)


# --- 核心入口 ---


def process_folder(
    input_dir, output_root, speed_ratio=DEFAULT_SPEED_RATIO, use_gpu=True
):
    """Processes all videos in the directory to create timelapse videos.

    Args:
        input_dir (Path): Input directory containing videos.
        output_root (Path): Output root directory.
        speed_ratio (int): Speed multiplier.
        use_gpu (bool): Whether to use GPU acceleration.
    """
    input_path = Path(input_dir).resolve()
    output_root_path = Path(output_root).resolve()

    # 创建同名子目录存放结果
    target_dir = output_root_path / input_path.name
    target_dir.mkdir(parents=True, exist_ok=True)

    extensions = VIDEO_EXTENSIONS
    videos = [p for p in input_path.iterdir() if p.suffix.lower() in extensions]
    videos.sort()

    if not videos:
        return

    print(f"\n⏩ Timelapse Task: {input_path.name}")
    print(f"   Ratio: {speed_ratio}:1 | Mode: {'GPU' if use_gpu else 'CPU'}")

    success_count = 0
    start_time = time.time()

    for v in videos:
        # 生成后缀，例如 _20x.mp4
        output_name = f"{v.stem}_{speed_ratio}x.mp4"
        output_file = target_dir / output_name

        # 1. 检查是否已经存在
        if output_file.exists():
            print(f"  ⏭️  Skipping (Exists): {output_name}")
            continue

        # 2. 检查是不是之前的产物 (防止死循环处理自己)
        if f"_{speed_ratio}x" in v.name:
            continue

        print(f"  🎬 {v.name} -> {output_name}")

        try:
            create_timelapse(v, output_file, speed_ratio, use_gpu)
            success_count += 1
        except Exception as e:
            print(f"  ❌ Failed: {v.name}")

    total_time = time.time() - start_time
    if success_count > 0:
        print(f"✅ Done! Processed {success_count} videos in {total_time:.1f}s")
        print(f"📂 Output: {target_dir}")
