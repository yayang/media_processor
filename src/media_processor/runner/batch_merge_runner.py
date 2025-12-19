import os
from pathlib import Path
from media_processor.constant.extensions import VIDEO_EXTENSIONS
from media_processor.service.media_process import merge_processor


def is_video_folder(folder_path):
    """Checks if the folder contains video files."""
    extensions = VIDEO_EXTENSIONS
    try:
        for item in folder_path.iterdir():
            if (
                item.is_file()
                and item.suffix.lower() in extensions
                and not item.name.startswith(".")
            ):
                return True
    except PermissionError:
        pass
    return False


def run(input_dirs, output_dir):
    """Executes the batch video merge task.

    Args:
        input_dirs (list[str]): List of input directories.
        output_dir (str): Output directory.
    """
    print(f"=== Starting Batch Video Merge ===")
    print(f"Output: {output_dir}\n")

    output_root = Path(output_dir)
    tasks_found = 0

    for root_dir in input_dirs:
        root_path = Path(root_dir).resolve()
        if not root_path.exists():
            print(f"⚠️  Directory not found: {root_dir}")
            continue

        # Recursively walk directories
        for current_root, dirs, files in os.walk(root_path):
            current_path = Path(current_root)

            # Check if this folder has videos
            if is_video_folder(current_path):
                # Avoid processing the output directory itself if it's nested
                if output_root in current_path.parents or current_path == output_root:
                    continue

                tasks_found += 1

                # Determine relative path for mirroring structure if needed,
                # but merge_processor.process_folder creates a folder named after the leaf folder.
                # Let's delegate simply.

                merge_processor.process_folder(
                    input_dir=current_path, output_root=output_root
                )

    if tasks_found == 0:
        print("No video folders found.")
    else:
        print(f"\n🎉 All Merge Tasks Completed.")


if __name__ == "__main__":
    # Test stub
    pass
