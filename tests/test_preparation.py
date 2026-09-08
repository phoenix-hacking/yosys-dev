"""Regression tests for source/schema drift, tool audits and fresh-clone bootstrap."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import stack
import tool_audit


class BuildLockTests(unittest.TestCase):
    def setUp(self):
        self.source = stack.load_lock()
        nodes = {"root": {"inputs": {"librelane": "ll", "yosys-stock": "stock", "yosys-candidate": "candidate", "hotspot-thermal-source": "thermal"}}}
        revisions = {"ll": self.source["sources"]["librelane"]["revision"],
                     "stock": self.source["sources"]["yosys_stock"]["revision"],
                     "candidate": self.source["sources"]["yosys_candidate"]["revision"],
                     "eda": self.source["inherited"]["nix_eda_revision"],
                     "np": self.source["inherited"]["nixpkgs_revision"],
                     "thermal": self.source["extension_sources"]["hotspot-thermal"]["revision"]}
        for node, revision in revisions.items():
            nodes[node] = {"locked": {"rev": revision, "narHash": "unit-test-fixture-not-a-real-build-lock"}}
        nodes["ll"]["inputs"] = {"nix-eda": "eda"}
        nodes["eda"]["inputs"] = {"nixpkgs": "np"}
        self.build = {"version": 7, "root": "root", "nodes": nodes}

    def verify(self):
        with patch.object(stack, "load_lock", return_value=self.source), patch.object(stack, "read_json", return_value=self.build):
            return stack.verify_build_lock()

    def test_resolved_pins_are_not_build_acceptance(self):
        self.assertFalse(self.verify()["eda_validated"])

    def test_each_changed_revision_rejected(self):
        for node in ("ll", "stock", "candidate", "eda", "np", "thermal"):
            with self.subTest(node=node):
                previous = self.build["nodes"][node]["locked"]["rev"]
                self.build["nodes"][node]["locked"]["rev"] = "0" * 40
                with self.assertRaisesRegex(ValueError, "differs from source pins"):
                    self.verify()
                self.build["nodes"][node]["locked"]["rev"] = previous

    def test_follows_path_supported(self):
        self.build["nodes"]["root"]["inputs"]["shared-pkgs"] = "np"
        self.build["nodes"]["eda"]["inputs"]["nixpkgs"] = ["shared-pkgs"]
        self.assertEqual(len(self.verify()["revisions"]), 6)

    def test_follows_cycle_rejected(self):
        self.build["nodes"]["eda"]["inputs"]["nixpkgs"] = ["librelane", "nix-eda", "nixpkgs"]
        with self.assertRaisesRegex(ValueError, "Cyclic"):
            self.verify()

    def test_unhashed_source_rejected(self):
        del self.build["nodes"]["np"]["locked"]["narHash"]
        with self.assertRaises(ValueError):
            self.verify()


class ToolAuditTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.lock_path, self.catalog_path, self.identity_path = [self.root / name for name in ("lock.json", "catalog.json", "identity.json")]
        self.lock = {"schema_version": 2, "tooling_contract": {
            "digital_required": ["sim"], "analog_required": ["sim"], "rf_required": ["skrf"]}}
        self.catalog = {"sim": {"kind": "native", "programs": ["sim"]},
                        "skrf": {"kind": "python", "programs": [], "module": "skrf"}}
        self.lock_path.write_text(json.dumps(self.lock))
        self.catalog_path.write_text(json.dumps(self.catalog))
        self.package = self.root / "package"
        (self.package / "bin").mkdir(parents=True)
        self.program = self.package / "bin/sim"
        self.program.write_text("#!/bin/sh\nexit 0\n")
        self.program.chmod(0o755)
        self.module = self.package / "skrf.py"
        self.module.write_text("# fixture\n")
        self.identity = {"schema_version": 1, "profile": "candidate",
                         "toolchain_lock_sha256": tool_audit.sha256(self.lock_path),
                         "tool_catalog_sha256": tool_audit.sha256(self.catalog_path),
                         "tool_packages": {}}
        for name, spec in self.catalog.items():
            self.identity["tool_packages"][name] = {"available": True, "version": "fixture",
                                                   "kind": spec["kind"], "store_path": str(self.package)}

    def write_identity(self):
        self.identity_path.write_text(json.dumps(self.identity))

    def audit(self, lane="analog"):
        self.write_identity()
        return tool_audit.audit(self.identity_path, self.lock_path, self.catalog_path, lane)

    def test_available_executable_is_not_qualification(self):
        result = self.audit()
        self.assertEqual(result["status"], "AVAILABLE_NOT_QUALIFIED")
        self.assertFalse(result["eda_validated"])

    def test_missing_package_blocks(self):
        self.identity["tool_packages"]["sim"]["available"] = False
        self.assertEqual(self.audit()["blocked_tools"], ["sim"])

    def test_missing_program_blocks(self):
        self.program.unlink()
        self.assertEqual(self.audit()["tools"]["sim"]["status"], "UNUSABLE_PACKAGE")

    def test_unknown_version_blocks(self):
        self.identity["tool_packages"]["sim"]["version"] = "unknown"
        self.assertEqual(self.audit()["blocked_tools"], ["sim"])

    def test_foreign_python_import_blocks(self):
        foreign = self.root / "outside.py"
        foreign.write_text("# foreign\n")
        with patch.object(tool_audit, "probe_module", return_value=[str(foreign)]):
            self.assertEqual(self.audit("rf")["blocked_tools"], ["skrf"])

    def test_pinned_python_import_available(self):
        with patch.object(tool_audit, "probe_module", return_value=[str(self.module)]):
            self.assertEqual(self.audit("rf")["blocked_tools"], [])

    def test_import_failure_blocks(self):
        with patch.object(tool_audit, "probe_module", side_effect=subprocess.TimeoutExpired("python", 20)):
            self.assertEqual(self.audit("rf")["blocked_tools"], ["skrf"])

    def test_unrelated_lane_does_not_block_selected_lane(self):
        self.identity["tool_packages"]["skrf"]["available"] = False
        self.assertEqual(self.audit()["blocked_tools"], [])
        self.assertEqual(self.audit("mixed_signal")["blocked_tools"], ["skrf"])

    def test_stale_lock_blocks(self):
        self.lock_path.write_text(json.dumps(self.lock) + "\n")
        with self.assertRaisesRegex(ValueError, "Stale"):
            self.audit()

    def test_identity_version_drift_rejected(self):
        self.identity["schema_version"] = 2
        with self.assertRaisesRegex(ValueError, "schema"):
            self.audit()

    def test_cli_missing_package_is_nonzero(self):
        self.identity["tool_packages"] = {}
        self.write_identity()
        result = subprocess.run([sys.executable, str(ROOT / "scripts/tool_audit.py"),
                                 "--identity", str(self.identity_path), "--lock", str(self.lock_path),
                                 "--catalog", str(self.catalog_path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "BLOCKED")


class BootstrapTests(unittest.TestCase):
    def git(self, root, *args):
        return subprocess.check_output(["git", "-c", "user.name=Bootstrap Test", "-c",
                                        "user.email=bootstrap@example.invalid", *args],
                                       cwd=root, text=True, stderr=subprocess.PIPE).strip()

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        source, self.root = [Path(temporary.name) / name for name in ("compiler", "flow")]
        for path in (source, self.root):
            path.mkdir()
            self.git(path, "init", "--initial-branch=main")
        (source / "CMakeLists.txt").write_text("# unit test compiler fixture\n")
        self.git(source, "add", "CMakeLists.txt")
        self.git(source, "commit", "-m", "compiler fixture")
        self.revision = self.git(source, "rev-parse", "HEAD")
        (self.root / ".gitmodules").write_text('[submodule "components/yosys"]\n\tpath = components/yosys\n\turl = ' + source.as_uri() + '\n')
        self.git(self.root, "add", ".gitmodules")
        self.git(self.root, "update-index", "--add", "--cacheinfo", "160000," + self.revision + ",components/yosys")
        self.git(self.root, "commit", "-m", "flow fixture")
        self.component = self.root / "components/yosys"
        self.component.mkdir(parents=True)
        self.lock = {"sources": {"yosys_candidate": {"revision": self.revision}}}

    def bootstrap(self):
        # Only these local fixture clones allow the file protocol; no global Git changes.
        with patch.object(stack, "load_lock", return_value=self.lock), patch.dict(os.environ, {"GIT_ALLOW_PROTOCOL": "file"}):
            stack.clone_component(self.root)

    def test_empty_gitlink_initializes_and_is_repeatable(self):
        self.bootstrap()
        self.assertEqual(self.git(self.component, "rev-parse", "HEAD"), self.revision)
        self.bootstrap()
        self.assertEqual(self.git(self.root, "status", "--porcelain"), "")

    def test_noncheckout_contents_are_preserved(self):
        note = self.component / "local-work.txt"
        note.write_text("preserve me")
        with self.assertRaisesRegex(ValueError, "not its own checkout"):
            self.bootstrap()
        self.assertEqual(note.read_text(), "preserve me")

    def test_dirty_compiler_is_preserved(self):
        self.bootstrap()
        source = self.component / "CMakeLists.txt"
        source.write_text("local edits")
        with self.assertRaisesRegex(ValueError, "refusing to reset"):
            self.bootstrap()
        self.assertEqual(source.read_text(), "local edits")

    def test_gitlink_lock_mismatch_blocks_before_clone(self):
        self.lock["sources"]["yosys_candidate"]["revision"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "gitlink differs"):
            self.bootstrap()
        self.assertEqual(list(self.component.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
