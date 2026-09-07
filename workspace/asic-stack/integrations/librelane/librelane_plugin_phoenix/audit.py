"""Executed by the SAME Yosys process that subsequently performs synthesis."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import runpy
import sys


def main() -> None:
    # Load a sibling directly: the embedded interpreter need not import LibreLane.
    helper = Path(__file__).with_name("contract.py")
    spec = importlib.util.spec_from_file_location("phoenix_contract", helper)
    assert spec and spec.loader
    contract = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(contract)
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--phoenix-script", required=True)
    parser.add_argument("--phoenix-identity", required=True)
    parser.add_argument("--phoenix-report", required=True)
    args, forwarded = parser.parse_known_args()
    expected = json.loads(Path(args.phoenix_identity).read_text())
    proc = Path("/proc/self/exe")
    if not proc.exists():
        raise RuntimeError("Runtime binary audit currently requires Linux /proc")
    from pyosys import libyosys
    identity = contract.validate_native_identity(
        expected, proc.resolve(strict=True), getattr(libyosys, "__file__", None)
    )
    identity.update({
        "schema_version": 1,
        "librelane_revision": expected["librelane_revision"],
        "script_sha256": contract.digest_file(Path(args.phoenix_script)),
        "mode": "clean-pass-through", "native_cache_enabled": False,
    })
    report = Path(args.phoenix_report)
    temporary = report.with_suffix(report.suffix + ".tmp")
    temporary.write_text(json.dumps(identity, indent=2) + "\n")
    os.replace(temporary, report)
    sys.argv = [args.phoenix_script] + forwarded
    runpy.run_path(args.phoenix_script, run_name="__main__")


if __name__ == "__main__":
    main()
