#!/bin/bash

# Go to the directory this script is in
BASE_DIR="/home/$(whoami)/TelegramBot/bots/$0"

# Set PYTHONPATH to this directory (for config.py)
echo "Setting PYTHONPATH to $(pwd)"
PYTHONPATH="$(pwd)" python3 /home/gmxceisz/TelegramBot/ai_summerize_bot/bot.py
