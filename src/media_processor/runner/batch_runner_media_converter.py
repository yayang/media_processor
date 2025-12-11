import os
from pathlib import Path

from media_processor.constant.constant import INPUT_DIR, OUTPUT_DIR
from media_processor.service.media_process import video_processor

# --- ⚙️ 批量任务配置 ---

# 待扫描的根目录列表
INPUT_DIRS = [
    INPUT_DIR
]

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

            # 排除输出目录本身
            if output_root in current_path.parents or current_path == output_root:
                continue

            # 过滤视频文件
            video_files = []
            extensions = {".mp4", ".mov", ".mkv", ".flv", ".avi", ".ts"}
            for f in files:
                f_path = current_path / f
                if f_path.is_file() and f_path.suffix.lower() in extensions:
                    # 避免处理自己生成的临时文件或输出文件 (如果输出目录重叠)
                    if "_720p_" in f: 
                        continue
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
                
                # 构造输出文件名: OriginalName_720p_GPU.mp4
                mode_suffix = "_GPU" if USE_GPU else "_CPU"
                output_filename = f"{v_path.stem}_720p{mode_suffix}.mp4"
                final_output_path = target_output_dir / output_filename
                
                video_processor.process_video(
                    input_path=v_path,
                    output_path=final_output_path,
                    use_gpu=USE_GPU
                )

    if tasks_found == 0:
        print("No video folders found to process.")
    else:
        print(f"\n🎉 All Batch Tasks Completed.")


if __name__ == "__main__":
    main()