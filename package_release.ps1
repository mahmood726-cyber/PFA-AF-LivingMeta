$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSCommandPath
$repoName = Split-Path -Leaf $root
$releaseDir = Join-Path $root 'release'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$zipPath = Join-Path $releaseDir ($repoName + '-' + $stamp + '.zip')
$excludeNames = @('.git', '.github', '.playwright-cli', '.pytest_cache', '__pycache__', '.venv', 'venv', 'node_modules', 'dist', 'coverage', 'release', '.local_server.pid')

New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null

$items = Get-ChildItem -LiteralPath $root -Force | Where-Object {
    $excludeNames -notcontains $_.Name
}

if (-not $items) {
    throw 'No files available to package.'
}

Compress-Archive -Path $items.FullName -DestinationPath $zipPath -CompressionLevel Optimal -Force
& (Join-Path $root 'generate_release_notes.ps1') -Summary 'Release archive created from the current working tree.'
Write-Output "Release package: $zipPath"
