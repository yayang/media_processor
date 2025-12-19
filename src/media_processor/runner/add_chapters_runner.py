import os
from pathlib import Path

from media_processor.constant.constant import OUTPUT_DIR

from media_processor.service.media_process import chapter_processor

# --- ⚙️ 任务配置区域 (TaskList) ---

# 这里配置具体的视频和章节
# 格式: { "file": "路径", "chapters": [ ("时间", "标题"), ... ] }
# 格式: { "file": "路径", "chapters": [ ("时间", "标题"), ... ] }
TASKS = []


# --------------------


def run(tasks, output_dir=None):
    """Executes the chapter injection task.

    Args:
        tasks (list): List of task dictionaries.
        output_dir (str, optional): Output directory. If None, saves next to source.
    """
    print(f"=== Starting Chapter Injection ===")
    if output_dir:
        output_root = Path(output_dir)
        output_root.mkdir(parents=True, exist_ok=True)
        print(f"Output Dir: {output_dir}\n")
    else:
        output_root = None
        print(f"Output Dir: [Same as Source]\n")

    for task in tasks:
        source_path = Path(task["file"])
        chapters_data = task["chapters"]

        if not source_path.exists():
            print(f"⚠️  Source file not found: {source_path}")
            continue

        # 自动生成输出文件名 (原文件名_chapters.mp4)
        output_filename = f"{source_path.stem}_chapters{source_path.suffix}"
        if output_root:
            output_path = output_root / output_filename
        else:
            output_path = source_path.parent / output_filename

        # 调用处理器
        chapter_processor.inject_chapters(
            video_path=source_path, output_path=output_path, chapters=chapters_data
        )

    print("\n🎉 All Tasks Completed.")


if __name__ == "__main__":
    from media_processor.constant.constant import OUTPUT_DIR

    run([], OUTPUT_DIR)
