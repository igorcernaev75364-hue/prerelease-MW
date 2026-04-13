@echo off
set SCRIPT_DIR=%~dp0
start "MW STORE Local Server" powershell -NoExit -ExecutionPolicy Bypass -File "%SCRIPT_DIR%start_local_server.ps1"
timeout /t 4 /nobreak >nul
start "MW STORE Public Tunnel" powershell -NoExit -ExecutionPolicy Bypass -File "%SCRIPT_DIR%start_public_tunnel.ps1"
