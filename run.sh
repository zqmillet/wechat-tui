#!/bin/bash
# Quick start script for WeChat TUI

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Check if dependencies are installed
if ! python -c "import textual" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -e .
fi

# Run the application
echo "Starting WeChat TUI..."
python -m wechat_tui.main