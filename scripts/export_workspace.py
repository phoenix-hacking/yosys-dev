#!/usr/bin/env python3
"""Export ONLY checksummed workspace source and create an independent Git index.

Does not copy parent history, runtime files, credentials or PDKs. Does not create
remote repositories, push, reset a checkout, or overwrite a destination.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys

from stack import ROOT, digest_file, load_lock


def source_files(source: Path) -> list[Path]:
    manifest = json.loads((source / "EXPORT_MANIFEST.json").read_text())
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported export manifest")
    result = []
    for relative, expected in manifest["files"].items():
        rel = PurePosixPath(relative)
        if rel.is_absolute() or ".." in rel.parts or not rel.parts:
            raise ValueError("Unsafe export path")
        if any(p in (".git", ".state", ".runs", ".cache", "__pycache__", ".env") for p in rel.parts):
            raise ValueError("Runtime or credential path in export manifest")
        path = source / str(rel)
        if path.is_symlink() or not path.resolve().is_relative_to(source.resolve()):
            raise ValueError("Source file escapes workspace")
        if digest_file(path) != expected:
            raise ValueError(f"Source changed after manifest publication: {relative}")
        result.append(path)
    return result


def export(source: Path, destination: Path) -> None:
    source = source.resolve(strict=True)
    destination = destination.absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError("Destination already exists; refusing overwrite")
    resolved = destination.resolve()
    if resolved.is_relative_to(source) or source.is_relative_to(resolved):
        raise ValueError("Export must be outside the staging workspace")
    for parent in resolved.parents:
        if (parent / ".git").exists():
            raise ValueError("Destination must not be nested inside another Git repository")
    files = source_files(source)  # Validate everything before making the directory.
    lock = load_lock(source)
    destination.mkdir(parents=True, exist_ok=False)
    for path in files:
        target = destination / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    shutil.copy2(source / "EXPORT_MANIFEST.json", destination / "EXPORT_MANIFEST.json")
    revision = lock["sources"]["yosys_candidate"]["revision"]
    repo = lock["sources"]["yosys_candidate"]["repository"]
    (destination / ".gitmodules").write_text(
        '[submodule "yosys"]\n\tpath = components/yosys\n'
        f'\turl = https://github.com/{repo}.git\n'
    )
    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=destination, check=True, stdout=subprocess.PIPE)
    git("init", "--initial-branch=main")
    git("add", "--all")
    git("update-index", "--add", "--cacheinfo", f"160000,{revision},components/yosys")
    print(f"Created independent workspace and staged files: {destination}")
    print("No remote repository was created and nothing was pushed.")
    print("Review staged changes, commit with your configured Git identity, then create/push asic-stack.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        export(ROOT, args.destination)
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
