"""Validate a portable SKILL.md bundle without third-party dependencies."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import write_result


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REFERENCE_RE = re.compile(r"(?:(?:core|references|profiles|scripts|examples|templates)/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*)")


def validate(root: Path) -> dict:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    skill_path = root / "SKILL.md"
    if not skill_path.exists():
        return {"ok": False, "errors": ["missing SKILL.md"], "warnings": []}
    try:
        text = skill_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return {"ok": False, "errors": [f"SKILL.md must be UTF-8: {exc}"], "warnings": []}

    if not text.startswith("---\n"):
        errors.append("SKILL.md: YAML frontmatter must start with ---")
        frontmatter = ""
    else:
        end = text.find("\n---", 4)
        if end < 0:
            errors.append("SKILL.md: YAML frontmatter is not closed")
            frontmatter = text[4:]
        else:
            frontmatter = text[4:end]
    fields: dict[str, str] = {}
    for line in frontmatter.splitlines():
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*)\s*:\s*(.*?)\s*$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip('"\'')
    name = fields.get("name", "")
    description = fields.get("description", "")
    if not name:
        errors.append("SKILL.md: missing name")
    elif not NAME_RE.fullmatch(name):
        errors.append("SKILL.md: name must use lowercase letters, digits and hyphens")
    if not description:
        errors.append("SKILL.md: missing description")
    elif len(description) > 160:
        errors.append("SKILL.md: description must be at most 160 characters")
    if "version" not in fields:
        warnings.append("SKILL.md: version is absent; release identity is less explicit")

    references = sorted(set(REFERENCE_RE.findall(text)))
    checked: list[str] = []
    for relative in references:
        candidate = (root / relative).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            errors.append(f"SKILL.md: reference escapes bundle: {relative}")
            continue
        checked.append(relative)
        if not candidate.exists():
            errors.append(f"SKILL.md: referenced file does not exist: {relative}")
    return {"ok": not errors, "name": name, "version": fields.get("version"), "references": checked, "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(args.root)
    write_result(args.output, result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
