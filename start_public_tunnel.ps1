$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$toolsDir = Join-Path $projectRoot "tools"
$cloudflaredExe = Join-Path $toolsDir "cloudflared.exe"

New-Item -ItemType Directory -Force -Path $toolsDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot "logs") | Out-Null

if (-not (Test-Path $cloudflaredExe)) {
    Invoke-WebRequest `
        -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" `
        -OutFile $cloudflaredExe
}

Push-Location $projectRoot
try {
    & $cloudflaredExe tunnel --url http://127.0.0.1:5000
}
finally {
    Pop-Location
}
