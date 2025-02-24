@echo off
set "script_name=forward-translate-bot.py"
set "current_path=%CD%"

cd "%CD%\sessions"

"C:\Program Files\Python312\python.exe" "%CD%\%script_name%"
