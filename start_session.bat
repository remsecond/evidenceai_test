@echo off
python src/initialize_session.py
if errorlevel 1 (
    echo Session initialization failed
    pause
    exit /b 1
)