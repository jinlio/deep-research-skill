"""Shared helpers for the dependency-free research run validators."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    if not path.exists():
        return records, [f"missing file: {path.name}"]
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{path.name}:{line_no}: invalid JSON ({exc.msg})")
                continue
            if not isinstance(value, dict):
                errors.append(f"{path.name}:{line_no}: record must be an object")
                continue
            records.append(value)
    return records, errors


def require_fields(record: dict[str, Any], fields: Iterable[str], label: str) -> list[str]:
    return [f"{label}: missing or empty field '{field}'" for field in fields if not record.get(field)]


def ids(records: Iterable[dict[str, Any]], field: str, label: str) -> tuple[set[str], list[str]]:
    seen: set[str] = set()
    errors: list[str] = []
    for index, record in enumerate(records, 1):
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label}[{index}]: missing {field}")
        elif value in seen:
            errors.append(f"{label}[{index}]: duplicate {field} '{value}'")
        else:
            seen.add(value)
    return seen, errors


def write_result(path: Path | None, payload: dict[str, Any]) -> None:
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if path:
        path.write_text(rendered, encoding="utf-8")
    print(rendered, end="")

