@echo off
echo Starting OFW Processing Pipeline...
python ofw_processor.py
echo.
echo If successful, check these folders for outputs:
echo - output: Raw data
echo - ab_tools_NotebookLM: NotebookLM formatted files
echo - ab_tools_ChatGPT: ChatGPT/Claude formatted files
echo.
pause