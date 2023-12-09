@echo off
set "process_name=forward-translate-bot.exe"

tasklist /FI "IMAGENAME eq %process_name%" 2>NUL | findstr /I /C:"%process_name%" >NUL

if errorlevel 1 (
    echo No existing instance found. Starting a new process.
    cd /d C:\Users\avish\git\TelegramBot\output\forward-translate-bot
    start /B C:\Users\avish\git\TelegramBot\output\forward-translate-bot\forward-translate-bot.exe
) else (
    echo An instance is already running. No new process started.
)
