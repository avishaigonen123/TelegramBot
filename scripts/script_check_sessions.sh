#!/bin/bash

# Start from the current directory
START_DIR="/home/$(whoami)/TelegramBot/bots"

# Loop through all non-hidden subdirectories
for dir in $(find $START_DIR -type d -not -path '*/\.*'); do
    echo "Entering directory: $dir"
    cd "$dir"

    # Check if the check_sessions.py script exists in the parent directory
    if [ -f "../check_sessions.py" ]; then
        echo "Running check_sessions.py in directory: $dir"
        python3 ../check_sessions.py
    else
        echo "check_sessions.py not found in the parent directory of $dir"
    fi

    # Return to the starting directory
    cd $START_DIR
done
