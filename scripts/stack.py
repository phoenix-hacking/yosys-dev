#!/usr/bin/env python3
"""Source locks, environment checks and honest clean-flow smoke execution.

No incremental synthesis or ECO is implemented by this orchestration module.
Python >= 3.10. Run inside the selected Nix development shell for EDA commands.
"""
from __future__ import annotations

import argparse
import configparser
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone

from tool_audit import audit as audit_tools

ROOT = Path(__file__).resolve().parents[1]
SHA = re.compile(r"^[0-9a-f]{40}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
PROFILES = ("reference", "stock", "candidate")


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        value = json.load(f)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_lock(root: Path = ROOT) -> dict:
    value = read_json(root / "toolchain.lock.json")
    if value.get("schema_version") != 2 or value.get("system") != "x86_64-linux":
        raise ValueError("Unsupported lock schema or platform")
    for key in ("librelane", "yosys_stock", "yosys_candidate"):
        entry = value["sources"][key]
        if not REPO.fullmatch(entry["repository"]) or not SHA.fullmatch(entry["revision"]):
            raise ValueError(f"{key}: require repository and immutable 40-hex revision")
    for key in ("nix_eda_revision", "nixpkgs_revision"):
        if not SHA.fullmatch(value["inherited"][key]):
            raise ValueError(f"Unpinned inherited dependency: {key}")
    catalog = read_json(root / "nix/tool-catalog.json")
    required = set()
    for lane in ("digital", "analog", "rf"):
        names = value["tooling_contract"][lane + "_required"]
        if (not isinstance(names, list) or not names
                or any(not isinstance(name, str) for name in names)
                or len(set(names)) != len(names)):
            raise ValueError(f"Invalid required tool list: {lane}")
        required.update(names)
    if required != set(catalog):
        raise ValueError("Required tooling contract differs from Nix tool catalog")
    if value["initial_envelope"]["native_incremental_synthesis"] or value["initial_envelope"]["physical_eco"]:
        raise ValueError("Bootstrap does not support incremental synthesis or physical ECO")
    return value


def rendered_flake(root: Path = ROOT) -> str:
    lock = load_lock(root)
    text = (root / "nix/flake.nix.in").read_text()
    for token, key in (("LIBRELANE", "librelane"), ("CANDIDATE", "yosys_candidate"), ("STOCK", "yosys_stock")):
        text = text.replace(f"@{token}_REV@", lock["sources"][key]["revision"])
        text = text.replace(f"@{token}_REPO@", lock["sources"][key]["repository"])
    if re.search(r"@[A-Z_]+@", text):
        raise ValueError("Unresolved flake template token")
    return text


def check_static(root: Path = ROOT) -> dict:
    lock = load_lock(root)
    if (root / "flake.nix").read_text() != rendered_flake(root):
        raise ValueError("flake.nix differs from source lock; run render-flake --write")
    transition = read_json(root / "benchmarks/transitions/local-edit.json")
    # Test artifacts explicitly compare the updated design against updated RTL.
    if transition.get("gold_revision") != "B":
        raise ValueError("Edit-replay proof reference must be revision B")
    for name in ("digital", "analog", "rf", "mixed_signal"):
        if not (root / "flows" / name / "README.md").is_file():
            raise ValueError(f"Missing flow domain: {name}")
    for name in ("integrations/analog/README.md", "verification/README.md",
                 "platforms/README.md", "MIXED_SIGNAL_EXECUTION_PLAN.md"):
        if not (root / name).is_file():
            raise ValueError(f"Missing architecture contract: {name}")
    modules = configparser.ConfigParser()
    modules.read(root / ".gitmodules")
    section = 'submodule "components/yosys"'
    if modules.get(section, "path", fallback=None) != "components/yosys":
        raise ValueError("Missing pinned Yosys submodule")
    expected_url = "https://github.com/" + lock["sources"]["yosys_candidate"]["repository"] + ".git"
    if modules.get(section, "url", fallback=None) not in ("./", expected_url):
        raise ValueError("Yosys submodule source differs from source lock")
    return {"status": "PASS", "scope": "offline configuration only", "eda_validated": False}


def capture(command: list[str], cwd: Path | None = None) -> str:
    return subprocess.run(command, cwd=cwd, check=True, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=120).stdout.strip()


def verify_identity(identity: dict, profile: str, lock: dict) -> None:
    if identity.get("schema_version") != 1 or identity.get("profile") != profile:
        raise ValueError("Wrong profile identity; enter the matching Nix shell")
    if identity.get("librelane_revision") != lock["sources"]["librelane"]["revision"]:
        raise ValueError("LibreLane revision mismatch")
    if profile != "reference":
        expected = lock["sources"]["yosys_" + profile]["revision"]
        if identity.get("yosys_revision") != expected:
            raise ValueError("Yosys revision mismatch")
    if not Path(identity["yosys_native"]).is_file():
        raise ValueError("Selected native compiler is missing")


def verify_build_lock(root: Path = ROOT) -> dict:
    source = load_lock(root)
    resolved = read_json(root / "flake.lock")
    if resolved.get("version") != 7:
        raise ValueError("Unsupported Nix lock format")
    nodes, origin = resolved["nodes"], resolved["root"]

    def edge(node: str, name: str, seen: frozenset = frozenset()) -> str:
        key = (node, name)
        if key in seen:
            raise ValueError("Cyclic Nix follows input")
        target = nodes[node]["inputs"][name]
        if isinstance(target, str):
            if target not in nodes:
                raise ValueError("Unknown Nix input node")
            return target
        if not isinstance(target, list) or not target or any(not isinstance(x, str) for x in target):
            raise ValueError("Invalid Nix follows input")
        current = origin
        for part in target:
            current = edge(current, part, seen | {key})
        return current

    expected = {
        ("librelane",): source["sources"]["librelane"]["revision"],
        ("yosys-stock",): source["sources"]["yosys_stock"]["revision"],
        ("yosys-candidate",): source["sources"]["yosys_candidate"]["revision"],
        ("librelane", "nix-eda"): source["inherited"]["nix_eda_revision"],
        ("librelane", "nix-eda", "nixpkgs"): source["inherited"]["nixpkgs_revision"],
    }
    checked = {}
    for path, revision in expected.items():
        node = origin
        for part in path:
            node = edge(node, part)
        locked = nodes[node]["locked"]
        if locked.get("rev") != revision or not locked.get("narHash"):
            raise ValueError("Resolved Nix identity differs from source pins: " + "/".join(path))
        checked["/".join(path)] = revision
    return {"status": "LOCK_IDENTITIES_CHECKED", "revisions": checked, "eda_validated": False}


def doctor(profile: str, root: Path = ROOT) -> dict:
    check_static(root)
    if not (root / "flake.lock").is_file():
        raise ValueError("Build lock unresolved: run python3 scripts/stack.py resolve")
    verify_build_lock(root)
    for command in ("nix", "phoenix-toolchain", "phoenix-librelane"):
        if shutil.which(command) is None:
            raise ValueError(f"Missing {command}; enter nix develop .#{profile}")
    path = Path(capture(["phoenix-toolchain", "--path"]))
    identity = read_json(path)
    verify_identity(identity, profile, load_lock(root))
    tools = audit_tools(path, root / "toolchain.lock.json", root / "nix/tool-catalog.json", "digital")
    if tools["blocked_tools"]:
        raise ValueError("Required digital tools unavailable: " + ", ".join(tools["blocked_tools"]))
    identity["tool_audit"] = tools
    identity["identity_file"] = str(path)
    identity["yosys_native_sha256"] = digest_file(Path(identity["yosys_native"]))
    identity["doctor_status"] = "PACKAGE_PATHS_CHECKED; in-process audit occurs during synthesis"
    return identity


def tree_digest(directory: Path) -> tuple[str, int]:
    """Hash file content and logical paths, following symlinks with cycle detection.

    Absolute symlink target paths are excluded from the digest for portability;
    their referenced content IS included. Special files and cycles are rejected.
    """
    digest, count = hashlib.sha256(), 0
    def visit(path: Path, relative: str, ancestors: frozenset[Path]) -> None:
        nonlocal count
        real = path.resolve(strict=True)
        if path.is_dir():
            if real in ancestors:
                raise ValueError(f"Cyclic platform symlink: {relative}")
            for child in sorted(path.iterdir(), key=lambda p: p.name):
                visit(child, relative + "/" + child.name, ancestors | {real})
        elif path.is_file():
            digest.update(relative.encode() + b"\0" + digest_file(path).encode() + b"\n")
            count += 1
        else:
            raise ValueError(f"Unsupported special file: {path}")
    visit(directory.resolve(strict=True), "", frozenset())
    if not count:
        raise ValueError("Empty platform inventory")
    return digest.hexdigest(), count


def seal_platform(pdk_root: Path, revision: str, root: Path = ROOT) -> dict:
    if not SHA.fullmatch(revision):
        raise ValueError("Require the selected PDK build/source 40-hex revision")
    platform = read_json(root / "platforms/sky130hd.json")
    effective = (pdk_root / platform["pdk"]).resolve(strict=True)
    digest, count = tree_digest(effective)
    result = {"schema_version": 1, "pdk": platform["pdk"],
              "standard_cell_library": platform["standard_cell_library"],
              "revision": revision, "content_sha256": digest, "files": count,
              "local_path": str(effective), "status": "RECORDED_NOT_QUALIFIED"}
    write_json(root / ".state/platform.lock.json", result)
    return result


def clone_component(root: Path = ROOT) -> None:
    entry = load_lock(root)["sources"]["yosys_candidate"]
    path = root / "components/yosys"
    indexed = capture(["git", "ls-files", "--stage", "--", "components/yosys"], root)
    if not indexed.startswith("160000 " + entry["revision"] + " 0\t"):
        raise ValueError("Compiler gitlink differs from source lock; review both pins together")
    if path.is_symlink():
        raise ValueError("Compiler checkout must not be a symlink")
    if path.exists() and any(path.iterdir()):
        # An uninitialized gitlink is an empty directory; Git otherwise walks up
        # to the superproject and would mistake its HEAD for the compiler HEAD.
        if not (path / ".git").exists() or Path(capture(["git", "rev-parse", "--show-toplevel"], path)).resolve() != path.resolve():
            raise ValueError("Existing compiler directory is not its own checkout")
        head = capture(["git", "rev-parse", "HEAD"], path)
        dirty = capture(["git", "status", "--porcelain", "--untracked-files=normal"], path)
        if head != entry["revision"] or dirty:
            raise ValueError("Existing compiler checkout differs or is dirty; refusing to reset it")
    subprocess.run(["git", "submodule", "update", "--init", "--recursive", "--", "components/yosys"], cwd=root, check=True)
    if capture(["git", "rev-parse", "HEAD"], path) != entry["revision"]:
        raise ValueError("Initialized compiler revision differs from source lock")
    statuses = capture(["git", "submodule", "status", "--recursive"], path)
    if any(line.startswith(("-", "+", "U")) for line in statuses.splitlines()):
        raise ValueError("Compiler has uninitialized or mismatched nested submodules")


def prepare_config(root: Path, revision: str, identity_file: Path) -> dict:
    if revision not in ("A", "B"):
        raise ValueError("Unknown fixture revision")
    config = read_json(root / "benchmarks/designs/mixed/config.json")
    config["VERILOG_FILES"] = [str((root / f"benchmarks/designs/mixed/{revision}/top.v").resolve())]
    config["meta"] = {"version": 2, "flow": "Phoenix.Classic"}
    config["PHOENIX_TOOLCHAIN_FILE"] = str(identity_file.resolve())
    return config


def run_smoke(args: argparse.Namespace, root: Path = ROOT) -> int:
    identity = doctor(args.profile, root)
    platform = read_json(root / ".state/platform.lock.json")
    effective = (args.pdk_root / platform["pdk"]).resolve(strict=True)
    current_digest, _ = tree_digest(effective)
    if current_digest != platform["content_sha256"]:
        raise ValueError("PDK content differs from recorded platform; refusing comparison")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    out = root / ".runs" / f"{stamp}-{args.profile}-{args.revision}"
    out.mkdir(parents=True, exist_ok=False)
    config = prepare_config(root, args.revision, Path(identity["identity_file"]))
    write_json(out / "config.json", config)
    command = ["phoenix-librelane", "--pdk-root", str(args.pdk_root.resolve()),
               "--pdk", platform["pdk"], "--scl", platform["standard_cell_library"],
               "--tag", "smoke"]
    if args.stage == "synthesis":
        command += ["--to", "Phoenix.Synthesis"]
    command.append(str(out / "config.json"))
    result = {"schema_version": 1, "profile": args.profile, "revision": args.revision,
              "mode": "clean-pass-through", "stage": args.stage, "command": command,
              "toolchain": identity, "platform": platform,
              "config_sha256": digest_file(out / "config.json"),
              "rtl_sha256": digest_file(Path(config["VERILOG_FILES"][0])),
              "status": "RUNNING", "formal_status": "NOT_RUN", "accepted": False,
              "peak_process_tree_rss_bytes": None,
              "memory_note": "Process-tree sampling is not implemented in bootstrap",
              "ppa": None, "native_incremental_synthesis": False, "physical_eco": False}
    write_json(out / "result.json", result)
    start = time.monotonic()
    proc = None
    code = 1
    try:
        with (out / "console.log").open("w") as log:
            proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                    cwd=out, start_new_session=True)
            code = proc.wait(timeout=args.timeout)
        reports = list(out.rglob("synthesis.identity.json"))
        result["runtime_audits"] = [str(p.relative_to(out)) for p in reports]
        if code == 0 and len(reports) != 1:
            result["status"] = "INFRASTRUCTURE_ERROR_MISSING_OR_AMBIGUOUS_AUDIT"
            code = 1
        else:
            result["status"] = "FLOW_COMPLETED_UNVERIFIED" if code == 0 else "FLOW_FAILED"
    except (subprocess.TimeoutExpired, KeyboardInterrupt):
        result["status"] = "INTERRUPTED_OR_TIMEOUT"
        code = 124
    finally:
        if proc is not None and proc.poll() is None:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
        result["wall_seconds"] = time.monotonic() - start
        result["return_code"] = code
        write_json(out / "result.json", result)
    print(out / "result.json")
    return code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="action", required=True)
    subs.add_parser("check")
    render = subs.add_parser("render-flake")
    render.add_argument("--write", action="store_true")
    subs.add_parser("resolve", help="Generate the real transitive Nix lock on a Nix host")
    subs.add_parser("check-build-lock", help="Verify resolved source and inherited Nix revisions")
    subs.add_parser("bootstrap", help="Checkout compiler without overwriting existing work")
    check = subs.add_parser("doctor")
    check.add_argument("--profile", choices=PROFILES, required=True)
    platform = subs.add_parser("seal-platform")
    platform.add_argument("--pdk-root", type=Path, required=True)
    platform.add_argument("--revision", required=True)
    run = subs.add_parser("run")
    run.add_argument("--profile", choices=PROFILES, required=True)
    run.add_argument("--revision", choices=("A", "B"), required=True)
    run.add_argument("--stage", choices=("synthesis", "full"), default="synthesis")
    run.add_argument("--pdk-root", type=Path, required=True)
    run.add_argument("--timeout", type=float, default=3600)
    args = parser.parse_args()
    try:
        if args.action == "check":
            print(json.dumps(check_static(), indent=2))
        elif args.action == "render-flake":
            text = rendered_flake()
            if args.write:
                (ROOT / "flake.nix").write_text(text)
            else:
                print(text, end="")
        elif args.action == "resolve":
            check_static()
            subprocess.run(["nix", "--extra-experimental-features", "nix-command flakes", "flake", "lock"], cwd=ROOT, check=True)
            print(json.dumps(verify_build_lock(), indent=2))
        elif args.action == "check-build-lock":
            print(json.dumps(verify_build_lock(), indent=2))
        elif args.action == "bootstrap":
            clone_component()
        elif args.action == "doctor":
            print(json.dumps(doctor(args.profile), indent=2))
        elif args.action == "seal-platform":
            print(json.dumps(seal_platform(args.pdk_root, args.revision), indent=2))
        elif args.action == "run":
            return run_smoke(args)
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
