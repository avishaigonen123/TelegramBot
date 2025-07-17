#!/bin/bash

# List of bot directories
BOT_DIRS=(
    "bot_palastine"
    "bot_jenin"
    "bot_suria"
    "bot_tubas"
    "bot_kalkilia"
    "bot_nablus"
    "bot_iran"
    "bot_iranFactChecker"
    "bot_osintNAYA"
    "bot_salfit"
)

BASE_DIR="/home/$(whoami)/TelegramBot/bots"

# Run each bot's script_bot.sh if it exists
for bot in "${BOT_DIRS[@]}"; do
    SCRIPT="$BASE_DIR/$bot/script_bot.sh"
    if [[ -x "$SCRIPT" ]]; then
        bash "$SCRIPT" > /dev/null 2>&1 &
    fi
done

# Run special DOS bot separately (every 30 minutes)
if [[ "$(date +%M)" =~ ^(00|30)$ ]]; then
    DOS_SCRIPT="$BASE_DIR/bot_zaken/script_DOS_zaken.sh"
    if [[ -x "$DOS_SCRIPT" ]]; then
        bash "$DOS_SCRIPT" > /dev/null 2>&1 &
    fi
fi
