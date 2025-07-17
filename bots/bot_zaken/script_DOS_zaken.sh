#!/bin/bash

# Get the directory where the script itself is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$SCRIPT_DIR/DOS_zaken.py"

# Check if DOS_zaken.py exists in the same folder
if [[ -f "$SCRIPT" ]]; then
    echo "Running $SCRIPT..."
    cd "$SCRIPT_DIR" || {
        echo "Failed to change directory to $SCRIPT_DIR"
        exit 1
    }
    python3 "$SCRIPT"
else
    echo "Error: DOS_zaken.py not found in $SCRIPT_DIR"
    exit 1
fi
