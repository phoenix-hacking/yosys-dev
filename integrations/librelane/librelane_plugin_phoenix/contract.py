"""Pure helpers shared by the step, embedded audit, and offline tests."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Sequence


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()


def audited_command(command: Sequence[str], wrapper: str, identity: str, report: str) -> list[str]:
    """Wrap LibreLane 3.0.14's documented-in-source `yosys -y ... -- ...`."""
    result = list(command)
    if result.count("-y") != 1 or result.count("--") != 1:
        raise ValueError("Unsupported upstream command shape; audit the pinned LibreLane step")
    index, separator = result.index("-y"), result.index("--")
    if index + 1 >= separator:
        raise ValueError("Missing upstream Python script")
    original = result[index + 1]
    result[index + 1] = wrapper
    result[separator + 1:separator + 1] = [
        "--phoenix-script", original,
        "--phoenix-identity", identity,
        "--phoenix-report", report,
    ]
    return result


def validate_native_identity(expected: dict, actual_binary: Path, binding_file: str | None) -> dict:
    """Validate code bytes, not PATH labels. Linux is the initial support envelope."""
    if expected.get("schema_version") != 1:
        raise ValueError("Unsupported toolchain identity schema")
    expected_binary = Path(expected["yosys_native"])
    wanted, actual = digest_file(expected_binary), digest_file(actual_binary)
    if wanted != actual:
        raise ValueError("The synthesis process is not the selected Yosys binary")
    if binding_file:
        binding_path = Path(binding_file).resolve(strict=True)
        roots = [Path(p).resolve() for p in expected["pyosys_roots"]]
        if not any(binding_path.is_relative_to(p) for p in roots):
            raise ValueError("Pyosys loaded outside the selected compiler package")
        binding = {"kind": "extension", "path": str(binding_path), "sha256": digest_file(binding_path)}
    else:
        binding = {"kind": "embedded", "path": None, "sha256": None}
    return {
        "native_path": str(actual_binary.resolve()), "native_sha256": actual,
        "binding": binding, "profile": expected["profile"],
        "source_revision": expected["yosys_revision"],
    }
