param(
    [switch]$KeepPostgres
)

$ErrorActionPreference = 'Stop'
$projectDir = $PSScriptRoot
$backendDir = Join-Path $projectDir 'backend'
$pythonPath = 'D:\miniconda3\python.exe'
$backendScript = Join-Path $backendDir 'app.py'
$tunnelPath = Join-Path $projectDir 'cloudflared.exe'
$tunnelConfig = Join-Path $projectDir 'cloudflare-tunnel.yml'
$runtimeDir = Join-Path $projectDir 'instance\runtime'
$logDir = Join-Path $projectDir 'instance\logs'
$backendPidFile = Join-Path $runtimeDir 'backend.pid'
$tunnelPidFile = Join-Path $runtimeDir 'cloudflared.pid'
$pgServiceName = 'postgresql-x64-18'

function Write-Step($message) { Write-Host "`n$message" -ForegroundColor Yellow }
function Fail($message) { Write-Host "ERROR: $message" -ForegroundColor Red; exit 1 }
function Test-Port($port) {
    return [bool](Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue)
}
function Wait-Port($port, $timeoutSeconds = 30) {
    $deadline = (Get-Date).AddSeconds($timeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-Port $port) { return $true }
        Start-Sleep -Seconds 1
    }
    return $false
}
function Read-Pid($path) {
    if (-not (Test-Path $path)) { return $null }
    $value = Get-Content $path -Raw
    $pid = 0
    if ([int]::TryParse($value.Trim(), [ref]$pid)) { return $pid }
    return $null
}
function Test-ProcessPid($pid, $name) {
    if (-not $pid) { return $false }
    $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
    return $null -ne $process -and $process.ProcessName -eq $name
}

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $PSCommandPath) -Verb RunAs -Wait
    exit 0
}

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
New-Item -ItemType Directory -Force -Path $runtimeDir, $logDir | Out-Null

Write-Host '============================================' -ForegroundColor Cyan
Write-Host '  Starting lsnuts2 Project' -ForegroundColor Cyan
Write-Host '============================================' -ForegroundColor Cyan

if (-not (Test-Path $pythonPath)) { Fail "Python not found: $pythonPath" }
if (-not (Test-Path $backendScript)) { Fail "Backend entrypoint not found: $backendScript" }
if (-not (Test-Path $tunnelPath)) { Fail "cloudflared not found: $tunnelPath" }
if (-not (Test-Path $tunnelConfig)) { Fail "Tunnel config not found: $tunnelConfig" }

Write-Step '[1/3] Checking PostgreSQL'
$pgService = Get-Service $pgServiceName -ErrorAction SilentlyContinue
if (-not $pgService) { Fail "PostgreSQL service not found: $pgServiceName" }
if ($pgService.Status -ne 'Running') {
    Start-Service $pgServiceName
    $pgService.WaitForStatus('Running', '00:00:20')
}
if ((Get-Service $pgServiceName).Status -ne 'Running') { Fail 'PostgreSQL failed to start' }
Write-Host 'PostgreSQL is running' -ForegroundColor Green

Write-Step '[2/3] Starting backend'
$existingBackendPid = Read-Pid $backendPidFile
if (Test-ProcessPid $existingBackendPid 'python') {
    Write-Host "Backend is already running (PID $existingBackendPid)" -ForegroundColor Green
} else {
    Remove-Item $backendPidFile -Force -ErrorAction SilentlyContinue
    $backendOut = Join-Path $logDir 'backend.out.log'
    $backendErr = Join-Path $logDir 'backend.err.log'
    $backendProcess = Start-Process -FilePath $pythonPath -WorkingDirectory $backendDir -ArgumentList @('-u', $backendScript) -RedirectStandardOutput $backendOut -RedirectStandardError $backendErr -PassThru
    Set-Content $backendPidFile $backendProcess.Id
    if (-not (Wait-Port 5000 30)) {
        Write-Host "Backend log: $backendErr" -ForegroundColor Gray
        Fail 'Backend did not listen on port 5000'
    }
    Write-Host "Backend is running (PID $($backendProcess.Id))" -ForegroundColor Green
}

Write-Step '[3/3] Starting Cloudflare Tunnel'
$existingTunnelPid = Read-Pid $tunnelPidFile
if (Test-ProcessPid $existingTunnelPid 'cloudflared') {
    Write-Host "Cloudflare Tunnel is already running (PID $existingTunnelPid)" -ForegroundColor Green
} else {
    Remove-Item $tunnelPidFile -Force -ErrorAction SilentlyContinue
    $tunnelOut = Join-Path $logDir 'cloudflared.out.log'
    $tunnelErr = Join-Path $logDir 'cloudflared.err.log'
    $tunnelProcess = Start-Process -FilePath $tunnelPath -WorkingDirectory $projectDir -ArgumentList @('tunnel', '--config', $tunnelConfig, 'run') -RedirectStandardOutput $tunnelOut -RedirectStandardError $tunnelErr -PassThru
    Set-Content $tunnelPidFile $tunnelProcess.Id
    Start-Sleep -Seconds 3
    if ($tunnelProcess.HasExited) { Fail "Cloudflare Tunnel failed; log: $tunnelErr" }
    Write-Host "Cloudflare Tunnel is running (PID $($tunnelProcess.Id))" -ForegroundColor Green
}

Write-Host "`nFrontend: https://118201820.xyz" -ForegroundColor White
Write-Host 'API:      https://api.118201820.xyz' -ForegroundColor White
Write-Host "Logs:     $logDir" -ForegroundColor Gray
if (-not $KeepPostgres) { Write-Host 'Stop:     .\stop.ps1' -ForegroundColor Yellow }
Write-Host '============================================' -ForegroundColor Cyan
