#!/bin/bash

# Go to the directory this script is in
cd "$(dirname "$0")"

# Set PYTHONPATH to this directory (for config.py)
PYTHONPATH="." python3 /home/gmxceisz/TelegramBot/ai_summerize_bot/bot.py
