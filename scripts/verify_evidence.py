"""Verify evidence quotes against their registered sources by re-locating the quote text.

Network mode fetches each source URL, extracts page text, and checks whether the
registered original-text excerpt actually appears on the page. Results are appended
to verification.jsonl; --require-verified enforces that high-impact claims keep at
least one located quote. The script is dependency-free and never performs writes
beyond its own verification.jsonl artifact.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import ipaddress
import json
import re
import socket
import sys
import unicodedata
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from common import load_jsonl, write_result

VERIFIED_STATUSES = {"verified", "verified_fuzzy"}
KNOWN_STATUSES = VERIFIED_STATUSES | {"mismatch", "unavailable", "unverifiable"}
USER_AGENT = "deep-research-skill-verify/0.3 (+https://github.com/jinlio/deep-research-skill)"
BLOCK_ELEMENTS = {
    "p", "div", "section", "article", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6",
    "blockquote", "pre", "br", "td", "th", "table", "ul", "ol", "header", "footer",
}
SKIP_ELEMENTS = {"script", "style", "noscript", "template", "svg", "head"}


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        if tag in SKIP_ELEMENTS:
            self._skip_depth += 1
        elif tag in BLOCK_ELEMENTS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIP_ELEMENTS and self._skip_depth > 0:
            self._skip_depth -= 1
        elif tag in BLOCK_ELEMENTS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self.parts.append(data)


def html_to_text(html: str) -> str:
    extractor = _TextExtractor()
    try:
        extractor.feed(html)
        extractor.close()
    except Exception:
        return html
    return "".join(extractor.parts)


def normalize(text: str) -> str:
    """Fold quotes for matching: NFKC, casefold, drop every non-word character.

    Dropping punctuation and whitespace merges CJK and Latin text uniformly and
    neutralizes curly-vs-straight quotes, full-width punctuation and line wraps.
    """
    folded = unicodedata.normalize("NFKC", text).casefold()
    return re.sub(r"[^\w]+", "", folded, flags=re.UNICODE)


def _segment_quote(quote: str) -> list[str]:
    segments = [part for part in re.split(r"(\.{2,}|…|\[\.\.\.\]|\[\.\.\.\])", quote) if part]
    pieces: list[str] = []
    for part in segments:
        if re.fullmatch(r"(\.{2,}|…|\[\.\.\.\]|\[\.\.\.\])", part):
            continue
        folded = normalize(part)
        if len(folded) >= 8:
            pieces.append(folded)
    return pieces or ([normalize(quote)] if normalize(quote) else [])


def locate_quote(page_text: str, quote: str) -> tuple[str, float, str]:
    """Return (status, ratio, method) for one quote against one page text."""
    folded_page = normalize(page_text)
    segments = _segment_quote(quote)
    if not segments:
        return "unverifiable", 0.0, "empty_quote"
    cursor = 0
    covered = 0
    for segment in segments:
        index = folded_page.find(segment, cursor)
        if index < 0:
            break
        covered += len(segment)
        cursor = index + len(segment)
    if covered == sum(len(segment) for segment in segments):
        return "verified", 1.0, "ordered_segments"
    ratio = _best_window_ratio(folded_page, normalize(quote))
    if ratio >= 0.85:
        return "verified_fuzzy", round(ratio, 4), "window_ratio"
    return "mismatch", round(ratio, 4), "window_ratio"


def _best_window_ratio(page: str, quote: str, max_page: int = 240000, max_windows: int = 400) -> float:
    if len(page) > max_page:
        page = page[:max_page]
    if not quote:
        return 0.0
    if len(page) < len(quote) // 2:
        return difflib.SequenceMatcher(None, page, quote).ratio()
    window = min(len(quote) * 3, len(page))
    stride = max(len(quote) // 2, (len(page) - window) // max_windows + 1, 1)
    best = 0.0
    for start in range(0, len(page) - window + 1, stride):
        candidate = page[start : start + window]
        matcher = difflib.SequenceMatcher(None, candidate, quote)
        if matcher.real_quick_ratio() < best:
            continue
        best = max(best, matcher.ratio())
        if best >= 0.99:
            break
    return best


def assert_public_http_url(url: str) -> None:
    """Reject non-http(s) schemes and hosts that resolve to loopback, private or reserved IPs.

    The hostname string alone is not trusted: DNS is resolved and every returned
    address must be globally routable, so 'localhost' and rebinding-style lookups
    are both refused before any request is made.
    """
    parsed = urllib_parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"unsupported URL scheme '{parsed.scheme or '(none)'}'")
    host = parsed.hostname
    if not host:
        raise ValueError("URL has no host")
    try:
        infos = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"DNS resolution failed for '{host}': {exc}") from exc
    for info in infos:
        address = info[4][0]
        ip = ipaddress.ip_address(address.split("%")[0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            raise ValueError(f"host '{host}' resolves to a non-public address ({ip})")


class FetchResult:
    def __init__(self, status: int | None, content: bytes, final_url: str, error: str | None) -> None:
        self.status = status
        self.content = content
        self.final_url = final_url
        self.error = error


def default_fetcher(url: str, timeout: float, max_bytes: int) -> FetchResult:
    assert_public_http_url(url)
    request = urllib_request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,text/plain,application/pdf;q=0.5,*/*;q=0.1"})
    try:
        with urllib_request.urlopen(request, timeout=timeout) as response:
            return FetchResult(response.status, response.read(max_bytes), response.geturl(), None)
    except urllib_error.HTTPError as exc:
        return FetchResult(exc.code, b"", url, f"http {exc.code}")
    except Exception as exc:  # noqa: BLE001 - report any fetch failure as a status, not a crash
        return FetchResult(None, b"", url, str(exc))


def _read_local(path: Path) -> FetchResult:
    try:
        return FetchResult(200, path.read_bytes(), str(path), None)
    except OSError as exc:
        return FetchResult(None, b"", str(path), str(exc))


def fetch_source(source: dict, run_dir: Path, fetcher, timeout: float, max_bytes: int) -> FetchResult:
    raw = source.get("url") or source.get("path") or ""
    value = str(raw).strip()
    if value.startswith("file://"):
        local = Path(urllib_parse.urlparse(value).path if urllib_parse.urlparse(value).netloc == "" else value[len("file://") :])
        return _read_local(local)
    parsed = urllib_parse.urlsplit(value)
    if parsed.scheme in {"http", "https"}:
        return fetcher(value, timeout, max_bytes)
    if not parsed.scheme and value:
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = (run_dir / candidate).resolve()
        allowed_roots = {run_dir.resolve(), Path.cwd().resolve()}
        if not any(root in candidate.parents or candidate == root for root in allowed_roots):
            return FetchResult(None, b"", value, "local source escapes run directory and working directory")
        return _read_local(candidate)
    return FetchResult(None, b"", value, "no fetchable url/path")


def extract_text(content: bytes) -> tuple[str, str | None]:
    if content.startswith(b"%PDF"):
        return "", "pdf_text_extraction_unsupported"
    sample = content[:4096].lower()
    if b"<html" in sample or b"<!doctype html" in sample or b"<body" in sample:
        return html_to_text(content.decode("utf-8", errors="replace")), None
    try:
        return content.decode("utf-8"), None
    except UnicodeDecodeError:
        return content.decode("latin-1", errors="replace"), None


def verify_run(
    run_dir: Path,
    fetcher=None,
    timeout: float = 10.0,
    max_bytes: int = 2_000_000,
    min_ratio: float = 0.85,
    offline: bool = False,
) -> dict:
    """Verify every evidence record; offline mode re-checks an existing verification.jsonl."""
    fetcher = fetcher or (lambda url, t, m: default_fetcher(url, t, m))
    sources, source_errors = load_jsonl(run_dir / "sources.jsonl")
    evidence, evidence_errors = load_jsonl(run_dir / "evidence.jsonl")
    errors = source_errors + evidence_errors
    by_source = {str(item.get("source_id")): item for item in sources if item.get("source_id")}

    if offline:
        existing, parse_errors = load_jsonl(run_dir / "verification.jsonl")
        errors.extend(parse_errors)
        latest: dict[str, dict] = {}
        for record in existing:
            evidence_id = str(record.get("evidence_id"))
            if evidence_id:
                latest[evidence_id] = record
        missing = [str(item.get("evidence_id")) for item in evidence if str(item.get("evidence_id")) not in latest]
        if missing:
            errors.append(f"verification.jsonl is missing records for evidence: {', '.join(missing)}")
        for evidence_id, record in latest.items():
            if record.get("status") not in KNOWN_STATUSES:
                errors.append(f"verification[{evidence_id}]: unknown status '{record.get('status')}'")
        summary = _status_counts(latest)
        return {"ok": not errors, "mode": "offline-check", "verified": summary, "missing": missing, "errors": errors, "warnings": []}

    records: list[dict] = []
    warnings: list[str] = []
    checked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    for index, item in enumerate(evidence, 1):
        evidence_id = str(item.get("evidence_id", f"row-{index}"))
        source = by_source.get(str(item.get("source_id")))
        quote = str(item.get("quote") or item.get("excerpt") or "")
        record: dict = {"evidence_id": evidence_id, "source_id": item.get("source_id"), "status": "unverifiable", "method": "none", "ratio": 0.0, "checked_at": checked_at}
        if not source:
            record["error"] = "evidence references unknown source"
        elif not quote.strip():
            record["error"] = "evidence has no quote to locate"
        else:
            result = fetch_source(source, run_dir, fetcher, timeout, max_bytes)
            record["fetched_url"] = result.final_url
            if result.error:
                record["status"] = "unavailable"
                record["error"] = result.error
            else:
                record["content_sha256"] = hashlib.sha256(result.content).hexdigest()
                page_text, extraction_note = extract_text(result.content)
                if extraction_note:
                    record["error"] = extraction_note
                else:
                    status, ratio, method = locate_quote(page_text, quote)
                    if ratio < min_ratio and status == "verified_fuzzy":
                        status = "mismatch"
                    record.update({"status": status, "ratio": ratio, "method": method})
        if record["status"] == "mismatch":
            warnings.append(f"{evidence_id}: quote not found on source page; the excerpt may be fabricated or the page may have changed")
        if record["status"] in {"unavailable", "unverifiable"} and record.get("error"):
            warnings.append(f"{evidence_id}: could not verify ({record['error']})")
        records.append(record)

    output_path = run_dir / "verification.jsonl"
    with output_path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    latest: dict[str, dict] = {}
    for record in records:
        latest[str(record.get("evidence_id"))] = record
    summary = _status_counts(latest)
    return {"ok": not errors, "mode": "network", "verified": summary, "records": len(records), "errors": errors, "warnings": warnings}


def _status_counts(latest: dict[str, dict]) -> dict[str, int]:
    counts = {status: 0 for status in sorted(KNOWN_STATUSES)}
    for record in latest.values():
        status = record.get("status")
        if status in counts:
            counts[status] += 1
    return counts


def check_claims(run_dir: Path) -> tuple[dict[str, int], list[str]]:
    """Require high-impact claims to keep at least one located quote; warn for the rest."""
    claims, claim_errors = load_jsonl(run_dir / "claims.jsonl")
    errors = list(claim_errors)
    existing, _ = load_jsonl(run_dir / "verification.jsonl")
    latest: dict[str, str] = {}
    for record in existing:
        evidence_id = str(record.get("evidence_id"))
        if evidence_id:
            latest[evidence_id] = str(record.get("status"))
    counts = _status_counts({evidence_id: {"status": status} for evidence_id, status in latest.items()})
    warnings: list[str] = []
    for claim in claims:
        evidence_ids = [str(value) for value in claim.get("evidence_ids", []) if str(value)]
        verified = [evidence_id for evidence_id in evidence_ids if latest.get(evidence_id) in VERIFIED_STATUSES]
        if claim.get("impact") == "high" and claim.get("status") in {"supported", "partially_supported"} and not verified:
            errors.append(f"claim {claim.get('claim_id')}: high-impact claim has no verified evidence")
        elif claim.get("status") in {"supported", "partially_supported"} and evidence_ids and not verified:
            warnings.append(f"claim {claim.get('claim_id')}: no verified evidence (statuses: {[latest.get(e) for e in evidence_ids]})")
    return counts, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--max-bytes", type=int, default=2_000_000)
    parser.add_argument("--min-ratio", type=float, default=0.85)
    parser.add_argument("--offline-check", action="store_true", help="validate an existing verification.jsonl without network access")
    parser.add_argument("--require-verified", action="store_true", help="fail unless high-impact claims keep at least one verified evidence")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    result = verify_run(run_dir, timeout=args.timeout, max_bytes=args.max_bytes, min_ratio=args.min_ratio, offline=args.offline_check)
    if args.require_verified:
        counts, warnings = check_claims(run_dir)
        result["verified"] = counts
        result["warnings"] = result.get("warnings", []) + warnings
        result["require_verified"] = True
        if counts.get("mismatch", 0):
            result["errors"].append("at least one evidence quote was not found on its source page")
    write_result(args.output, result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
