from pathlib import Path
from media_processor.constant import extensions
from media_processor.service.media_process import subtitle_processor


def run(input_dirs, output_dir, remove_subtitle=True):
    """
    Run subtitle embedding in batch.
    """
    print(f"📂 Scanning directories: {input_dirs}")
    print(f"💾 Output directory: {output_dir}")

    for input_dir_str in input_dirs:
        input_dir = Path(input_dir_str)
        if not input_dir.exists():
            print(f"⚠️ Directory not found: {input_dir}")
            continue

        # Recursively find all video files
        all_files = input_dir.rglob("*")
        video_files = [
            f
            for f in all_files
            if f.is_file() and f.suffix.lower() in extensions.VIDEO_EXTENSIONS
        ]

        print(f"🔎 Found {len(video_files)} video files in {input_dir}")

        for video_path in video_files:
            # Calculate output path
            if output_dir:
                # Normal mode: Output to separate directory
                rel_path = video_path.relative_to(input_dir)
                output_path = Path(output_dir) / rel_path
                # Best practice for mov_text
                output_path = output_path.with_suffix(".mp4")
            else:
                # In-place mode: Output to same file (will use temp file mechanism)
                output_path = video_path

            try:
                subtitle_processor.process_subtitle_embedding(
                    input_path=video_path,
                    output_path=output_path,
                    remove_subtitle=remove_subtitle,
                )
            except Exception as e:
                print(f"❌ Error processing {video_path}: {e}")
