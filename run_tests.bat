@echo off
echo [95m==================================[0m
echo [95m   EvidenceAI Pipeline Tests      [0m
echo [95m==================================[0m
echo.

REM Check if Python is installed
python --version 2>NUL
if errorlevel 1 (
    echo [91mError: Python is not installed or not in PATH![0m
    echo [93mPlease install Python and try again.[0m
    pause
    exit /b 1
)

REM Check for input PDF
if not exist "input\*.pdf" (
    echo [91mError: No PDF files found in input directory![0m
    echo [93mPlease place an OFW PDF file in the input directory and try again.[0m
    echo.
    echo [94mExpected location:[0m
    echo %~dp0input\
    pause
    exit /b 1
)

REM Show test configuration
echo [96mTest Configuration:[0m
echo [96m------------------[0m
echo [97mInput Directory:[0m %~dp0input
echo [97mOutput Directory:[0m %~dp0output
echo.

REM Run tests
echo [95mRunning tests...[0m
echo [90m-----------------[0m
python src/test_pipeline.py

REM Check if test succeeded
if errorlevel 1 (
    echo.
    echo [91m❌ Test run failed! Check the error messages above.[0m
) else (
    echo.
    echo [92m✓ Test run completed successfully![0m
)

echo.
echo [94mTest Results:[0m
echo [94m-------------[0m
if exist "output\test_results_*.json" (
    echo [92m✓ Results saved to output directory[0m
    dir /B "output\test_results_*.json"
) else (
    echo [91m❌ No result files generated[0m
)

echo.
echo [93mPress any key to exit...[0m
pause >nul