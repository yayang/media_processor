# User Manual

## 🚀 Quick Start

### 1. Setup Environment
```bash
make install
```

### 2. Configure Your Task
The tool uses a JSON configuration file to manage parameters. We provide examples for different tasks in the `params/` directory.

1.  **Choose a template**:
    - `params/audio.example.json`: Extract/Merge Audio.
    - `params/convert.example.json`: Compress/Convert Videos.
    - `params/timelapse.example.json`: Create Timelapse.
    - `params/chapter.example.json`: Add Chapters to Video.
    - `params/merge.json`: Merge Videos.

2.  **Create your config**:
    Copy the example to `params/params.json` (this file is ignored by git).
    ```bash
    cp params/convert.example.json params/params.json
    ```

3.  **Edit parameters**:
    Open `params/params.json` and update the paths:
    ```json
    {
        "task": "convert",
        "input_dirs": ["/Users/me/Movies/RawFootage"],
        "output_dir": "/Users/me/Movies/Output",
        "use_gpu": true
    }
    ```

### 3. Run
Execute the tool. It will automatically read `params/params.json` and start the appropriate task.

```bash
make run
# OR
python main.py run
```

## 📚 Configuration Reference

### Common Fields
- `task`: Task type (`audio`, `convert`, `timelapse`, `chapter`, `merge`).
- `output_dir`: Where to save the results.

### Task: `convert`
- `input_dirs`: List of folders to scan.
- `use_gpu`: `true` (fast, larger size) or `false` (slower, better compression).
- `resolution`: `720p` or `1080p`.
- `delete_source`: `true` to delete original files after success (Use with caution!).

### Task: `audio`
- `batch_size`: Number of videos to merge into one MP3. `0` means merge all into one file.

### Task: `timelapse`
- `input_dirs`: List of **Folders** containing video clips. The tool will recursively find all subfolders with videos.
- `speed_ratio`: Acceleration factor (e.g., `20` = 20x speed).

### Task: `chapter`
- `tasks`: List of video tasks.

### Task: `merge`
- No extra params. Simply merges files per folder.

## 📖 Cookbook (Examples)

### 1. Audio Extraction
**Goal**: Combine many short video clips into a single MP3 audio file.

1.  Create config: `cp params/examples/audio.json params/audio.json`
2.  Edit `params/audio.json`:
    ```json
    {
        "task": "audio",
        "input_dirs": ["/path/to/your/input/videos"],
        "output_dir": "/path/to/your/output/audio",
        "batch_size": 0
    }
    ```
    > **Note on `batch_size`**:
    > - `0` (Default): Merge ALL extracted audios from the folder into **one single MP3**.
    > - `5`: Group every 5 videos into one MP3 (e.g., `part1.mp3`, `part2.mp3`...).
3.  Run:
    ```bash
    make run config=params/audio.json
    ```

### 2. Video Conversion (Batch Compression)
**Goal**: Compress all videos in a folder to 1080p to save space.

1.  Create config: `cp params/examples/convert.json params/convert.json`
2.  Edit `params/convert.json`:
    ```json
    {
        "task": "convert",
        "input_dirs": ["/path/to/your/input/videos"],
        "output_dir": "/path/to/your/output/videos",
        "use_gpu": false,
        "resolution": "1080p",
        "delete_source": false
    }
    ```
3.  Run:
    ```bash
    make run config=params/convert.json
    ```

### 3. Add Chapters
**Goal**: Add chapter markers to a finished video.

1.  Create config: `cp params/examples/chapter.json params/chapters.json`
2.  Edit `params/chapters.json`:
    ```json
    {
        "task": "chapter",
        "tasks": [
            {
                "file": "/path/to/your/video.mp4",
                "chapters": [
                    ["00:00", "Start"],
                    ["02:15", "Middle"],
                    ["05:00", "End"]
                ]
            }
        ],
        ],
        "_comment_output": "output_dir is optional. If removed, saves as video_chapters.mp4 next to source."
    }
    ```
3.  Run:
    ```bash
    make run config=params/chapters.json
    ```

### 4. Timelapse Creation
**Goal**: Create high-speed timelapse videos from dashcam footage (process each file individually).

1.  Create config: `cp params/examples/timelapse.json params/timelapse.json`
2.  Edit `params/timelapse.json`:
    ```json
    {
        "task": "timelapse",
        "input_dirs": ["/path/to/your/dashcam/footage"],
        "_comment_input": "Must be FOLDERS, not files. It will process all videos inside recursively.",
        "output_dir": "/path/to/your/output/timelapse",
        "speed_ratio": 20,
        "use_gpu": true
    }
    ```
3.  Run:
    ```bash
    make run config=params/timelapse.json
    ```

### 5. Video Merge
**Goal**: Merge all video clips in a folder into a single file (like joining dashcam 1-minute clips into one full trip video).

1.  Create config: `cp params/examples/merge.json params/merge.json`
2.  Edit `params/merge.json`:
    ```json
    {
        "task": "merge",
        "input_dirs": ["/path/to/dashcam/trip_folder"],
        "output_dir": "/path/to/output/merged"
    }
    ```
3.  Run:
    ```bash
    make run config=params/merge.json
    ```
