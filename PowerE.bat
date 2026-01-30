@echo off
REM PowerE Launcher
REM This batch file runs PowerE with proper permissions

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    REM Already admin, run the Python script
    goto :RunScript
) else (
    REM Not admin, request elevation
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:RunScript
REM Change to script directory
cd /d "%~dp0"

REM Run PowerE GUI
echo Starting PowerE...
pythonw.exe PowerE.py

REM If pythonw.exe failed, try python.exe
if %errorLevel% neq 0 (
    python.exe PowerE.py
)

exit /b



