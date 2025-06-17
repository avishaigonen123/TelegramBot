#!/bin/bash

# Path to the original bot.py file
source_file="bot.py"

# Find all non-hidden directories matching the pattern bot_*
for dir in bot_*/; do
  # Check if the directory name does not start with a dot (hidden directory)
  if [[ ! "$dir" =~ /[.]/ ]]; then
    # Force copy (overwrite) the bot.py file if it exists
    cp -f "$source_file" "$dir"
    echo "Copied bot.py to $dir"
  fi
done
