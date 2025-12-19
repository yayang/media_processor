import os
from pathlib import Path

from media_processor.constant.extensions import VIDEO_EXTENSIONS
from media_processor.constant.constant import DEFAULT_SPEED_RATIO
from media_processor.service.media_process import timelapse_processor


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
                # 排除已经是 Timelapse 的结果文件
                if f"_{SPEED_RATIO}x" not in item.name:
                    return True
    except PermissionError:
        pass
    return False


def run(input_dirs, output_dir, speed_ratio=DEFAULT_SPEED_RATIO, use_gpu=True):
    """Executes the timelapse batch processing task.

    Args:
        input_dirs (list[str]): List of input directories.
        output_dir (str): Output directory.
        speed_ratio (int): Speed multiplier.
        use_gpu (bool): Whether to use GPU acceleration.
    """
    print(f"=== Starting Timelapse Batch Processing ===")
    print(f"Speed: {speed_ratio}x")
    print(f"Mode:  {'GPU' if use_gpu else 'CPU'}")
    print(f"Output:{output_dir}\n")

    output_root = Path(output_dir)
    tasks_found = 0

    for root_dir in input_dirs:
        root_path = Path(root_dir).resolve()
        if not root_path.exists():
            print(f"⚠️  Directory not found: {root_dir}")
            continue

        for current_root, dirs, files in os.walk(root_path):
            current_path = Path(current_root)

            # 只有当它是包含视频的文件夹，且不是输出目录本身时才处理
            if is_video_folder(current_path):
                if output_root in current_path.parents or current_path == output_root:
                    continue

                tasks_found += 1

                timelapse_processor.process_folder(
                    input_dir=current_path,
                    output_root=output_root,
                    speed_ratio=speed_ratio,
                    use_gpu=use_gpu,
                )

    if tasks_found == 0:
        print("No video folders found.")
    else:
        print(f"\n🎉 All Timelapse Tasks Completed.")


if __name__ == "__main__":
    # For backward compatibility testing
    # Mock defaults for direct run
    CURRENT_FILE = Path(__file__).resolve()
    PROJECT_ROOT = CURRENT_FILE.parents[3]
    INPUT_DIRS = [PROJECT_ROOT / "resources/行车记录仪"]
    OUTPUT_DIR = PROJECT_ROOT / "output" / "Timelapse_Collection"
    run(INPUT_DIRS, OUTPUT_DIR, 20, True)
