param(
    [switch]$NoBrowser
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSCommandPath
$port = 8783
$entry = 'PFA_AF_LivingMeta.html'
$pidFile = Join-Path $root '.local_server.pid'
$url = "http://127.0.0.1:$port/$entry"

function Test-AppUrl {
    param([string]$TargetUrl)
    try {
        $null = Invoke-WebRequest -UseBasicParsing -Uri $TargetUrl -TimeoutSec 2
        return $true
    } catch {
        return $false
    }
}

if (-not (Test-AppUrl -TargetUrl $url)) {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        throw 'python not found on PATH; install Python 3 to use open_app.ps1.'
    }

    $listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($listener) {
        throw "Port $port is already in use by PID $($listener.OwningProcess)."
    }

    $proc = Start-Process -FilePath $python.Source -WorkingDirectory $root -ArgumentList @('-m', 'http.server', $port, '--bind', '127.0.0.1') -PassThru -WindowStyle Hidden
    Set-Content -LiteralPath $pidFile -Value $proc.Id -Encoding ascii

    $ready = $false
    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep -Milliseconds 300
        if (Test-AppUrl -TargetUrl $url) {
            $ready = $true
            break
        }
    }

    if (-not $ready) {
        throw "Local server did not become reachable at $url"
    }
}

if (-not $NoBrowser) {
    Start-Process $url | Out-Null
}

Write-Output "App URL: $url"
