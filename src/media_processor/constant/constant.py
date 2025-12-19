from pathlib import Path

# --- Default Paths ---
# (Legacy, kept for backward compatibility if needed, but not used by main.py)
INPUT_DIR = Path("resources")
OUTPUT_DIR = Path("output")


# --- FFmpeg Settings ---

# Audio
AUDIO_BITRATE = "128k"
AUDIO_SAMPLE_RATE = "44100"
AUDIO_CODEC = "libmp3lame"

# Video Conversion
VIDEO_CRF_DEFAULT = "28"  # Balanced compression
VIDEO_PRESET_DEFAULT = "fast"  # Good speed/size balance
VIDEO_AUDIO_BITRATE = "128k"

# Timelapse
TIMELAPSE_CRF = "24"  # Higher quality for timelapse
TIMELAPSE_PRESET = "fast"
TIMELAPSE_FRAMERATE = "30"
DEFAULT_SPEED_RATIO = 20
