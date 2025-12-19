import os
import subprocess
import math
from pathlib import Path
from media_processor.constant.extensions import VIDEO_EXTENSIONS
from media_processor.constant.constant import AUDIO_SAMPLE_RATE


# --- 工具函数 ---


def run_ffmpeg(cmd):
    try:
        # -loglevel error: 保持清爽
        full_cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + cmd
        subprocess.run(full_cmd, check=True)
    except subprocess.CalledProcessError:
        print(f"❌ Error executing FFmpeg.")
        # 这里不抛出异常，让主流程尝试处理下一个
        pass


def extract_audio_to_wav(video_path, temp_audio_path):
    """Extracts audio from video to WAV format (PCM).

    Args:
        video_path (Path): Path to the input video file.
        temp_audio_path (Path): Path to the output temporary WAV file.
    """
    cmd = [
        "-i",
        str(video_path),
        "-vn",
        "-ac",
        "2",
        "-ar",
        AUDIO_SAMPLE_RATE,
        "-c:a",
        "pcm_s16le",
        str(temp_audio_path),
    ]
    # print(f"  🎵 Extracting: {video_path.name}")
    run_ffmpeg(cmd)


def merge_wavs_to_mp3(audio_files, output_path):
    """Merges multiple WAV files and converts them to MP3.

    Args:
        audio_files (list[Path]): List of WAV file paths.
        output_path (Path): Path to the output MP3 file.
    """
    list_filename = output_path.parent / "temp_concat_list.txt"

    with open(list_filename, "w", encoding="utf-8") as f:
        for audio in audio_files:
            safe_path = str(audio.resolve()).replace("'", "'\\''")
            f.write(f"file '{safe_path}'\n")

    cmd = [
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_filename),
        "-c:a",
        "libmp3lame",
        "-q:a",
        "2",
        str(output_path),
    ]
    print(f"  🔗 Merging -> {output_path.name}")
    run_ffmpeg(cmd)

    if list_filename.exists():
        os.remove(list_filename)


# --- 核心入口 ---


def process_folder(input_dir, output_root, batch_size=0):
    """Processes all videos in the folder, extracting and merging audio.

    Args:
        input_dir (Path): Source directory containing videos.
        output_root (Path): Output root directory.
        batch_size (int): Number of videos per merged audio file. 0 for all-in-one.
    """
    root = Path(input_dir).resolve()

    # 为了防止不同文件夹的文件名冲突（比如都有 001.mp4），
    # 我们在输出目录下创建一个同名子目录来存放结果
    # 结果路径: ./Output/源文件夹名/001.mp3
    target_dir = Path(output_root).resolve() / root.name
    target_dir.mkdir(parents=True, exist_ok=True)

    extensions = VIDEO_EXTENSIONS
    videos = [p for p in root.iterdir() if p.suffix.lower() in extensions]
    videos.sort()

    if not videos:
        # print(f"No videos in {root.name}")
        return

    print(f"\n🎧 Processing: {root.name} ({len(videos)} files)")

    # 临时存放 WAV 的目录 (放在目标目录下)
    temp_dir = target_dir / "temp_wav_extracted"
    temp_dir.mkdir(parents=True, exist_ok=True)

    temp_audios = []

    # --- 阶段 1: 抽取 WAV ---
    print("  ...Extracting WAVs...")
    for v in videos:
        audio_name = v.stem + ".wav"
        temp_audio = temp_dir / audio_name

        if not temp_audio.exists():
            extract_audio_to_wav(v, temp_audio)
        temp_audios.append(temp_audio)

    # --- 阶段 2: 合并 MP3 ---
    # 如果 BATCH_SIZE 为 0，则设为总长度（全量合并）
    current_batch_size = (
        batch_size if batch_size and batch_size > 0 else len(temp_audios)
    )
    num_batches = math.ceil(len(temp_audios) / current_batch_size)

    for i in range(num_batches):
        start_idx = i * current_batch_size
        end_idx = start_idx + current_batch_size
        batch = temp_audios[start_idx:end_idx]

        # 命名规则: 使用该组第一个文件的文件名
        first_file_name = batch[0].stem
        output_name = f"{first_file_name}.mp3"

        final_mp3_path = target_dir / output_name

        # 避免重复合并
        if final_mp3_path.exists():
            print(f"  ⏭️  Skipping existing: {output_name}")
        else:
            merge_wavs_to_mp3(batch, final_mp3_path)

    # --- 清理 ---
    print("  🧹 Cleaning temp files...")
    for t in temp_audios:
        try:
            os.remove(t)
        except:
            pass
    try:
        temp_dir.rmdir()
    except:
        pass

    print(f"  ✅ Done: {target_dir}")
