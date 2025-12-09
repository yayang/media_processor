import os
from pathlib import Path

from service.media_process import timelapse_processor

# 引入核心处理器

# --- ⚙️ 批量任务配置 ---

INPUT_DIRS = [
    "../resources",  # 递归扫描
]

OUTPUT_DIR = "../output/Timelapse_Collection"

# 加速比例 (20:1 即 20倍速)
SPEED_RATIO = 20

# True=极速(GPU), False=画质(CPU)
# 延迟摄影通常计算量大，推荐用 GPU，因为加速后的画面细节丢失不明显
USE_GPU = True


# --------------------

def is_video_folder(folder_path):
    """判断文件夹里是否包含视频文件"""
    extensions = {".mp4", ".mov", ".mkv", ".flv", ".avi"}
    try:
        for item in folder_path.iterdir():
            if item.is_file() and item.suffix.lower() in extensions:
                # 排除已经是 Timelapse 的结果文件
                if f"_{SPEED_RATIO}x" not in item.name:
                    return True
    except PermissionError:
        pass
    return False


def main():
    print(f"=== Starting Timelapse Batch Processing ===")
    print(f"Speed: {SPEED_RATIO}x")
    print(f"Mode:  {'GPU' if USE_GPU else 'CPU'}")
    print(f"Output:{OUTPUT_DIR}\n")

    output_root = Path(OUTPUT_DIR)
    tasks_found = 0

    for root_dir in INPUT_DIRS:
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
                    speed_ratio=SPEED_RATIO,
                    use_gpu=USE_GPU
                )

    if tasks_found == 0:
        print("No video folders found.")
    else:
        print(f"\n🎉 All Timelapse Tasks Completed.")


if __name__ == "__main__":
    main()