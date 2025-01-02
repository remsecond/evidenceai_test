@echo off
setlocal enabledelayedexpansion

:menu
cls
echo EvidenceAI Development Tools
echo =========================
echo 1. Start New Session
echo 2. Run Pipeline Test
echo 3. Test Specific Component
echo 4. Check Status
echo 5. View Logs
echo 6. Exit
echo.

set /p choice="Select option (1-6): "

if "%choice%"=="1" (
    echo Creating new session...
    python src/create_session.py
    for /f "delims=" %%i in ('dir /b /o:d SESSION_PROMPT_*.md') do set LATEST=%%i
    if defined LATEST (
        notepad !LATEST!
    )
    goto menu
)
if "%choice%"=="2" (
    echo Running pipeline test...
    python src/test_pipeline.py
    pause
    goto menu
)
if "%choice%"=="3" (
    echo Select component:
    echo 1. Parser
    echo 2. Threader
    echo 3. Validator
    set /p comp="Select component (1-3): "
    if "!comp!"=="1" python src/test_component.py parser
    if "!comp!"=="2" python src/test_component.py threader
    if "!comp!"=="3" python src/test_component.py validator
    pause
    goto menu
)
if "%choice%"=="4" (
    echo Checking status...
    python src/report_checkpoints.py
    pause
    goto menu
)
if "%choice%"=="5" (
    echo Viewing logs...
    if exist "output\logs\pipeline.log" (
        notepad output\logs\pipeline.log
    ) else (
        echo No logs found
        pause
    )
    goto menu
)
if "%choice%"=="6" (
    exit /b
)

echo Invalid option
pause
goto menu