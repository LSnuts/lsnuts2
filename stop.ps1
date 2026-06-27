Write-Host "============================================" -ForegroundColor Red
Write-Host "  Stopping lsnuts2 Project" -ForegroundColor Red
Write-Host "============================================" -ForegroundColor Red
Write-Host ""

Write-Host "[1/2] Stopping backend service..." -ForegroundColor Yellow
$backendProcess = Get-Process python -ErrorAction SilentlyContinue
if ($backendProcess) {
    Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    Write-Host "Backend service stopped" -ForegroundColor Green
} else {
    Write-Host "No backend service running" -ForegroundColor Gray
}
Write-Host ""

Write-Host "[2/2] Stopping Cloudflare Tunnel..." -ForegroundColor Yellow
$tunnelProcess = Get-Process cloudflared -ErrorAction SilentlyContinue
if ($tunnelProcess) {
    Stop-Process -Name cloudflared -Force -ErrorAction SilentlyContinue
    Write-Host "Cloudflare Tunnel stopped" -ForegroundColor Green
} else {
    Write-Host "No Cloudflare Tunnel running" -ForegroundColor Gray
}
Write-Host ""

Write-Host "============================================" -ForegroundColor Red
Write-Host "  All services stopped!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Red

Read-Host "Press Enter to exit"