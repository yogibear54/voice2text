#!/bin/bash
# Helper script to run pytest with the virtual environment

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run: python3 -m venv venv"
    exit 1
fi

# Run pytest with the venv's Python interpreter
# Pass all arguments to pytest
./venv/bin/pytest "$@"
