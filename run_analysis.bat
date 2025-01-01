@echo off
title EvidenceAI Analysis Pipeline
cls

echo Starting EvidenceAI Analysis...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Run the analysis
powershell -NoProfile -ExecutionPolicy Bypass -Command "python src/run_analysis.py"

REM Check for errors
if errorlevel 1 (
    echo.
    echo Error occurred during analysis
    echo Check the output above for details
) else (
    echo.
    echo Analysis completed successfully
)

echo.
echo Press any key to exit...
pause >nul