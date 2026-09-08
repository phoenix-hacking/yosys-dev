# Executable bring-up handoff

Use the prepared flow branch from README.md. The supported build host is Linux
x86_64 with Git, Python >= 3.10 and Nix >= 2.27 (flakes enabled), network access
to the locked upstream sources and binary caches, and space for tools/PDKs/runs.
The initial preparation environment has no Nix or EDA binaries installed.

## 1. Verify source and initialize the compiler

```sh
python3 scripts/stack.py check
python3 -m compileall -q scripts integrations tests
python3 -m unittest discover -s tests -v
python3 scripts/stack.py bootstrap
git -C components/yosys rev-parse HEAD
git -C components/yosys submodule status --recursive
```

The expected compiler HEAD is `43bbfbf71cba0435ebf806e9be8a888027c2903d`.
An uninitialized, mismatched or dirty component is not a valid candidate build.
The offline test suite explicitly skips the two live LibreLane tests outside
the selected environment.

## 2. Resolve, review and build the real Nix closure (STK-09–12)

```sh
nix-instantiate --eval --strict nix/tests/tool-discovery.nix
python3 scripts/stack.py resolve
python3 scripts/stack.py check-build-lock
git diff -- flake.lock
nix build .#reference .#stock .#candidate
nix flake check
nix develop .#reference --command python3 scripts/stack.py doctor --profile reference
nix develop .#stock --command python3 scripts/stack.py doctor --profile stock
nix develop .#candidate --command python3 scripts/stack.py doctor --profile candidate
nix develop .#candidate --command python3 -m unittest discover -s tests -p test_live_plugin.py -v
```

`resolve` checks the actual locked LibreLane, stock/candidate Yosys, inherited
nix-eda and nixpkgs revisions against the source contract, including Nix follows
links. Retain the resolved `flake.lock`, derivation/store identities and build
logs. Run upstream Yosys regressions before accepting STK-11. No transitive lock
is committed by the preparation work because it has not been resolved by Nix.

## 3. Close required analog/RF tooling (ANA-01/02, RF-01)

```sh
nix develop .#reference --command phoenix-analog-tool-audit --lane analog
nix develop .#reference --command phoenix-analog-tool-audit --lane rf
nix develop .#reference --command phoenix-analog-tool-audit --lane all
```

The audit binds the identity to the source lock and tool catalog, checks package
versions and executables, and imports Python modules with the selected interpreter.
Missing, unusable or foreign packages return status `BLOCKED` and exit code 2.
`AVAILABLE_NOT_QUALIFIED` only establishes availability; simulator/model loading,
GUI/headless support and representative flow tests remain required.

The catalog discovers GDSFactory and scikit-rf under `python3.pkgs`. The pinned
nixpkgs source provides scikit-rf 1.8.0; its build/import is still untested here.
CACE, openEMS, Palace and scikit-rf remain explicit closure/qualification tasks.
The selected nix-eda revision does not explicitly add OpenVAF Reloaded; check
the selected package set and package it if missing. Today's upstream package list
does not establish availability at our older immutable pin.

## 4. Provision and qualify platforms (STK-13, ANA-03/04, RF-02)

Provision SKY130A through the pinned Ciel environment. Choose and record the
actual build revision; do not substitute a moving tag for a PDK identity. With
`PDK_ROOT` pointing to the directory containing `sky130A` and
`SKY130_BUILD_REVISION` containing its verified 40-hex build revision:

```sh
python3 scripts/stack.py seal-platform --pdk-root "$PDK_ROOT" --revision "$SKY130_BUILD_REVISION"
nix develop .#reference --command python3 scripts/stack.py run --profile reference --revision A --stage full --pdk-root "$PDK_ROOT"
nix develop .#stock --command python3 scripts/stack.py run --profile stock --revision B --stage full --pdk-root "$PDK_ROOT"
nix develop .#candidate --command python3 scripts/stack.py run --profile candidate --revision B --stage full --pdk-root "$PDK_ROOT"
```

The runner records `FLOW_COMPLETED_UNVERIFIED` on tool exit 0. Acceptance still
requires the appropriate EQY gold-B/gate-B proof, timing and physical checks.

For IHP SG13G2, select a reviewed immutable PDK commit with its submodules and
record model, Verilog-A, layout/DRC/LVS, extraction, digital and EM collateral.
The current `seal-platform` and digital smoke runner are SKY130-specific; IHP
provisioning and platform adapters remain ANA-04/RF-02 implementation tasks.
GF180MCU stays a later portability target. Do not commit PDK content or run data.

## 5. Complete the first cross-domain qualification

Follow `MIXED_SIGNAL_EXECUTION_PLAN.md` in dependency order: a small analog cell
through schematic simulation, layout, DRC/LVS, extraction and post-layout CACE;
an IHP RF passive through deterministic geometry, EM convergence and circuit-model
correlation; then immutable macro releases and a small mixed-signal digital top.
Supply/voltage, clock/jitter, noise/load, keepout/routing, substrate and thermal
constraints must travel with the macro views. A larger CPU/GPU/DSP/NPU benchmark
comes after these acceptance gates.

## Source maintenance

After reviewing and staging intended source changes:

```sh
python3 scripts/stack.py render-flake --write
python3 scripts/update_export_manifest.py
python3 -m unittest discover -s tests -v
git diff --check
```

The manifest refresher includes tracked/staged source only. Independent export
regenerates `.gitmodules` with an absolute compiler URL; the main repository uses
a relative URL to survive its rename. Neither workflow counts as compiler progress.
