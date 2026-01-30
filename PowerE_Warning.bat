@echo off
REM PowerE Warning Launcher
REM This is called by Task Scheduler to show the shutdown warning

REM Change to script directory
cd /d "%~dp0"

REM Try pythonw.exe first (no console)
pythonw.exe PowerE.py --warn
set EXITCODE=%errorLevel%

REM If pythonw.exe failed, try python.exe
if %EXITCODE% neq 0 (
    python.exe PowerE.py --warn
    set EXITCODE=%errorLevel%
)

REM Log to file if error
if %EXITCODE% neq 0 (
    echo Error: Exit code %EXITCODE% at %date% %time% >> PowerE_bat_errors.log
)

exit /b %EXITCODE%
