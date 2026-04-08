# RapidMeta Cardiology - PFA in AF Living Meta-Analysis

Browser-based living meta-analysis workspace for pulse field ablation versus thermal ablation in atrial fibrillation.

## Quick Start

1. Run `powershell -ExecutionPolicy Bypass -File .\open_app.ps1` to start the local launcher and open the app.
2. Review the local source assets in `trials_db.json`, `ct_gov_engine.py`, and `audit_meta.R`.
3. Run `python tests/test_smoke.py` for a quick repository smoke check.

## Repository Contents

- `PFA_AF_LivingMeta.html`: primary browser application.
- `open_app.ps1`: local browser launcher with static-server support.
- `stop_local_server.ps1`: stops the local launcher server.
- `package_release.ps1`: creates a timestamped release zip under `release/`.
- `generate_release_notes.ps1`: writes timestamped release notes under `release/`.
- `trials_db.json`: local trial data snapshot.
- `ct_gov_engine.py`: CT.gov helper script.
- `audit_meta.R`: audit helper script.
- `tests/test_smoke.py`: lightweight structural validation.

## Release Hygiene

Use `generate_release_notes.ps1`, `package_release.ps1`, `CITATION.cff`, `.zenodo.json`, and `RELEASE_CHECKLIST.md` when preparing a public release. `package_release.ps1` calls the release-note generator automatically.
