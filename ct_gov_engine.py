from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from datetime import date
from pathlib import Path

import requests


class CTGovEngine:
    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
    DEFAULT_DB = {"studies": [], "screening": [], "extraction": []}

    def __init__(self, project_dir: str | Path):
        self.project_dir = Path(project_dir).resolve()
        self.db_path = self.project_dir / "trials_db.json"
        self.db = self.load_db()

    def load_db(self) -> dict:
        if not self.db_path.exists():
            return deepcopy(self.DEFAULT_DB)

        with self.db_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        if not isinstance(data, dict):
            return deepcopy(self.DEFAULT_DB)

        for key, default_value in self.DEFAULT_DB.items():
            if key not in data or not isinstance(data[key], list):
                data[key] = deepcopy(default_value)

        return data

    def save_db(self) -> None:
        self.db_path.write_text(
            json.dumps(self.db, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def classify_study(self, title: str) -> tuple[str, bool, str]:
        title_lower = title.lower()

        pfa_pat = r"(pulsed field|pfa|electroporation|pulse-field)"
        thermal_pat = r"(thermal|radiofrequency|cryo|rfa|cba|conventional|standard of care|soc|radio-frequency)"
        rct_pat = r"(randomized|randomised|rct|comparison|versus|vs\.|head-to-head)"
        exclude_pat = r"(registry|observational|single-arm|single arm|feasibility|pilot|case series|cohort|non-randomized|non-randomised)"

        has_pfa = re.search(pfa_pat, title_lower)
        has_thermal = re.search(thermal_pat, title_lower)
        has_rct = re.search(rct_pat, title_lower)
        is_exclude = re.search(exclude_pat, title_lower)

        if is_exclude:
            return "EXCLUDE", False, "Excluded by regex: observational/registry/feasibility"

        if has_pfa and has_thermal and has_rct:
            return "INCLUDE", False, "Auto-included by regex: PFA vs thermal RCT"

        if has_pfa and (has_thermal or has_rct):
            return "PENDING", True, "PFA mentioned with partial comparator or RCT evidence"

        if has_pfa:
            return "PENDING", True, "PFA mentioned but no clear RCT comparator"

        return "EXCLUDE", False, "Excluded by regex: no PFA evidence"

    def _screening_index(self, nct_id: str) -> int | None:
        return next((i for i, item in enumerate(self.db["screening"]) if item["nctId"] == nct_id), None)

    def search_pfa(
        self,
        condition: str = "Atrial Fibrillation",
        term: str = "Pulsed Field Ablation",
        page_size: int = 50,
    ) -> int | None:
        print("Searching ClinicalTrials.gov for PFA vs thermal RCTs...")
        params = {
            "query.cond": condition,
            "query.term": term,
            "filter.overallStatus": "COMPLETED,ACTIVE_NOT_RECRUITING,RECRUITING",
            "pageSize": page_size,
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            print(f"ClinicalTrials.gov request failed: {exc}")
            return None

        data = response.json()
        new_hits = 0
        for study in data.get("studies", []):
            protocol = study.get("protocolSection", {})
            ident = protocol.get("identificationModule", {})
            nct_id = ident.get("nctId")
            title = ident.get("briefTitle", "")

            if not nct_id:
                continue

            if not any(item.get("nctId") == nct_id for item in self.db["studies"]):
                decision, conflict, notes = self.classify_study(title)
                self.process_new_study(study, decision, conflict, notes)
                new_hits += 1
                continue

            screen_idx = self._screening_index(nct_id)
            if screen_idx is None:
                continue

            if self.db["screening"][screen_idx]["decision"] == "PENDING":
                decision, conflict, notes = self.classify_study(title)
                self.db["screening"][screen_idx]["decision"] = decision
                self.db["screening"][screen_idx]["conflict"] = conflict
                self.db["screening"][screen_idx]["notes"] = notes

        self.save_db()
        print(f"Sync complete. Added {new_hits} new trial records.")
        return new_hits

    def process_new_study(self, study: dict, decision: str, conflict: bool, notes: str) -> None:
        protocol = study.get("protocolSection", {})
        ident = protocol.get("identificationModule", {})
        status = protocol.get("statusModule", {})
        design = protocol.get("designModule", {})

        nct_id = ident.get("nctId")
        if not nct_id:
            return

        phase_list = design.get("phaseList") or {}
        phases = phase_list.get("phases") if isinstance(phase_list, dict) else phase_list

        self.db["studies"].append(
            {
                "nctId": nct_id,
                "title": ident.get("briefTitle", ""),
                "status": status.get("overallStatus"),
                "phase": phases or [],
                "source": "CT.gov auto-extraction",
            }
        )

        self.db["screening"].append(
            {
                "nctId": nct_id,
                "decision": decision,
                "conflict": conflict,
                "notes": notes,
            }
        )

    def auto_extract_data(self, nct_id: str) -> None:
        if not any(item.get("nctId") == nct_id for item in self.db["studies"]):
            return

        extracted = {
            "nctId": nct_id,
            "n_pfa": None,
            "e_pfa": None,
            "n_thermal": None,
            "e_thermal": None,
            "verified": False,
            "last_auto_extract": date.today().isoformat(),
            "notes": "Extraction shell created during CT.gov sync. Manual event extraction is still required.",
        }

        existing_idx = next((i for i, item in enumerate(self.db["extraction"]) if item["nctId"] == nct_id), None)
        if existing_idx is None:
            self.db["extraction"].append(extracted)
        else:
            self.db["extraction"][existing_idx] = extracted

        self.save_db()

    def auto_extract_included(self) -> int:
        included_ids = [
            item["nctId"]
            for item in self.db["screening"]
            if item.get("decision") == "INCLUDE" and item.get("nctId")
        ]
        for nct_id in included_ids:
            self.auto_extract_data(nct_id)
        return len(included_ids)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sync PFA trials from ClinicalTrials.gov into trials_db.json")
    parser.add_argument(
        "--project-dir",
        default=str(Path(__file__).resolve().parent),
        help="Project directory containing trials_db.json. Defaults to this script directory.",
    )
    parser.add_argument("--condition", default="Atrial Fibrillation", help="Clinical condition query.")
    parser.add_argument("--term", default="Pulsed Field Ablation", help="Intervention search term.")
    parser.add_argument("--page-size", type=int, default=50, help="Maximum page size for the API request.")
    parser.add_argument(
        "--auto-extract-included",
        action="store_true",
        help="Populate placeholder extraction rows for currently included studies after syncing.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    engine = CTGovEngine(args.project_dir)
    new_hits = engine.search_pfa(condition=args.condition, term=args.term, page_size=args.page_size)

    if args.auto_extract_included and new_hits is not None:
        extracted = engine.auto_extract_included()
        print(f"Created extraction shells for {extracted} included studies.")
    elif args.auto_extract_included:
        print("Skipped auto-extraction because the ClinicalTrials.gov sync did not complete.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
