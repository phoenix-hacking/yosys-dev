# Tools added for specific capability gaps

These opt-in workflows reuse the pinned EDA environment. They add no alternate
RTL-to-GDS flow. OpenROAD continues to own placement, routing, OpenRCX extraction,
PDNSim power-grid analysis and its DFT/partitioning facilities.

| Gap in this repository | Addition | Concrete integration | Acceptance |
|---|---|---|---|
| Simulator binaries had no reusable Python testbench | cocotb | Revision A reset, arithmetic, select and counter-wrap oracle | Original passes; a deliberately incorrect scratch copy fails |
| No measurement of which mutations a testbench detects | MCY | 50 seeded mutations run through that cocotb oracle | Compile/import/timeout errors stop the run; survivors receive equivalence triage |
| No reusable IP fileset/dependency/build manifest | FuseSoC + Edalize | CAPI2 core for the existing benchmark and an Icarus simulation target | Core resolves and self-checking target exits successfully |
| No CPU-stack or heap-allocation capture for compiler work | perf + heaptrack | Runner binds capture to stock/candidate Yosys and records input/binary hashes | Successful command plus nonempty profile data |
| Thermal constraints had no executable thermal model | UVA HotSpot | Pinned native/Nix build and a two-block heat-response oracle | Zero-power ambient and positive lateral heat response pass |

The first six packages already have derivations in the inherited pinned sources:
[cocotb 2.0.1](https://github.com/fossi-foundation/nix-eda/blob/8f990fb77529c09e540e453cd836af9930ec58db/nix/cocotb.nix),
[MCY](https://github.com/NixOS/nixpkgs/blob/b3aad468604d3e488d627c0b43984eb60e75e782/pkgs/by-name/mc/mcy/package.nix),
[FuseSoC 2.2.1](https://github.com/NixOS/nixpkgs/blob/b3aad468604d3e488d627c0b43984eb60e75e782/pkgs/by-name/fu/fusesoc/package.nix),
[Edalize 0.6.1](https://github.com/NixOS/nixpkgs/blob/b3aad468604d3e488d627c0b43984eb60e75e782/pkgs/development/python-modules/edalize/default.nix),
[perf](https://github.com/NixOS/nixpkgs/blob/b3aad468604d3e488d627c0b43984eb60e75e782/pkgs/by-name/pe/perf/package.nix)
and [heaptrack](https://github.com/NixOS/nixpkgs/blob/b3aad468604d3e488d627c0b43984eb60e75e782/pkgs/by-name/he/heaptrack/package.nix).
[HotSpot](https://github.com/uvahotspot/HotSpot/tree/f18831e48cef5d62580585cca0d7fab6c71bc3cc)
has a project derivation; the unrelated KDE `pkgs.hotspot` is never selected.

## Select a workflow

Complete the Nix resolution steps in [BRINGUP.md](BRINGUP.md). Shell suffixes
`verification`, `ip`, `profiling`, and `thermal` work with each of `reference`,
`stock`, and `candidate`. `extended` enables all four. Plain profiles keep their
existing required-tool contract. Missing extension tools block that extension's
audit; `--lane all` still checks the baseline digital/analog/RF contract only.

```sh
nix develop .#reference-verification
phoenix-tool-audit --extension verification
```

MCY's embedded Yosys paths are overridden to the selected comparison profile.
Package availability is separate from workflow acceptance. Nix evaluation/build
and live cocotb/MCY/FuseSoC/profiling runs remain unqualified in this handoff.

## RTL oracle and mutation detection

From the repository root, inside `reference-verification`:

```sh
make -C verification/cocotb SIM=icarus
python3 scripts/simulation_result.py .runs/cocotb/icarus/results.xml --make-exit 0
export ASIC_FLOW_ROOT="$PWD"
mkdir .runs/mcy-mixed
cp verification/mcy/config.mcy .runs/mcy-mixed/config.mcy
cp benchmarks/designs/mixed/A/top.v .runs/mcy-mixed/top.v
cd .runs/mcy-mixed
mcy init
mcy run -j2
```

Before accepting the oracle, also run it on a scratch copy with the `count + 1'b1`
expression changed to `count + 2'd2`, setting `VERILOG_SOURCES`, `SIM_BUILD` and
`COCOTB_RESULTS_FILE` to that separate run. Require an `AssertionError` failure.
Keep revision A and its oracle unchanged. The MCY adapter checks the actual Make
exit status and fresh cocotb XML; missing tests, imports, skips and timeouts are
errors. `SURVIVED` includes equivalent mutations, so it is not a coverage deficit
until formal triage classifies it. Preserve the MCY seed/database and tool identity.

## Reusable IP build

Inside `reference-ip`, from the repository root:

```sh
phoenix-tool-audit --extension ip
fusesoc --cores-root benchmarks/designs/mixed run --target=sim --build-root .runs/fusesoc-mixed asic-flow:benchmarks:mixed:0.1.0
```

Require exit 0 and `ASIC_FLOW_IP_PASS` in the simulation log. The default fileset
contains revision A RTL only; the `sim` target adds its testbench. This establishes
a reusable IP manifest/target convention for later SoC composition. LibreLane
remains the implementation flow.

## Compiler CPU and memory profiling

Inside `candidate-profiling`, from the repository root:

```sh
phoenix-tool-audit --extension profiling
python3 scripts/profile_yosys.py --profile candidate --tool perf --script benchmarks/designs/mixed/profile.ys --input benchmarks/designs/mixed/A/top.v --output .runs/candidate-perf
python3 scripts/profile_yosys.py --profile candidate --tool heaptrack --script benchmarks/designs/mixed/profile.ys --input benchmarks/designs/mixed/A/top.v --output .runs/candidate-heap
perf report -i .runs/candidate-perf/perf.data
heaptrack_print .runs/candidate-heap/heaptrack.gz
```

Repeat with `stock-profiling`, `--profile stock` and fresh output directories.
For larger benchmarks, supply their Yosys script and repeat `--input` for every
RTL/include/data file read. Captures include binary/input hashes, the package
identity, host kernel, command, elapsed time and exit status. The timeout kills
the entire profiling process group. Host perf permissions must already allow
capture; the runner does not change them. Profile overhead is not a QoR metric.
Keep traces under `.runs/` and require symbols for actionable stack attribution.

## Thermal response

```sh
nix build .#hotspot-thermal --out-link .state/hotspot-result
python3 scripts/thermal_smoke.py --hotspot .state/hotspot-result/bin/hotspot --config .state/hotspot-result/share/hotspot-thermal/template.config --output .runs/thermal-check
```

The Nix derivation also runs this check during its build. It tests two adjacent
1 mm square blocks at 300 K ambient, first with zero power and then with 1 W in
the digital block. Both temperatures must rise, with the powered block hotter.
The native source build passed this check locally; the Nix derivation has not
been evaluated here. Process/package calibration, actual power maps and thermal
release limits remain necessary before applying the model to a real design.
