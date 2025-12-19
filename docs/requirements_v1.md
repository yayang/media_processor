# Functional Requirements v1.0

## 1. Overview
The Media Processor is a suite of tools designed to automate common video and audio processing tasks using FFmpeg. It focuses on batch processing, GPU acceleration, and ease of use via a unified CLI and JSON configuration.

## 2. Core Functional Modules

### 2.1 Audio Extraction (`audio`)
- **Input**: Directory containing video files.
- **Output**: 
    - Extracted audio in MP3 format.
    - Option to merge all audios into a single file or group by batch size.
- **Process**:
    1. Extract PCM WAV from video.
    2. Merge WAV files.
    3. Transcode to MP3 (128aa).

### 2.2 Video Transcoding (`convert`)
- **Input**: Directory containing video files.
- **Output**: Transcoded video files (H.264).
- **Features**:
    - **Resolution Control**: 720p, 1080p.
    - **Hardware Acceleration**: Support for Apple VideoToolbox (GPU) or CPU (libx264).
    - **Structure Preservation**: Maintains subdirectory structure in output.

### 2.3 Timelapse Creation (`timelapse`)
- **Input**: Directory containing dashcam or vlog footage.
- **Output**: Accelerated video files.
- **Features**:
    - **Speed Control**: Configurable speed ratio (e.g., 20x).
    - **Audio**: Audio is removed (standard for timelapse).
    - **Duplicate Prevention**: Skips already processed files.

### 2.4 Chapter Injection (`chapter`)
- **Input**: Specific video files and a list of chapters (Timecode + Title).
- **Output**: Video file with embedded chapter markers.
- **Format**: Supports Apple QuickTime/MP4 chaptes.

### 2.5 Video Merge (`merge`)
- **Input**: Directory containing video segments (e.g., Dashcam clips).
- **Output**: Single merged video file per input directory.
- **Process**: Uses FFmpeg Concat Demuxer (Stream Copy) for lossless and fast merging.

## 3. Interface Requirements

### 3.1 Configuration
- **JSON-based**: All complex parameters (paths, lists) must be provided via a `params/params.json` file.
- **Security**: The active configuration file `params.json` is git-ignored to prevent leaking local paths.

### 3.2 CLI
- **Single Entry Point**: `python main.py` or `make run`.
- **Auto-Detection**: The tool automatically detects the task type (`task` field) from the JSON config.
