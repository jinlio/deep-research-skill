"""Validate the structure and referential integrity of a research run."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import ids, load_json, load_jsonl, require_fields, write_result


STATUSES = {"supported", "partially_supported", "contradicted", "insufficient", "unknown"}
SOURCE_STATUSES = {"ok", "partial", "failed", "blocked", "pending"}


def validate(run_dir: Path, require_final: bool = False) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    spec = run_dir / "research_spec.yaml"
    if not spec.exists():
        errors.append("missing research_spec.yaml")
    else:
        text = spec.read_text(encoding="utf-8")
        for token in ("question:", "goal:", "scope:", "constraints:", "clarification_rounds:", "depth:"):
            if token not in text:
                errors.append(f"research_spec.yaml: missing '{token}'")
        if "time:" not in text:
            errors.append("research_spec.yaml: scope.time is required")

    manifest_path = run_dir / "run_manifest.json"
    if not manifest_path.exists():
        errors.append("missing run_manifest.json")
        manifest = {}
    else:
        try:
            manifest = load_json(manifest_path)
            if not isinstance(manifest, dict):
                errors.append("run_manifest.json: root must be an object")
                manifest = {}
            errors.extend(require_fields(manifest, ("run_id", "status", "started_at"), "run_manifest.json"))
        except Exception as exc:  # pragma: no cover - exact parser errors vary
            errors.append(f"run_manifest.json: invalid JSON ({exc})")
            manifest = {}

    plans = run_dir / "plan.yaml"
    if not plans.exists():
        errors.append("missing plan.yaml")

    sources, source_errors = load_jsonl(run_dir / "sources.jsonl")
    evidence, evidence_errors = load_jsonl(run_dir / "evidence.jsonl")
    claims, claim_errors = load_jsonl(run_dir / "claims.jsonl")
    conflicts, conflict_errors = load_jsonl(run_dir / "conflicts.jsonl")
    errors.extend(source_errors + evidence_errors + claim_errors + conflict_errors)

    source_ids, source_id_errors = ids(sources, "source_id", "sources")
    evidence_ids, evidence_id_errors = ids(evidence, "evidence_id", "evidence")
    claim_ids, claim_id_errors = ids(claims, "claim_id", "claims")
    conflict_ids, conflict_id_errors = ids(conflicts, "conflict_id", "conflicts")
    errors.extend(source_id_errors + evidence_id_errors + claim_id_errors + conflict_id_errors)

    for index, source in enumerate(sources, 1):
        errors.extend(require_fields(source, ("source_id", "url", "title", "source_type", "retrieved_at", "retrieval_status"), f"sources[{index}]"))
        if source.get("retrieval_status") not in SOURCE_STATUSES:
            errors.append(f"sources[{index}]: invalid retrieval_status")

    for index, item in enumerate(evidence, 1):
        errors.extend(require_fields(item, ("evidence_id", "source_id", "quote"), f"evidence[{index}]"))
        if item.get("source_id") not in source_ids:
            errors.append(f"evidence[{index}]: unknown source_id '{item.get('source_id')}'")
        supports = item.get("supports_claim_ids", [])
        refutes = item.get("refutes_claim_ids", [])
        if not isinstance(supports, list) or not isinstance(refutes, list):
            errors.append(f"evidence[{index}]: claim references must be arrays")
            refs = []
        else:
            refs = supports + refutes
        if not refs:
            warnings.append(f"evidence[{index}]: no claim relationship recorded")
        else:
            errors.extend(f"evidence[{index}]: unknown claim_id '{ref}'" for ref in refs if ref not in claim_ids)

    for index, claim in enumerate(claims, 1):
        errors.extend(require_fields(claim, ("claim_id", "text", "status", "evidence_ids"), f"claims[{index}]"))
        if claim.get("status") not in STATUSES:
            errors.append(f"claims[{index}]: invalid status '{claim.get('status')}'")
        if "impact" in claim and claim.get("impact") not in {"low", "medium", "high"}:
            errors.append(f"claims[{index}]: invalid impact '{claim.get('impact')}'")
        if "minimum_evidence" in claim and (not isinstance(claim.get("minimum_evidence"), int) or claim.get("minimum_evidence") < 1):
            errors.append(f"claims[{index}]: minimum_evidence must be a positive integer")
        refs = claim.get("evidence_ids")
        if not isinstance(refs, list):
            errors.append(f"claims[{index}]: evidence_ids must be an array")
        else:
            errors.extend(f"claims[{index}]: unknown evidence_id '{ref}'" for ref in refs if ref not in evidence_ids)
            if claim.get("status") in {"supported", "partially_supported", "contradicted"} and not refs:
                errors.append(f"claims[{index}]: resolved claim must have evidence")
            if claim.get("status") == "unknown" and not claim.get("reason"):
                errors.append(f"claims[{index}]: unknown claim requires a reason")

    for index, conflict in enumerate(conflicts, 1):
        errors.extend(require_fields(conflict, ("conflict_id", "claim_id", "evidence_ids", "resolution"), f"conflicts[{index}]"))
        if conflict.get("claim_id") not in claim_ids:
            errors.append(f"conflicts[{index}]: unknown claim_id '{conflict.get('claim_id')}'")
        refs = conflict.get("evidence_ids", [])
        if isinstance(refs, list):
            errors.extend(f"conflicts[{index}]: unknown evidence_id '{ref}'" for ref in refs if ref not in evidence_ids)

    if require_final and not (run_dir / "final_report.md").exists():
        errors.append("missing final_report.md")
    elif (run_dir / "final_report.md").exists():
        report = (run_dir / "final_report.md").read_text(encoding="utf-8")
        if claims and not re.search(r"C-[A-Za-z0-9_-]+", report):
            warnings.append("final_report.md contains no claim identifiers; traceability may be incomplete")

    return {"ok": not errors, "errors": errors, "warnings": warnings, "counts": {"sources": len(sources), "evidence": len(evidence), "claims": len(claims), "conflicts": len(conflicts)}, "run_id": manifest.get("run_id")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--require-final", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(args.run_dir, args.require_final)
    write_result(args.output, result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
