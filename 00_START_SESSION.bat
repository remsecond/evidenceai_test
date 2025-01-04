@echo off
setlocal EnableDelayedExpansion

:: Environment setup
title EvidenceAI Control Panel
set "ROOT_DIR=%~dp0"
cd "%ROOT_DIR%"
set "PYTHONPATH=%ROOT_DIR%src;%PYTHONPATH%"

call "%ROOT_DIR%src\utils\start_session.bat"
endlocal