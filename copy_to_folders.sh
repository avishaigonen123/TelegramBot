#!/bin/bash

# Path to the original script_ai_bot.sh file
source_file=$1

if [[ -z "$source_file" ]]; then
    echo "Usage: $0 <path_to_script_ai_bot.sh>"
    exit 1
fi

# Check if the source file exists
if [[ ! -f "$source_file" ]]; then
    echo "$source_file not exists"
    exit 1
fi

# Find all non-hidden directories matching the pattern bot_*
for dir in bot_*/; do
  # Check if the directory name does not start with a dot (hidden directory)
  if [[ ! "$dir" =~ /[.]/ ]]; then
    # Force copy (overwrite) the script_ai_bot.sh file if it exists
    cp -f "$source_file" "$dir"
    echo "Copied $source_file to $dir"
  fi
done
