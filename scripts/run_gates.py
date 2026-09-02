"""Run all dependency-free research quality gates for a run directory."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--require-final", action="store_true")
    parser.add_argument("--fail-on-pii", action="store_true")
    parser.add_argument("--preflight", action="store_true", help="allow an unconfirmed, empty run before formal research")
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    root = Path(__file__).resolve().parent
    commands = [
        [sys.executable, str(root / "validate_artifacts.py"), str(run_dir)] + (["--require-final"] if args.require_final else []),
        [sys.executable, str(root / "check_claim_coverage.py"), str(run_dir)] + (["--require-final"] if args.require_final else []) + (["--allow-empty"] if args.preflight else []),
        [sys.executable, str(root / "check_clarification.py"), str(run_dir)] + (["--allow-unconfirmed"] if args.preflight else []),
        [sys.executable, str(root / "check_sources.py"), str(run_dir)],
        [sys.executable, str(root / "check_run_manifest.py"), str(run_dir)],
        [sys.executable, str(root / "scan_sensitive_data.py"), str(run_dir)] + (["--fail-on-pii"] if args.fail_on_pii else []),
    ]
    failed = 0
    for command in commands:
        print(f"\n$ {' '.join(command)}")
        completed = subprocess.run(command, cwd=run_dir.parent)
        failed += completed.returncode != 0
    print(f"\nGATES: {'PASS' if not failed else 'FAIL'} ({failed} failed)")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
