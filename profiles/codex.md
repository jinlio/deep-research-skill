# Codex Capability Profile

Codex CLI supports file-backed skills, a read-only/workspace-write sandbox, shell execution, host-configured search/MCP tools, and non-interactive `codex exec` sessions. Search is runtime configuration, not a portable CLI flag; record what the current session exposes in the capability JSON. Do not use OpenClaw `sessions_spawn` or Hermes `delegate_task` names inside a Codex run; use a new Codex session or run stages serially when no delegation bridge is configured.

## Load and smoke test

Run from the skill root or a repository that contains the skill:

```bash
codex exec --ephemeral --sandbox read-only -C <workspace> \
  "Read SKILL.md and references/adapter-contract.md. Run python scripts/validate_skill.py . and report the exit status. Do not modify files."
```

For a real research run, use the existing native search tool only when the user permits external reads and the current Codex host exposes it:

```bash
codex exec --sandbox workspace-write -C <workspace> \
  "Load SKILL.md. Complete clarification before using web_search; write only research-run/ artifacts."
```

Use `--output-schema` when the host needs machine-readable packets. Use `--json` to capture lifecycle and command events in the run manifest. `--ephemeral` is suitable for smoke tests; it is not a checkpoint mechanism for research.

## Mapping

| Contract operation | Codex implementation | Fallback |
|---|---|---|
| `load_skill` | file-backed skill loaded from workspace/project skill roots | read `SKILL.md` explicitly |
| `search` | native `web_search` enabled by `--search` | user-provided links/materials |
| `read_source` | shell/browser/MCP tools available to the session | mark source pending/blocked |
| `delegate` | separate `codex exec` sessions or app-server sessions, if orchestration is available | serial phases in one session |
| `artifact_io` | shell/file tools under `research-run/` | export bundle before session ends |
| `checkpoint` | append-only run bundle plus persisted Codex session ID | manual resume from manifest |
| `audit` | `python {baseDir}/scripts/run_gates.py ...` | run in host CI |

## Safety and verification

Use `--sandbox read-only` for inspection and `--sandbox workspace-write` only when the run must write its local bundle. Never use `--dangerously-bypass-approvals-and-sandbox` for research. `--search` is read-only web retrieval, but sources still require opening and recording evidence. Before delivery run:

```bash
python {baseDir}/scripts/run_gates.py <run-dir> --require-final --fail-on-pii
```

The Codex runtime may load unrelated local plugins; plugin warnings are not evidence and must not enter the research ledger.
