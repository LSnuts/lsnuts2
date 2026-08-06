param([switch]$KeepPostgres)

$ErrorActionPreference = 'Stop'
$projectDir = $PSScriptRoot
$runtimeDir = Join-Path $projectDir 'instance\runtime'
$backendPidFile = Join-Path $runtimeDir 'backend.pid'
$tunnelPidFile = Join-Path $runtimeDir 'cloudflared.pid'
$pgServiceName = 'postgresql-x64-18'

function Read-Pid($path) {
    if (-not (Test-Path $path)) { return $null }
    $value = 0
    if ([int]::TryParse((Get-Content $path -Raw).Trim(), [ref]$value)) { return $value }
    return $null
}
function Stop-Owned($path, $name, $label) {
    $pid = Read-Pid $path
    if ($pid) {
        $p = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($p -and $p.ProcessName -eq $name) { Stop-Process -Id $pid -Force; Write-Host "$label stopped" -ForegroundColor Green }
    }
    Remove-Item $path -Force -ErrorAction SilentlyContinue
}

try {
    $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        $ps = Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe'
        Start-Process -FilePath $ps -WorkingDirectory $projectDir -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',$PSCommandPath) -Verb RunAs -Wait
        exit 0
    }
    Write-Host 'Stopping lsnuts2...' -ForegroundColor Red
    Stop-Owned $backendPidFile 'python' 'Backend'
    Stop-Owned $tunnelPidFile 'cloudflared' 'Cloudflare Tunnel'
    if ($KeepPostgres) {
        Write-Host 'PostgreSQL kept running' -ForegroundColor Yellow
    } else {
        $pg = Get-Service $pgServiceName -ErrorAction SilentlyContinue
        if ($pg -and $pg.Status -eq 'Running') { Stop-Service $pgServiceName; Write-Host 'PostgreSQL stopped' -ForegroundColor Green }
    }
    Read-Host 'Stop completed. Press Enter to close'
} catch {
    Write-Host "Stop failed: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host 'Press Enter to close'
    exit 1
}
