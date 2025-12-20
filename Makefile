.PHONY: install test run clean help

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies using uv"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Remove build artifacts and temp files"
	@echo ""
	@echo "Run Tasks:"
	@echo "  make run                            - Run with default params/params.json"
	@echo "  make run config=params/my_task.json - Run with specific config file"
	@echo ""
	@echo "Examples:"
	@echo "  1. Audio Extraction:"
	@echo "     cp params/examples/audio.json params/audio.json"
	@echo "     # Edit params/audio.json..."
	@echo "     make run config=params/audio.json"
	@echo ""
	@echo "  2. Video Conversion:"
	@echo "     cp params/examples/convert.json params/convert.json"
	@echo "     # Edit params/convert.json..."
	@echo "     make run config=params/convert.json"
	@echo ""
	@echo "  3. Timelapse:"
	@echo "     cp params/examples/timelapse.json params/timelapse.json"
	@echo "     # Edit params/timelapse.json..."
	@echo "     make run config=params/timelapse.json"

install:
	@echo "Creating virtual environment and installing dependencies..."
	uv venv --allow-existing --python 3.12
	uv sync

test:
	PYTHONPATH=src uv run pytest

# Support `make run config=path/to/file.json`
# If config is not defined, default to params/params.json
config ?= params/params.json
run:
	PYTHONPATH=src uv run main.py run --config $(config)

clean:
	@echo "🧹 Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*_processing.*" -delete
	@find . -type f -name ".DS_Store" -delete
	@echo "✨ Done!"
