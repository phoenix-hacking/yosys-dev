#!/usr/bin/env python3
"""Check required package paths, programs and Python imports; never qualify a flow."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LANES = ("digital", "analog", "rf", "mixed_signal", "all")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def probe_module(name: str) -> list[str]:
    # Use the selected Nix interpreter, with no user site or cwd import shadowing.
    code = (
        "import sys; sys.path = [p for p in sys.path if p]; "
        "import importlib, json; m = importlib.import_module(sys.argv[1]); "
        "print(json.dumps([m.__file__] if getattr(m, '__file__', None) "
        "else list(m.__path__)))"
    )
    result = subprocess.run([sys.executable, "-s", "-c", code, name],
                            text=True, capture_output=True, check=True, timeout=20)
    paths = json.loads(result.stdout)
    if not isinstance(paths, list) or not paths or any(not isinstance(p, str) for p in paths):
        raise ValueError("Module did not report its source paths")
    return paths


def audit(identity_path: Path, lock_path: Path, catalog_path: Path, lane: str,
          extension: str | None = None) -> dict:
    if lane not in LANES:
        raise ValueError("Unknown tool lane")
    identity, lock, catalog = (json.loads(p.read_text())
                               for p in (identity_path, lock_path, catalog_path))
    if identity.get("schema_version") != 1 or lock.get("schema_version") != 2:
        raise ValueError("Unsupported runtime identity or source lock schema")
    for field, path in (("toolchain_lock_sha256", lock_path), ("tool_catalog_sha256", catalog_path)):
        if identity.get(field) != sha256(path):
            raise ValueError(f"Stale or missing {field}; rebuild the selected profile")
    contract = lock["tooling_contract"]
    if extension is not None:
        groups = contract.get("extensions", {})
        if extension != "all" and extension not in groups:
            raise ValueError(f"Unknown tool extension: {extension}")
        selected_groups = sorted(groups) if extension == "all" else [extension]
        required = sorted({name for group in selected_groups for name in groups[group]})
    else:
        lanes = ("digital", "analog", "rf") if lane in ("all", "mixed_signal") else (lane,)
        required = sorted({name for selected in lanes for name in contract[selected + "_required"]})
    if not required:
        raise ValueError("Empty required tool contract")
    entries = {}
    for name in required:
        spec = catalog[name]
        package = identity.get("tool_packages", {}).get(name, {})
        item = {"status": "MISSING_PACKAGE", "qualified": False,
                "version": package.get("version"), "store_path": package.get("store_path")}
        entries[name] = item
        if package.get("available") is not True:
            item["reason"] = spec.get("packaging_note", "Package absent from selected profile")
            continue
        try:
            if package.get("kind") != spec["kind"]:
                raise ValueError("Package kind differs from tool catalog")
            if not package.get("version") or package["version"] == "unknown":
                raise ValueError("Package version is unknown")
            if not isinstance(package.get("store_path"), str) or not Path(package["store_path"]).is_absolute():
                raise ValueError("Package path must be absolute")
            root = Path(package["store_path"]).resolve(strict=True)
            if not root.is_dir():
                raise ValueError("Package store path is not a directory")
            item["programs"] = {}
            for program in spec["programs"]:
                path = root / "bin" / program
                if not path.is_file() or not os.access(path, os.X_OK):
                    raise ValueError(f"Missing executable in selected package: {program}")
                item["programs"][program] = str(path)
            if spec["kind"] == "python":
                paths = [Path(p).resolve(strict=True) for p in probe_module(spec["module"])]
                if any(not p.is_relative_to(root) for p in paths):
                    raise ValueError("Python module loaded outside selected package")
                item["module_paths"] = [str(p) for p in paths]
            item["status"] = "AVAILABLE_NOT_QUALIFIED"
        except (ValueError, OSError, subprocess.SubprocessError) as exc:
            item.update(status="UNUSABLE_PACKAGE", error=str(exc))
    blocked = [name for name, item in entries.items() if item["status"] != "AVAILABLE_NOT_QUALIFIED"]
    return {"schema_version": 1, "lane": lane if extension is None else None,
            "extension": extension, "profile": identity.get("profile"),
            "status": "BLOCKED" if blocked else "AVAILABLE_NOT_QUALIFIED",
            "eda_validated": False, "blocked_tools": blocked, "tools": entries}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--identity", required=True, type=Path)
    parser.add_argument("--lock", type=Path, default=ROOT / "toolchain.lock.json")
    parser.add_argument("--catalog", type=Path, default=ROOT / "nix/tool-catalog.json")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--lane", choices=LANES, default="analog")
    selection.add_argument("--extension", help="Opt-in group from tooling_contract.extensions, or all")
    args = parser.parse_args()
    try:
        result = audit(args.identity, args.lock, args.catalog, args.lane, args.extension)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2 if result["blocked_tools"] else 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
