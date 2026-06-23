$backendPath = (Get-Location).Path + "\backend"
$frontendPath = (Get-Location).Path + "\frontend"

Write-Host "=== LSnuts2 Quick Start ===" -ForegroundColor Cyan

Write-Host "`n[1/2] Starting Backend Server..." -ForegroundColor Yellow
Start-Process -FilePath "py.exe" -ArgumentList "app.py" -WorkingDirectory $backendPath

Start-Sleep -Seconds 3

Write-Host "`n[2/2] Starting Frontend Server..." -ForegroundColor Yellow
Start-Process -FilePath "npm.cmd" -ArgumentList "run dev" -WorkingDirectory $frontendPath

Write-Host "`n=== Servers Started! ===" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173/"
Write-Host "Backend:  http://127.0.0.1:5000/"