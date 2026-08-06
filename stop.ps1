param(
    [switch]$KeepPostgres
)

$ErrorActionPreference = 'Stop'
$projectDir = $PSScriptRoot
$runtimeDir = Join-Path $projectDir 'instance\runtime'
$backendPidFile = Join-Path $runtimeDir 'backend.pid'
$tunnelPidFile = Join-Path $runtimeDir 'cloudflared.pid'
$pgServiceName = 'postgresql-x64-18'

function Stop-OwnedProcess($pidFile, $processName, $label) {
    if (-not (Test-Path $pidFile)) {
        Write-Host "$label is not managed by this project" -ForegroundColor Gray
        return
    }
    $pid = 0
    $raw = Get-Content $pidFile -Raw
    if (-not [int]::TryParse($raw.Trim(), [ref]$pid)) {
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
        Write-Host "$label PID file is invalid" -ForegroundColor Gray
        return
    }
    $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
    if ($process -and $process.ProcessName -eq $processName) {
        Stop-Process -Id $pid -Force
        Write-Host "$label stopped (PID $pid)" -ForegroundColor Green
    } else {
        Write-Host "$label is not running" -ForegroundColor Gray
    }
    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
}

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $PSCommandPath) -Verb RunAs -Wait
    exit 0
}

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

Write-Host '============================================' -ForegroundColor Red
Write-Host '  Stopping lsnuts2 Project' -ForegroundColor Red
Write-Host '============================================' -ForegroundColor Red

Stop-OwnedProcess $backendPidFile 'python' 'Backend'
Stop-OwnedProcess $tunnelPidFile 'cloudflared' 'Cloudflare Tunnel'

if ($KeepPostgres) {
    Write-Host 'PostgreSQL kept running' -ForegroundColor Yellow
} else {
    $pgService = Get-Service $pgServiceName -ErrorAction SilentlyContinue
    if ($pgService -and $pgService.Status -eq 'Running') {
        Stop-Service $pgServiceName
        Write-Host 'PostgreSQL stopped' -ForegroundColor Green
    } else {
        Write-Host 'PostgreSQL is not running' -ForegroundColor Gray
    }
}

Write-Host '============================================' -ForegroundColor Red
