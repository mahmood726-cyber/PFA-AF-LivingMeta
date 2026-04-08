# Validation

## Quick Checks

- Run `powershell -ExecutionPolicy Bypass -File .\open_app.ps1 -NoBrowser` to start or reuse the local app server without opening a browser window.
- Run `powershell -ExecutionPolicy Bypass -File .\run_validation.ps1` for the standard local validation entry point.
- Run `python tests/test_smoke.py` to confirm the repository structure and primary files are present.
- Run `Rscript audit_meta.R` to reproduce the local pooled efficacy estimate from the curated trial counts.
- Run `powershell -ExecutionPolicy Bypass -File .\generate_release_notes.ps1 -Summary 'Describe the release scope.'` when you need standalone release notes without creating a zip.

## CT.gov Sync

- Run `powershell -ExecutionPolicy Bypass -File .\run_ctgov_sync.ps1` from the project root to refresh `trials_db.json`.
- Network access is required for the CT.gov sync step.
- The sync script now defaults to the local project directory instead of a machine-specific absolute path.
- When the app is served from the project root, it reloads `trials_db.json` on every open with `cache: 'no-store'`.
- Existing non-search screening decisions and local reviewer notes are preserved over unverified auto-imported decisions during refresh.

## Notes

- `ct_gov_engine.py` writes `trials_db.json` in-place with UTF-8 encoding.
- Auto-created extraction rows are empty shells and are not intended for analysis until manually verified in the application.
- Run `powershell -ExecutionPolicy Bypass -File .\package_release.ps1` when you need a packaged release snapshot and matching release notes under `release/`.
