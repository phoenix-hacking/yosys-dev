# Agent execution contract

Read `README.md`, `SOFTWARE_REQUIREMENTS.md`, `TOOLCHAIN_MATRIX.md` and `STACK_PROGRESS.md` first. This is an ASIC tool-development workspace supporting digital, analog/custom, RF/EM and mixed-signal integration. LibreLane is not OpenROAD-flow-scripts (ORFS).

## Ownership

- Native Yosys passes, artifact store, revisions, analyses and mapping belong in `components/yosys`, whose compiler-tree history is preserved in this repository, with component regression tests.
- Digital flow/Nix/LibreLane integration, adapters and end-to-end benchmarks belong at top level.
- Analog orchestration belongs under `flows/analog`, `integrations/analog`, analog benchmarks/platform code and shared verification infrastructure.
- RF/EM orchestration belongs under `flows/rf`, solver adapters, RF benchmarks/platform collateral and shared verification infrastructure.
- Mixed-signal view/assembly metadata belongs under `flows/mixed_signal`, schemas/platforms and top-level verification.
- OpenROAD/OpenSTA are dependencies. Do not rewrite placement/routing/STA here.
- Xschem/ngspice/Xyce/OpenVAF/CACE/KLayout/Magic/Netgen/GDSFactory/openEMS/Palace/scikit-rf are dependencies or adapters unless a concrete upstream gap requires a fork.
- Existing BAS/VAL/OLN/CAS/MAP/etc. IDs remain canonical in the compiler plan. STK/ANA/RF/MS IDs describe stack bring-up and do not count as compiler completion.

## Execution discipline

Work in isolated clones/build directories. Never reset another agent's checkout. Do not recursively clone this staging branch back into itself. Candidate Yosys source remains the pinned compiler revision until an explicit component pin update.

Keep patches narrow. An agent must not change the PDK, device model, golden RTL, analog specification, RF reference structure, test oracle or benchmark threshold merely to make its own change appear correct.

Run the applicable lane checks before proposing a commit. A skipped test, proof timeout, missing tool, unconverged simulation, failed DRC/LVS, missing PDK model or placeholder is **not** a pass.

Digital evidence hierarchy:

- Nix evaluation != compiler build
- compiler build != LibreLane smoke
- smoke != formal equivalence
- equivalence != routed PPA acceptance

Analog evidence hierarchy:

- schematic netlist != simulation qualification
- pre-layout simulation != DRC/LVS
- DRC/LVS != extracted post-layout simulation
- post-layout simulation != full specification/corner/mismatch qualification

RF evidence hierarchy:

- ideal passive model != EM extraction
- one EM run != convergence evidence
- S-parameter generation != compact-model/circuit correlation
- solver success != DRC-clean manufacturable geometry

Mixed-signal evidence hierarchy:

- matching macro name != matching macro revision
- behavioral simulation != physical-view consistency
- digital implementation with a black box != qualified analog/RF integration

Do not substitute stock Pyosys bindings while labeling a run candidate. Preserve same-process audit checks and declare unsupported command shapes explicitly. No native incremental feature exists in this bootstrap. Do not fake it by skipping an entire LibreLane invocation or merely finding an old run directory.

## Data and security

No tokens, credentials, proprietary RTL, restricted PDK/model files, binary caches, waveforms, field-solver databases or large physical databases in Git. Treat benchmark RTL, SPICE decks, PDK collateral and logs as untrusted inputs until identity and integrity checks pass.

## Handoff

Record: branch/commit, selected task IDs, lane, files changed, exact tool/PDK/model identities, test commands/results, skipped checks, proof/simulation assumptions, evidence paths, actual blockers and the next dependency-ready task. Do not credit lines of code or scaffolding as validated design-flow progress.
