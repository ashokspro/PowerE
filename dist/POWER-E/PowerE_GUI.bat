@echo off
REM PowerE Settings Launcher (Portable Version)
REM Double-click to open the settings GUI

REM Get the directory of the batch file (no matter where it's run from)
cd /d "./dist/main/"

REM Run the EXE from the same directory with --settings argument and admin permission
powershell -Command "Start-Process '.\POWER-E.exe' -ArgumentList '--settings' -Verb RunAs"

pause