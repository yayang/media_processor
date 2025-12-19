import os
from pathlib import Path

from media_processor.constant.constant import INPUT_DIR, OUTPUT_DIR
from media_processor.constant.constant import INPUT_DIR, OUTPUT_DIR
from media_processor.constant.extensions import VIDEO_EXTENSIONS
from media_processor.service.audio_abstracter import audio_processor


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


def run(input_dirs, output_dir, batch_size=0):
    """Executes the batch audio extraction task.

    Args:
        input_dirs (list[str]): List of input directories.
        output_dir (str): Output directory.
        batch_size (int): Batch size for merging.
    """
    print(f"=== Starting Audio Extraction Batch ===")
    print(f"Output Root: {output_dir}")
    print(f"Batch Size:  {'All in one' if batch_size == 0 else batch_size}")

    output_root = Path(output_dir)
    tasks_found = 0

    for root_dir in input_dirs:
        root_path = Path(root_dir).resolve()
        if not root_path.exists():
            print(f"⚠️  Directory not found: {root_dir}")
            continue

        # 递归遍历
        for current_root, dirs, files in os.walk(root_path):
            current_path = Path(current_root)

            # 只有包含视频的文件夹才处理
            if is_video_folder(current_path):
                # 防止处理输出目录自己
                if output_root in current_path.parents or current_path == output_root:
                    continue

                tasks_found += 1

                # 计算相对路径
                try:
                    relative_path = current_path.relative_to(root_path)
                except ValueError:
                    # 如果不是 root_path 的子目录 (理论上不会发生，因为 walk 是从 root_path 开始的)
                    relative_path = Path(current_path.name)

                # 拼接输出路径
                target_output_dir = output_root / relative_path

                # 调用核心处理函数
                audio_processor.process_folder(
                    input_dir=current_path,
                    output_root=target_output_dir,
                    batch_size=batch_size,
                )

    if tasks_found == 0:
        print("No video folders found.")
    else:
        print(f"\n🎉 All Audio Tasks Completed.")


if __name__ == "__main__":
    # For backward compatibility testing
    from media_processor.constant.constant import INPUT_DIR, OUTPUT_DIR

    run([INPUT_DIR], OUTPUT_DIR, 0)
