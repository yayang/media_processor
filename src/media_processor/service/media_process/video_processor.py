import os
import subprocess
import time
from pathlib import Path

"""
先合并, 后压缩
全局码率分配 (Bitrate Efficiency): 
视频编码器 (Encoder) 如果能看到完整的长视频，它能更智能地分配比特率。
比如，前5分钟是静态画面（少给点数据），后5分钟是剧烈运动（多给点数据）。
如果分开压缩，每一段都只能基于局部优化，合并后的整体积往往比"一次性压缩"要大，或者画质不均匀。

压缩: 使用 H.264 编码，CRF=28 (数值越大文件越小，画质越差，23是默认，28是比较明显的压缩)
分辨率限制: 限制最大宽度为 720p (如果原视频是 4K，会自动缩放以大幅减小体积)
"""

# --- 封装好的工具函数 ---

def run_ffmpeg(cmd, use_gpu):
    try:
        # -loglevel error: 保持清爽
        # -stats: 显示进度条
        #         但日志高概率卡死Pycharm的UI
        #         如果是在系统Terminal执行 python3 batch_runner.py , 可以加上-stats
        # full_cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-stats"] + cmd
        full_cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + cmd
        mode_str = 'GPU (VideoToolbox)' if use_gpu else 'CPU (libx264)'
        print(f"🚀 Running FFmpeg [{mode_str}]...")
        subprocess.run(full_cmd, check=True)
    except subprocess.CalledProcessError:
        print(f"\n❌ FFmpeg process failed.")
        raise


def generate_concat_list(video_files, list_path):
    with open(list_path, "w", encoding="utf-8") as f:
        for video in video_files:
            safe_path = str(video.resolve()).replace("'", "'\\''")
            f.write(f"file '{safe_path}'\n")


def process_folder(input_dir, output_root, use_gpu=False):
    """
    核心入口函数
    :param input_dir: 包含视频的源文件夹路径 (Path对象或字符串)
    :param output_root: 结果输出的总目录 (Path对象或字符串)
    :param use_gpu: True使用GPU加速, False使用CPU高压缩
    """
    input_path = Path(input_dir).resolve()
    output_root_path = Path(output_root).resolve()

    # 确保输出目录存在
    output_root_path.mkdir(parents=True, exist_ok=True)

    folder_name = input_path.name
    mode_suffix = "_GPU" if use_gpu else "_CPU"
    output_filename = f"{folder_name}_720p{mode_suffix}.mp4"
    final_output_path = output_root_path / output_filename

    # 扫描视频文件
    extensions = {".mp4", ".mov", ".mkv", ".flv", ".avi", ".ts"}
    # 排除掉可能已经在源目录里的输出文件(虽然现在输出到别处了, 但防卫性编程是个好习惯)
    videos = [
        p for p in input_path.iterdir()
        if p.suffix.lower() in extensions and "_720p_" not in p.name
    ]
    videos.sort(key=lambda f: f.name)

    if not videos:
        print(f"⚠️  No videos found in: {folder_name}")
        return

    # 如果目标文件已存在，跳过
    if final_output_path.exists():
        print(f"⏭️  Skipping (Exists): {final_output_path.name}")
        return

    print(f"\n📂 Processing Task: {folder_name}")
    print(f"   Input:  {input_path}")
    print(f"   Output: {final_output_path}")
    print(f"   Count:  {len(videos)} files")

    # 生成临时列表
    list_filename = input_path / "temp_concat_list.txt"
    generate_concat_list(videos, list_filename)

    # 构建命令
    cmd = [
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_filename),
        "-vf", "scale='min(1280,iw)':-2",  # 720p 限制
        "-c:a", "aac",
        "-b:a", "128k",
    ]

    if use_gpu:
        cmd.extend(["-c:v", "h264_videotoolbox", "-q:v", "50"])
    else:
        cmd.extend(["-c:v", "libx264", "-crf", "28", "-preset", "fast"])

    cmd.append(str(final_output_path))

    try:
        start_time = time.time()
        run_ffmpeg(cmd, use_gpu)
        duration = time.time() - start_time

        file_size = final_output_path.stat().st_size / (1024 * 1024)
        print(f"✅ Done! Time: {duration:.1f}s | Size: {file_size:.2f} MB")

    except Exception as e:
        print(f"❌ Failed to process {folder_name}: {e}")
        # 如果失败，清理可能生成的半成品
        if final_output_path.exists():
            os.remove(final_output_path)
    finally:
        if list_filename.exists():
            os.remove(list_filename)


def process_video(input_path, output_path, use_gpu=False):
    """
    单个视频处理函数 (1:1 转码)
    :param input_path: 源视频文件路径 (Path对象)
    :param output_path: 目标视频文件路径 (Path对象)
    :param use_gpu: 是否使用 GPU
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
    cmd = [
        "-i", str(input_path),
        "-vf", "scale='min(1280,iw)':-2",  # 720p 限制
        "-c:a", "aac",
        "-b:a", "128k",
    ]

    if use_gpu:
        cmd.extend(["-c:v", "h264_videotoolbox", "-q:v", "50"])
    else:
        cmd.extend(["-c:v", "libx264", "-crf", "28", "-preset", "fast"])

    cmd.append(str(output_path))

    try:
        start_time = time.time()
        run_ffmpeg(cmd, use_gpu)
        duration = time.time() - start_time

        file_size = output_path.stat().st_size / (1024 * 1024)
        print(f"✅ Done! Time: {duration:.1f}s | Size: {file_size:.2f} MB")

    except Exception as e:
        print(f"❌ Failed to process {input_path.name}: {e}")
        # 如果失败，清理可能生成的半成品
        if output_path.exists():
            os.remove(output_path)