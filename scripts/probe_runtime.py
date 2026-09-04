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
    "discover_sources",
    "fetch_source",
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
        details = dict(value)
        details.setdefault("tested", False)
        details.setdefault("evidence", [])
        return value.get("available") is True, details
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
        raw = capabilities.get(operation)
        # `search` was the pre-0.2.2 combined operation. Treat it as a
        # compatibility declaration for source discovery and fetching when
        # the more precise fields are absent.
        if operation in {"discover_sources", "fetch_source"} and raw is None:
            raw = capabilities.get("search")
        available, details = _normalise(raw)
        details.setdefault("tested", False)
        details.setdefault("evidence", [])
        if not isinstance(details.get("evidence"), list):
            errors.append(f"{operation}.evidence must be an array")
            details["evidence"] = []
        if not isinstance(details.get("tested"), bool):
            errors.append(f"{operation}.tested must be boolean")
            details["tested"] = False
        normalized[operation] = {"available": available, **details}
        if operation in HARD_REQUIREMENTS and not available:
            errors.append(f"required capability unavailable: {operation}")
        elif not available:
            reason = {
                "search": "use user-provided sources only; disclose coverage limits",
                "discover_sources": "use user-provided URLs or a manually supplied source list",
                "fetch_source": "retain source as pending/blocked; do not create evidence",
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

    for operation in ("discover_sources", "fetch_source"):
        if normalized[operation]["available"] and not normalized[operation].get("tested"):
            warnings.append(f"{operation} is declared available but has no runtime test evidence")

    artifact = normalized["artifact_io"]
    if artifact["available"] and artifact.get("append_only") is False:
        errors.append("artifact_io must support append-only writes")

    permissions = payload.get("permissions", {})
    if not isinstance(permissions, dict):
        errors.append("permissions must be an object")
        permissions = {}
    if permissions.get("external_write_default") is True:
        errors.append("external_write_default must be false for the default research mode")

    required_for_complete = [name for name in OPERATIONS if not (name == "search" and ("discover_sources" in capabilities or "fetch_source" in capabilities))]
    complete = not errors and all(normalized[name]["available"] for name in required_for_complete)
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
