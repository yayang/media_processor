import os
from pathlib import Path

from service.audio_abstracter import audio_processor

# 引入刚才写的处理器

# --- ⚙️ 批量任务配置 ---
INPUT_DIRS = [
    "../resources",
]

OUTPUT_DIR = "../output/audios"

# 每多少个视频合并成一个音频文件 (0 = 该文件夹内所有视频合并成一个长音频)
BATCH_SIZE = 0


# --------------------

def is_video_folder(folder_path):
    """判断是否包含视频文件"""
    extensions = {".mp4", ".mov", ".mkv", ".flv", ".avi", ".ts"}
    try:
        for item in folder_path.iterdir():
            if item.is_file() and item.suffix.lower() in extensions:
                return True
    except PermissionError:
        pass
    return False


def main():
    print(f"=== Starting Audio Extraction Batch ===")
    print(f"Output Root: {OUTPUT_DIR}")
    print(f"Batch Size:  {'All in one' if BATCH_SIZE == 0 else BATCH_SIZE}")

    output_root = Path(OUTPUT_DIR)
    tasks_found = 0

    for root_dir in INPUT_DIRS:
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

                # 调用核心处理函数
                audio_processor.process_folder(
                    input_dir=current_path,
                    output_root=output_root,
                    batch_size=BATCH_SIZE
                )

    if tasks_found == 0:
        print("No video folders found.")
    else:
        print(f"\n🎉 All Audio Tasks Completed.")


if __name__ == "__main__":
    main()