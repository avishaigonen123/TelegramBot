@echo off
set "process_name=forward-translate-bot.exe"

tasklist /FI "IMAGENAME eq %process_name%" 2>NUL | findstr /I /C:"%process_name%" >NUL

if errorlevel 1 (
    echo No instance of %process_name% is currently running.
) else (
    echo Terminating the %process_name% process.
    taskkill /F /IM %process_name%
    echo %process_name% terminated successfully.
)
