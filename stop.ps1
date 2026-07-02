[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[System.Console]::InputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 > $null

$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "需要管理员权限停止 PostgreSQL 服务..." -ForegroundColor Yellow
    Write-Host "正在重新以管理员身份运行..." -ForegroundColor Yellow
    Start-Process -FilePath "powershell.exe" -ArgumentList "-ExecutionPolicy Bypass -File `"$($MyInvocation.MyCommand.Path)`"" -Verb RunAs -Wait
    exit 0
}

Write-Host "============================================" -ForegroundColor Red
Write-Host "  Stopping lsnuts2 Project" -ForegroundColor Red
Write-Host "============================================" -ForegroundColor Red
Write-Host ""

Write-Host "[1/3] Stopping backend service..." -ForegroundColor Yellow
$backendProcess = Get-Process python -ErrorAction SilentlyContinue
if ($backendProcess) {
    Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    Write-Host "Backend service stopped" -ForegroundColor Green
} else {
    Write-Host "No backend service running" -ForegroundColor Gray
}
Write-Host ""

Write-Host "[2/3] Stopping Cloudflare Tunnel..." -ForegroundColor Yellow
$tunnelProcess = Get-Process cloudflared -ErrorAction SilentlyContinue
if ($tunnelProcess) {
    Stop-Process -Name cloudflared -Force -ErrorAction SilentlyContinue
    Write-Host "Cloudflare Tunnel stopped" -ForegroundColor Green
} else {
    Write-Host "No Cloudflare Tunnel running" -ForegroundColor Gray
}
Write-Host ""

Write-Host "[3/3] Stopping PostgreSQL database..." -ForegroundColor Yellow
$pgService = Get-Service postgresql-x64-18 -ErrorAction SilentlyContinue
if ($pgService -and $pgService.Status -eq 'Running') {
    try {
        Stop-Service postgresql-x64-18 -ErrorAction Stop
        Write-Host "PostgreSQL stopped" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to stop PostgreSQL: $_" -ForegroundColor Red
    }
} else {
    Write-Host "PostgreSQL is not running" -ForegroundColor Gray
}
Write-Host ""

Write-Host "============================================" -ForegroundColor Red
Write-Host "  All services stopped!" -ForegroundColor Green
Write-Host ""
Write-Host "To start all services, run: start.ps1" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Red

Read-Host "Press Enter to exit"
