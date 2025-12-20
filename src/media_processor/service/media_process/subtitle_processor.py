import datetime
import os
import subprocess
import time
from pathlib import Path

"""
Subtitle Processor:
Embeds external subtitles into video files using Stream Copy (no transcoding).
"""


def run_ffmpeg(cmd):
    try:
        # -loglevel error: Keep it clean
        full_cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + cmd
        print(f"🚀 Running FFmpeg [Stream Copy]...")
        subprocess.run(full_cmd, check=True)
    except subprocess.CalledProcessError:
        print(f"\n❌ FFmpeg process failed.")
        raise


def process_subtitle_embedding(
    input_path,
    output_path,
    remove_subtitle=True,
):
    """Embeds subtitle into video without transcoding (Stream Copy).

    Args:
        input_path (Path): Path to the source video file.
        output_path (Path): Path to the destination video file.
        delete_source (bool): Whether to delete the source file after success.
    """
    input_path = Path(input_path).resolve()
    output_path = Path(output_path).resolve()

    if output_path.exists() and output_path != input_path:
        print(f"⏭️  Skipping (Exists): {output_path.name}")
        return

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"🎬 Processing Subtitle Embed: {input_path.name}")
    print(f"   Input:  {input_path}")
    print(f"   Output: {output_path}")

    # --- 1. Subtitle Detection ---
    possible_subs = [input_path.with_suffix(ext) for ext in [".srt", ".ass", ".vtt"]]
    sub_path = next((p for p in possible_subs if p.exists()), None)

    if not sub_path:
        print(f"⏭️  Skipping (No Subtitle Found): {input_path.name}")
        return

    print(f"   Subtitle: {sub_path.name} (Embedding as soft-sub)")

    # --- 1.1 Validation: Check Container Support ---
    # Many containers (avi, rmvb, wmv) do not support modern soft-sub embedding nicely or at all via this method.
    supported_extensions = [".mp4", ".mov", ".m4v", ".mkv"]
    if output_path.suffix.lower() not in supported_extensions:
        print(
            f"❌ Error: Container '{output_path.suffix}' ({input_path.name}) does not support in-place subtitle embedding."
        )
        print(f"   Supported formats: {supported_extensions}")
        return

    # --- 2. Build FFmpeg Command ---
    # Inputs
    cmd = ["-i", str(input_path), "-i", str(sub_path)]

    # Determine subtitle format based on container
    # .mp4/.mov -> mov_text
    # .mkv -> copy (ass/srt/etc) or ssa/subrip
    output_suffix = output_path.suffix.lower()
    if output_suffix in [".mp4", ".mov", ".m4v"]:
        sub_codec = "mov_text"
    else:
        # For MKV and others, usually 'copy' works best for SRT/ASS
        sub_codec = "copy"

    # Maps: Video, Audio, Subtitle
    cmd.extend(
        [
            "-map",
            "0:v",  # Copy all video streams
            "-map",
            "0:a",  # Copy all audio streams
            "-map",
            "1:0",  # Add first stream from subtitle file
            "-c",
            "copy",  # Stream copy for Video/Audio
            "-c:s",
            sub_codec,  # Adaptive subtitle codec
            "-metadata:s:s:0",
            "title=默认字幕",  # Generic display title
            "-disposition:s:0",
            "default",  # Mark this subtitle track as default
        ]
    )

    # Output path temp
    stem = output_path.stem
    suffix = output_path.suffix
    # If source is MKV but we want MP4 for mov_text compatibility, usually fine to change extension
    # but stream copy h264/aac from mkv to mp4 works.
    # User didn't strictly specify container, but mov_text implies MP4/MOV container.
    # Let's ensure output is .mp4 if we use mov_text, or just respect output_path.

    processing_output_path = output_path.with_name(f"{stem}_processing{suffix}")
    cmd.append(str(processing_output_path))

    try:
        start_time = time.time()
        run_ffmpeg(cmd)
        duration = time.time() - start_time

        if processing_output_path.exists():
            processing_output_path.rename(output_path)

        file_size = output_path.stat().st_size / (1024 * 1024)
        print(
            f"✅ Done! Time: {duration:.1f}s | Size: {file_size:.2f} MB | DateTime: {datetime.datetime.now()}"
        )

        # Delete subtitle file if requested
        if remove_subtitle and sub_path and sub_path.exists():
            print(f"🗑️ Deleting subtitle: {sub_path.name}")
            os.remove(sub_path)

    except Exception as e:
        print(f"❌ Failed to process {input_path.name}: {e}")
        if processing_output_path.exists():
            os.remove(processing_output_path)
        if output_path.exists():
            os.remove(output_path)
