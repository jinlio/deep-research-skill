# Deep Research Skill

[中文文档](README.zh-CN.md) · [GitHub](https://github.com/jinlio/deep-research-skill) · MIT

> Deep research you can actually audit: every claim links back to a located quote in its original source — conflicts, unknowns and failed retrievals stay visible instead of being smoothed over.

AI research tools fabricate citations at a documented, painful rate: 2026 analyses report **39–55% of generated citations are entirely fabricated** ([INRA](https://www.inra.ai/blog/ai-hallucinations)), and even OpenAI Deep Research attaches the right URL to the wrong claim about **~22% of the time** ([FACT framework, arXiv](https://arxiv.org/html/2604.03173v1)). The failure mode is never "the report looks empty" — it is a fluent report you cannot trust.

Deep Research Skill is a **pure-workflow** research protocol for coding agents (Claude Code, Codex CLI, OpenCode, and generic agents). It ships no search engine, no model, and no API keys. It orchestrates the tools your agent already has into a pipeline that:

1. **Clarifies before searching** — configurable N rounds of questions freeze a `research_spec.yaml` you confirm, so the run answers the question you actually asked.
2. **Binds every claim to evidence** — each claim references located original-text excerpts (`claim → evidence → source`), never search snippets or model memory.
3. **Keeps conflicts and unknowns first-class** — contradictions, retrieval failures and `insufficient` findings are recorded in dedicated artifacts, not hidden behind fluent prose.
4. **Gates delivery deterministically** — dependency-free scripts check citation coverage, source independence, clarification confirmation, privacy and path safety before a report may be delivered.
5. **Resumes and hands off** — the append-only run bundle survives interruption; teammates (or another agent) can pick up the same ledger.

## Install

**One line (Claude Code, Codex CLI, or any [agentskills.io](https://agentskills.io)-compatible host):**

```bash
npx skills add jinlio/deep-research-skill
```

**Claude Code plugin marketplace:**

```
/plugin marketplace add jinlio/deep-research-skill
/plugin install deep-research@deep-research-skill
```

**Manual (any host):** copy this repository into your skill directory, e.g. `~/.claude/skills/deep-research/`. The root `SKILL.md` is self-sufficient; `core/references/`, `scripts/` and `profiles/` provide the full protocol.

**Per-runtime trimmed packages:**

```bash
python scripts/build_adapters.py --output dist
# install dist/<runtime>/deep-research/ for openclaw | hermesagent | codex | opencode | claude-code | generic
```

## Quick start

```bash
# 1. Create a run bundle
python scripts/init_run.py research-run --question "Your research question" --goal "The decision this supports" --depth standard

# 2. ...clarify, register sources, extract evidence, verify claims...

# 3. Gate the delivery
python scripts/run_gates.py research-run --require-final --fail-on-pii
```

The host agent does the searching, reading and writing; the scripts only perform deterministic validation. Everything lands in one auditable folder:

```
research-run/
  research_spec.yaml      # confirmed question, scope, evidence standard
  clarification_log.jsonl # every round of questions and answers
  sources.jsonl           # source metadata, retrieval status, independence groups
  evidence.jsonl          # original-text excerpts with page/section locators
  claims.jsonl            # status, confidence, evidence references per claim
  conflicts.jsonl         # contradictions, unknowns, retrieval failures
  run_manifest.json       # runtime, attempts, degradation reasons
  final_report.md         # derived from the ledger — the ledger is the ground truth
```

## Research modes

| depth | Clarification | Good for |
|---|---|---|
| `quick` | 0 rounds (assumptions written into the spec and shown to you) | fact lookups, time-sensitive questions |
| `standard` | 1 round + final confirmation | most research |
| `deep` | 2–3 rounds + final confirmation | high-impact decisions, competitive analysis, due diligence |

Any mode can be cut short by saying "start with your current understanding"; unresolved items become explicit assumptions in the spec, never silent guesses.

## How it compares

Most deep-research skills optimize for **more searching**: parallel agents, long reports, pretty formatting. That helps coverage, but the documented failure — citations that don't check out — survives every one of those tricks. This project optimizes for **verifiability** instead:

| | Typical research skill | Deep Research Skill |
|---|---|---|
| Evidence | URLs in a bibliography | located original-text excerpts per claim |
| Conflicts | best-effort synthesis | first-class `conflicts.jsonl`, never silently resolved |
| Missing evidence | fluent filler | explicit `unknown` / `insufficient` statuses |
| Quality control | prompt-level advice | deterministic, dependency-free gate scripts |
| Portability | one host | same protocol across 6 runtimes via capability profiles |
| Interruption | restart from zero | append-only bundle, resume from checkpoint |
| Permissions | varies | read-only by default; never touches permissions, credentials or network config |

The trade-off is honest: this workflow asks questions up front and produces ledgers alongside prose. If you want a fast uncited summary, use plain web search; if the report will inform a decision, that friction is the product.

## Runtime support

| Runtime | Status | Notes |
|---|---|---|
| Claude Code | ✅ maintained | serial-first; delegation mapped via capability profile |
| Codex CLI | ✅ maintained | smoke-tested (`codex exec --sandbox read-only`) |
| OpenCode | ✅ maintained | real end-to-end run validated (degraded serial mode) |
| generic | ✅ maintained | protocol-only fallback for other hosts |
| OpenClaw | 🔧 maintenance mode | profile kept current; no new features planned |
| HermesAgent | 🔧 maintenance mode | profile kept current; no new features planned |

Validation boundaries, smoke-test commands and the OpenCode run summary live in [runtime_validation.md](runtime_validation.md).

## Documentation

- [中文文档](README.zh-CN.md)
- [Implementation plan](implementation_plan.md) — architecture and engineering trade-offs
- [Research findings](research_findings.md) — market scan that motivated this design
- [Runtime validation](runtime_validation.md) — what was actually tested, per runtime
- [Benchmarks](benchmarks/README.md) — golden cases and evaluation protocol
- [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md)

## Design principles

- The final report is a derivative; `sources`, `evidence`, `claims` and `conflicts` are the factual foundation. Without evidence, the output is `unknown` or `insufficient` — never fluent filler.
- No bundled search service, model or provider. Runtime capabilities are declared in profiles; missing capabilities degrade transparently and are recorded in the manifest.
- Read-only by default. The skill never requests or modifies permissions, approvals, sandboxes, tool/network configuration, or credentials.

## License

MIT
