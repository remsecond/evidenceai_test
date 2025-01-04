@echo off
echo Creating session prompt...
python create_session.py
if errorlevel 1 (
    echo Failed to create session prompt
    pause
    exit /b 1
)
echo Opening prompt...
for /f "delims=" %%i in ('dir /b /od SESSION_PROMPT_*.md') do set LATEST=%%i
start "" "%LATEST%"