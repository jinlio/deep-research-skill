"""Build self-contained skill bundles for each supported Agent runtime."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


RUNTIMES = ("openclaw", "hermesagent", "codex", "opencode", "claude-code", "generic")


def _copy_tree(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, dirs_exist_ok=True)


def build(root: Path, output: Path) -> dict:
    root = root.resolve()
    output = output.resolve()
    core = root / "core"
    if not (core / "references").is_dir():
        raise FileNotFoundError(f"missing core references: {core / 'references'}")
    if output == root:
        raise ValueError("output must not be the repository root")

    output.mkdir(parents=True, exist_ok=True)
    built: list[str] = []
    for runtime in RUNTIMES:
        adapter = root / "adapters" / runtime / "SKILL.md"
        if not adapter.is_file():
            raise FileNotFoundError(f"missing adapter entry: {adapter}")
        destination = output / runtime / "deep-research"
        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir(parents=True)
        shutil.copy2(adapter, destination / "SKILL.md")
        _copy_tree(core / "references", destination / "references")
        _copy_tree(
            root / "scripts",
            destination / "scripts",
        )
        for repo_only in ("build_adapters.py", "test_runtime_matrix.py", "release_check.py", "README.md"):
            (destination / "scripts" / repo_only).unlink(missing_ok=True)
        _copy_tree(root / "profiles", destination / "profiles")
        for filename in ("LICENSE", "SECURITY.md", "VERSION"):
            source = root / filename
            if source.is_file():
                shutil.copy2(source, destination / filename)
        built.append(runtime)
    return {"ok": True, "output": str(output), "runtimes": built}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.root, args.output)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
