# Reddit r/ClaudeAI 帖子草稿

## Title

```
I built a deep-research skill for Claude Code where every citation is re-verified against the live source page
```

## 正文

> Every AI research report I got had the same problem: citations that look real until you open them. So I built a skill that treats that as the core failure to fix, not a footnote.
>
> **What it does differently:** after the research finishes, `verify_evidence.py` re-fetches every cited source and checks that each quoted excerpt actually appears on the page (fuzzy matching handles formatting; CJK-aware). Quotes that don't come back are flagged `mismatch`/`unavailable` — and in strict mode, high-impact claims without a verified quote block delivery. It's deterministic Python (stdlib only), not a model judging itself.
>
> **The workflow around it:**
> - asks N clarifying questions first and freezes a spec you confirm (there's a `quick` mode with 0 questions — assumptions recorded instead)
> - every claim is bound to a located quote with page/section locators in an append-only run bundle (sources/evidence/claims/conflicts .jsonl)
> - conflicts and "insufficient evidence" are delivered as such — my example run ends with a claim honestly marked insufficient because the official docs alone don't answer it
> - works on Claude Code (`npx skills add jinlio/deep-research-skill` or `/plugin marketplace add jinlio/deep-research-skill`), Codex CLI, OpenCode, other agents
>
> There's a complete real example in the repo (SQLite vs DuckDB for embedded analytics) with an HTML report where hovering a citation shows the original quote + a verified badge.
>
> Repo: https://github.com/jinlio/deep-research-skill
>
> Honest limits: it's slower than a plain search because it builds an audit trail; PDFs can't be auto-verified yet; first public benchmark run is still pending so I'm not quoting accuracy numbers.
>
> What would make you actually install something like this? Would an "audit a report I already have from ChatGPT/Gemini" mode be more useful than the full workflow?

## 发布注意

- Flair 选 "Resources" 或 "Tips & Reviews"（按当时版规）。
- 不用短链；直接给 GitHub 链接。
- 准备好回答 "why not just use built-in Research"：内置工具不给你逐 claim 的账本和离线复验；这个 skill 在你的 CLI 里跑、工件留在本地。
