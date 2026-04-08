param(
    [string]$Version = 'unversioned snapshot',
    [string]$Summary = 'Release snapshot generated from the current working tree.'
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSCommandPath
$repoName = Split-Path -Leaf $root
$releaseDir = Join-Path $root 'release'
$stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'
$fileStamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$outPath = Join-Path $releaseDir ('release-notes-' + $fileStamp + '.md')

New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null

$latestZip = Get-ChildItem -LiteralPath $releaseDir -Filter '*.zip' -File -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

$validationCommand = if (Test-Path (Join-Path $root 'run_validation.ps1')) {
    'powershell -ExecutionPolicy Bypass -File .\run_validation.ps1'
} elseif (Test-Path (Join-Path $root 'tests\test_smoke.py')) {
    'python tests/test_smoke.py'
} elseif (Test-Path (Join-Path $root 'tests\validate_structure.py')) {
    'python tests/validate_structure.py'
} else {
    'Document the validation command for this release.'
}

$launchCommand = if (Test-Path (Join-Path $root 'open_app.ps1')) {
    'powershell -ExecutionPolicy Bypass -File .\open_app.ps1'
} else {
    'No local launcher configured.'
}

$packageName = if ($latestZip) { $latestZip.Name } else { 'Run package_release.ps1 to generate a zip asset.' }
$changelogNote = if (Test-Path (Join-Path $root 'CHANGELOG.md')) {
    '- Review `CHANGELOG.md` for user-facing changes included in this release.'
} else {
    '- Document user-facing changes before publishing this release.'
}

$content = @"
# Release Notes

## Overview
- Project: $repoName
- Version: $Version
- Generated: $stamp
- Summary: $Summary

## Validation
- Command: $validationCommand

## Launch
- Command: $launchCommand

## Assets
- Package: $packageName
- Citation metadata: `CITATION.cff`, `.zenodo.json`
- Checklist: `RELEASE_CHECKLIST.md`

## Publishing Notes
$changelogNote
- Confirm the working tree is clean before tagging.
- Publish the zip asset together with these notes for external release.
"@

Set-Content -LiteralPath $outPath -Value $content -Encoding utf8
Write-Output "Release notes: $outPath"
