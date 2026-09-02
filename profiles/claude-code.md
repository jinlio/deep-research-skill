# Claude Code Capability Profile

Claude Code can consume a repository `SKILL.md`/instruction bundle, use the tools enabled by the host, and run shell commands in a configured working directory. Run `python scripts/build_adapters.py --output dist`, then install `dist/claude-code/deep-research/`. The conventional project location is `.claude/skills/deep-research/SKILL.md`; user-level installs use `~/.claude/skills/deep-research/SKILL.md`. Exact discovery and sub-agent features vary by installation, so adapters must record observed behavior rather than assume a CLI version.

## Capability contract

Load this skill from the project instruction/skill directory, start a fresh session, and verify that `SKILL.md` plus the referenced protocol files are visible. Map web search/browser, file tools, shell, MCP, session delegation and resume to `references/adapter-contract.md`; save the observation as capability JSON and run `scripts/probe_runtime.py`.

Use independent sessions or sub-agents for discoverer, verifier and challenger when the host provides them. Pass each child a self-contained goal and the run path; children must return packets and never write the final report. Without delegation, use serial phases and disclose the downgrade.

## Safety

Use a read-only permission mode for inspection and a project-scoped write mode only for `research-run/`. Never grant broad shell or network write authority to a research agent. Run `python scripts/run_gates.py <run-dir> --require-final --fail-on-pii` before delivery.
