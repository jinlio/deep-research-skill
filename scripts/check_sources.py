"""Validate source records without performing network requests by default."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib.parse import urlparse

from common import load_jsonl, write_result


VALID_STATUSES = {"ok", "partial", "failed", "blocked", "pending"}


def canonical(value: str) -> str:
    parsed = urlparse(value.strip())
    if parsed.scheme in {"http", "https"}:
        path = parsed.path.rstrip("/") or "/"
        return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{path}?{parsed.query}".rstrip("?")
    return value.strip().replace("\\", "/")


def check(run_dir: Path) -> dict:
    records, errors = load_jsonl(run_dir / "sources.jsonl")
    seen: dict[str, str] = {}
    duplicates: list[dict[str, str]] = []
    warnings: list[str] = []
    for index, record in enumerate(records, 1):
        source_id = str(record.get("source_id", f"row-{index}"))
        value = record.get("url")
        if not isinstance(value, str) or not value.strip():
            errors.append(f"sources[{index}]: url/path is required")
            continue
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https", "file", ""}:
            errors.append(f"sources[{index}]: unsupported URL scheme '{parsed.scheme}'")
        key = canonical(value)
        if key in seen:
            duplicates.append({"source_id": source_id, "duplicate_of": seen[key], "canonical": key})
        else:
            seen[key] = source_id
        status = record.get("retrieval_status")
        if status not in VALID_STATUSES:
            errors.append(f"sources[{index}]: invalid retrieval_status '{status}'")
        if status in {"failed", "blocked"}:
            warnings.append(f"{source_id}: retrieval status is {status}; coverage may be incomplete")
        if record.get("source_type") in {"search_result", "snippet"}:
            warnings.append(f"{source_id}: search result is not a suitable final evidence source")
    return {"ok": not errors and not duplicates, "sources": len(records), "duplicates": duplicates, "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = check(args.run_dir)
    write_result(args.output, result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

