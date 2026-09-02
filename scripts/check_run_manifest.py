"""Validate run metadata and ensure artifact paths stay inside the run directory."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from common import load_json, write_result


def check(run_dir: Path) -> dict:
    path = run_dir / "run_manifest.json"
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists():
        return {"ok": False, "errors": ["missing run_manifest.json"], "warnings": []}
    try:
        manifest = load_json(path)
    except Exception as exc:
        return {"ok": False, "errors": [f"invalid JSON: {exc}"], "warnings": []}
    if not isinstance(manifest, dict):
        return {"ok": False, "errors": ["manifest root must be an object"], "warnings": []}
    for field in ("run_id", "status", "started_at"):
        if not manifest.get(field):
            errors.append(f"missing field '{field}'")
    if manifest.get("status") not in {"running", "completed", "failed", "blocked", "partial"}:
        errors.append("status must be running/completed/failed/blocked/partial")
    attempts = manifest.get("attempts", [])
    if not isinstance(attempts, list):
        errors.append("attempts must be an array")
    artifacts = manifest.get("artifacts", [])
    if not isinstance(artifacts, list):
        errors.append("artifacts must be an array")
    else:
        root = run_dir.resolve()
        for item in artifacts:
            if not isinstance(item, dict) or not item.get("path"):
                errors.append("each artifact must have a path")
                continue
            artifact = (run_dir / str(item["path"])).resolve()
            try:
                artifact.relative_to(root)
            except ValueError:
                errors.append(f"artifact escapes run directory: {item['path']}")
                continue
            if item.get("status") == "complete" and not artifact.exists():
                errors.append(f"completed artifact does not exist: {item['path']}")
    if not manifest.get("tooling"):
        warnings.append("tooling metadata is absent; reproducibility is limited")
    return {"ok": not errors, "errors": errors, "warnings": warnings, "run_id": manifest.get("run_id")}


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

