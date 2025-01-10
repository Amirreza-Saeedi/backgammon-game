@echo off
rem Navigate to the directory containing the Python scripts
cd /d "%~dp0"

rem Run each Python file in separate command windows
start "Server" cmd /k python server.py
start "R3" cmd /k python r3.py
start "R2" cmd /k python r2.py
start "R1" cmd /k python r1.py

@REM rem Optional: Pause the batch script if needed
@REM pause
