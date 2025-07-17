#!/bin/bash

# Get the directory where the script itself is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$SCRIPT_DIR/bot.py"

# Check if bot.py exists in the same folder
if [[ -f "$SCRIPT" ]]; then
    echo "Running $SCRIPT..."
    cd "$SCRIPT_DIR" || {
        echo "Failed to change directory to $SCRIPT_DIR"
        exit 1
    }
    python3 "$SCRIPT"
else
    echo "Error: bot.py not found in $SCRIPT_DIR"
    exit 1
fi
