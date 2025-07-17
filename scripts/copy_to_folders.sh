#!/bin/bash

# Path to the original script.sh file
source_file=$1

if [[ -z "$source_file" ]]; then
    echo "Usage: $0 <path_to_script.sh>"
    exit 1
fi

# Check if the source file exists
if [[ ! -f "$source_file" ]]; then
    echo "$source_file not exists"
    exit 1
fi

BASE_DIR="/home/$(whoami)/TelegramBot/bots"

# Find all non-hidden directories matching the pattern bot_*
for dir in "$BASE_DIR"/bot_*/; do
  # Check if the directory name does not start with a dot (hidden directory)
  if [[ ! "$dir" =~ /[.]/ ]]; then
    # Force copy (overwrite) the script.sh file if it exists
    cp -f "$source_file" "$dir"
    echo "Copied $source_file to $dir"
  fi
done
