@echo off
set PYTHONIOENCODING=utf-8
REM Paper Surfer Background Runner for Windows Task Scheduler
REM This batch file runs Paper Surfer in the background
REM Scheduled to run every Saturday at 2:00 AM

cd /d "%~dp0"

REM Set window to minimized
if not DEFINED IS_MINIMIZED set IS_MINIMIZED=1 && start "" /min "%~dpnx0" %* && exit

REM Log the start time
echo [%date% %time%] Starting Paper Surfer background runner... >> logs\scheduler.log

REM Run Paper Surfer once
python main.py --once >> logs\scheduler.log 2>&1

REM Log the end time
echo [%date% %time%] Paper Surfer background runner finished >> logs\scheduler.log

REM Optional: Clean old log files (keep last 30 days)
forfiles /p logs /s /m *.log /d -30 /c "cmd /c del @path" 2>nul

exit 