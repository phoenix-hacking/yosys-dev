"""Offline regression suite: no Nix, PDK, network or synthesis required."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import stack
import export_workspace

spec = importlib.util.spec_from_file_location("contract", ROOT / "integrations/librelane/librelane_plugin_phoenix/contract.py")
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


class ConfigurationTests(unittest.TestCase):
    def test_lock_is_pinned(self):
        self.assertEqual(stack.load_lock()["sources"]["librelane"]["release"], "3.0.14")

    def test_generated_flake_matches(self):
        self.assertEqual((ROOT / "flake.nix").read_text(), stack.rendered_flake())

    def test_offline_check_does_not_claim_eda(self):
        self.assertFalse(stack.check_static()["eda_validated"])

    def test_reject_moving_revision(self):
        value = copy.deepcopy(stack.load_lock())
        value["sources"]["yosys_candidate"]["revision"] = "main"
        with patch.object(stack, "read_json", return_value=value), self.assertRaises(ValueError):
            stack.load_lock()

    def test_reject_false_incremental_claim(self):
        value = copy.deepcopy(stack.load_lock())
        value["initial_envelope"]["native_incremental_synthesis"] = True
        with patch.object(stack, "read_json", side_effect=[value, stack.read_json(ROOT / "nix/tool-catalog.json")]), self.assertRaisesRegex(ValueError, "incremental synthesis"):
            stack.load_lock()

    def test_updated_rtl_is_selected(self):
        config = stack.prepare_config(ROOT, "B", Path("identity.json"))
        self.assertTrue(config["VERILOG_FILES"][0].endswith("/B/top.v"))
        self.assertEqual(config["meta"]["flow"], "Phoenix.Classic")

    def test_unsupported_revision(self):
        with self.assertRaises(ValueError):
            stack.prepare_config(ROOT, "../secret", Path("identity.json"))

    def test_fixture_contains_actual_edit(self):
        a = ROOT / "benchmarks/designs/mixed/A/top.v"
        b = ROOT / "benchmarks/designs/mixed/B/top.v"
        self.assertNotEqual(stack.digest_file(a), stack.digest_file(b))

    def test_missing_build_lock_fails(self):
        with tempfile.TemporaryDirectory() as t, patch.object(stack, "check_static", return_value={}):
            with self.assertRaisesRegex(ValueError, "Build lock unresolved"):
                stack.doctor("candidate", Path(t))

    def test_wrong_profile_fails(self):
        with self.assertRaises(ValueError):
            stack.verify_identity({"schema_version": 1, "profile": "stock"}, "candidate", stack.load_lock())

    def test_wrong_revision_fails(self):
        lock = stack.load_lock()
        value = {"schema_version": 1, "profile": "candidate", "librelane_revision": lock["sources"]["librelane"]["revision"], "yosys_revision": "0" * 40}
        with self.assertRaisesRegex(ValueError, "Yosys revision"):
            stack.verify_identity(value, "candidate", lock)


class CommandTests(unittest.TestCase):
    def test_command_preserves_config_and_extra(self):
        command = ["yosys", "-y", "/flow.py", "-Q", "--", "--config-in", "a b.json", "--extra-in", "e.json"]
        result = contract.audited_command(command, "/audit.py", "/identity.json", "/out.json")
        self.assertEqual(result[:5], ["yosys", "-y", "/audit.py", "-Q", "--"])
        self.assertEqual(result[-4:], command[-4:])
        self.assertEqual(command[2], "/flow.py")

    def test_missing_separator_fails(self):
        with self.assertRaises(ValueError):
            contract.audited_command(["yosys", "-y", "s.py"], "a", "b", "c")

    def test_missing_script_fails(self):
        with self.assertRaises(ValueError):
            contract.audited_command(["yosys", "-y", "--"], "a", "b", "c")

    def test_duplicate_y_fails(self):
        with self.assertRaises(ValueError):
            contract.audited_command(["yosys", "-y", "s", "-y", "x", "--"], "a", "b", "c")


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.binary = self.root / "yosys"
        self.binary.write_bytes(b"native-compiler-fixture")
        self.identity = {"schema_version": 1, "yosys_native": str(self.binary), "pyosys_roots": [str(self.root / "python")], "profile": "candidate", "yosys_revision": "1" * 40}

    def test_matching_embedded(self):
        result = contract.validate_native_identity(self.identity, self.binary, None)
        self.assertEqual(result["binding"]["kind"], "embedded")

    def test_wrong_binary_rejected(self):
        wrong = self.root / "stock"
        wrong.write_bytes(b"other-compiler")
        with self.assertRaises(ValueError):
            contract.validate_native_identity(self.identity, wrong, None)

    def test_external_binding_rejected(self):
        wrong = self.root / "foreign.so"
        wrong.write_bytes(b"x")
        with self.assertRaises(ValueError):
            contract.validate_native_identity(self.identity, self.binary, str(wrong))

    def test_selected_binding_accepted(self):
        binding = self.root / "python/libyosys.so"
        binding.parent.mkdir()
        binding.write_bytes(b"binding")
        result = contract.validate_native_identity(self.identity, self.binary, str(binding))
        self.assertEqual(result["binding"]["kind"], "extension")

    def test_unknown_schema_rejected(self):
        self.identity["schema_version"] = 2
        with self.assertRaises(ValueError):
            contract.validate_native_identity(self.identity, self.binary, None)


class InventoryTests(unittest.TestCase):
    def test_platform_changes_invalidate(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "lib.lib").write_text("a")
            before, count = stack.tree_digest(root)
            (root / "lib.lib").write_text("b")
            self.assertEqual(count, 1)
            self.assertNotEqual(before, stack.tree_digest(root)[0])

    def test_relocated_platform_same_digest(self):
        with tempfile.TemporaryDirectory() as t:
            a, b = Path(t) / "a", Path(t) / "b"
            a.mkdir(); b.mkdir()
            (a / "lib.lib").write_text("abc")
            (b / "lib.lib").write_text("abc")
            self.assertEqual(stack.tree_digest(a), stack.tree_digest(b))

    def test_cycle_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "loop").symlink_to(root, target_is_directory=True)
            with self.assertRaises(ValueError):
                stack.tree_digest(root)

    def test_empty_platform_rejected(self):
        with tempfile.TemporaryDirectory() as t, self.assertRaises(ValueError):
            stack.tree_digest(Path(t))

    def test_external_file_content_included(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t) / "pdk"; root.mkdir()
            outside = Path(t) / "external.lib"; outside.write_text("a")
            (root / "lib.lib").symlink_to(outside)
            before = stack.tree_digest(root)
            outside.write_text("b")
            self.assertNotEqual(before, stack.tree_digest(root))


class ExportTests(unittest.TestCase):
    def test_export_has_pinned_gitlink(self):
        with tempfile.TemporaryDirectory() as t:
            dest = Path(t) / "standalone"
            export_workspace.export(ROOT, dest)
            result = subprocess.check_output(["git", "ls-files", "--stage", "components/yosys"], cwd=dest, text=True)
            expected = stack.load_lock()["sources"]["yosys_candidate"]["revision"]
            self.assertTrue(result.startswith("160000 " + expected))
            self.assertFalse((dest / ".runs").exists())
            self.assertTrue((dest / ".gitmodules").is_file())
            self.assertFalse(stack.check_static(dest)["eda_validated"])

    def test_existing_destination_rejected(self):
        with tempfile.TemporaryDirectory() as t, self.assertRaises(ValueError):
            export_workspace.export(ROOT, Path(t))

    def test_nested_destination_rejected(self):
        with self.assertRaises(ValueError):
            export_workspace.export(ROOT, ROOT / "new-export")

    def test_parent_git_repository_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / ".git").mkdir()
            with self.assertRaises(ValueError):
                export_workspace.export(ROOT, Path(t) / "child")

    def test_changed_source_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "file.txt").write_text("changed")
            (root / "EXPORT_MANIFEST.json").write_text(json.dumps({"schema_version": 1, "files": {"file.txt": "0" * 64}}))
            with self.assertRaises(ValueError):
                export_workspace.source_files(root)

    def test_manifest_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "EXPORT_MANIFEST.json").write_text(json.dumps({"schema_version": 1, "files": {"../secret": "0" * 64}}))
            with self.assertRaises(ValueError):
                export_workspace.source_files(root)

    def test_manifest_runtime_path_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "EXPORT_MANIFEST.json").write_text(json.dumps({"schema_version": 1, "files": {".env": "0" * 64}}))
            with self.assertRaises(ValueError):
                export_workspace.source_files(root)

    def test_export_manifest_integrity(self):
        self.assertGreater(len(export_workspace.source_files(ROOT)), 20)


if __name__ == "__main__":
    unittest.main()
