Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Starting lsnuts2 Project" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Starting backend service..." -ForegroundColor Yellow
$backendPath = Join-Path $PWD "backend\app.py"
Start-Process -FilePath "D:\miniconda3\python.exe" -ArgumentList $backendPath
Write-Host "Backend started on port 5000" -ForegroundColor Green
Write-Host ""

Write-Host "[2/2] Starting Cloudflare Tunnel..." -ForegroundColor Yellow
$tunnelPath = Join-Path $PWD "cloudflared.exe"
$configPath = Join-Path $PWD "cloudflare-tunnel.yml"
Start-Process -FilePath $tunnelPath -ArgumentList "tunnel","--config",$configPath,"run"
Write-Host "Cloudflare Tunnel started" -ForegroundColor Green
Write-Host ""

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: https://118201820.xyz" -ForegroundColor White
Write-Host "API: https://api.118201820.xyz" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan

Read-Host "Press Enter to exit"