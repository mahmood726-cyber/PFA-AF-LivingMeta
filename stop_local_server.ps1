$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSCommandPath
$port = 8783
$pidFile = Join-Path $root '.local_server.pid'
$stopped = $false

if (Test-Path $pidFile) {
    $pidText = Get-Content -LiteralPath $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($pidText -match '^\d+$') {
        try {
            Stop-Process -Id ([int]$pidText) -Force -ErrorAction Stop
            Write-Output "Stopped PID $pidText from pid file."
            $stopped = $true
        } catch {
        }
    }
    Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
}

if (-not $stopped) {
    $listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($listener) {
        Stop-Process -Id $listener.OwningProcess -Force
        Write-Output "Stopped PID $($listener.OwningProcess) on port $port."
        $stopped = $true
    }
}

if (-not $stopped) {
    Write-Output "No local server found on port $port."
}
