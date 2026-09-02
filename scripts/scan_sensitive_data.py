"""Scan a research run for high-confidence secrets and common PII."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import write_result


SECRET_PATTERNS = {
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "github_token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "bearer_token": re.compile(r"\bBearer\s+[A-Za-z0-9._~-]{20,}\b", re.I),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}
PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone": re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)"),
}


def scan(run_dir: Path, fail_on_pii: bool = False) -> dict:
    secrets: list[dict[str, object]] = []
    pii: list[dict[str, object]] = []
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file() or path.name in {"audit.json", "sensitive_scan.json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            for kind, pattern in SECRET_PATTERNS.items():
                if pattern.search(line):
                    secrets.append({"file": str(path.relative_to(run_dir)), "line": line_no, "type": kind})
            for kind, pattern in PII_PATTERNS.items():
                if pattern.search(line):
                    pii.append({"file": str(path.relative_to(run_dir)), "line": line_no, "type": kind})
    return {"ok": not secrets and (not fail_on_pii or not pii), "secrets": secrets, "pii": pii, "fail_on_pii": fail_on_pii}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--fail-on-pii", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = scan(args.run_dir, args.fail_on_pii)
    write_result(args.output, result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

