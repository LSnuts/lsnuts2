Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Starting lsnuts2 Project" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Starting PostgreSQL database..." -ForegroundColor Yellow
$pgService = Get-Service postgresql-x64-18 -ErrorAction SilentlyContinue
if ($pgService -and $pgService.Status -eq 'Running') {
    Write-Host "PostgreSQL is already running" -ForegroundColor Green
} else {
    try {
        Start-Service postgresql-x64-18 -ErrorAction Stop
        Write-Host "Waiting for PostgreSQL to start..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
        $pgService = Get-Service postgresql-x64-18
        if ($pgService.Status -eq 'Running') {
            Write-Host "PostgreSQL started successfully" -ForegroundColor Green
        } else {
            Write-Host "Failed to start PostgreSQL, trying with admin privileges..." -ForegroundColor Yellow
            Start-Process -FilePath "powershell.exe" -ArgumentList "-Command", "Start-Service postgresql-x64-18" -Verb RunAs -Wait
            Start-Sleep -Seconds 3
            $pgService = Get-Service postgresql-x64-18
            if ($pgService.Status -eq 'Running') {
                Write-Host "PostgreSQL started successfully" -ForegroundColor Green
            } else {
                Write-Host "ERROR: Failed to start PostgreSQL" -ForegroundColor Red
                Read-Host "Press Enter to exit"
                exit 1
            }
        }
    } catch {
        Write-Host "ERROR: Failed to start PostgreSQL: $_" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}
Write-Host ""

Write-Host "[2/3] Starting backend service..." -ForegroundColor Yellow
$backendPath = Join-Path $PWD "backend\app.py"
Start-Process -FilePath "D:\miniconda3\python.exe" -ArgumentList $backendPath
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

$backendRunning = $false
for ($i = 1; $i -le 5; $i++) {
    $portCheck = netstat -ano | findstr ":5000"
    if ($portCheck) {
        $backendRunning = $true
        break
    }
    Write-Host "Retry $i/5..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
}

if ($backendRunning) {
    Write-Host "Backend started on port 5000" -ForegroundColor Green
} else {
    Write-Host "WARNING: Backend may not have started properly" -ForegroundColor Red
}
Write-Host ""

Write-Host "[3/3] Starting Cloudflare Tunnel..." -ForegroundColor Yellow
$tunnelPath = Join-Path $PWD "cloudflared.exe"
$configPath = Join-Path $PWD "cloudflare-tunnel.yml"
Start-Process -FilePath $tunnelPath -ArgumentList "tunnel","--config",$configPath,"run"
Write-Host "Waiting for Cloudflare Tunnel to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

$tunnelRunning = $false
for ($i = 1; $i -le 5; $i++) {
    $tunnelProcess = Get-Process cloudflared -ErrorAction SilentlyContinue
    if ($tunnelProcess) {
        $tunnelRunning = $true
        break
    }
    Write-Host "Retry $i/5..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
}

if ($tunnelRunning) {
    Write-Host "Cloudflare Tunnel started" -ForegroundColor Green
} else {
    Write-Host "WARNING: Cloudflare Tunnel may not have started properly" -ForegroundColor Red
}
Write-Host ""

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: https://118201820.xyz" -ForegroundColor White
Write-Host "API: https://api.118201820.xyz" -ForegroundColor White
Write-Host ""
Write-Host "To stop all services, run: stop.ps1" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan

Read-Host "Press Enter to exit"
