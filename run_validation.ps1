python tests/test_smoke.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$rscript = $null
$cmd = Get-Command Rscript -ErrorAction SilentlyContinue
if ($cmd) {
    $rscript = $cmd.Source
} else {
    $candidates = @(
        (Get-ChildItem 'C:\Program Files\R' -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending | ForEach-Object {
            Join-Path $_.FullName 'bin\Rscript.exe'
        }),
        (Get-ChildItem 'C:\Program Files (x86)\R' -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending | ForEach-Object {
            Join-Path $_.FullName 'bin\Rscript.exe'
        })
    ) | Where-Object { $_ -and (Test-Path $_) }
    $rscript = $candidates | Select-Object -First 1
}

if ($rscript) {
    & $rscript audit_meta.R
    exit $LASTEXITCODE
}

Write-Output "Rscript not found on PATH or common install locations; skipped audit_meta.R"
exit 0
