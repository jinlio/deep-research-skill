"""Validate a runtime capability declaration and choose safe execution modes.

The probe is deliberately offline: it validates observations supplied by a
platform adapter instead of guessing capabilities from a runtime name.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from common import load_json, write_result


OPERATIONS = (
    "load_skill",
    "search",
    "read_source",
    "delegate",
    "artifact_io",
    "checkpoint",
    "audit",
)
HARD_REQUIREMENTS = {"load_skill", "artifact_io"}


def _normalise(value: Any) -> tuple[bool, dict[str, Any]]:
    if isinstance(value, bool):
        return value, {"available": value}
    if isinstance(value, dict):
        return value.get("available") is True, value
    return False, {"available": False}


def probe(payload: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    degradations: list[dict[str, str]] = []
    runtime = payload.get("runtime")
    if not isinstance(runtime, str) or not runtime.strip():
        errors.append("runtime must be a non-empty string")

    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, dict):
        errors.append("capabilities must be an object")
        capabilities = {}

    normalized: dict[str, dict[str, Any]] = {}
    for operation in OPERATIONS:
        available, details = _normalise(capabilities.get(operation))
        normalized[operation] = {"available": available, **details}
        if operation in HARD_REQUIREMENTS and not available:
            errors.append(f"required capability unavailable: {operation}")
        elif not available:
            reason = {
                "search": "use user-provided sources only; disclose coverage limits",
                "read_source": "retain source as pending/blocked; do not create evidence",
                "delegate": "run all stages serially in one agent",
                "checkpoint": "export the run bundle at each stage; recovery is manual",
                "audit": "run local scripts or CI outside the runtime before delivery",
            }.get(operation, "use the documented fallback")
            degradations.append({"capability": operation, "mode": reason})

    search = normalized["search"]
    if search["available"] and search.get("mode") not in {"host-provided", "user-provided", "mcp", "runtime"}:
        warnings.append("search mode is not recognised; verify it is an existing host tool")
    if search["available"] and search.get("read_only") is False:
        errors.append("search capability must be read-only")

    artifact = normalized["artifact_io"]
    if artifact["available"] and artifact.get("append_only") is False:
        errors.append("artifact_io must support append-only writes")

    permissions = payload.get("permissions", {})
    if not isinstance(permissions, dict):
        errors.append("permissions must be an object")
        permissions = {}
    if permissions.get("external_write_default") is True:
        errors.append("external_write_default must be false for the default research mode")

    complete = not errors and all(normalized[name]["available"] for name in OPERATIONS)
    mode = "complete" if complete else "serial-degraded" if not errors else "blocked"
    if not normalized["delegate"]["available"]:
        mode = "serial-degraded" if not errors else "blocked"
    return {
        "ok": not errors,
        "runtime": runtime,
        "mode": mode,
        "capabilities": normalized,
        "degradations": degradations,
        "warnings": warnings,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capabilities", type=Path, help="capability JSON file, or '-' for stdin")
    parser.add_argument("--strict", action="store_true", help="fail unless every capability is available")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        payload = json.load(sys.stdin) if str(args.capabilities) == "-" else load_json(args.capabilities)
    except Exception as exc:
        write_result(args.output, {"ok": False, "errors": [f"invalid capability JSON: {exc}"]})
        return 1
    if not isinstance(payload, dict):
        write_result(args.output, {"ok": False, "errors": ["capability JSON root must be an object"]})
        return 1
    result = probe(payload)
    if args.strict and result["ok"] and result["mode"] != "complete":
        result["ok"] = False
        result["errors"].append("strict mode requires all capabilities")
        result["mode"] = "blocked"
    write_result(args.output, result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

