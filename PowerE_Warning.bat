@echo off
REM PowerE Warning Launcher

cd /d "%~dp0"

pythonw.exe PowerE.py --warn
set EXITCODE=%errorLevel%

if %EXITCODE% neq 0 (
    python.exe PowerE.py --warn
    set EXITCODE=%errorLevel%
)

if %EXITCODE% neq 0 (
    echo Error: Exit code %EXITCODE% at %date% %time% >> PowerE_errors.log
)

exit /b %EXITCODE%
