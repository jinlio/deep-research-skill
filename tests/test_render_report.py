from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_report import render  # noqa: E402

DEEP_DIVE = ROOT / "examples" / "deep-dive" / "run"


class RenderReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.out = Path(self.temp.name) / "report.html"
        # Copy the example bundle: local security hooks re-run network
        # verification against the tracked copy and append passes to it,
        # so assertions must not read the working-tree file directly.
        self.run_dir = Path(self.temp.name) / "run"
        shutil.copytree(DEEP_DIVE, self.run_dir)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_renders_real_example_with_hover_cards(self) -> None:
        result = render(self.run_dir, self.out)
        self.assertTrue(result["ok"], result.get("errors"))
        html = self.out.read_text(encoding="utf-8")
        self.assertIn("Evidence chain: 7 verified", html)
        self.assertIn("SQLite competes with fopen()", html)
        self.assertIn("✅ verified", html)
        self.assertIn("Why DuckDB", html)

    def test_ledger_content_is_escaped(self) -> None:
        import json
        run_dir = Path(self.temp.name) / "synthetic-run"
        run_dir.mkdir(parents=True)
        (run_dir / "final_report.md").write_text("# T\n\n[C-001] claim\n", encoding="utf-8")
        (run_dir / "sources.jsonl").write_text(json.dumps({"source_id": "S-001", "url": "https://x", "title": "t"}), encoding="utf-8")
        (run_dir / "evidence.jsonl").write_text(json.dumps({"evidence_id": "E-001", "source_id": "S-001", "quote": "<script>alert(1)</script>"}), encoding="utf-8")
        (run_dir / "claims.jsonl").write_text(json.dumps({"claim_id": "C-001", "text": "<img src=x onerror=alert(1)>", "status": "supported", "evidence_ids": ["E-001"]}), encoding="utf-8")
        result = render(run_dir, self.out)
        self.assertTrue(result["ok"])
        html = self.out.read_text(encoding="utf-8")
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertNotIn("<img src=x", html)
        self.assertIn("&lt;script&gt;", html)

    def test_missing_report_fails_cleanly(self) -> None:
        run_dir = Path(self.temp.name) / "empty"
        run_dir.mkdir()
        self.assertFalse(render(run_dir, self.out)["ok"])


if __name__ == "__main__":
    unittest.main()
