"""Create a standard research-run bundle without invoking a model or search tool."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


EMPTY_FILES = ("sources.jsonl", "evidence.jsonl", "claims.jsonl", "conflicts.jsonl")


def init_run(run_dir: Path, question: str, goal: str, depth: str = "standard") -> dict:
    run_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    spec = f'''question: "{question.replace('"', '\\"')}"
goal: "{goal.replace('"', '\\"')}"
scope:
  time: "待确认"
  geography: "待确认"
  domain: "待确认"
constraints:
  budget: "{depth}"
  deadline: "待确认"
  privacy: "private"
sources:
  preferred: []
  forbidden: []
  user_materials: []
clarification_rounds: auto
depth: {depth}
'''
    (run_dir / "research_spec.yaml").write_text(spec, encoding="utf-8")
    (run_dir / "plan.yaml").write_text("# Generated after research_spec confirmation.\nsubquestions: []\n", encoding="utf-8")
    (run_dir / "clarification_log.jsonl").write_text(json.dumps({"round": 0, "kind": "understanding_echo", "text": question}, ensure_ascii=False) + "\n", encoding="utf-8")
    (run_dir / "orientation_notes.md").write_text("# Orientation Notes\n\nNo orientation pass has been recorded.\n", encoding="utf-8")
    for name in EMPTY_FILES:
        (run_dir / name).touch()
    manifest = {"run_id": f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}", "status": "running", "started_at": now, "clarification_rounds": "auto", "tooling": {}, "attempts": [], "artifacts": []}
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--question", required=True)
    parser.add_argument("--goal", required=True)
    parser.add_argument("--depth", choices=("quick", "standard", "deep"), default="standard")
    args = parser.parse_args()
    result = init_run(args.run_dir, args.question, args.goal, args.depth)
    print(json.dumps({"ok": True, "run_dir": str(args.run_dir.resolve()), "run_id": result["run_id"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

