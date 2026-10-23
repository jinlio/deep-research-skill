"""Render a run bundle's final_report.md into a self-contained HTML evidence-chain report.

Citation tokens in the report ([C-xxx] / [S-xxx]) become hover cards that show the
claim's status plus the located original-text quotes and their verification badges
from verification.jsonl. Everything is generated server-side with the standard
library only; all ledger content is HTML-escaped.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

from common import load_jsonl, write_result

CITE_RE = re.compile(r"\[(C-[A-Za-z0-9_-]+|S-[A-Za-z0-9_-]+)\]")


def _badge(status: str | None) -> str:
    labels = {
        "verified": ("✅ verified", "ok"),
        "verified_fuzzy": ("✅ fuzzy match", "ok"),
        "mismatch": ("⛔ not found on page", "bad"),
        "unavailable": ("⚠️ source unreachable", "warn"),
        "unverifiable": ("⚠️ unverifiable", "warn"),
    }
    if status is None:
        return '<span class="badge warn">· not checked</span>'
    label, kind = labels.get(status, (status, "warn"))
    return f'<span class="badge {kind}">{label}</span>'


def _load_ledger(run_dir: Path) -> tuple[dict[str, dict], dict[str, dict], dict[str, dict], dict[str, str]]:
    sources = {str(item.get("source_id")): item for item in load_jsonl(run_dir / "sources.jsonl")[0] if item.get("source_id")}
    evidence = {str(item.get("evidence_id")): item for item in load_jsonl(run_dir / "evidence.jsonl")[0] if item.get("evidence_id")}
    claims = {str(item.get("claim_id")): item for item in load_jsonl(run_dir / "claims.jsonl")[0] if item.get("claim_id")}
    verification: dict[str, str] = {}
    path = run_dir / "verification.jsonl"
    if path.exists():
        for record in load_jsonl(path)[0]:
            evidence_id = str(record.get("evidence_id"))
            if evidence_id:
                verification[evidence_id] = str(record.get("status"))
    return claims, evidence, sources, verification


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _claim_card(claim_id: str, claims: dict, evidence: dict, sources: dict, verification: dict) -> str | None:
    claim = claims.get(claim_id)
    if not claim:
        return None
    rows = []
    for evidence_id in claim.get("evidence_ids", []):
        item = evidence.get(str(evidence_id))
        if not item:
            continue
        source = sources.get(str(item.get("source_id")), {})
        rows.append(
            '<div class="ev"><div class="ev-quote">“{quote}”</div>'
            '<div class="ev-meta">{source} · {location} {badge}</div></div>'.format(
                quote=_esc(item.get("quote", "")),
                source=_esc(source.get("title", item.get("source_id", ""))),
                location=_esc(item.get("location", "")),
                badge=_badge(verification.get(str(evidence_id))),
            )
        )
    status = _esc(claim.get("status", "unknown"))
    impact = _esc(claim.get("impact", "medium"))
    return (
        '<span class="cite claim"><code>{cid}</code><span class="pop">'
        '<b>{cid}</b> · {status} · impact {impact} · confidence {confidence}<br>{text}'
        '<div class="evs">{rows}</div></span></span>'
    ).format(
        cid=_esc(claim_id),
        status=status,
        impact=impact,
        confidence=_esc(claim.get("confidence", "-")),
        text=_esc(claim.get("text", "")),
        rows="".join(rows),
    )


def _source_card(source_id: str, sources: dict, evidence: dict, verification: dict) -> str | None:
    source = sources.get(source_id)
    if not source:
        return None
    badges = []
    for evidence_id, item in sorted(evidence.items()):
        if str(item.get("source_id")) == source_id:
            badges.append(_badge(verification.get(evidence_id)))
    counts: dict[str, int] = {}
    for badge in badges:
        label = re.sub(r"<[^>]+>", "", badge)
        counts[label] = counts.get(label, 0) + 1
    summary = ", ".join(f"{count}×{label.strip()}" for label, count in sorted(counts.items())) or "no evidence"
    return (
        '<span class="cite src"><code>{sid}</code><span class="pop"><b>{title}</b><br>'
        '<a href="{url}">{url}</a><br>{kind} · {summary}</span></span>'
    ).format(
        sid=_esc(source_id),
        title=_esc(source.get("title", "")),
        url=_esc(source.get("url", "")),
        kind=_esc(source.get("source_type", "source")),
        summary=_esc(summary),
    )


def _inline(text: str) -> str:
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def _render_markdown(markdown: str, claims: dict, evidence: dict, sources: dict, verification: dict) -> str:
    """Markdown subset: headings, paragraphs, lists, blockquotes, tables, fenced code."""
    out: list[str] = []
    lines = markdown.splitlines()
    index = 0
    in_code = False
    code_buffer: list[str] = []
    while index < len(lines):
        line = lines[index]
        if line.strip().startswith("```"):
            if in_code:
                out.append("<pre><code>" + _esc("\n".join(code_buffer)) + "</code></pre>")
                code_buffer = []
            in_code = not in_code
            index += 1
            continue
        if in_code:
            code_buffer.append(line)
            index += 1
            continue
        heading = re.match(r"^(#{1,4})\s+(.*)$", line)
        if heading:
            level = len(heading.group(1)) + 1
            out.append(f"<h{level}>{_inline(_esc(heading.group(2)))}</h{level}>")
            index += 1
            continue
        if line.strip() == "":
            index += 1
            continue
        if line.lstrip().startswith("- "):
            items = []
            while index < len(lines) and lines[index].lstrip().startswith("- "):
                items.append(lines[index].lstrip()[2:])
                index += 1
            out.append("<ul>" + "".join(f"<li>{_cite(_inline(_esc(item)), claims, evidence, sources, verification)}</li>" for item in items) + "</ul>")
            continue
        if line.strip().startswith("|") and index + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[index + 1]):
            header = [cell.strip() for cell in line.strip().strip("|").split("|")]
            index += 2
            body_rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                body_rows.append([cell.strip() for cell in lines[index].strip().strip("|").split("|")])
                index += 1
            head_html = "<tr>" + "".join(f"<th>{_cite(_inline(_esc(cell)), claims, evidence, sources, verification)}</th>" for cell in header) + "</tr>"
            body_html = "".join(
                "<tr>" + "".join(f"<td>{_cite(_inline(_esc(cell)), claims, evidence, sources, verification)}</td>" for cell in row) + "</tr>"
                for row in body_rows
            )
            out.append(f"<table>{head_html}{body_html}</table>")
            continue
        if line.startswith(">"):
            out.append(f"<blockquote>{_cite(_inline(_esc(line[1:].strip())), claims, evidence, sources, verification)}</blockquote>")
            index += 1
            continue
        paragraph: list[str] = []
        while index < len(lines) and lines[index].strip() != "" and not re.match(r"^(#{1,4}\s|[-*]\s|\||>|```)", lines[index]):
            paragraph.append(lines[index])
            index += 1
        out.append(f"<p>{_cite(_inline(_esc(' '.join(paragraph))), claims, evidence, sources, verification)}</p>")
    return "\n".join(out)


def _cite(text: str, claims: dict, evidence: dict, sources: dict, verification: dict) -> str:
    def replace(match: re.Match) -> str:
        token = match.group(1)
        if token.startswith("C-"):
            card = _claim_card(token, claims, evidence, sources, verification)
        else:
            card = _source_card(token, sources, evidence, verification)
        return card or match.group(0)

    return CITE_RE.sub(replace, text)


def _summary(verification: dict) -> str:
    counts: dict[str, int] = {}
    for status in verification.values():
        counts[status] = counts.get(status, 0) + 1
    pieces = [f"{count} {status}" for status, count in sorted(counts.items())]
    return " · ".join(pieces) if pieces else "verification.jsonl not present — run scripts/verify_evidence.py"


CSS = """
:root { --ink:#1a2233; --muted:#5b6472; --line:#e3e7ee; --bg:#ffffff; --pop:#101828; --ok:#0a7d4f; --warn:#9a6700; --bad:#b3261e; }
* { box-sizing: border-box; }
body { font-family: -apple-system, 'Segoe UI', 'Noto Sans CJK SC', sans-serif; color: var(--ink); background: var(--bg); margin: 0; }
main { max-width: 860px; margin: 0 auto; padding: 2.5rem 1.25rem 4rem; line-height: 1.65; }
h1 { font-size: 1.7rem; } h2 { margin-top: 2.2em; border-bottom: 1px solid var(--line); padding-bottom: .3em; }
code { background: #f2f4f8; padding: .1em .35em; border-radius: 4px; font-size: .92em; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; } th, td { border: 1px solid var(--line); padding: .45em .7em; text-align: left; }
blockquote { border-left: 3px solid var(--line); margin: 0; padding-left: 1em; color: var(--muted); }
.summary { color: var(--muted); font-size: .9rem; border: 1px solid var(--line); border-radius: 8px; padding: .6em .9em; margin: 1.2em 0; }
.cite { position: relative; }
.cite code { cursor: help; }
.cite .pop { display: none; position: absolute; left: 0; top: 1.5em; z-index: 5; width: 26rem; max-width: 78vw;
  background: var(--pop); color: #e8ecf3; border-radius: 10px; padding: .8em 1em; font-size: .82rem; line-height: 1.5;
  box-shadow: 0 10px 30px rgba(8, 12, 24, .35); }
.cite:hover .pop, .cite:focus-within .pop { display: block; }
.cite .pop a { color: #9ec1ff; word-break: break-all; }
.cite .ev { margin-top: .55em; border-top: 1px solid rgba(255,255,255,.14); padding-top: .45em; }
.cite .ev-quote { font-style: italic; }
.cite .ev-meta { color: #a7b0bf; font-size: .78rem; margin-top: .15em; }
.badge { border-radius: 999px; padding: .05em .55em; font-size: .74rem; white-space: nowrap; }
.badge.ok { background: rgba(16,185,129,.18); color: #34d399; }
.badge.warn { background: rgba(234,179,8,.16); color: #fbbf24; }
.badge.bad { background: rgba(239,68,68,.18); color: #f87171; }
"""


def render(run_dir: Path, output: Path | None = None) -> dict:
    run_dir = run_dir.resolve()
    report_path = run_dir / "final_report.md"
    if not report_path.exists():
        return {"ok": False, "errors": ["missing final_report.md"]}
    claims, evidence, sources, verification = _load_ledger(run_dir)
    body = _render_markdown(report_path.read_text(encoding="utf-8"), claims, evidence, sources, verification)
    target = output or run_dir / "final_report.html"
    document = (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>{title}</title><style>{css}</style></head><body><main>"
        '<div class="summary">Evidence chain: {summary}</div>{body}</main></body></html>'
    ).format(title=_esc(run_dir.name + " — research report"), css=CSS, summary=_esc(_summary(verification)), body=body)
    target.write_text(document, encoding="utf-8")
    return {"ok": True, "output": str(target), "claims": len(claims), "evidence": len(evidence), "sources": len(sources), "verification": verification}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = render(args.run_dir, args.output)
    if not result.get("ok"):
        result.setdefault("errors", ["render failed"])
        write_result(None, result)
        return 1
    write_result(None, result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
