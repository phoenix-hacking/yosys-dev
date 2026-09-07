# Stack execution plan

Version 0.1 — 2026-09-07. Goal: make the Yosys ASIC roadmap executable in LibreLane,
without merging upstream tool histories or claiming unperformed validation.

## Authority and dependency boundaries

The compiler's original 240 core/48 research tasks remain in `yosys-dev`.
STK tasks are integration gates, not additions to the compiler's completion
numerator. BAS/VAL/OLN are linked requirements; TIM/PHY/ECO span component and
integration acceptance. Existing reports remain linked rather than duplicated.

Source authority: `toolchain.lock.json`. Build closure: generated `flake.lock`.
Final superproject component selection: Yosys gitlink must equal the source lock.
Runtime authority: generated package identity plus same-process compiler audit.
Platform authority: selected revision and actual content inventory. None replaces
a required formal proof or physical validation result.

## Bring-up backlog

Each unchecked task requires evidence, not just code presence.

- [x] **STK-01** Preserve compiler layout and stage an independently exportable workspace. Evidence: additive-only publication diff and export tests.
- [x] **STK-02** Pin current LibreLane release and stock/candidate source revisions. Evidence: source API audit and immutable manifest.
- [x] **STK-03** Implement fail-closed configuration/profile checks. Evidence: offline negative tests.
- [x] **STK-04** Implement same-process audit helpers; reject foreign native binaries and bindings. Evidence: offline helper tests only; live gate is STK-12.
- [x] **STK-05** Supply a real A/B RTL change with B declared as proof reference. Evidence: fixture checks; no synthesis credited.
- [x] **STK-06** Implement safe PDK content inventory including symlink-cycle rejection. Evidence: offline inventory tests; qualification remains pending.
- [x] **STK-07** Implement independent export, pinned gitlink and no-overwrite checks. Evidence: local Git-index tests.
- [ ] **STK-08** Publish independent `asic-stack` remote. Blocker: connector lacks repository creation. Run supplied export/admin publication path.
- [ ] **STK-09** Resolve/review/commit transitive Nix lock; verify inherited nix-eda/nixpkgs selections. Do not use a fabricated narHash.
- [ ] **STK-10** Evaluate and build reference profile on supported Linux host. Capture store paths, closure and tool versions.
- [ ] **STK-11** Build stock and candidate CMake/Python packages. Exercise native driver and importable/embedded Pyosys; run upstream Yosys tests.
- [ ] **STK-12** Run real LibreLane plugin tests and synthesis audit. Prove exactly one synthesis substitution and correct binary/binding selection.
- [ ] **STK-13** Provision/record first PDK revision, corners, Liberty, LEF, RC and cell functional models. A directory name is not a pin.
- [ ] **STK-14** Run reference A/B synthesis smoke. Retain resolved configs, original script digests, outputs and failures.
- [ ] **STK-15** Run matched stock/candidate A/B synthesis smoke. Same downstream flow, library and constraints; explain reference/control differences.
- [ ] **STK-16** Add process-tree resource measurement, cancellation tests and metrics schema validation. Null metrics remain explicit until measured.
- [ ] **STK-17** Add EQY gold-B/gate-B validation plus intentionally wrong-netlist rejection. Timeout/infrastructure errors cannot satisfy proof.
- [ ] **STK-18** Run full matched LibreLane A/B flows, final-netlist proof and required physical checks. Collect scenario coverage and negative outliers.
- [ ] **STK-19** Expand corpus to independent modules, shared specializations, DSP/SIMD/control/memory/interconnect and large single modules.
- [ ] **STK-20** Integrate native Yosys mapping-cache outputs with explicit read-only cache inputs and step-local output publication. Depends on compiler CAS/MAP.
- [ ] **STK-21** Implement complete edit histories and invalidation assertions, including A→B→C→A and library/script/SDC changes.
- [ ] **STK-22** Add versioned physical-context adapter with old/new netlist identities, constraints and freshness checks. No stale RC reuse.
- [ ] **STK-23** Validate a narrow pre-CTS combinational ECO path with rollback; clock/reset/macro/interface changes initially force broader rebuild.
- [ ] **STK-24** Promote an independently reproduced release with held-out designs, second-library coverage and documented unsupported cases.

## Immediate work queue

1. Resolve the package closure and build the reference shell (STK-09/10).
2. Build stock/candidate with the CMake override and debug any real API mismatch
   before expanding the plugin (STK-11/12).
3. Record PDK/model inputs; run the actual clean baselines (STK-13–15).
4. Add independent equivalence/oracle checks and resource accounting (STK-16/17).
5. Only then promote native mapping reuse through the same measured flow.

The bootstrap is intentionally pass-through. It does not wait for the entire
incremental architecture before testing that LibreLane executes the right fork.

## Acceptance experiment matrix

R0: unmodified packaged reference where needed to isolate integration problems.
S0: pinned stock compiler, clean synthesis, full downstream flow.
S1: candidate compiler, reuse disabled, full downstream flow.
S2: candidate native incremental synthesis, full downstream flow (future).
S3: same synthesis plus independently validated physical reuse (future).

The current runner supports only clean smoke runs. S2/S3 are not aliases for S1.
Compare stock with the same partition policy when hierarchy changes. For A→B,
all equivalence references use B. Record the cost of populating A separately.

Required invalidation classes: no-op; local/shared edits; width/signedness;
parameters/generate; interface; package/include/define; child constant/tie facts;
Liberty/ABC/recipe/exclusion; SDC/load/clock; memory/macro models; rename/delete;
cache corruption; interrupted publication; revision reversal.

Every run records configuration, RTL, source/build identity, actual status and
missing metrics. Required accepted reports add CPU/wall/process-tree memory,
cache overhead and weighted reuse, area, scenario WNS/TNS/coverage, hold/electrical
violations, physical checks and proof status. Never report a percentage of WNS as
general speedup. Keep fixed-floorplan and fixed-utilization experiments separate.

## Extension interfaces

Synthesis manifests describe semantic/recipe/library dependencies and object
correspondence. Physical manifests additionally require exact database revision,
scenario, extraction assumptions and per-object freshness. These future interfaces
are not implemented by the current runtime-identity report.

LibreLane Steps must not mutate inputs or undeclared global caches. The outer
runner selects immutable cache snapshots, Steps write new artifacts in their own
output directories, and validated results are published afterward. Same-process
OpenROAD services may be explored later, but must still export reproducible state.

## Stop/go rules

A failed identity audit blocks a benchmark. A missing PDK lock blocks a comparison.
A completed smoke with no formal proof remains unverified. A mapped quality win
must survive downstream implementation before major QoR promotion. A research
experiment may conclude negatively; evidence completion is not a production win.
