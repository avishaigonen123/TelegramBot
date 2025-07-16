#!/bin/bash

# Path to the original script_ai_bot.sh file
source_file="script_ai_bot.sh"

# Find all non-hidden directories matching the pattern bot_*
for dir in bot_*/; do
  # Check if the directory name does not start with a dot (hidden directory)
  if [[ ! "$dir" =~ /[.]/ ]]; then
    # Force copy (overwrite) the script_ai_bot.sh file if it exists
    cp -f "$source_file" "$dir"
    echo "Copied script_ai_bot.sh to $dir"
  fi
done
