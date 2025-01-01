@echo off
echo [101;93m Caution: This will delete all test outputs and checkpoints! [0m
echo.
echo This will:
echo [94m1. Clear all files from the output directory[0m
echo [94m2. Remove all checkpoints[0m
echo [94m3. Remove any temporary files[0m
echo [94m4. Reset the environment to initial state[0m
echo.

:PROMPT
set /P CONFIRM=Are you sure you want to continue? (Y/N): 
if /I "%CONFIRM%" NEQ "Y" goto END

echo.
echo [93mCleaning up test environment...[0m

REM Clear output directory
if exist "output\*" (
    echo [96mClearing output directory...[0m
    del /F /Q "output\*" 2>nul
    if errorlevel 1 (
        echo [91mError clearing output directory![0m
    ) else (
        echo [92mOutput directory cleared.[0m
    )
)

REM Clear checkpoints
if exist "output\checkpoints\*" (
    echo [96mClearing checkpoints...[0m
    del /F /Q "output\checkpoints\*" 2>nul
    if errorlevel 1 (
        echo [91mError clearing checkpoints![0m
    ) else (
        echo [92mCheckpoints cleared.[0m
    )
)

REM Clear any Python cache files
if exist "src\__pycache__" (
    echo [96mClearing Python cache...[0m
    rmdir /S /Q "src\__pycache__" 2>nul
)
if exist "src\parsers\__pycache__" (
    rmdir /S /Q "src\parsers\__pycache__" 2>nul
)
if exist "src\threader\__pycache__" (
    rmdir /S /Q "src\threader\__pycache__" 2>nul
)
if exist "src\analyzers\__pycache__" (
    rmdir /S /Q "src\analyzers\__pycache__" 2>nul
)

echo [92mCleanup complete![0m
echo.
echo [94mTest environment has been reset to initial state.[0m
goto END

:END
echo.
echo Press any key to exit...
pause >nul