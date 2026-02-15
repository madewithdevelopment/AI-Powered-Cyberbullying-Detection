@echo off
echo Starting CyberShield AI...
echo using Python from .venv

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" bully_detector.py
) else (
    echo [ERROR] Virtual environment not found!
    echo Please ensure the .venv folder exists.
    pause
    exit /b 1
)

pause
