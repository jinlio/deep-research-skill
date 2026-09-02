"""Validate every generated runtime adapter package and its capability fixture."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from build_adapters import RUNTIMES, build
from common import load_json
from probe_runtime import probe
from validate_skill import validate


def test_matrix(root: Path) -> dict:
    root = root.resolve()
    results: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="deep-research-matrix-") as temp_dir:
        output = Path(temp_dir)
        build(root, output)
        for runtime in RUNTIMES:
            package = output / runtime / "deep-research"
            skill = validate(package)
            fixture_path = root / "profiles" / "capabilities" / f"{runtime}.example.json"
            capability = probe(load_json(fixture_path)) if fixture_path.exists() else {"ok": False, "errors": ["missing fixture"]}
            results.append({"runtime": runtime, "skill": skill, "capability": capability})
    return {"ok": all(item["skill"]["ok"] and item["capability"]["ok"] for item in results), "runtimes": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = test_matrix(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
