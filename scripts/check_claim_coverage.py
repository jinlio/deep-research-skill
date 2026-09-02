"""Check that claims and final-report claim references are evidence-backed."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import load_jsonl, write_result


def check(run_dir: Path, threshold: float = 1.0, require_final: bool = False, allow_empty: bool = False) -> dict:
    claims, errors = load_jsonl(run_dir / "claims.jsonl")
    evidence, evidence_errors = load_jsonl(run_dir / "evidence.jsonl")
    errors.extend(evidence_errors)
    evidence_ids = {item.get("evidence_id") for item in evidence}
    missing: list[str] = []
    invalid: list[str] = []
    eligible = 0
    for claim in claims:
        claim_id = claim.get("claim_id", "<missing>")
        refs = claim.get("evidence_ids")
        if not isinstance(refs, list):
            invalid.append(claim_id)
            continue
        if claim.get("status") in {"supported", "partially_supported", "contradicted"}:
            eligible += 1
            if not refs:
                missing.append(claim_id)
            if any(ref not in evidence_ids for ref in refs):
                invalid.append(claim_id)
    total = len(claims)
    backed = eligible - len(set(missing + invalid))
    coverage = backed / eligible if eligible else (1.0 if claims and not require_final else 0.0)
    report_path = run_dir / "final_report.md"
    report_claims: set[str] = set()
    if report_path.exists():
        report_claims = set(re.findall(r"\bC-[A-Za-z0-9_-]+\b", report_path.read_text(encoding="utf-8")))
    elif require_final:
        errors.append("final_report.md is required")
    if require_final and claims and not report_claims:
        errors.append("final_report.md contains no claim identifiers")
    unreferenced = sorted({c.get("claim_id") for c in claims if c.get("claim_id") not in report_claims}) if report_claims else []
    if require_final and unreferenced:
        errors.append(f"final_report.md omits {len(unreferenced)} claim(s)")
    if not claims and allow_empty:
        ok = not errors
    else:
        ok = not errors and not missing and not invalid and coverage >= threshold
    return {"ok": ok, "coverage": round(coverage, 4), "threshold": threshold, "total_claims": total, "eligible_claims": eligible, "backed_claims": backed, "missing_evidence": sorted(set(missing)), "invalid_evidence_refs": sorted(set(invalid)), "unreferenced_claims": unreferenced, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--threshold", type=float, default=1.0)
    parser.add_argument("--require-final", action="store_true")
    parser.add_argument("--allow-empty", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = check(args.run_dir, args.threshold, args.require_final, args.allow_empty)
    write_result(args.output, result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
