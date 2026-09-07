# ASIC Stack Software Requirements

This file defines the high-level software contract for the Phoenix ASIC stack. The top-level repository is the integration product; Yosys is one component beneath it.

## 1. Supported host

Initial supported bring-up host:

- Linux x86_64
- Nix >= 2.27 with flakes enabled
- Git with recursive submodule support
- Python >= 3.10
- Sufficient local NVMe space for Nix store paths, PDKs, build trees, caches and physical-design runs

The stack must fail closed when the selected environment cannot prove tool identity.

## 2. Flow/orchestration layer

The reference flow is LibreLane, the successor to OpenLane.

Pinned starting point:

- LibreLane release: `3.0.14`
- LibreLane commit: `f24e0ea5db2260719e9a0c7d51d07db74a87fa23`

LibreLane owns flow ordering, configuration/state handoff, step execution, result collection and flow-level metrics.

Project-specific LibreLane code belongs under `integrations/librelane/`.

## 3. Synthesis layer

Candidate compiler:

- Path: `components/yosys`
- Repository: `phoenix-hacking/yosys-dev`
- Pinned bootstrap commit: `43bbfbf71cba0435ebf806e9be8a888027c2903d`

Stock comparison compiler:

- Repository: `YosysHQ/yosys`
- Pinned bootstrap commit: `435977e97008578a4532da60e70f75b5e88d076d`

Yosys owns:

- RTL elaboration and synthesis semantics
- Native incremental compilation
- Persistent synthesis artifacts
- dependency and invalidation tracking
- maintained compiler analyses
- hierarchy/specialization logic
- memory inference and ASIC macro mapping policy
- technology mapping and ABC integration
- arithmetic/mux/control candidate generation
- synthesis-side timing/physical-context queries
- proof obligations and logical correspondence
- synthesis diagnostics and provenance

The top-level flow must never claim a Yosys improvement when it has silently executed a different binary or different Pyosys bindings.

## 4. Timing layer

OpenSTA is the reference timing-analysis semantic engine where feasible.

Requirements:

- clean and incremental timing must be comparable on the same updated netlist and parasitics
- timing constraints must have explicit lifetime/correspondence across synthesis edits
- unresolved clocks, endpoints or SDC collections are hard evidence failures
- scenario/corner identity must be recorded in result manifests
- Yosys must not grow a second full signoff STA engine

## 5. Physical implementation layer

OpenROAD is the first-class provider of placement, optimization, clock-tree, routing, parasitic and congestion context.

OpenROAD owns:

- floorplanning
- placement and legalization
- buffering/sizing and physical repair
- CTS
- global/detailed routing
- parasitic estimation/extraction
- physical legality and implementation state

Yosys may consume versioned physical context but must not absorb OpenROAD's placer/router responsibilities.

## 6. Physical verification and supporting tools

The LibreLane environment may include and pin, as required by the selected flow:

- KLayout
- Magic
- Netgen
- Verilator
- Icarus Verilog
- EQY/SBY and supported formal solvers
- ABC and Yosys plugins/frontends
- Ciel and PDK-management tooling

Every tool used in accepted evidence must have an immutable version/build identity.

## 7. PDK and standard-cell requirements

The first bring-up platform is SKY130A / `sky130_fd_sc_hd` for infrastructure validation only. It is not a proxy for advanced-node commercial PPA.

Accepted runs must identify:

- PDK source/build revision
- standard-cell library
- Liberty corner(s)
- LEF/tech LEF
- RC/corner data
- functional cell models
- SRAM/macro models where used
- excluded/dont-use cells
- floorplan/utilization parameters

No PDK or restricted model content is committed to this repository unless redistribution is explicitly permitted.

## 8. Reproducibility profiles

The stack maintains three independent profiles:

1. `reference` — LibreLane's packaged reference environment.
2. `stock` — pinned upstream Yosys under the same comparison packaging path used by the fork.
3. `candidate` — `components/yosys` / the Phoenix fork.

The generated result identity must include the actual executable path, Pyosys module path, Yosys source/build revision, ABC identity, LibreLane revision, OpenROAD/OpenSTA identities, PDK/library identities and configuration digest.

## 9. Validation hierarchy

Fast PR gate:

- static configuration checks
- unit tests
- Yosys compiler regressions for compiler changes
- edit-replay harness sanity

Nightly gate:

- stock vs candidate clean synthesis
- EQY/formal validation
- Yosys + OpenSTA metrics
- adversarial revision histories

Milestone gate:

- full matched LibreLane/OpenROAD implementation
- post-place and post-route timing
- area, wirelength, buffering and congestion
- DRC/LVS/antenna checks as applicable
- total RTL-to-GDS turnaround
- held-out workloads and negative outliers

A synthesis QoR optimization is not promoted as a major win until the benefit survives downstream physical implementation.

## 10. Incremental modes

`incremental_exact` is the first production target. It reuses valid synthesis artifacts while preserving the intended clean synthesis semantics of the supported recipe.

`incremental_eco` is later. It may intentionally preserve more implementation structure than a clean build, but every updated result must still satisfy functional proof, constraint correctness and explicit QoR/physical acceptance gates.

Physical ECO reuse is measured separately from Yosys synthesis reuse.

## 11. Repository ownership

Top-level stack owns:

- `flake.nix` / `flake.lock`
- `toolchain.lock.json`
- `integrations/`
- `benchmarks/`
- `platforms/`
- `schemas/`
- `scripts/`
- `tests/`
- `evidence/`
- stack execution/progress documents

`components/yosys` owns native compiler implementation and compiler-local tests.

Fork LibreLane, OpenROAD or OpenSTA only when a concrete missing extension/API requires a source change. Prefer narrow adapters and upstream-compatible interfaces.

## 12. Non-goals

Do not:

- replace RTLIL without profile evidence
- build a new STA engine inside Yosys
- build placement/routing inside Yosys
- count FPGA QoR as an ASIC project success criterion
- claim commercial parity from stock-Yosys comparisons alone
- treat a cache hit as correctness evidence
- treat a clean-flow checkpoint restart as native incremental synthesis
- commit restricted PDKs, proprietary RTL or credentials

## 13. Acceptance principle

The governing rule is:

> The stack may do less work, search better implementation alternatives, and reuse valid physical state, but it may never weaken correctness or conceal which tool actually produced the result.
