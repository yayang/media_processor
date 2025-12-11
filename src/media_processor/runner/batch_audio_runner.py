import os
from pathlib import Path

from media_processor.constant.constant import INPUT_DIR, OUTPUT_DIR
from media_processor.service.audio_abstracter import audio_processor

# --- ⚙️ 批量任务配置 ---
INPUT_DIRS = [
    INPUT_DIR,
]


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
                    output_root=target_output_dir, # 注意：process_folder 内部可能还是把这个当作 root，需要确认 process_folder 内部是否会再拼目录。
                    # 查看 audio_processor 接口，如果 input_dir 是 A, output_root 是 B, 它生成的并在 B 下面吗？
                    # 假设 process_folder 主要是输出到 output_root。
                    # 如果原逻辑是 output_root=audios,  current_path=subset, 它会直接丢在 audios 里吗？
                    # 原逻辑: process_folder(current_path, output_root=OUTPUT_DIR...)
                    # 应该 audio_processor 内部会把文件输出到 output_root.
                    # 现在我们希望输出到 output_root/sub/path.
                    # 所以传入 target_output_dir 是对的。
                    batch_size=BATCH_SIZE
                )

    if tasks_found == 0:
        print("No video folders found.")
    else:
        print(f"\n🎉 All Audio Tasks Completed.")


if __name__ == "__main__":
    main()