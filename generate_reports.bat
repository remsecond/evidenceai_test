@echo off
echo =========================================
echo EvidenceAI Report Generation
echo =========================================
echo.

rem Create timestamp for this run
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set timestamp=%datetime:~0,8%_%datetime:~8,6%

echo Timestamp: %timestamp%
echo.

rem Ensure directories exist
echo Checking directories...
if not exist "input" mkdir input
if not exist "output" mkdir output
if not exist "ab_tools_NotebookLM" mkdir ab_tools_NotebookLM
if not exist "ab_tools_ChatGPT" mkdir ab_tools_ChatGPT
if not exist "logs" mkdir logs

rem Run the processor
echo Starting OFW Message Processing...
python ofw_processor.py

rem Generate additional reports
echo.
echo Generating analysis reports...
python report_generator.py

echo.
echo =========================================
echo Checking Output Files:
echo =========================================
echo.

rem Check for expected files
set ERROR=0

rem Check OFW messages
if exist "output\OFW_Messages_Report_Dec_messages.json" (
    echo [✓] OFW Messages JSON generated
) else (
    echo [×] Missing OFW Messages JSON
    set ERROR=1
)

rem Check NotebookLM output
if exist "ab_tools_NotebookLM\OFW_Messages_Report_Dec_notebooklm.txt" (
    echo [✓] NotebookLM format generated
) else (
    echo [×] Missing NotebookLM format
    set ERROR=1
)

rem Check ChatGPT/Claude output
if exist "ab_tools_ChatGPT\OFW_Messages_Report_Dec_for_analysis.txt" (
    echo [✓] LLM Analysis format generated
) else (
    echo [×] Missing LLM Analysis format
    set ERROR=1
)

echo.
if %ERROR%==0 (
    echo All outputs generated successfully!
) else (
    echo Some outputs are missing. Check the logs for details.
)

echo.
echo =========================================
echo Output Locations:
echo =========================================
echo 1. Raw data:        output/
echo 2. NotebookLM:      ab_tools_NotebookLM/
echo 3. ChatGPT/Claude:  ab_tools_ChatGPT/
echo =========================================
echo.

pause