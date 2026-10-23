# Show HN 草稿

## Title

```
Show HN: Deep-research skill for coding agents that re-locates every quote on its source page
```

（备选：`Show HN: An auditable deep-research workflow for Claude Code / Codex — every claim links to a verified quote`）

## 首评（text post 正文或 first comment）

> I kept getting burned by AI research reports where the citations were real URLs attached to the wrong claims — or not real at all. 2026 analyses put fabricated-citation rates at 39–55% across AI research tools, and ~78% citation accuracy even for OpenAI Deep Research (links in the README).
>
> So I built a different kind of deep-research skill. It's a pure workflow — no bundled search engine, no API keys — that runs on Claude Code, Codex CLI, OpenCode and other agent hosts, and it treats "verify" as a first-class step:
>
> - N rounds of clarification freeze a research spec before any search (0 rounds in quick mode; assumptions recorded instead)
> - every claim is bound to a located original-text excerpt (claim → evidence → source)
> - `scripts/verify_evidence.py` re-fetches each source and re-locates every quote on the live page; a quote that isn't there anymore (or never was) is flagged, and high-impact claims without a located quote fail the gate
> - conflicts, unknowns and retrieval failures are first-class artifacts, not smoothing noise
> - everything lands in an append-only run bundle you can resume or hand off
>
> There's a complete real run in `examples/deep-dive/` (SQLite vs DuckDB) where the honest outcome is a claim marked `insufficient` — the docs alone don't decide the boundary — plus an HTML report where hovering a citation shows the original quote and its verification badge.
>
> Install: `npx skills add jinlio/deep-research-skill` (or `/plugin marketplace add jinlio/deep-research-skill` in Claude Code).
>
> Repo: https://github.com/jinlio/deep-research-skill
>
> Known trade-offs: it asks a clarifying question where other tools just start (quick mode exists), it produces JSONL ledgers alongside the prose, and PDF quotes can't be re-located automatically yet (marked unverifiable, honestly). Benchmark protocol is defined; first public scored run is pending — I didn't want to put placeholder numbers in the README.
>
> Feedback wanted most on: is `--require-verified` too strict as a default for `deep` mode, and would an offline "audit any report you already have" mode be more useful than the research workflow itself?

## 预期追问与回答要点

- "How is this different from X skill?" → 大多数优化"搜得多"；本项目优化"引用可复核"。逐 claim 回贴定位是确定性脚本，不是提示词请求。
- "Doesn't fetching every source cost tokens/money?" → 核验是宿主脚本的 HTTP 抓取，不走模型；URL 结果缓存在 verification.jsonl，可离线复验。
- "Why Chinese docs?" → 双语仓库；中文来源方法论在 core/references/source-playbook.zh.md，但流程本身语言无关。
