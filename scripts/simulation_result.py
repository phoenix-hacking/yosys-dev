#!/usr/bin/env python3
"""Classify the specific cocotb oracle; infrastructure errors never count as detections."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def classify(path: Path, make_exit: int) -> str:
    root = ET.parse(path).getroot()
    cases = list(root.iter("testcase"))
    if (len(cases) != 1 or cases[0].get("name") != "check_mixed" or cases[0].get("classname") != "test_mixed"
            or cases[0].find("skipped") is not None or cases[0].find("error") is not None
            or make_exit in (124, 137, 143)):
        return "ERROR"
    failure = cases[0].find("failure")
    if failure is None:
        return "PASS" if make_exit == 0 else "ERROR"
    return "FAIL" if failure.get("error_type") == "AssertionError" and make_exit != 0 else "ERROR"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--make-exit", type=int, required=True)
    parser.add_argument("--mcy-output", type=Path)
    args = parser.parse_args()
    try:
        result = classify(args.report, args.make_exit)
    except (OSError, ValueError, ET.ParseError):
        result = "ERROR"
    if args.mcy_output:
        args.mcy_output.write_text(f"1 {result}\n")
    print(json.dumps({"simulation": result, "eda_validated": False}))
    return 2 if result == "ERROR" else (0 if args.mcy_output or result == "PASS" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
