import os
from pathlib import Path

from service.media_process import video_processor

# 引入刚才写好的 processor 模块

# --- ⚙️ 批量任务配置 ---

# 待扫描的根目录列表
INPUT_DIRS = [
    # "../resources"
]

# 所有生成的结果都放在这里
OUTPUT_DIR = "../output/Videos"
# True=极速(Apple 硬件加速 GPU, VideoToolbox), False=高压缩(CPU)
# 经测试, 350M 9分钟的视频文件, GPU 压缩后138M, 耗时45秒 适合快速处理, CPU 压缩后102M, 耗时70s, 适合归档
# 通常完成 1小时 的视频, 需要6分钟以上
USE_GPU = False


# --------------------
def is_video_folder(folder_path):
    """判断文件夹里是否包含视频文件"""
    extensions = {".mp4", ".mov", ".mkv", ".flv", ".avi", ".ts"}
    try:
        for item in folder_path.iterdir():
            if item.is_file() and item.suffix.lower() in extensions:
                return True
    except PermissionError:
        pass
    return False


def main():
    print(f"=== Starting Batch Processing ===")
    print(f"Mode: {'GPU' if USE_GPU else 'CPU'}")
    print(f"Output Root: {OUTPUT_DIR}\n")

    output_root = Path(OUTPUT_DIR)
    tasks_found = 0

    for root_dir in INPUT_DIRS:
        root_path = Path(root_dir).resolve()
        if not root_path.exists():
            print(f"⚠️  Directory not found: {root_dir}")
            continue

        # os.walk 递归遍历所有子目录
        for current_root, dirs, files in os.walk(root_path):
            current_path = Path(current_root)

            # 检查当前文件夹是否包含视频 (即：它是一个任务节点)
            if is_video_folder(current_path):
                print(current_path)
                # 排除输出目录本身，防止死循环 (如果输出目录在输入目录内部)
                if output_root in current_path.parents or current_path == output_root:
                    continue

                tasks_found += 1

                # --- 调用核心处理函数 ---
                video_processor.process_folder(
                    input_dir=current_path,
                    output_root=output_root,
                    use_gpu=USE_GPU
                )

    if tasks_found == 0:
        print("No video folders found to process.")
    else:
        print(f"\n🎉 All Batch Tasks Completed.")


if __name__ == "__main__":
    main()