from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_evidence import (  # noqa: E402
    FetchResult,
    assert_public_http_url,
    check_claims,
    extract_text,
    locate_quote,
    normalize,
    verify_run,
)


PAGE = """<html><head><style>.x{color:red}</style><script>var a=1;</script></head>
<body><h1>Quarterly Report</h1>
<p>Revenue reached 1.2 billion USD in the third quarter, driven by cloud growth.</p>
<p>研究显示，该方案在对照实验中将错误率降低了 37%（p&lt;0.05）。</p>
</body></html>"""

PLAIN = "The library ships with zero third-party dependencies and runs on Python 3.11+."


class FakeFetcher:
    """Deterministic fetcher keyed by URL prefix; no network access."""

    def __init__(self, pages: dict[str, bytes], errors: dict[str, str] | None = None) -> None:
        self.pages = pages
        self.errors = errors or {}

    def __call__(self, url: str, timeout: float, max_bytes: int) -> FetchResult:
        if url in self.errors:
            return FetchResult(None, b"", url, self.errors[url])
        if url not in self.pages:
            return FetchResult(404, b"", url, "http 404")
        return FetchResult(200, self.pages[url], url, None)


def write_run(run_dir: Path, sources: list[dict], evidence: list[dict], claims: list[dict] | None = None) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "sources.jsonl").write_text("\n".join(json.dumps(item) for item in sources) + "\n", encoding="utf-8")
    (run_dir / "evidence.jsonl").write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in evidence) + "\n", encoding="utf-8")
    (run_dir / "claims.jsonl").write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in (claims or [])) + "\n", encoding="utf-8")


class VerifyEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.run_dir = Path(self.temp.name) / "run"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_normalize_folds_punctuation_and_width(self) -> None:
        self.assertEqual(normalize("Hello, world!"), normalize("hello world"))
        self.assertEqual(normalize("错误率降低了 37%（p＜0.05）。"), normalize("错误率降低了37%(p<0.05)"))

    def test_exact_and_ellipsis_and_cjk_matches(self) -> None:
        text, note = extract_text(PAGE.encode("utf-8"))
        self.assertIsNone(note)
        self.assertEqual(locate_quote(text, "Revenue reached 1.2 billion USD in the third quarter")[0], "verified")
        status, _, method = locate_quote(text, "Revenue reached 1.2 billion USD … driven by cloud growth.")
        self.assertEqual(status, "verified")
        self.assertEqual(method, "ordered_segments")
        self.assertEqual(locate_quote(text, "该方案在对照实验中将错误率降低了 37%（p<0.05）")[0], "verified")

    def test_fabricated_quote_is_mismatch(self) -> None:
        text, _ = extract_text(PAGE.encode("utf-8"))
        status, ratio, _ = locate_quote(text, "Revenue reached 9.9 trillion USD according to internal leaks")
        self.assertEqual(status, "mismatch")
        self.assertLess(ratio, 0.85)

    def test_network_run_verifies_and_fabricates(self) -> None:
        write_run(
            self.run_dir,
            sources=[{"source_id": "S-001", "url": "https://example.com/report", "retrieval_status": "ok"}],
            evidence=[
                {"evidence_id": "E-001", "source_id": "S-001", "quote": "Revenue reached 1.2 billion USD in the third quarter."},
                {"evidence_id": "E-002", "source_id": "S-001", "quote": "An internal leak admits the numbers were invented."},
            ],
        )
        fetcher = FakeFetcher({"https://example.com/report": PAGE.encode("utf-8")})
        result = verify_run(self.run_dir, fetcher=fetcher)
        self.assertTrue(result["ok"], result["errors"])
        summary = result["verified"]
        self.assertEqual(summary["verified"], 1)
        self.assertEqual(summary["mismatch"], 1)
        records = [json.loads(line) for line in (self.run_dir / "verification.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(records[0]["status"], "verified")
        self.assertEqual(records[1]["status"], "mismatch")
        self.assertTrue(records[0]["content_sha256"])

    def test_require_verified_fails_on_fabrication(self) -> None:
        write_run(
            self.run_dir,
            sources=[{"source_id": "S-001", "url": "https://example.com/report"}],
            evidence=[{"evidence_id": "E-001", "source_id": "S-001", "quote": "An internal leak admits the numbers were invented."}],
            claims=[{"claim_id": "C-001", "impact": "high", "status": "supported", "evidence_ids": ["E-001"]}],
        )
        fetcher = FakeFetcher({"https://example.com/report": PAGE.encode("utf-8")})
        verify_run(self.run_dir, fetcher=fetcher)
        counts, _ = check_claims(self.run_dir)
        self.assertEqual(counts.get("mismatch"), 1)

    def test_unavailable_and_pdf_and_local(self) -> None:
        write_run(
            self.run_dir,
            sources=[
                {"source_id": "S-001", "url": "https://example.com/down"},
                {"source_id": "S-002", "url": "https://example.com/paper.pdf"},
                {"source_id": "S-003", "url": "material.txt"},
            ],
            evidence=[
                {"evidence_id": "E-001", "source_id": "S-001", "quote": "anything at all here"},
                {"evidence_id": "E-002", "source_id": "S-002", "quote": "anything at all here"},
                {"evidence_id": "E-003", "source_id": "S-003", "quote": "zero third-party dependencies"},
            ],
        )
        (self.run_dir / "material.txt").write_text(PLAIN, encoding="utf-8")
        fetcher = FakeFetcher(
            {"https://example.com/paper.pdf": b"%PDF-1.7 fake"},
            errors={"https://example.com/down": "http 500"},
        )
        result = verify_run(self.run_dir, fetcher=fetcher)
        records = {json.loads(line)["evidence_id"]: json.loads(line) for line in (self.run_dir / "verification.jsonl").read_text(encoding="utf-8").splitlines()}
        self.assertEqual(records["E-001"]["status"], "unavailable")
        self.assertEqual(records["E-002"]["status"], "unverifiable")
        self.assertEqual(records["E-002"]["error"], "pdf_text_extraction_unsupported")
        self.assertEqual(records["E-003"]["status"], "verified")
        self.assertTrue(result["ok"])

    def test_local_source_cannot_escape_run_directory(self) -> None:
        write_run(
            self.run_dir,
            sources=[{"source_id": "S-001", "url": "../../etc/passwd"}],
            evidence=[{"evidence_id": "E-001", "source_id": "S-001", "quote": "root"}],
        )
        verify_run(self.run_dir, fetcher=FakeFetcher({}))
        records = [json.loads(line) for line in (self.run_dir / "verification.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(records[0]["status"], "unavailable")
        self.assertIn("escapes", records[0]["error"])

    def test_offline_check_requires_full_coverage(self) -> None:
        write_run(
            self.run_dir,
            sources=[{"source_id": "S-001", "url": "https://example.com/report"}],
            evidence=[{"evidence_id": "E-001", "source_id": "S-001", "quote": "Revenue reached 1.2 billion USD in the third quarter."}],
        )
        result = verify_run(self.run_dir, fetcher=FakeFetcher({}), offline=True)
        self.assertFalse(result["ok"])
        self.assertTrue(any("missing records" in item for item in result["errors"]))

        fetcher = FakeFetcher({"https://example.com/report": PAGE.encode("utf-8")})
        verify_run(self.run_dir, fetcher=fetcher)
        result = verify_run(self.run_dir, fetcher=FakeFetcher({}), offline=True)
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["verified"]["verified"], 1)

    def test_ssrf_guard_blocks_private_hosts(self) -> None:
        for url in (
            "http://127.0.0.1/x",
            "http://localhost/x",
            "http://10.1.2.3/x",
            "http://192.168.1.1/x",
            "http://169.254.169.254/latest/meta-data",
            "http://[::1]/x",
            "ftp://example.com/file",
            "file:///etc/passwd",
        ):
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    assert_public_http_url(url)
        assert_public_http_url("https://example.com/page")  # must not raise

    def test_dns_resolving_to_loopback_is_blocked(self) -> None:
        import socket
        original = socket.getaddrinfo

        def fake_getaddrinfo(host, port, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
            if host == "rebind.example":
                return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", port))]
            return original(host, port, *args, **kwargs)

        socket.getaddrinfo = fake_getaddrinfo
        try:
            with self.assertRaises(ValueError):
                assert_public_http_url("http://rebind.example/x")
        finally:
            socket.getaddrinfo = original


if __name__ == "__main__":
    unittest.main()
