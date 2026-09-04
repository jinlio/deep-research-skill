from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_claim_coverage import check as check_coverage  # noqa: E402
from check_clarification import check as check_clarification  # noqa: E402
from check_run_manifest import check as check_manifest  # noqa: E402
from check_sources import check as check_sources  # noqa: E402
from build_adapters import RUNTIMES, build  # noqa: E402
from evaluate_benchmark import evaluate  # noqa: E402
from init_run import init_run  # noqa: E402
from probe_runtime import probe  # noqa: E402
from scan_sensitive_data import scan as scan_sensitive  # noqa: E402
from validate_artifacts import validate  # noqa: E402
from validate_skill import validate as validate_skill  # noqa: E402


FIXTURE = ROOT / "examples" / "minimal" / "run"


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.run_dir = Path(self.temp.name) / "run"
        shutil.copytree(FIXTURE, self.run_dir)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_fixture_passes_all_gates(self) -> None:
        self.assertTrue(validate(self.run_dir, require_final=True)["ok"])
        self.assertTrue(check_coverage(self.run_dir)["ok"])
        self.assertTrue(check_clarification(self.run_dir)["ok"])
        self.assertTrue(check_sources(self.run_dir)["ok"])
        self.assertTrue(check_manifest(self.run_dir)["ok"])
        self.assertTrue(scan_sensitive(self.run_dir)["ok"])

    def test_duplicate_source_fails(self) -> None:
        source_path = self.run_dir / "sources.jsonl"
        lines = source_path.read_text(encoding="utf-8").splitlines()
        duplicate = json.loads(lines[0])
        duplicate["source_id"] = "S-003"
        lines.append(json.dumps(duplicate))
        source_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = check_sources(self.run_dir)
        self.assertFalse(result["ok"])
        self.assertEqual(len(result["duplicates"]), 1)

    def test_missing_evidence_fails_claim_gate(self) -> None:
        claims_path = self.run_dir / "claims.jsonl"
        claims = [json.loads(line) for line in claims_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        claims[0]["evidence_ids"] = []
        claims_path.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in claims) + "\n", encoding="utf-8")
        self.assertFalse(validate(self.run_dir)["ok"])
        self.assertFalse(check_coverage(self.run_dir)["ok"])

    def test_manifest_rejects_path_escape(self) -> None:
        path = self.run_dir / "run_manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["artifacts"].append({"path": "../outside.txt", "status": "complete"})
        path.write_text(json.dumps(manifest), encoding="utf-8")
        result = check_manifest(self.run_dir)
        self.assertFalse(result["ok"])
        self.assertTrue(any("escapes" in item for item in result["errors"]))

    def test_secret_is_blocked(self) -> None:
        (self.run_dir / "leak.txt").write_text("OPENAI_KEY=sk-abcdefghijklmnopqrstuvwxyz123456\n", encoding="utf-8")
        result = scan_sensitive(self.run_dir)
        self.assertFalse(result["ok"])
        self.assertEqual(result["secrets"][0]["type"], "openai_key")

    def test_unconfirmed_clarification_fails(self) -> None:
        path = self.run_dir / "clarification_log.jsonl"
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if '"user_confirmation"' not in line]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = check_clarification(self.run_dir)
        self.assertFalse(result["ok"])
        self.assertFalse(result["confirmed"])

    def test_orientation_material_cannot_enter_sources(self) -> None:
        path = self.run_dir / "sources.jsonl"
        lines = path.read_text(encoding="utf-8").splitlines()
        record = json.loads(lines[0])
        record["orientation_only"] = True
        lines[0] = json.dumps(record)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = check_clarification(self.run_dir)
        self.assertFalse(result["ok"])
        self.assertTrue(any("orientation_only" in item for item in result["errors"]))

    def test_init_run_creates_preflight_bundle(self) -> None:
        target = Path(self.temp.name) / "new-run"
        manifest = init_run(target, "新问题", "新目标", "quick")
        self.assertTrue((target / "research_spec.yaml").exists())
        self.assertEqual(manifest["status"], "running")
        self.assertTrue(check_clarification(target, require_confirmation=False)["ok"])

    def test_init_run_rejects_overwrite_and_escapes_yaml_text(self) -> None:
        target = Path(self.temp.name) / "safe-run"
        init_run(target, 'question with "quotes"\nand a newline', "goal", "standard")
        with self.assertRaises(FileExistsError):
            init_run(target, "replacement", "goal")
        spec = (target / "research_spec.yaml").read_text(encoding="utf-8")
        self.assertIn('question: "question with \\"quotes\\"\\nand a newline"', spec)

    def test_capability_probe_accepts_complete_profile(self) -> None:
        payload = json.loads((ROOT / "profiles" / "capabilities" / "openclaw.example.json").read_text(encoding="utf-8"))
        result = probe(payload)
        self.assertTrue(result["ok"])
        self.assertEqual(result["mode"], "complete")

    def test_all_capability_fixtures_are_valid(self) -> None:
        fixture_dir = ROOT / "profiles" / "capabilities"
        fixtures = sorted(fixture_dir.glob("*.example.json"))
        self.assertGreaterEqual(len(fixtures), 6)
        for path in fixtures:
            with self.subTest(fixture=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                result = probe(payload)
                self.assertTrue(result["ok"], result)
                self.assertIn(payload["runtime"], set(RUNTIMES))

    def test_capability_probe_reports_safe_degradation(self) -> None:
        payload = {"runtime": "generic", "capabilities": {"load_skill": True, "artifact_io": {"available": True, "append_only": True}}}
        result = probe(payload)
        self.assertTrue(result["ok"])
        self.assertEqual(result["mode"], "serial-degraded")
        self.assertTrue(any(item["capability"] == "delegate" for item in result["degradations"]))

    def test_capability_probe_blocks_external_write(self) -> None:
        payload = {"runtime": "generic", "capabilities": {"load_skill": True, "artifact_io": {"available": True, "append_only": True}}, "permissions": {"external_write_default": True}}
        self.assertFalse(probe(payload)["ok"])

    def test_capability_probe_splits_discovery_and_fetch(self) -> None:
        payload = {
            "runtime": "generic",
            "capabilities": {
                "load_skill": {"available": True, "tested": True, "evidence": ["skill-load"]},
                "discover_sources": {"available": False, "tested": True, "evidence": ["no-search"]},
                "fetch_source": {"available": True, "tested": True, "mode": "webfetch", "evidence": ["fetch-smoke"]},
                "read_source": {"available": True, "tested": True, "evidence": ["read-smoke"]},
                "artifact_io": {"available": True, "tested": True, "append_only": True},
            },
            "permissions": {"external_write_default": False},
        }
        result = probe(payload)
        self.assertTrue(result["ok"])
        self.assertEqual(result["capabilities"]["fetch_source"]["mode"], "webfetch")
        self.assertTrue(any(item["capability"] == "discover_sources" for item in result["degradations"]))

    def test_high_impact_claim_requires_independent_sources(self) -> None:
        claims_path = self.run_dir / "claims.jsonl"
        claims = [json.loads(line) for line in claims_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        claims[0]["impact"] = "high"
        claims[0]["evidence_ids"] = ["E-001", "E-002"]
        claims_path.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in claims) + "\n", encoding="utf-8")
        result = check_coverage(self.run_dir)
        self.assertTrue(result["ok"])

        evidence_path = self.run_dir / "evidence.jsonl"
        evidence = [json.loads(line) for line in evidence_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        evidence[0]["independence_group"] = "example-institution"
        evidence[1]["independence_group"] = "example-institution"
        evidence_path.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in evidence) + "\n", encoding="utf-8")
        result = check_coverage(self.run_dir)
        self.assertFalse(result["ok"])
        self.assertIn("C-001", result["non_independent_evidence"])

    def test_skill_bundle_and_benchmark_fixture_pass(self) -> None:
        self.assertTrue(validate_skill(ROOT)["ok"])
        self.assertTrue(validate_skill(ROOT / "core")["ok"])
        result = evaluate(ROOT / "benchmarks" / "cases", ROOT / "benchmarks" / "fixtures" / "reference_results.jsonl")
        self.assertTrue(result["ok"])
        self.assertEqual(result["aggregate_score"], 1.0)

    def test_adapter_builds_self_contained_packages(self) -> None:
        output = Path(self.temp.name) / "dist"
        result = build(ROOT, output)
        self.assertEqual(result["runtimes"], list(RUNTIMES))
        for runtime in RUNTIMES:
            package = output / runtime / "deep-research"
            self.assertTrue(validate_skill(package)["ok"], runtime)
            self.assertTrue((package / "references" / "workflow.md").exists())
            self.assertTrue((package / "scripts" / "run_gates.py").exists())
            self.assertTrue((package / "protocol" / "capability.schema.json").exists())


if __name__ == "__main__":
    unittest.main()
