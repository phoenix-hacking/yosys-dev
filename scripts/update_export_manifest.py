#!/usr/bin/env python3
"""Refresh checksums for reviewed tracked/staged source; never add untracked files."""
from __future__ import annotations

import subprocess

from stack import ROOT, digest_file, write_json


def main() -> None:
    result = subprocess.check_output(["git", "ls-files", "--stage", "-z"], cwd=ROOT)
    files = {}
    for record in result.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, _, stage = metadata.decode().split()
        path = raw_path.decode()
        if stage != "0":
            raise ValueError("Resolve index conflicts before publishing source checksums")
        # The manifest is self-referential; .gitmodules is derived on export so
        # the independent destination still points at the original compiler.
        if mode == "160000" or path in ("EXPORT_MANIFEST.json", ".gitmodules"):
            continue
        if mode not in ("100644", "100755") or (ROOT / path).is_symlink():
            raise ValueError(f"Unsupported source file mode: {path}")
        if any(part in (".git", ".state", ".runs", ".cache", ".venv", "__pycache__", ".env")
               for part in (ROOT / path).relative_to(ROOT).parts):
            raise ValueError(f"Runtime/credential file staged for export: {path}")
        files[path] = digest_file(ROOT / path)
    write_json(ROOT / "EXPORT_MANIFEST.json", {"schema_version": 1, "files": files})
    print(f"Recorded {len(files)} tracked source files")


if __name__ == "__main__":
    main()
