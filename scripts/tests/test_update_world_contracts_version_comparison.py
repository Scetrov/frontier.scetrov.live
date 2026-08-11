#!/usr/bin/env python3
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "update-world-contracts-version-comparison.py"
spec = importlib.util.spec_from_file_location("comparison", SCRIPT)
comparison = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = comparison
spec.loader.exec_module(comparison)


def command(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


def chapter_text(v0, v1, base, body=""):
    return f"+++\ntitle = 'Comparison'\ncomparison_schema = 1\nupstream_repository = 'evefrontier/world-contracts'\ncomparison_mode = 'tip-to-tip'\nv0_ref = 'main'\nv0_reviewed_commit = '{v0}'\nv1_ref = 'dev'\nv1_reviewed_commit = '{v1}'\nmerge_base_commit = '{base}'\nreviewed_at = '2026-08-10T00:00:00Z'\nreview_status = 'complete'\n+++\n{body}"


class Fixture(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.upstream = self.root / "upstream.git"
        subprocess.run(["git", "init", "--bare", str(self.upstream)], check=True, capture_output=True)
        self.repo = self.root / "repo"; self.repo.mkdir()
        for args in (("init",), ("config", "user.email", "test@example.invalid"), ("config", "user.name", "World Contracts test"), ("config", "commit.gpgSign", "false"), ("config", "core.hooksPath", str(self.root / "empty-hooks")), ("config", "core.editor", ":"), ("config", f"url.file://{self.root}/upstream.insteadOf", "https://github.com/evefrontier/world-contracts")):
            command(self.repo, *args)
        (self.root / "empty-hooks").mkdir()
        command(self.repo, "remote", "add", "origin", "https://github.com/evefrontier/world-contracts.git")
        (self.repo / "base.move").write_text("module test::base {}")
        command(self.repo, "add", "."); command(self.repo, "commit", "-m", "base")
        self.base = command(self.repo, "rev-parse", "HEAD")
        command(self.repo, "branch", "-M", "main")
        (self.repo / "main.move").write_text("module test::main {}")
        command(self.repo, "add", "."); command(self.repo, "commit", "-m", "main")
        self.main = command(self.repo, "rev-parse", "HEAD")
        command(self.repo, "checkout", "-b", "dev", self.base)
        (self.repo / "dev.move").write_text("module test::dev {}")
        command(self.repo, "add", "."); command(self.repo, "commit", "-m", "dev")
        self.dev = command(self.repo, "rev-parse", "HEAD")
        command(self.repo, "push", "origin", "main", "dev")
        command(self.repo, "fetch", "origin", "main", "dev")
        self.chapter = self.root / "chapter"; self.chapter.mkdir()
        (self.chapter / "_index.md").write_text(chapter_text(self.main, self.dev, self.base), encoding="utf-8")

    def baseline(self):
        return comparison.validate_metadata(self.chapter)

    def json(self, name, value):
        path = self.root / name; path.write_text(json.dumps(value), encoding="utf-8"); return path

    def coverage(self, text):
        path = self.root / "coverage.toml"; path.write_text(text, encoding="utf-8"); return path


class MetadataTests(Fixture):
    def test_malformed_metadata_is_rejected(self):
        (self.chapter / "_index.md").write_text(chapter_text(self.main, self.dev, self.base).replace("comparison_schema = 1", "comparison_schema = 2"))
        with self.assertRaises(comparison.ValidationError): comparison.validate_metadata(self.chapter)

    def test_noninteractive_fixture_configuration_is_local(self):
        self.assertEqual(command(self.repo, "config", "--local", "commit.gpgSign"), "false")
        self.assertEqual(command(self.repo, "config", "--local", "core.editor"), ":")
        self.assertTrue(command(self.repo, "config", "--local", "core.hooksPath").endswith("empty-hooks"))

    def test_wrong_remote_is_rejected(self):
        command(self.repo, "remote", "set-url", "origin", "https://github.com/example/not-world-contracts.git")
        with self.assertRaisesRegex(comparison.ValidationError, "origin remote"):
            comparison.plan_review(self.repo, self.baseline())

    def test_stale_local_branch_is_not_used(self):
        command(self.repo, "checkout", "main")
        command(self.repo, "reset", "--hard", self.base)
        plan = comparison.plan_review(self.repo, self.baseline())
        self.assertEqual(plan["candidates"]["v0"], self.main)

    def test_missing_complete_inputs_are_rejected(self):
        with self.assertRaisesRegex(comparison.ValidationError, "requires"):
            comparison.validate_complete(self.chapter, self.repo, None, None, None)

    def test_candidate_wrong_type_and_nonexistent_object_are_rejected(self):
        candidates = self.json("candidates.json", {"candidates": {"v0": 1, "v1": self.dev, "merge_base": self.base}})
        with self.assertRaises(comparison.ValidationError): comparison.validate_cursor_candidates(self.repo, self.baseline(), candidates)
        candidates = self.json("candidates.json", {"candidates": {"v0": "f" * 40, "v1": self.dev, "merge_base": self.base}})
        with self.assertRaises(comparison.ValidationError): comparison.validate_cursor_candidates(self.repo, self.baseline(), candidates)

    def test_incorrect_merge_base_is_rejected(self):
        candidates = self.json("candidates.json", {"candidates": {"v0": self.main, "v1": self.dev, "merge_base": self.main}})
        with self.assertRaisesRegex(comparison.ValidationError, "does not match"):
            comparison.validate_cursor_candidates(self.repo, self.baseline(), candidates)

    def test_unrelated_evidence_commit_and_missing_path_are_rejected(self):
        other = "d" * 40
        (self.chapter / "_index.md").write_text(chapter_text(self.main, self.dev, self.base, f"[bad](https://github.com/evefrontier/world-contracts/blob/{other}/base.move)"))
        with self.assertRaisesRegex(comparison.ValidationError, "outside"):
            comparison.validate_evidence(self.repo, self.baseline(), self.chapter)
        (self.chapter / "_index.md").write_text(chapter_text(self.main, self.dev, self.base, f"[bad](https://github.com/evefrontier/world-contracts/blob/{self.main}/missing.move)"))
        with self.assertRaises(comparison.ValidationError): comparison.validate_evidence(self.repo, self.baseline(), self.chapter)

    def test_exact_coverage_rejects_missing_and_archive_as_active(self):
        inventory = self.json("inventory.json", {"v0_move_modules": ["base.move"], "v1_active_move_modules": ["main.move"], "v1_archive_move_modules": ["contracts/archive/old.move"], "tip_to_tip_changed_files": ["main.move"]})
        coverage = self.coverage('[[v0_module]]\npath="base.move"\nstate="main-only"\ndisposition="reviewed"\n\n[[active_module]]\npath="contracts/archive/old.move"\nstate="active-v1"\ndisposition="wrong"\n\n[[archived_module]]\npath="contracts/archive/old.move"\nstate="archived-only"\ndisposition="reviewed"\n\n[[changed_path]]\npath="main.move"\nstate="active-v1"\ndisposition="reviewed"\n')
        with self.assertRaises(comparison.ValidationError): comparison.validate_inventory_coverage(inventory, coverage)

    def test_malformed_inventory_and_coverage_are_controlled_errors(self):
        inventory = self.root / "inventory.json"; inventory.write_text("{not json", encoding="utf-8")
        coverage = self.coverage("not = [valid")
        with self.assertRaisesRegex(comparison.ValidationError, "malformed JSON"):
            comparison.validate_inventory_coverage(inventory, coverage)
        inventory.write_text(json.dumps({"v0_move_modules": [], "v1_active_move_modules": [], "v1_archive_move_modules": [], "tip_to_tip_changed_files": []}), encoding="utf-8")
        with self.assertRaisesRegex(comparison.ValidationError, "malformed TOML"):
            comparison.validate_inventory_coverage(inventory, coverage)

    def test_rewritten_history_selects_full_rebaseline(self):
        baseline = comparison.Baseline("_index.md", "evefrontier/world-contracts", "main", self.main, "dev", self.main, self.base, "2026-08-10T00:00:00Z", "complete")
        self.assertEqual(comparison.plan_review(self.repo, baseline)["mode"], "full-rebaseline")

    def test_final_refs_reports_pending_without_cursor_substitution(self):
        candidates = self.json("candidates.json", {"candidates": {"v0": self.main, "v1": self.dev, "merge_base": self.base}})
        (self.repo / "dev2.move").write_text("module test::dev2 {}")
        command(self.repo, "add", "."); command(self.repo, "commit", "-m", "advance dev")
        advanced = command(self.repo, "rev-parse", "HEAD"); command(self.repo, "push", "origin", "dev")
        result = comparison.final_refs(self.repo, self.baseline(), candidates)
        self.assertEqual(result["pending"], {"v1": advanced})
        self.assertEqual(result["candidates"]["v1"], self.dev)

    def test_noop_final_refs_are_stable(self):
        candidates = self.json("candidates.json", {"candidates": {"v0": self.main, "v1": self.dev, "merge_base": self.base}})
        self.assertTrue(comparison.final_refs(self.repo, self.baseline(), candidates)["stable"])


if __name__ == "__main__":
    unittest.main()
