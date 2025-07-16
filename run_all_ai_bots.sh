#!/bin/bash

cd "$(dirname "$0")"
mkdir -p logs

# List of bots to run
BOT_FOLDERS=(
    bot_nablus
    bot_suria
    bot_tubas
    bot_kalkilia
    bot_palastine
    bot_jenin
    bot_iran
    bot_iranFactChecker
    bot_osintNAYA
    bot_salfit
)

# Run each bot's script
for bot in "${BOT_FOLDERS[@]}"; do
    SCRIPT="./$bot/script_ai_bot.sh"
    if [[ -x "$SCRIPT" ]]; then
        echo "Running $bot..."
        bash "$SCRIPT" >> logs/${bot}.log 2>&1 &
    else
        echo "No script_ai_bot.sh found in $bot"
    fi
    sleep 10 # Sleep for 10 seconds before starting the next bot
done
