# Stack execution plan

Version 0.2 — 2026-09-07. Goal: make the Yosys ASIC roadmap executable inside a complete open-source `asic-flow` that also supports analog/custom IC, RF/EM and mixed-signal SoC assembly.

Digital integration tasks remain here. Analog/RF/mixed-signal bring-up is tracked in `MIXED_SIGNAL_EXECUTION_PLAN.md`. Tool presence/qualification is tracked in `TOOLCHAIN_MATRIX.md`.

## Authority and dependency boundaries

The compiler's original core/research tasks remain in the Yosys plan. STK tasks are integration gates, not additions to the compiler completion numerator. ANA/RF/MS tasks likewise measure non-compiler flow capability.

Source authority: `toolchain.lock.json`. Build closure: generated `flake.lock`. Final superproject component selection: Yosys gitlink must equal the source lock. Runtime authority: generated package identity plus same-process compiler audit. Platform authority: selected PDK revision and actual content inventory. None replaces required formal, analog, RF or physical evidence.

## Digital bring-up backlog

Each unchecked task requires evidence, not code presence.

- [x] **STK-01** Preserve compiler layout and stage an independently exportable top-level flow workspace.
- [x] **STK-02** Pin current LibreLane release and stock/candidate source revisions.
- [x] **STK-03** Implement fail-closed configuration/profile checks.
- [x] **STK-04** Implement same-process audit helpers; reject foreign native binaries/bindings. Live gate remains STK-12.
- [x] **STK-05** Supply a real A/B RTL change with B declared as proof reference.
- [x] **STK-06** Implement safe PDK content inventory including symlink-cycle rejection.
- [x] **STK-07** Implement independent export, pinned gitlink and no-overwrite checks.
- [ ] **STK-08** Publish/rename independent `asic-flow` remote. Blocker: current GitHub connector lacks repository administration.
- [ ] **STK-09** Resolve/review/commit transitive Nix lock; verify inherited nix-eda/nixpkgs selections.
- [ ] **STK-10** Evaluate/build reference digital profile on supported Linux host. Capture store paths, closure and tool versions.
- [ ] **STK-11** Build stock/candidate CMake/Python packages. Exercise native driver and embedded/importable Pyosys; run upstream Yosys tests.
- [ ] **STK-12** Run real LibreLane plugin tests and synthesis audit. Prove exactly one synthesis substitution and correct binary/binding selection.
- [ ] **STK-13** Provision/record first digital PDK revision, corners, Liberty, LEF, RC and cell functional models.
- [ ] **STK-14** Run reference A/B synthesis smoke.
- [ ] **STK-15** Run matched stock/candidate A/B synthesis smoke.
- [ ] **STK-16** Add process-tree resource measurement, cancellation tests and metrics schema validation.
- [ ] **STK-17** Add EQY gold-B/gate-B validation plus intentionally wrong-netlist rejection.
- [ ] **STK-18** Run full matched LibreLane A/B flows, final-netlist proof and required physical checks.
- [ ] **STK-19** Expand corpus to independent modules, shared specializations, DSP/SIMD/control/memory/interconnect and large single modules.
- [ ] **STK-20** Integrate native Yosys mapping-cache outputs with explicit read-only cache inputs and step-local publication.
- [ ] **STK-21** Implement complete edit histories and invalidation assertions including A→B→C→A and library/script/SDC changes.
- [ ] **STK-22** Add versioned physical-context adapter with old/new netlist identities, constraints and freshness checks.
- [ ] **STK-23** Validate a narrow pre-CTS combinational ECO path with rollback.
- [ ] **STK-24** Promote an independently reproduced digital release with held-out designs, second-library coverage and documented unsupported cases.

## Cross-domain bring-up gates

The digital lane is not the complete `asic-flow` release. Before calling mixed-signal support available, complete the applicable ANA/RF/MS tasks in `MIXED_SIGNAL_EXECUTION_PLAN.md`.

Required cross-domain milestones are:

1. **Analog tool closure** — Xschem, ngspice, Xyce, OpenVAF, CACE, Magic, KLayout, Netgen and GDSFactory are all reproducibly available.
2. **Analog reference qualification** — one block passes schematic simulation, DRC, LVS, extraction, post-layout simulation and spec regression.
3. **RF tool closure** — openEMS, Palace and scikit-rf are reproducibly available for the selected RF platform.
4. **RF reference qualification** — one passive structure passes solver/convergence/model-correlation and DRC requirements.
5. **Mixed-signal assembly** — exact analog/RF macro views are integrated into a digital top level and pass view consistency plus top-level physical checks.

## Immediate work queue

1. Resolve package closure/build reference shell (STK-09/10).
2. Build stock/candidate Yosys and run live LibreLane identity smoke (STK-11/12).
3. Provision SKY130A and run the clean digital baseline (STK-13–18).
4. In parallel, close the analog package set and run ANA-01 through ANA-10.
5. Provision IHP SG13G2 and close RF-01 through RF-08.
6. Integrate the first qualified macro under MS-01 through MS-07.
7. Only then use the combined flow as the acceptance environment for aggressive Yosys QoR and incremental/ECO work.

## Digital acceptance experiment matrix

R0: unmodified packaged reference where needed to isolate integration problems.
S0: pinned stock compiler, clean synthesis, full downstream flow.
S1: candidate compiler, reuse disabled, full downstream flow.
S2: candidate native incremental synthesis, full downstream flow (future).
S3: same synthesis plus independently validated physical reuse (future).

The current runner supports only clean smoke runs. S2/S3 are not aliases for S1. Compare stock with the same partition policy when hierarchy changes. For A→B, all equivalence references use B.

Required invalidation classes: no-op; local/shared edits; width/signedness; parameters/generate; interface; package/include/define; child constant/tie facts; Liberty/ABC/recipe/exclusion; SDC/load/clock; memory/macro models; rename/delete; cache corruption; interrupted publication; revision reversal.

## Evidence model

Digital reports add CPU/wall/process-tree memory, cache overhead and weighted reuse, area, scenario WNS/TNS/coverage, hold/electrical violations, physical checks and proof status.

Analog reports add model/corner identity, operating-point/spec metrics, simulator settings, DRC/LVS/extraction status, pre/post-layout correlation, and CACE results.

RF reports add geometry/material identity, port setup, solver/mesh configuration, convergence, S-parameters, compact-model correlation and DRC status.

Mixed-signal reports bind digital implementation revision to exact macro release identities and top-level checks.

## Stop/go rules

A failed identity audit blocks a benchmark. A missing PDK/model/tool lock blocks a comparison. A completed smoke with no required proof/physical/analog/RF verification remains unverified. A mapped digital quality win must survive downstream implementation before major QoR promotion. An analog/RF research experiment may conclude negatively; evidence completion is not a production win.
