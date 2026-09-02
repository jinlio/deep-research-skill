# OpenCode Capability Profile

OpenCode is supported through its file-backed `SKILL.md`/instruction mechanism and the tools configured by the host. This profile is intentionally command-neutral because OpenCode distributions and providers expose different CLI names and config layouts.

## Capability contract

Run `python scripts/build_adapters.py --output dist`, then install or link `dist/opencode/deep-research/` as `.opencode/skills/deep-research/` in the project (or `~/.opencode/skills/deep-research/` for a user-level install). Restart/open a fresh session and verify that `SKILL.md` is loaded. OpenCode also accepts skills-compatible layouts in distributions that expose an alternate configured directory; record the observed path. Map the host's web search/fetch, file read/write, shell, MCP and sub-agent features to `references/adapter-contract.md` and record the result in a capability JSON file.

If the host exposes an OpenCode agent/session delegation API, assign independent source paths to discoverer, verifier and challenger. Otherwise run the same stages serially. Do not infer support from an `opencode` binary alone; use `scripts/probe_runtime.py` with observed capabilities.

## Safety

Allow writes only below `research-run/`, keep external operations read-only, and run `scripts/run_gates.py` before delivery. When structured output is unavailable, use the JSONL templates and deterministic validators in this repository.
