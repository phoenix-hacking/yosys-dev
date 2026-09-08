"""Capability boundaries and failure oracles for opt-in workflows."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import stack
import tool_audit
import simulation_result
import thermal_smoke
import profile_yosys


class ExtensionContractTests(unittest.TestCase):
    def test_existing_tool_cannot_be_reintroduced_as_extension(self):
        lock = copy.deepcopy(stack.load_lock())
        lock["tooling_contract"]["extensions"]["verification"].append("openroad")
        with patch.object(stack, "read_json", side_effect=[lock, stack.read_json(ROOT / "nix/tool-catalog.json")]):
            with self.assertRaisesRegex(ValueError, "duplicates an existing tool"):
                stack.load_lock()

    def test_thermal_source_cannot_float(self):
        lock = copy.deepcopy(stack.load_lock())
        lock["extension_sources"]["hotspot-thermal"]["revision"] = "master"
        with patch.object(stack, "read_json", side_effect=[lock, stack.read_json(ROOT / "nix/tool-catalog.json")]):
            with self.assertRaisesRegex(ValueError, "Unpinned extension"):
                stack.load_lock()

    def test_opt_in_failure_is_separate_from_baseline(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "bin").mkdir()
            executable = root / "bin/sim"
            executable.write_text("#!/bin/sh\nexit 0\n")
            executable.chmod(0o755)
            lock = {"schema_version": 2, "tooling_contract": {
                "digital_required": ["sim"], "analog_required": ["sim"], "rf_required": ["sim"],
                "extensions": {"profiling": ["perf"]}}}
            catalog = {name: {"kind": "native", "programs": [name]} for name in ("sim", "perf")}
            for name, value in (("lock", lock), ("catalog", catalog)):
                (root / name).write_text(json.dumps(value))
            identity = {"schema_version": 1, "toolchain_lock_sha256": tool_audit.sha256(root / "lock"),
                        "tool_catalog_sha256": tool_audit.sha256(root / "catalog"),
                        "tool_packages": {"sim": {"available": True, "kind": "native", "version": "fixture",
                                                  "store_path": str(root)}}}
            (root / "identity").write_text(json.dumps(identity))
            args = [root / "identity", root / "lock", root / "catalog", "all"]
            self.assertEqual(tool_audit.audit(*args)["blocked_tools"], [])
            self.assertEqual(tool_audit.audit(*args, "profiling")["blocked_tools"], ["perf"])
            with self.assertRaisesRegex(ValueError, "Unknown tool extension"):
                tool_audit.audit(*args, "typo")


class SimulationOracleTests(unittest.TestCase):
    def test_only_completed_assertions_are_detected_mutations(self):
        cases = [
            ("", 0, "PASS"), ("", 2, "ERROR"),
            ('<failure error_type="AssertionError"/>', 2, "FAIL"),
            ('<failure error_type="AssertionError"/>', 0, "ERROR"),
            ('<failure error_type="AssertionError"/>', 124, "ERROR"),
            ('<failure error_type="ImportError"/>', 2, "ERROR"),
            ('<failure error_type="ValueError"/>', 2, "ERROR"),
            ('<failure message="Initialization failed"/>', 2, "ERROR"),
            ("<skipped/>", 0, "ERROR"), ("<error/>", 0, "ERROR")]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "results.xml"
            for child, exit_code, expected in cases:
                with self.subTest(child=child, exit_code=exit_code):
                    path.write_text('<testsuites><testsuite><testcase name="check_mixed" classname="test_mixed">'
                                    + child + '</testcase></testsuite></testsuites>')
                    self.assertEqual(simulation_result.classify(path, exit_code), expected)

    def test_empty_or_foreign_report_is_not_a_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "results.xml"
            for xml in ('<testsuites/>', '<testsuite><testcase name="another_test"/></testsuite>'):
                path.write_text(xml)
                self.assertEqual(simulation_result.classify(path, 0), "ERROR")


class ThermalOracleTests(unittest.TestCase):
    def test_constant_or_inverted_response_is_rejected(self):
        cold = {"digital": 300.0, "analog": 300.0}
        for hot in (cold, {"digital": 301.0, "analog": 302.0}, {"digital": 307.0, "analog": 300.0}):
            with self.subTest(hot=hot), self.assertRaises(ValueError):
                thermal_smoke.check_response(cold, hot)

    def test_malformed_or_nonfinite_solver_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "result"
            for content in ("digital nan\nanalog 300\n", "digital 300\n", "digital 300\ndigital 300\nanalog 300\n"):
                path.write_text(content)
                with self.assertRaises(ValueError):
                    thermal_smoke.temperatures(path)


class ProfilingTests(unittest.TestCase):
    def test_failed_profiler_or_empty_capture_never_counts_as_success(self):
        for create_data, returncode, expected in ((True, 0, "PROFILE_CAPTURED"),
                                                 (True, 1, "PROFILE_FAILED"),
                                                 (False, 0, "MISSING_PROFILE_DATA")):
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                executable = root / "perf-fixture"
                executable.write_text("#!/bin/sh\n" + ('printf data > "$4"\n' if create_data else '')
                                      + f"exit {returncode}\n")
                executable.chmod(0o755)
                script = root / "input.ys"
                script.write_text("# fixture\n")
                identity = {"yosys_native": sys.executable}
                availability = {"blocked_tools": [], "tools": {"perf": {"programs": {"perf": str(executable)}}}}
                with patch.object(stack, "load_lock", return_value={}), \
                     patch.object(stack, "capture", return_value=str(root / "identity")), \
                     patch.object(stack, "read_json", return_value=identity), \
                     patch.object(stack, "verify_identity"), patch.object(profile_yosys, "audit", return_value=availability):
                    result = profile_yosys.profile("perf", "candidate", script, [script], root / "output", 5)
                self.assertEqual(result["status"], expected)
                self.assertFalse(result["eda_validated"])
                self.assertEqual(result["yosys_sha256"], stack.digest_file(Path(sys.executable)))


if __name__ == "__main__":
    unittest.main()
