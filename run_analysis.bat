@echo off
echo ========================================
echo EvidenceAI Report Generator
echo ========================================
echo.

rem Ensure Python environment is active
call python generate_reports.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo Report generation completed successfully!
) else (
    echo Report generation failed - check error messages above.
)

echo.
pause