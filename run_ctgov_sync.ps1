$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
python (Join-Path $scriptRoot 'ct_gov_engine.py') --project-dir $scriptRoot --auto-extract-included
