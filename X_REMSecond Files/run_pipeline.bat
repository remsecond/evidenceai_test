@echo off

REM Check if advanced_pattern_detector.py exists
if exist src\analyzers\advanced_pattern_detector.py (
    echo advanced_pattern_detector.py exists.
) else (
    echo Error: advanced_pattern_detector.py does not exist.
    exit /b 1
)

REM Run the pipeline test
python src\test_pipeline.py
if %errorlevel% neq 0 (
    echo Error: Pipeline test failed.
    exit /b 1
) else (
    echo Pipeline test executed successfully.
)

REM Check the output directory for results
if exist output\ (
    echo Contents of the output directory:
    dir output\
) else (
    echo Error: output directory does not exist.
    exit /b 1
)
