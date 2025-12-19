import os
import subprocess
from pathlib import Path
from media_processor.constant.extensions import VIDEO_EXTENSIONS


def run_ffmpeg(cmd):
    """Executes FFmpeg command."""
    try:
        # -loglevel error to keep output clean
        full_cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + cmd
        subprocess.run(full_cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"❌ FFmpeg failed.")
        return False


def merge_videos(video_files, output_path):
    """Merges multiple video files into one using FFmpeg concat demuxer (stream copy).

    Args:
        video_files (list[Path]): List of video file paths to merge.
        output_path (Path): Path for the output merged video.

    Returns:
        bool: True if successful, False otherwise.
    """
    if not video_files:
        return False

    # Create temporary concat list file
    list_filename = output_path.parent / f"temp_concat_list_{output_path.stem}.txt"

    try:
        with open(list_filename, "w", encoding="utf-8") as f:
            for video in video_files:
                # Escape single quotes for ffmpeg concat file
                safe_path = str(video.resolve()).replace("'", "'\\''")
                f.write(f"file '{safe_path}'\n")

        print(f"  🔗 Merging {len(video_files)} clips -> {output_path.name}")

        # Stream copy (-c copy) is fast and lossless but requires identical codecs
        cmd = [
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_filename),
            "-c",
            "copy",
            str(output_path),
        ]

        result = run_ffmpeg(cmd)

        if result:
            print(f"  ✅ Created: {output_path}")

        return result

    except Exception as e:
        print(f"❌ Error during merge: {e}")
        return False

    finally:
        # Cleanup
        if list_filename.exists():
            try:
                os.remove(list_filename)
            except OSError:
                pass


def process_folder(input_dir, output_root):
    """Processes a single folder: merges all videos inside into one file.

    Args:
        input_dir (Path): Source directory containing videos.
        output_root (Path): Directory where output will be saved.
    """
    input_path = Path(input_dir).resolve()

    # Supported video extensions
    extensions = VIDEO_EXTENSIONS

    # 1. Gather video files
    videos = [
        p
        for p in input_path.iterdir()
        if p.is_file() and p.suffix.lower() in extensions and not p.name.startswith(".")
    ]
    videos.sort()  # Ensure order (e.g. 001.mp4, 002.mp4)

    if not videos:
        return

    # 2. Determine output filename (Folder Name.mp4)
    # Output path structure: output_root / input_dir_name / input_dir_name.mp4
    # This keeps things organized similar to audio processor
    target_dir = output_root / input_path.name
    target_dir.mkdir(parents=True, exist_ok=True)

    output_filename = f"{input_path.name}.mp4"
    output_path = target_dir / output_filename

    # Avoid re-merging if exists? Or overwrite?
    # Logic: if output exists in input dir (recursive hazard), skip?
    # But we calculate output_path inside output_root, so safe if output_root != input_dir

    # Check if we are trying to merge the output file itself if folders overlap
    if output_path in videos:
        videos.remove(output_path)

    if not videos:
        return

    print(f"\n🎞️  Merging Folder: {input_path.name}")
    merge_videos(videos, output_path)
