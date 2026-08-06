param([switch]$KeepPostgres)

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

function Test-Port($port) { [bool](Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) }
function Wait-Port($port, $seconds) {
    $end = (Get-Date).AddSeconds($seconds)
    while ((Get-Date) -lt $end) { if (Test-Port $port) { return $true }; Start-Sleep 1 }
    return $false
}
function Read-Pid($path) {
    if (-not (Test-Path $path)) { return $null }
    $value = 0
    if ([int]::TryParse((Get-Content $path -Raw).Trim(), [ref]$value)) { return $value }
    return $null
}
function Is-OwnedProcess($pid, $name) {
    if (-not $pid) { return $false }
    $p = Get-Process -Id $pid -ErrorAction SilentlyContinue
    return $null -ne $p -and $p.ProcessName -eq $name
}
function Stop-ForFailure($pidFile) {
    $pid = Read-Pid $pidFile
    if ($pid) { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue }
    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
}

try {
    $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        $ps = Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe'
        Start-Process -FilePath $ps -WorkingDirectory $projectDir -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',$PSCommandPath) -Verb RunAs -Wait
        exit 0
    }

    New-Item -ItemType Directory -Force -Path $runtimeDir, $logDir | Out-Null
    Write-Host 'Starting lsnuts2...' -ForegroundColor Cyan

    foreach ($path in @($pythonPath, $backendScript, $tunnelPath, $tunnelConfig)) {
        if (-not (Test-Path $path)) { throw "Required file not found: $path" }
    }

    $pg = Get-Service $pgServiceName -ErrorAction SilentlyContinue
    if (-not $pg) { throw "PostgreSQL service not found: $pgServiceName" }
    if ($pg.Status -ne 'Running') { Start-Service $pgServiceName; (Get-Service $pgServiceName).WaitForStatus('Running','00:00:20') }
    if ((Get-Service $pgServiceName).Status -ne 'Running') { throw 'PostgreSQL failed to start' }
    Write-Host 'PostgreSQL: OK' -ForegroundColor Green

    $backendPid = Read-Pid $backendPidFile
    if (Is-OwnedProcess $backendPid 'python') {
        Write-Host "Backend already running: PID $backendPid" -ForegroundColor Green
    } else {
        Remove-Item $backendPidFile -Force -ErrorAction SilentlyContinue
        $p = Start-Process -FilePath $pythonPath -WorkingDirectory $backendDir -ArgumentList @('-u',$backendScript) -RedirectStandardOutput (Join-Path $logDir 'backend.out.log') -RedirectStandardError (Join-Path $logDir 'backend.err.log') -PassThru
        Set-Content $backendPidFile $p.Id
        if (-not (Wait-Port 5000 30)) { throw 'Backend did not listen on port 5000' }
        Write-Host "Backend: OK (PID $($p.Id))" -ForegroundColor Green
    }

    $tunnelPid = Read-Pid $tunnelPidFile
    if (Is-OwnedProcess $tunnelPid 'cloudflared') {
        Write-Host "Cloudflare Tunnel already running: PID $tunnelPid" -ForegroundColor Green
    } else {
        Remove-Item $tunnelPidFile -Force -ErrorAction SilentlyContinue
        $t = Start-Process -FilePath $tunnelPath -WorkingDirectory $projectDir -ArgumentList @('tunnel','--config',$tunnelConfig,'run') -RedirectStandardOutput (Join-Path $logDir 'cloudflared.out.log') -RedirectStandardError (Join-Path $logDir 'cloudflared.err.log') -PassThru
        Set-Content $tunnelPidFile $t.Id
        Start-Sleep 3
        if ($t.HasExited) { throw 'Cloudflare Tunnel failed to start' }
        Write-Host "Cloudflare Tunnel: OK (PID $($t.Id))" -ForegroundColor Green
    }

    Write-Host 'Frontend: https://118201820.xyz' -ForegroundColor White
    Write-Host 'API:      https://api.118201820.xyz' -ForegroundColor White
    Write-Host "Logs:     $logDir" -ForegroundColor Gray
    Read-Host 'Startup completed. Press Enter to close'
} catch {
    $message = $_.Exception.Message
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    Add-Content (Join-Path $logDir 'start-error.log') "$(Get-Date -Format s) $message"
    Write-Host "Startup failed: $message" -ForegroundColor Red
    Read-Host 'Press Enter to close'
    exit 1
}
