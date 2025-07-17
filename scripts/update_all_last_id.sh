#!/bin/bash

# Save current directory
BASE_DIR="/home/$(whoami)/TelegramBot/bots"

# Loop over each bot_* folder
for dir in "$BASE_DIR"/bot_*/ ; do
    echo "📂 Entering $dir"
    cd "$dir" || continue

    # Run the update script (adjust filename if needed)
    if [ -f update_last_id.py ]; then
        python3 update_last_id.py
    else
        echo "⚠️  No update_last_id.py found in $dir"
    fi

    # Return to root directory
    cd "$BASE_DIR" 
    echo ""
done

echo "✅ Done updating all last_id.txt files."
