@echo off
setlocal EnableDelayedExpansion

:MENU
cls
echo [95m================================[0m
echo [95m      EvidenceAI Pipeline       [0m
echo [95m================================[0m
echo.
echo [96mChoose an option:[0m
echo [94m1.[0m Run Tests
echo [94m2.[0m Clean Environment
echo [94m3.[0m Run Tests with Fresh Environment
echo [94m4.[0m Generate New Session Prompt
echo [94m5.[0m View Checkpoint Status
echo [94m6.[0m Manage Checkpoints
echo [94m7.[0m Exit
echo.
set /P choice=Enter your choice (1-7): 

if "%choice%"=="1" goto RUN_TESTS
if "%choice%"=="2" goto CLEANUP
if "%choice%"=="3" goto CLEAN_AND_TEST
if "%choice%"=="4" goto GENERATE_PROMPT
if "%choice%"=="5" goto VIEW_STATUS
if "%choice%"=="6" goto MANAGE_CHECKPOINTS
if "%choice%"=="7" goto END
echo [91mInvalid choice. Please try again.[0m
timeout /t 2 >nul
goto MENU

:GENERATE_PROMPT
cls
echo [95mGenerating new session prompt...[0m
python src/generate_session_prompt.py
echo.
echo [92mPrompt generated successfully![0m
echo [96mYou can find the prompt file in the project directory.[0m
echo [96mUse this to continue your work in the next session.[0m
pause
goto MENU

:VIEW_STATUS
cls
echo [95mChecking checkpoint status...[0m
python src/utils/test_checkpoint_manager.py --status
pause
goto MENU

:MANAGE_CHECKPOINTS
cls
echo [96mCheckpoint Management[0m
echo [94m1.[0m View Checkpoint Chain
echo [94m2.[0m Verify Checkpoints
echo [94m3.[0m Rollback to Previous Checkpoint
echo [94m4.[0m Prune Old Checkpoints
echo [94m5.[0m Back to Main Menu
echo.
set /P cp_choice=Enter your choice (1-5): 

if "%cp_choice%"=="1" (
    python src/utils/test_checkpoint_manager.py --chain
) else if "%cp_choice%"=="2" (
    python src/utils/test_checkpoint_manager.py --verify
) else if "%cp_choice%"=="3" (
    python src/utils/test_checkpoint_manager.py --rollback
) else if "%cp_choice%"=="4" (
    python src/utils/test_checkpoint_manager.py --prune
) else if "%cp_choice%"=="5" (
    goto MENU
)
pause
goto MANAGE_CHECKPOINTS

:CLEANUP
cls
echo [101;93m Caution: This will delete all test outputs and checkpoints! [0m
echo.
set /P CONFIRM=Are you sure you want to continue? (Y/N): 
if /I "%CONFIRM%" NEQ "Y" goto MENU

echo.
echo [93mCleaning up test environment...[0m

if exist "output\*" (
    echo [96mClearing output directory...[0m
    del /F /Q "output\*" 2>nul
)

if exist "output\checkpoints\*" (
    echo [96mClearing checkpoints...[0m
    del /F /Q "output\checkpoints\*" 2>nul
)

if exist "src\__pycache__" rmdir /S /Q "src\__pycache__" 2>nul
if exist "src\parsers\__pycache__" rmdir /S /Q "src\parsers\__pycache__" 2>nul
if exist "src\threader\__pycache__" rmdir /S /Q "src\threader\__pycache__" 2>nul
if exist "src\analyzers\__pycache__" rmdir /S /Q "src\analyzers\__pycache__" 2>nul
if exist "src\processors\__pycache__" rmdir /S /Q "src\processors\__pycache__" 2>nul

echo [92mCleanup complete![0m
echo.
pause
goto MENU

:RUN_TESTS
cls
call :CHECK_REQUIREMENTS || goto MENU

echo [95m==================================[0m
echo [95m   Running EvidenceAI Tests       [0m
echo [95m==================================[0m
echo.

echo [96mTest Configuration:[0m
echo [96m------------------[0m
echo [97mInput Directory:[0m %~dp0input
echo [97mOutput Directory:[0m %~dp0output
echo.

echo [95mRunning tests...[0m
echo [90m-----------------[0m
python src/test_pipeline.py

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

REM Generate new session prompt after tests
echo.
echo [95mGenerating new session prompt...[0m
python src/generate_session_prompt.py

echo.
pause
goto MENU

:CLEAN_AND_TEST
cls
call :CLEANUP
call :RUN_TESTS
goto MENU

:CHECK_REQUIREMENTS
python --version 2>NUL
if errorlevel 1 (
    echo [91mError: Python is not installed or not in PATH![0m
    echo [93mPlease install Python and try again.[0m
    pause
    exit /b 1
)

if not exist "input\*.pdf" (
    echo [91mError: No PDF files found in input directory![0m
    echo [93mPlease place an OFW PDF file in the input directory and try again.[0m
    echo.
    echo [94mExpected location:[0m
    echo %~dp0input\
    pause
    exit /b 1
)
exit /b 0

:END
echo [95mThank you for using EvidenceAI Pipeline![0m
endlocal
exit /b