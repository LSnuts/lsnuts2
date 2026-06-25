$backendPath = (Get-Location).Path + "\backend"
$frontendPath = (Get-Location).Path + "\frontend"

Write-Host "=== LSnuts2 Quick Start ===" -ForegroundColor Cyan

Write-Host "`n[0/3] Checking/Creating Admin Account..." -ForegroundColor Yellow
$adminCheck = & py -3 "$backendPath\create_admin.py" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host $adminCheck -ForegroundColor Green
} else {
    Write-Host "Admin check/create may have been skipped or already exists." -ForegroundColor DarkYellow
}

Write-Host "`n[1/3] Starting Backend Server..." -ForegroundColor Yellow
Start-Process -FilePath "py.exe" -ArgumentList "app.py" -WorkingDirectory $backendPath

Start-Sleep -Seconds 3

Write-Host "`n[2/3] Starting Frontend Server..." -ForegroundColor Yellow
Start-Process -FilePath "npm.cmd" -ArgumentList "run dev" -WorkingDirectory $frontendPath

Write-Host "`n=== Servers Started! ===" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173/"
Write-Host "Backend:  http://127.0.0.1:5000/"
Write-Host "`nPress any key to stop..."
[void][System.Console]::ReadKey($true)

Write-Host "`nStopping servers..."
taskkill /f /im python.exe /t 2>$null
taskkill /f /im py.exe /t 2>$null
taskkill /f /im node.exe /t 2>$null
Write-Host "Done!"
