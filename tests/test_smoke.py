from pathlib import Path
import json
import sys


REQUIRED_FILES = (
    "PFA_AF_LivingMeta.html",
    "ct_gov_engine.py",
    "audit_meta.R",
    "trials_db.json",
    "open_app.ps1",
    "stop_local_server.ps1",
    "package_release.ps1",
    "generate_release_notes.ps1",
    "run_ctgov_sync.ps1",
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    missing = [name for name in REQUIRED_FILES if not (root / name).exists()]
    if missing:
        print("Missing required files:", ", ".join(missing))
        return 1

    html = (root / "PFA_AF_LivingMeta.html").read_text(encoding="utf-8", errors="ignore")
    payload = json.loads((root / "trials_db.json").read_text(encoding="utf-8"))
    checks = {
        "PFA": "pfa" in html.lower(),
        "atrial fibrillation": "atrial fibrillation" in html.lower(),
        "title": "<title>" in html.lower(),
        "structured loader": "tryloadstructureddb" in html.lower() and "trials_db.json" in html,
        "refresh merge": "mergeTrials(importedTrials)" in html and "preserveExistingDecision" in html,
        "json studies": isinstance(payload.get("studies"), list) and len(payload["studies"]) > 0,
        "json screening": isinstance(payload.get("screening"), list) and len(payload["screening"]) == len(payload["studies"]),
        "json extraction": isinstance(payload.get("extraction"), list),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print("Smoke check failed:", ", ".join(failed))
        return 1

    print("test_smoke.py: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
