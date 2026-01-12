#!/bin/bash
# Helper script to run the voice dictation tool with sudo on Linux

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run: python3 -m venv venv"
    exit 1
fi

# Check if start.py exists
if [ ! -f "start.py" ]; then
    echo "Error: start.py not found in current directory"
    exit 1
fi

# Run with sudo using the venv's Python interpreter
echo "Running voice dictation tool with sudo (required for global hotkeys on Linux)..."
sudo venv/bin/python start.py
