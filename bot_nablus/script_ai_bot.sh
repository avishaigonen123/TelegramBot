#!/bin/bash

BOT_DIR="$(dirname "$0")"
PYTHONPATH="$BOT_DIR" python3 /home/gmxceisz/TelegramBot/ai_summerize_bot/bot.py $1
