@echo off
rem Navigate to the directory containing the Python scripts
cd /d "%~dp0"

rem Run each Python file in separate command windows
start "Server" cmd /k python server.py
timeout 1
start "R3" cmd /k python r3.py
timeout 1
start "R2" cmd /k python r2.py
timeout 1
start "R1" cmd /k python r1.py
timeout 1
@REM rem Optional: Pause the batch script if needed
@REM pause
