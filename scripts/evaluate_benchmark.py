"""Score benchmark result records against deterministic golden cases."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from common import load_json, load_jsonl, write_result


def _load_cases(directory: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    cases: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for path in sorted(directory.glob("*.json")):
        try:
            item = load_json(path)
        except Exception as exc:
            errors.append(f"{path.name}: invalid JSON ({exc})")
            continue
        if not isinstance(item, dict) or not isinstance(item.get("case_id"), str):
            errors.append(f"{path.name}: case_id is required")
            continue
        if item["case_id"] in cases:
            errors.append(f"duplicate case_id: {item['case_id']}")
        cases[item["case_id"]] = item
    if not cases:
        errors.append("no benchmark cases found")
    return cases, errors


def evaluate(cases_dir: Path, results_path: Path, threshold: float = 1.0) -> dict[str, Any]:
    cases, errors = _load_cases(cases_dir)
    results, result_errors = load_jsonl(results_path)
    errors.extend(result_errors)
    by_id: dict[str, dict[str, Any]] = {}
    for index, result in enumerate(results, 1):
        case_id = result.get("case_id")
        if not isinstance(case_id, str):
            errors.append(f"results[{index}]: case_id is required")
        elif case_id in by_id:
            errors.append(f"results[{index}]: duplicate case_id '{case_id}'")
        else:
            by_id[case_id] = result

    per_case: list[dict[str, Any]] = []
    for case_id, case in cases.items():
        result = by_id.get(case_id)
        if result is None:
            per_case.append({"case_id": case_id, "ok": False, "errors": ["missing result"]})
            continue
        claims = result.get("claims", [])
        claim_ids = {item.get("claim_id") for item in claims if isinstance(item, dict)} if isinstance(claims, list) else set()
        required = set(case.get("required_claim_ids", []))
        coverage = len(required & claim_ids) / len(required) if required else 1.0
        must_abstain = set(case.get("must_abstain_claim_ids", []))
        abstained = {item.get("claim_id") for item in claims if isinstance(item, dict) and item.get("claim_id") in must_abstain and item.get("status") in {"unknown", "insufficient"}}
        abstention = len(abstained) / len(must_abstain) if must_abstain else 1.0
        conflict = bool(result.get("conflicts"))
        conflict_score = 1.0 if not case.get("expects_conflict") or conflict else 0.0
        privacy_score = 0.0 if result.get("privacy_violation") is True else 1.0
        score = min(coverage, abstention, conflict_score, privacy_score)
        case_errors = []
        if coverage < threshold:
            case_errors.append(f"claim coverage {coverage:.4f} < {threshold:.4f}")
        if abstention < threshold:
            case_errors.append(f"abstention quality {abstention:.4f} < {threshold:.4f}")
        if conflict_score < threshold:
            case_errors.append("expected conflict was not reported")
        if privacy_score < threshold:
            case_errors.append("privacy violation reported")
        per_case.append({"case_id": case_id, "ok": not case_errors, "score": round(score, 4), "coverage": round(coverage, 4), "abstention": round(abstention, 4), "conflict_recall": conflict_score, "privacy": privacy_score, "errors": case_errors})

    aggregate = min((item.get("score", 0.0) for item in per_case), default=0.0)
    errors.extend(f"unknown result case_id: {case_id}" for case_id in by_id if case_id not in cases)
    return {"ok": not errors and all(item["ok"] for item in per_case) and aggregate >= threshold, "threshold": threshold, "cases": per_case, "aggregate_score": round(aggregate, 4), "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases_dir", type=Path)
    parser.add_argument("results", type=Path)
    parser.add_argument("--threshold", type=float, default=1.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate(args.cases_dir, args.results, args.threshold)
    write_result(args.output, result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

