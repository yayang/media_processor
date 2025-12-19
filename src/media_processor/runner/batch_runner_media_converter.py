import os
from pathlib import Path

from media_processor.constant.constant import INPUT_DIR, OUTPUT_DIR
from media_processor.constant.extensions import VIDEO_EXTENSIONS
from media_processor.service.media_process import video_processor
from media_processor.service.media_process.video_processor import VideoResolution


# -----------------


# --------------------
def is_video_folder(folder_path):
    """Checks if the folder contains video files.

    Args:
        folder_path (Path): Path to the folder.

    Returns:
        bool: True if video files are found, False otherwise.
    """
    extensions = VIDEO_EXTENSIONS
    try:
        for item in folder_path.iterdir():
            if item.is_file() and item.suffix.lower() in extensions:
                return True
    except PermissionError:
        pass
    return False


def run(
    input_dirs,
    output_dir,
    use_gpu=False,
    target_resolution="1080p",
    delete_source=False,
    use_suffix=False,
):
    """Executes the batch media conversion task.

    Args:
        input_dirs (list[str]): List of input directories.
        output_dir (str): Output directory.
        use_gpu (bool): Whether to use GPU acceleration.
        target_resolution (str): "1080p" or "720p".
        delete_source (bool): Whether to delete source files.
        use_suffix (bool): Whether to add suffix to output filename.
    """
    if target_resolution == "720p":
        resolution_enum = VideoResolution.P720
    else:
        resolution_enum = VideoResolution.P1080

    print(f"=== Starting Batch Processing ===")
    print(f"Mode: {'GPU' if use_gpu else 'CPU'}")
    print(f"Output Root: {output_dir}")
    print(f"Resolution: {target_resolution}")

    output_root = Path(output_dir)
    tasks_found = 0

    for root_dir in input_dirs:
        root_path = Path(root_dir).resolve()
        if not root_path.exists():
            print(f"⚠️  Directory not found: {root_dir}")
            continue

        # os.walk 递归遍历所有子目录
        for current_root, dirs, files in os.walk(root_path):
            current_path = Path(current_root)

            # 排除输出目录本身
            if output_root in current_path.parents or current_path == output_root:
                continue

            # 过滤视频文件
            video_files = []
            extensions = VIDEO_EXTENSIONS
            for f in files:
                f_path = current_path / f
                if f_path.is_file() and f_path.suffix.lower() in extensions:

                    video_files.append(f_path)

            if not video_files:
                continue

            # 计算相对路径并创建目标目录
            try:
                relative_path = current_path.relative_to(root_path)
            except ValueError:
                relative_path = Path(current_path.name)

            target_output_dir = output_root / relative_path

            # 处理该目录下的每个视频
            for v_path in video_files:
                tasks_found += 1

                # 构造输出文件名: OriginalName_Resolution_Mode.mp4
                mode_suffix = "_GPU" if use_gpu else "_CPU"
                resolution_suffix = f"_{resolution_enum.value}"
                if not use_suffix:
                    mode_suffix = ""
                    resolution_suffix = ""
                output_filename = f"{v_path.stem}{resolution_suffix}{mode_suffix}.mp4"
                final_output_path = target_output_dir / output_filename

                video_processor.process_video(
                    input_path=v_path,
                    output_path=final_output_path,
                    use_gpu=use_gpu,
                    resolution=resolution_enum,
                    delete_source=delete_source,
                )

    if tasks_found == 0:
        print("No video folders found to process.")
    else:
        print(f"\n🎉 All Batch Tasks Completed.")


if __name__ == "__main__":
    from media_processor.constant.constant import INPUT_DIR, OUTPUT_DIR

    run([INPUT_DIR], OUTPUT_DIR)
