"""Validate the pre-research clarification loop and orientation isolation."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import load_jsonl, write_result


def _round_limit(spec_text: str) -> int | None:
    match = re.search(r"clarification_rounds\s*:\s*(auto|\d+)", spec_text, re.I)
    if not match or match.group(1).lower() == "auto":
        return 5
    return int(match.group(1))


def check(run_dir: Path, require_confirmation: bool = True) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    spec_path = run_dir / "research_spec.yaml"
    log_path = run_dir / "clarification_log.jsonl"
    if not spec_path.exists():
        errors.append("missing research_spec.yaml")
        spec_text = ""
    else:
        spec_text = spec_path.read_text(encoding="utf-8")
    records, parse_errors = load_jsonl(log_path)
    errors.extend(parse_errors)
    if not records:
        errors.append("clarification_log.jsonl: at least one round is required")
    rounds: set[int] = set()
    has_echo = False
    has_question_round = False
    confirmed = False
    for index, record in enumerate(records, 1):
        value = record.get("round")
        if not isinstance(value, int) or value < 0:
            errors.append(f"clarification[{index}]: round must be a non-negative integer")
        else:
            rounds.add(value)
        if record.get("kind") == "understanding_echo":
            has_echo = True
        if isinstance(record.get("questions"), list) and record.get("questions"):
            has_question_round = True
        if record.get("kind") == "user_confirmation" and record.get("confirmed") is True:
            confirmed = True
    if not has_echo:
        errors.append("clarification_log.jsonl: missing understanding_echo")
    if not has_question_round:
        if require_confirmation:
            errors.append("clarification_log.jsonl: missing a question round")
        else:
            warnings.append("clarification_log.jsonl: no question round yet; run is at the initial preflight state")
    if require_confirmation and not confirmed:
        errors.append("clarification_log.jsonl: missing final user confirmation")
    limit = _round_limit(spec_text)
    if limit is not None and rounds and max(rounds) > limit:
        errors.append(f"clarification rounds exceed configured limit ({max(rounds)} > {limit})")

    for filename in ("sources.jsonl", "evidence.jsonl", "claims.jsonl", "conflicts.jsonl"):
        items, item_errors = load_jsonl(run_dir / filename)
        errors.extend(item_errors)
        for index, item in enumerate(items, 1):
            if item.get("orientation_only") is True or item.get("source_type") == "orientation_only":
                errors.append(f"{filename}[{index}]: orientation_only material leaked into formal artifacts")
    orientation_path = run_dir / "orientation_notes.md"
    if not orientation_path.exists():
        warnings.append("orientation_notes.md is absent; no orientation pass was recorded")
    return {"ok": not errors, "rounds": sorted(rounds), "confirmed": confirmed, "max_rounds": limit, "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--allow-unconfirmed", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = check(args.run_dir, not args.allow_unconfirmed)
    write_result(args.output, result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
