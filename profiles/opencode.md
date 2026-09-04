# OpenCode Capability Profile

OpenCode is supported through its file-backed `SKILL.md`/instruction mechanism and the tools configured by the host. This profile is intentionally command-neutral because OpenCode distributions and providers expose different CLI names and config layouts.

Observed OpenCode CLI/Windows behavior (1.18.x): skills may be discovered from several project/user paths and loaded on demand with `skill({name})`; duplicate names use last-wins behavior and concurrent discovery can be nondeterministic. Skill/config changes require a fresh session (no hot reload). `permission.skill` can restrict loading. The `task` sub-agent tool is available in some hosts, but must be smoke-tested rather than inferred; durable checkpoints are not assumed.

## Capability contract

Run `python scripts/build_adapters.py --output dist`, then install or link `dist/opencode/deep-research/` as `.opencode/skills/deep-research/` in the project (or `~/.opencode/skills/deep-research/` for a user-level install). Restart/open a fresh session and verify that `SKILL.md` is loaded. OpenCode also accepts skills-compatible layouts in distributions that expose an alternate configured directory; record the observed path. Map the host's source discovery/search, source fetch, file read/write, shell, MCP and sub-agent features to `references/adapter-contract.md` and record the result in a capability JSON file. Distinguish `discover_sources` from `fetch_source` and `read_source`; a host with `webfetch` but no search service should declare only fetch/read as available.

If the host exposes an OpenCode agent/session delegation API, assign independent source paths to discoverer, verifier and challenger. Otherwise run the same stages serially. Do not infer support from an `opencode` binary alone; use `scripts/probe_runtime.py` with observed capabilities.

## Safety

Allow writes only below `research-run/`, keep external operations read-only, and run `scripts/run_gates.py` before delivery. When structured output is unavailable, use the JSONL templates and deterministic validators in this repository.
