$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot "logs") | Out-Null

Push-Location $projectRoot
try {
    Write-Host "Открываю публичный туннель через localhost.run..." -ForegroundColor Cyan
    Write-Host "Ссылка появится ниже после успешного подключения." -ForegroundColor Green
    ssh `
        -o StrictHostKeyChecking=no `
        -o ServerAliveInterval=30 `
        -R 80:127.0.0.1:5000 `
        nokey@localhost.run
}
finally {
    Pop-Location
}
