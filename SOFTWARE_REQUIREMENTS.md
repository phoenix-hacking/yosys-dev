# ASIC Flow Software Requirements

This file defines the high-level software contract for `asic-flow`. The top-level repository is the integration product. It supports digital, analog/custom, RF/EM and mixed-signal ASIC implementation; Yosys is one component beneath the digital lane.

See [TOOLCHAIN_MATRIX.md](TOOLCHAIN_MATRIX.md) for the complete capability checklist and qualification state.

## 1. Supported host

Initial supported bring-up host:

- Linux x86_64
- Nix >= 2.27 with flakes enabled
- Git with recursive submodule support
- Python >= 3.10
- sufficient local NVMe for Nix store paths, PDKs, build trees, caches, SPICE/EM data and physical-design runs

The flow must fail closed when the selected environment cannot prove tool/model/PDK identity required by the active lane.

## 2. Digital flow/orchestration layer

The reference digital flow is LibreLane, the successor to OpenLane.

Pinned starting point:

- LibreLane release: `3.0.14`
- LibreLane commit: `f24e0ea5db2260719e9a0c7d51d07db74a87fa23`

LibreLane owns flow ordering, configuration/state handoff, step execution, result collection and flow-level metrics for digital implementation. Project-specific code belongs under `integrations/librelane/`.

## 3. Digital synthesis layer

Candidate compiler:

- path: `components/yosys`
- historical source URL: `phoenix-hacking/yosys-dev` (the same repository being renamed to `asic-flow`; compiler-tree history is preserved)
- pinned bootstrap commit: `43bbfbf71cba0435ebf806e9be8a888027c2903d`

Stock comparison compiler:

- repository: `YosysHQ/yosys`
- pinned bootstrap commit: `435977e97008578a4532da60e70f75b5e88d076d`

Yosys owns RTL elaboration/synthesis semantics, native incremental compilation, persistent synthesis artifacts, dependency/invalidation tracking, maintained compiler analyses, hierarchy/specialization, memory inference/macro mapping, technology mapping, arithmetic/mux/control candidate generation, synthesis-side timing/physical-context queries, proof obligations and synthesis provenance.

The top-level flow must never claim a Yosys improvement when it has silently executed a different native binary or different Pyosys bindings.

## 4. Digital timing and physical implementation

OpenSTA is the reference digital timing semantic engine where feasible. Clean and incremental timing must be comparable on the same updated netlist/parasitics, SDC correspondence must be explicit, and unresolved clocks/endpoints/collections are evidence failures.

OpenROAD is the first-class provider of floorplanning, placement, legalization, sizing/buffering, CTS, routing, parasitics, congestion and physical context. Yosys may consume versioned physical context but must not absorb OpenROAD's placer/router responsibilities.

## 5. Analog/custom IC design layer

Analog blocks are not passed through Yosys or treated as standard-cell logic. The baseline open-source analog lane requires:

- **Xschem** — schematic capture and hierarchical netlist generation.
- **ngspice** — baseline circuit simulator.
- **Xyce** — second simulator for larger/parallel or model-specific workloads on Linux.
- **OpenVAF Reloaded / OSDI** — Verilog-A compact-model compilation where required.
- **Magic and KLayout** — custom layout, geometry inspection, DRC/extraction as supported by the PDK.
- **Netgen and/or PDK-supported KLayout LVS** — LVS.
- **CACE** — specification-driven characterization/regression.
- **GDSFactory** — parameterized layout/PCells and programmatic geometry support.

Optional analog tools may include Qucs-S, Gnucap and pygmid when they provide reproducible value.

Accepted analog flows shall support:

```text
schematic
→ pre-layout simulation
→ custom layout
→ DRC
→ LVS
→ parasitic extraction
→ post-layout simulation
→ characterization/regression
→ qualified macro views
```

A passing schematic simulation is not tapeout qualification.

## 6. RF / electromagnetic layer

Distributed passives and RF structures require an EM lane rather than ideal lumped models alone.

The baseline RF capability requires:

- **openEMS** — open full-wave/FDTD electromagnetic analysis.
- **Palace** — open 3D FEM electromagnetic analysis.
- **GDSFactory** — deterministic parameterized RF/passive geometry and solver interchange where practical.
- **scikit-rf** — S-parameter/Touchstone network analysis and post-processing.
- **ngspice/Xyce** — circuit-level verification of extracted/derived passive models.

Optional meshing/visualization helpers may include Gmsh and ParaView.

RF qualification records geometry/material/PDK revision, ports/reference impedance, solver/version, mesh or discretization settings, sweep/convergence evidence, S-parameters and the compact model used by circuit simulation.

## 7. Mixed-signal integration contract

The mixed-signal lane composes independently qualified digital, analog and RF/EM blocks. It does not flatten transistor-level analog circuitry into Yosys.

Depending on the macro, the top level may require:

- GDS/OASIS physical view
- LEF abstract
- SPICE/CDL source and extracted netlists
- Verilog black-box/functional model
- Liberty timing/power model where meaningful
- SDC/interface constraints
- Verilog-A or real-number behavioral model
- pin/supply/voltage-domain metadata
- placement/routing keepouts
- substrate/noise sensitivity metadata
- load, jitter or bandwidth characterization

All views must carry one immutable macro release identity. The baseline open flow uses hierarchical macro verification and behavioral/interface models at system level. Proprietary-style full-chip continuous-time/event-driven AMS co-simulation is not claimed until an open implementation is independently validated.

## 8. Physical verification and supporting tools

The integrated environment shall expose or package, as applicable:

- KLayout
- Magic
- Netgen
- Verilator
- Icarus Verilog
- EQY/SBY and supported formal solvers
- ABC and Yosys plugins/frontends
- Xschem
- ngspice
- Xyce
- OpenVAF Reloaded/OSDI tooling
- CACE
- GDSFactory
- openEMS
- Palace
- scikit-rf
- Ciel and PDK-management tooling

Every tool used in accepted evidence must have an immutable version/build identity.

## 9. PDK requirements and reference platforms

### SKY130A

First digital RTL-to-GDS and analog compatibility platform. It is for infrastructure qualification, not advanced-node PPA claims.

### IHP SG13G2

First RF-capable mixed-signal reference target. It is preferred for the RF lane because the open PDK publishes analog/mixed/RF, Verilog-A, Xschem, ngspice/Xyce, KLayout/Magic/Netgen, GDSFactory, LibreLane/OpenROAD, openEMS and Palace collateral.

### GF180MCU

Secondary future mixed-signal portability target.

For any platform, accepted runs must identify applicable compact models/corners, simulator initialization, symbols/model bindings, layout tech files, DRC/LVS rules, extraction data, PCells/generators, layer mapping, standard-cell timing/LEF/GDS data and macro views. No restricted PDK/model content is committed unless redistribution is explicitly permitted.

## 10. Reproducibility profiles

Digital profiles remain:

1. `reference` — LibreLane packaged reference.
2. `stock` — pinned upstream Yosys under the comparison packaging path.
3. `candidate` — `components/yosys`.

Analog and RF runs require analogous resolved-toolchain manifests containing simulator/model compiler/layout/LVS/extraction/characterization/EM/PDK identities and configuration digests.

The Nix shell discovers required native and Python packages from the inherited
package set. `nix/tool-catalog.json` specifies their attributes, executables and
modules. The package audit exits nonzero for missing/unusable requirements and
checks that Python imports belong to the selected package. Passing the audit
establishes availability only; a release lane still requires its complete PDK,
simulation, verification and representative flow gates.

## 11. Validation hierarchy

Fast PR gate:

- static/configuration checks
- unit tests
- Yosys compiler regressions for compiler changes
- analog/RF netlist/model/configuration smoke tests where applicable

Nightly gate:

- stock-vs-candidate digital synthesis and EQY
- Yosys + OpenSTA metrics
- analog schematic-to-netlist regression
- representative ngspice/Xyce simulations
- CACE spec regressions
- selected RF solver smoke tests once packaged

Milestone gate:

- full LibreLane/OpenROAD digital implementation
- digital DRC/LVS/antenna/timing/PPA checks
- analog DRC/LVS/extraction and post-layout correlation
- analog spec/yield/corner characterization where models support it
- RF solver/convergence and compact-model correlation
- mixed-signal top-level assembly/view consistency

A digital synthesis QoR optimization is not promoted until it survives downstream physical implementation. An analog/RF block is not promoted based only on schematic or ideal-model simulation.

## 12. Incremental modes

`incremental_exact` and `incremental_eco` remain Yosys/digital implementation targets. Analog/RF flows may later add independent simulation/extraction/EM/characterization caches, but a cache hit never substitutes for model, layout, corner or solver validity.

## 13. Repository ownership

Top-level `asic-flow` owns toolchain locks, LibreLane integration, analog/RF orchestration adapters, benchmarks, platforms, schemas, scripts, tests, evidence, mixed-signal integration and release qualification.

`components/yosys` owns native compiler implementation and compiler-local tests.

Fork LibreLane, OpenROAD, OpenSTA, analog/RF tools or PDK tooling only when a concrete missing extension/API requires source changes. Prefer narrow adapters and upstream-compatible interfaces.

## 14. Non-goals and honest boundaries

Do not:

- force analog/RF circuits through Yosys
- build a new STA engine inside Yosys
- build placement/routing inside Yosys
- treat schematic simulation or ideal passive models as physical qualification
- claim proprietary AMS/signoff equivalence without evidence
- claim advanced-node production DFT, UPF, reliability or foundry-qualified RF signoff unless those capabilities are actually added and validated
- commit restricted PDKs, models, proprietary RTL or credentials
- mix digital/analog/RF view revisions silently

## 15. Acceptance principle

> `asic-flow` may reuse valid work and search better implementations, but every result must preserve correctness, tool/model identity, view consistency and reproducible evidence across digital, analog and RF domains.
