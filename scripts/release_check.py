"""Run the deterministic checks required before publishing a release."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from evaluate_benchmark import evaluate
from probe_runtime import probe
from validate_skill import validate
from common import load_json, write_result


def _run(command: list[str], root: Path) -> tuple[bool, str]:
    completed = subprocess.run(command, cwd=root, text=True, capture_output=True)
    output = (completed.stdout + completed.stderr).strip()
    return completed.returncode == 0, output


def release_check(root: Path, run_dir: Path | None = None) -> dict:
    root = root.resolve()
    run_dir = (run_dir or root / "examples" / "minimal" / "run").resolve()
    checks: list[dict] = []

    skill = validate(root)
    checks.append({"name": "skill_bundle", "ok": skill["ok"], "details": skill})

    for filename in ("openclaw.example.json", "hermesagent.example.json"):
        path = root / "profiles" / "capabilities" / filename
        try:
            result = probe(load_json(path))
        except Exception as exc:
            result = {"ok": False, "errors": [str(exc)]}
        checks.append({"name": f"capability:{filename}", "ok": result["ok"], "details": result})

    benchmark = evaluate(root / "benchmarks" / "cases", root / "benchmarks" / "fixtures" / "reference_results.jsonl")
    checks.append({"name": "benchmark_fixture", "ok": benchmark["ok"], "details": benchmark})

    gates_ok, gates_output = _run([sys.executable, str(root / "scripts" / "run_gates.py"), str(run_dir), "--require-final", "--fail-on-pii"], root)
    checks.append({"name": "minimal_run_gates", "ok": gates_ok, "output": gates_output})

    tests_ok, tests_output = _run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], root)
    checks.append({"name": "unit_tests", "ok": tests_ok, "output": tests_output})

    return {"ok": all(item["ok"] for item in checks), "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = release_check(args.root, args.run_dir)
    write_result(args.output, result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

