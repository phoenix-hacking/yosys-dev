#!/usr/bin/env python3
"""Capture CPU stacks or heap allocations for the selected, audited Yosys binary."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import time

import stack
from tool_audit import audit


def profile(tool: str, selected: str, script: Path, inputs: list[Path], output: Path,
            timeout: int) -> dict:
    lock = stack.load_lock()
    identity_path = Path(stack.capture(["phoenix-toolchain", "--path"]))
    identity = stack.read_json(identity_path)
    stack.verify_identity(identity, selected, lock)
    available = audit(identity_path, stack.ROOT / "toolchain.lock.json",
                      stack.ROOT / "nix/tool-catalog.json", "digital", "profiling")
    if available["blocked_tools"]:
        raise ValueError("Profiling tools unavailable: " + ", ".join(available["blocked_tools"]))
    script = script.resolve(strict=True)
    files = {str(path.resolve(strict=True)): stack.digest_file(path) for path in [script, *inputs]}
    native = Path(identity["yosys_native"]).resolve(strict=True)
    executable = available["tools"][tool]["programs"][tool]
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    command = ([executable, "record", "-g", "-o", str(output / "perf.data"), "--"] if tool == "perf"
               else [executable, "-o", str(output / "heaptrack")])
    command += [str(native), "-s", str(script)]
    result = {"profile": selected, "tool": tool, "command": command,
              "cwd": str(stack.ROOT), "input_sha256": files,
              "yosys_sha256": stack.digest_file(native), "toolchain_identity": identity,
              "host_kernel": os.uname().release, "eda_validated": False}
    start = time.monotonic()
    with (output / "profile.log").open("w") as log:
        proc = subprocess.Popen(command, cwd=stack.ROOT, stdout=log, stderr=subprocess.STDOUT,
                                start_new_session=True)
        try:
            code = proc.wait(timeout=timeout)
            result["status"] = "PROFILE_CAPTURED" if code == 0 else "PROFILE_FAILED"
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            code = proc.wait()
            result["status"] = "TIMEOUT"
    result.update(returncode=code, wall_seconds=time.monotonic() - start)
    artifacts = [p for p in output.glob("perf.data" if tool == "perf" else "heaptrack*")
                 if p.is_file() and p.stat().st_size > 0]
    if result["status"] == "PROFILE_CAPTURED" and not artifacts:
        result["status"] = "MISSING_PROFILE_DATA"
    result["artifacts"] = [p.name for p in artifacts]
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", choices=("perf", "heaptrack"), required=True)
    parser.add_argument("--profile", choices=("stock", "candidate"), required=True)
    parser.add_argument("--script", type=Path, required=True)
    parser.add_argument("--input", action="append", type=Path, required=True,
                        help="Repeat for every RTL/include/data input read by the Yosys script")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    try:
        if args.timeout <= 0:
            raise ValueError("Timeout must be positive")
        result = profile(args.tool, args.profile, args.script, args.input, args.output, args.timeout)
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "PROFILE_CAPTURED" else 2
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "BLOCKED_OR_FAILED", "error": str(exc), "eda_validated": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
