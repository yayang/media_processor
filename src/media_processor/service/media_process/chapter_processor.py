import os
import subprocess
from pathlib import Path


# --- 工具函数 ---

def get_duration(file_path):
    """Gets the total duration of the video in seconds using ffprobe.

    Args:
        file_path (Path): Path to the video file.

    Returns:
        float: Duration in seconds.
    """
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(file_path)
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"❌ Failed to get duration for {file_path}: {e}")
        return 0.0


def time_to_ms(time_str):
    """Converts a time string to milliseconds.

    Args:
        time_str (str): Time string in 'MM:SS' or 'HH:MM:SS' format.

    Returns:
        int: Time in milliseconds.
    """
    parts = list(map(int, time_str.split(":")))
    if len(parts) == 2:  # MM:SS
        return (parts[0] * 60 + parts[1]) * 1000
    elif len(parts) == 3:  # HH:MM:SS
        return (parts[0] * 3600 + parts[1] * 60 + parts[2]) * 1000
    return 0


def create_metadata_file(chapters, duration_sec, temp_file_path):
    """Creates a FFmpeg metadata file from the chapter list.

    Args:
        chapters (list): List of (start_time_str, title) tuples.
        duration_sec (float): Total duration of the video.
        temp_file_path (Path): Path to write the metadata file.
    """
    duration_ms = int(duration_sec * 1000)

    content = ";FFMETADATA1\n"

    for i, (start_time_str, title) in enumerate(chapters):
        start_ms = time_to_ms(start_time_str)

        # 结束时间 = 下一章的开始时间，如果是最后一章，则是视频总长度
        if i < len(chapters) - 1:
            end_ms = time_to_ms(chapters[i + 1][0])
        else:
            end_ms = duration_ms

        content += (
            f"[CHAPTER]\n"
            f"TIMEBASE=1/1000\n"
            f"START={start_ms}\n"
            f"END={end_ms}\n"
            f"title={title}\n\n"
        )

    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write(content)


def inject_chapters(video_path, output_path, chapters):
    """Injects chapters into a video file.

    Args:
        video_path (Path): Path to the input video.
        output_path (Path): Path to the output video.
        chapters (list): List of (start_time, title) tuples.
    """
    input_file = Path(video_path).resolve()
    output_file = Path(output_path).resolve()

    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        return

    print(f"\n📖 Processing Chapters for: {input_file.name}")

    # 1. 获取时长
    duration = get_duration(input_file)
    if duration == 0:
        return

    # 2. 创建临时 metadata 文件
    meta_file = input_file.parent / "temp_ffmetadata.txt"
    create_metadata_file(chapters, duration, meta_file)

    # 3. 执行混流 (Stream Mapping)
    # -map_metadata 1 表示使用第2个输入流(即txt文件)作为全局元数据
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(input_file), # Input 0: 视频
        "-i", str(meta_file),  # Input 1: 章节信息

        "-map_metadata", "1",  # 使用 Input 1 的全局元数据 (Title等)
        "-map_chapters", "1",  # 使用 Input 1 的章节信息 (Chapters)
        "-codec", "copy",  # 直接流拷贝，速度极快，不损画质
        # 即使是 MP4，有时也需要重新标记一下品牌格式，让 QuickTime 认为它是一个标准文件
        "-f", "mp4",
        str(output_file)
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Success! Saved to: {output_file.name}")
    except subprocess.CalledProcessError:
        print(f"❌ FFmpeg Error.")
    finally:
        # 清理临时文件
        if meta_file.exists():
            os.remove(meta_file)