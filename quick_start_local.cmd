@echo off
set SCRIPT_DIR=%~dp0
powershell -NoExit -ExecutionPolicy Bypass -File "%SCRIPT_DIR%start_local_server.ps1"
