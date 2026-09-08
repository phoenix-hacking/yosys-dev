#!/usr/bin/env python3
"""Exercise HotSpot's thermal response on two synthetic blocks; no PDK qualification."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess


def temperatures(path: Path) -> dict[str, float]:
    values = {}
    for line in path.read_text().splitlines():
        fields = line.split()
        if not fields:
            continue
        if len(fields) != 2 or fields[0] in values:
            raise ValueError("Malformed or duplicate thermal result")
        value = float(fields[1])
        if not math.isfinite(value) or value <= 0:
            raise ValueError("Temperature must be finite and positive in kelvin")
        values[fields[0]] = value
    if not {"digital", "analog"} <= values.keys():
        raise ValueError("Missing block temperatures")
    return values


def check_response(cold: dict, hot: dict) -> None:
    for block in ("digital", "analog"):
        if abs(cold[block] - 300.0) > 0.02:
            raise ValueError("Zero-power temperature must equal 300 K ambient")
        if hot[block] <= cold[block] + 0.02:
            raise ValueError("Added power must heat both coupled blocks")
    if hot["digital"] <= hot["analog"]:
        raise ValueError("Powered block must be warmer than its unpowered neighbor")


def run(hotspot: Path, config: Path, output: Path) -> dict:
    hotspot, config = hotspot.resolve(strict=True), config.resolve(strict=True)
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)  # preserve earlier evidence
    shutil.copyfile(config, output / "model.config")
    (output / "two_blocks.flp").write_text(
        "digital 0.001 0.001 0.000 0.000\nanalog 0.001 0.001 0.001 0.000\n")
    results, commands = {}, []
    for case, power in (("cold", 0), ("hot", 1)):
        (output / f"{case}.ptrace").write_text(f"digital analog\n{power} 0\n")
        command = [str(hotspot), "-c", "model.config", "-f", "two_blocks.flp",
                   "-p", f"{case}.ptrace", "-steady_file", f"{case}.steady",
                   "-model_type", "block", "-ambient", "300", "-leakage_used", "0",
                   "-package_model_used", "0"]
        commands.append(command)
        with (output / f"{case}.log").open("w") as log:
            subprocess.run(command, cwd=output, stdout=log, stderr=subprocess.STDOUT,
                           check=True, timeout=60)
        results[case] = temperatures(output / f"{case}.steady")
    check_response(results["cold"], results["hot"])
    result = {"status": "THERMAL_SMOKE_PASS", "eda_validated": False,
              "scope": "synthetic block-model response; no process/package calibration",
              "hotspot_sha256": hashlib.sha256(hotspot.read_bytes()).hexdigest(),
              "config_sha256": hashlib.sha256(config.read_bytes()).hexdigest(),
              "commands": commands, "temperatures_kelvin": results}
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hotspot", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.hotspot, args.config, args.output), indent=2))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "BLOCKED_OR_FAILED", "error": str(exc), "eda_validated": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
