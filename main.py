import json
import os
import sys
from pathlib import Path

import typer

# Runners
from media_processor.runner import (
    batch_audio_runner,
    batch_runner_media_converter,
    batch_timelapse,
    add_chapters_runner,
    batch_merge_runner,
)

app = typer.Typer(help="Media Processor CLI")


@app.callback()
def callback():
    """
    Media Processor CLI Entry Point
    """


DEFAULT_PARAMS_FILE = Path("params/params.json")


def load_params(config_path: Path):
    """Load parameters from JSON config file."""
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        if config_path == DEFAULT_PARAMS_FILE:
            print(
                f"👉 Please copy an example from params/ and rename it to params.json"
            )
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}")
        sys.exit(1)


@app.command()
def run(
    config: Path = typer.Option(
        DEFAULT_PARAMS_FILE, "--config", "-c", help="Path to JSON config file"
    )
):
    """Run task based on configuration file (default: params/params.json)."""
    params = load_params(config)
    task_type = params.get("task")
    output_dir = params.get("output_dir")

    if not task_type:
        print("❌ Missing 'task' field in params.json")
        sys.exit(1)

    if not output_dir:
        print("❌ Missing 'output_dir' field in params.json")
        sys.exit(1)

    print(f"🚀 Launching Task: {task_type.upper()}")

    if task_type == "audio":
        if not output_dir:
            print("❌ Missing 'output_dir' for audio task.")
            sys.exit(1)
        batch_audio_runner.run(
            input_dirs=params.get("input_dirs", []),
            output_dir=output_dir,
            batch_size=params.get("batch_size", 0),
        )

    elif task_type == "convert":
        if not output_dir:
            print("❌ Missing 'output_dir' for convert task.")
            sys.exit(1)
        batch_runner_media_converter.run(
            input_dirs=params.get("input_dirs", []),
            output_dir=output_dir,
            use_gpu=params.get("use_gpu", False),
            target_resolution=params.get("resolution", "1080p"),
            delete_source=params.get("delete_source", False),
            use_suffix=params.get("use_suffix", False),
        )

    elif task_type == "timelapse":
        if not output_dir:
            print("❌ Missing 'output_dir' for timelapse task.")
            sys.exit(1)
        batch_timelapse.run(
            input_dirs=params.get("input_dirs", []),
            output_dir=output_dir,
            speed_ratio=params.get("speed_ratio", 20),
            use_gpu=params.get("use_gpu", True),
        )

    elif task_type == "chapter":
        add_chapters_runner.run(tasks=params.get("tasks", []), output_dir=output_dir)

    elif task_type == "merge":
        if not output_dir:
            print("❌ Missing 'output_dir' for merge task.")
            sys.exit(1)
        batch_merge_runner.run(
            input_dirs=params.get("input_dirs", []), output_dir=output_dir
        )

    else:
        print(f"❌ Unknown task type: {task_type}")
        print("Available tasks: audio, convert, timelapse, chapter, merge")
        sys.exit(1)


if __name__ == "__main__":
    app()
