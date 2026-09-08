# ASIC Flow Software Requirements

This file defines the high-level software contract for `asic-flow`. The top-level repository is the integration product. It supports both digital and analog/mixed-signal ASIC implementation; Yosys is one component beneath the digital lane.

## 1. Supported host

Initial supported bring-up host:

- Linux x86_64
- Nix >= 2.27 with flakes enabled
- Git with recursive submodule support
- Python >= 3.10
- Sufficient local NVMe space for Nix store paths, PDKs, build trees, caches, SPICE data, and physical-design runs

The flow must fail closed when the selected environment cannot prove tool identity.

## 2. Digital flow/orchestration layer

The reference digital flow is LibreLane, the successor to OpenLane.

Pinned starting point:

- LibreLane release: `3.0.14`
- LibreLane commit: `f24e0ea5db2260719e9a0c7d51d07db74a87fa23`

LibreLane owns flow ordering, configuration/state handoff, step execution, result collection and flow-level metrics for digital implementation.

Project-specific LibreLane code belongs under `integrations/librelane/`.

## 3. Digital synthesis layer

Candidate compiler:

- Path: `components/yosys`
- Repository: `phoenix-hacking/yosys-dev`
- Pinned bootstrap commit: `43bbfbf71cba0435ebf806e9be8a888027c2903d`

Stock comparison compiler:

- Repository: `YosysHQ/yosys`
- Pinned bootstrap commit: `435977e97008578a4532da60e70f75b5e88d076d`

Yosys owns RTL elaboration/synthesis semantics, native incremental compilation, persistent synthesis artifacts, dependency/invalidation tracking, maintained compiler analyses, hierarchy/specialization, memory inference/macro mapping, technology mapping, arithmetic/mux/control candidate generation, synthesis-side timing/physical-context queries, proof obligations, and synthesis provenance.

The top-level flow must never claim a Yosys improvement when it has silently executed a different native binary or different Pyosys bindings.

## 4. Timing layer

OpenSTA is the reference digital timing-analysis semantic engine where feasible. Clean and incremental timing must be comparable on the same updated netlist/parasitics, SDC correspondence must be explicit, and unresolved clocks/endpoints/collections are evidence failures.

## 5. Digital physical implementation layer

OpenROAD is the first-class provider of floorplanning, placement, legalization, sizing/buffering, CTS, routing, parasitics, congestion and physical context. Yosys may consume versioned physical context but must not absorb OpenROAD's placer/router responsibilities.

## 6. Analog and mixed-signal design layer

Analog blocks are not passed through Yosys or treated as ordinary standard-cell logic. The initial supported open-source analog lane shall provide:

- **Xschem** for schematic capture and hierarchical analog/mixed-signal netlist generation.
- **ngspice** as the baseline SPICE simulator.
- **Xyce** as a second simulator for larger/parallel or model-specific workloads where supported.
- **OpenVAF / OSDI** for Verilog-A compact-model compilation where required by the selected PDK and simulator.
- **Magic and/or KLayout** for custom analog layout, DRC, geometry inspection, and GDS interchange.
- **Netgen** for LVS.
- **CACE** for specification-driven analog characterization and regression.

Optional later tools may include Qucs-S, GDSFactory, BAG/ALIGN-style generators, pygmid/gm-ID analysis, charlib, openEMS, and Palace where they provide measurable value and the PDK supplies usable collateral.

Accepted analog flows shall support the standard sequence:

```text
schematic
→ pre-layout simulation
→ custom layout
→ DRC
→ LVS
→ parasitic extraction
→ post-layout simulation
→ characterization/regression
→ qualified GDS/IP views
```

Every simulator, model compiler, layout tool, verification tool and characterization tool used in accepted evidence must have immutable version/build identity.

## 7. Mixed-signal integration contract

Analog/mixed-signal IP integrates with the digital flow through explicit abstract views rather than by flattening transistor-level circuitry into Yosys.

Depending on the block, the top level may require:

- GDS/OASIS physical view
- LEF abstract
- SPICE/CDL netlist
- Verilog or black-box functional model
- Liberty timing/power model where meaningful
- SDC/interface constraints
- extracted parasitics for analog verification
- pin/power-domain/voltage-domain metadata
- optional behavioral Verilog-A or real-number model for system simulation

Mixed-signal assembly must preserve view identity so the same analog revision is used by LVS, digital implementation, top-level integration and verification.

## 8. Physical verification and supporting tools

The integrated environment may include and pin, as required:

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
- OpenVAF/OSDI tooling
- CACE
- Ciel and PDK-management tooling

## 9. PDK requirements

The first digital bring-up platform remains SKY130A / `sky130_fd_sc_hd` for infrastructure validation only.

Analog qualification requires PDK collateral beyond a digital standard-cell flow. The selected analog-capable PDK must provide, as applicable:

- transistor/passive/HBT compact models and corners
- simulator initialization/model files
- Xschem or equivalent symbols/model bindings
- Magic/KLayout tech files and DRC decks
- Netgen LVS setup
- parasitic extraction rules/data
- device layout generators or parameterized-cell support where available
- process limits relevant to analog layout/reliability
- GDS layer mapping

IHP SG13G2 is a strong candidate for the analog/mixed/RF qualification lane because its open PDK documents Xschem, ngspice, Xyce, KLayout, Magic, Netgen, Verilog-A/model support and LibreLane/OpenROAD collateral. SKY130 remains useful for compatibility and existing open analog IP.

No restricted PDK/model content is committed unless redistribution is explicitly permitted.

## 10. Reproducibility profiles

Digital profiles remain:

1. `reference` — LibreLane packaged reference.
2. `stock` — pinned upstream Yosys under the comparison packaging path.
3. `candidate` — `components/yosys`.

Analog runs require an analogous resolved-toolchain manifest including Xschem, simulator, model-compiler, layout, extraction, LVS, characterization, PDK/model and configuration identities.

## 11. Validation hierarchy

Fast PR gate:

- static/configuration checks
- unit tests
- Yosys compiler regressions for compiler changes
- analog netlist/model/configuration smoke tests where applicable

Nightly gate:

- stock-vs-candidate digital synthesis and EQY
- Yosys + OpenSTA metrics
- analog schematic-to-netlist regression
- representative ngspice/Xyce simulations
- CACE spec regressions

Milestone gate:

- full LibreLane/OpenROAD digital implementation
- digital DRC/LVS/antenna/timing/PPA checks
- analog DRC/LVS
- analog pre/post-layout correlation
- analog spec/yield/corner characterization where models support it
- mixed-signal top-level assembly/view consistency

A digital synthesis QoR optimization is not promoted as a major win until it survives downstream physical implementation. An analog block is not promoted as qualified merely because its schematic simulation passes; layout verification and post-layout/spec checks are required.

## 12. Incremental modes

`incremental_exact` and `incremental_eco` remain Yosys/digital implementation targets. Analog flows may later gain independent incremental simulation/extraction/characterization caching, but analog cache hits must never substitute for model, layout or corner validity.

## 13. Repository ownership

Top-level `asic-flow` owns toolchain locks, LibreLane integration, analog orchestration adapters, benchmarks, platforms, schemas, scripts, tests, evidence, mixed-signal integration and release qualification.

`components/yosys` owns native compiler implementation and compiler-local tests.

Fork LibreLane, OpenROAD, OpenSTA, analog tools or PDK tooling only when a concrete missing extension/API requires source changes. Prefer narrow adapters and upstream-compatible interfaces.

## 14. Non-goals

Do not:

- force analog circuits through Yosys
- build a new STA engine inside Yosys
- build placement/routing inside Yosys
- treat pre-layout analog simulation alone as tapeout qualification
- claim signoff equivalence to proprietary foundry-qualified flows without evidence
- commit restricted PDKs, models, proprietary RTL or credentials
- mix digital and analog view revisions silently

## 15. Acceptance principle

> `asic-flow` may reuse valid work and search better implementations, but every result must preserve correctness, tool/model identity, view consistency and reproducible evidence across the digital and analog lanes.
