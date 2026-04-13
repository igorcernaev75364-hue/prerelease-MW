$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    throw "Python virtual environment not found at .venv\Scripts\python.exe"
}

New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot "logs") | Out-Null

Push-Location $projectRoot
try {
    Write-Host "Установка зависимостей и запуск локального сервера..." -ForegroundColor Cyan
    Write-Host "После запуска сайт будет доступен по адресу: http://127.0.0.1:5000" -ForegroundColor Green
    & $pythonExe -m pip install -r requirements.txt
    & $pythonExe -m waitress --host 0.0.0.0 --port 5000 app:app
}
finally {
    Pop-Location
}
