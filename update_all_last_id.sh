#!/bin/bash

# Save current directory
root_dir=$(pwd)

# Loop over each bot_* folder
for dir in bot_*/ ; do
    echo "📂 Entering $dir"
    cd "$dir" || continue

    # Run the update script (adjust filename if needed)
    if [ -f update_last_id.py ]; then
        python3 update_last_id.py
    else
        echo "⚠️  No update_last_id.py found in $dir"
    fi

    # Return to root directory
    cd "$root_dir"
    echo ""
done

echo "✅ Done updating all last_id.txt files."
