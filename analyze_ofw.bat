@echo off
echo Starting EvidenceAI Session...
echo ============================

python src/session_manager.py

if errorlevel 1 (
    echo Failed to create session
    pause
    exit /b 1
)

if "%~1"=="" (
    echo Please provide a PDF filename
    echo Usage: analyze_ofw.bat filename.pdf
    pause
    exit /b 1
)

python src/run_pipeline.py %1

if errorlevel 1 (
    echo Pipeline failed. Check error messages above.
    pause
    exit /b 1
)

echo.
echo Processing complete! Check the output directory for results.
pause