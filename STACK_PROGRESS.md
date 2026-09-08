# Stack progress

Updated 2026-09-08. This is integration/bootstrap progress, not compiler completion or tapeout qualification.

| Layer | Status |
|---|---|
| Top-level `asic-flow` architecture | PREPARED on branch: digital, analog, RF/EM and mixed-signal lanes documented |
| GitHub rename to `asic-flow` | BLOCKED; connector excludes administration. Exact owner command and post-rename steps in `docs/REPOSITORY_RENAME.md` |
| Digital source revisions | Pinned: LibreLane 3.0.14, stock Yosys and candidate Yosys |
| Transitive Nix build lock | NOT RESOLVED in this environment |
| CMake/Pyosys package override | Implemented, NOT BUILT |
| LibreLane pass-through plugin | Implemented; pure helpers tested previously; real API tests pending |
| Native/Python required-tool discovery | Corrected pinned attribute paths; package/program/import audit fails closed by lane; Nix evaluation/build NOT RUN |
| CACE packaging | REQUIRED, NOT YET CLOSED in project profile |
| openEMS packaging | REQUIRED RF CAPABILITY, NOT YET CLOSED |
| Palace packaging | REQUIRED RF CAPABILITY, NOT YET CLOSED |
| scikit-rf packaging | Pinned nixpkgs derivation 1.8.0 located and wired; build/import/qualification NOT RUN |
| Offline preparation checks | 63 tests: 61 PASS, 2 explicit live LibreLane skips; static/configuration and export checks PASS |
| Complementary verification / IP / profiling workflows | cocotb/MCY oracle + mutation adapter, FuseSoC/Edalize core, perf/heaptrack capture runner implemented; pinned Nix package paths wired; live workflow execution pending |
| HotSpot thermal workflow | Immutable source + Nix recipe; native GCC build and coupled-block heat-response smoke PASS; Nix build and calibrated process/package model pending |
| Compiler source bootstrap | Exact pinned compiler and all 10 nested submodule checkouts initialized; no compiler source changes |
| SKY130A PDK provisioning/qualification | NOT RUN |
| IHP SG13G2 PDK provisioning/qualification | NOT RUN |
| Digital Yosys compiler build/upstream tests | NOT RUN in this environment |
| Actual LibreLane synthesis / route / formal / PPA | NOT RUN |
| Analog schematic/SPICE smoke | NOT RUN |
| Analog DRC/LVS/extraction/post-layout/CACE | NOT RUN |
| RF/EM solver smoke/convergence/model correlation | NOT RUN |
| Mixed-signal macro integration | NOT RUN |
| Native incremental compiler / physical ECO | NOT IMPLEMENTED by this rearrangement |
| Original Yosys compiler task acceptance | Unchanged; no credit inferred from stack scaffolding |

The authoritative tool/capability checklist is `TOOLCHAIN_MATRIX.md`. Analog/RF/mixed-signal implementation tasks are in `MIXED_SIGNAL_EXECUTION_PLAN.md`. Digital stack bring-up remains in `STACK_EXECUTION_PLAN.md`.

## Current planning evidence

Completed repository-architecture work includes:

- four explicit flow domains under `flows/`;
- unified verification ownership;
- toolchain contract split into digital/analog/RF required sets;
- reference platform policy for SKY130A and IHP SG13G2;
- agent routing rules that prevent cross-domain evidence from being conflated;
- Nix package discovery/audit hooks for analog tooling already exposed by the inherited package set.

None of those items is runtime qualification.

## Preparation repair, 2026-09-08

Review of branch parent `ad39cce779264d26e9620baca776b3f92972b3db` reproduced
eight offline test errors. This preparation repairs source-lock schema drift,
restores runtime identity schema compatibility, refreshes the complete export
manifest, adds the missing analog integration directory and fixes empty-gitlink
bootstrap handling. The relative Yosys submodule URL follows a repository rename.

Required-tool audits now use a shared native/Python catalog, check selected
package versions/programs/imports and return nonzero for missing/unusable tools.
Resolved Nix locks are checked against all five declared source/inherited pins,
including follows links. Nix pure-evaluation tests are supplied but not run here.

See `evidence/preparation-validation-20260908.json` and `docs/BRINGUP.md`.
No additional STK build/flow or ANA/RF/MS qualification task is accepted by
these preparation repairs. The two live LibreLane tests remain skipped because
the pinned environment is absent. The earlier bootstrap evidence is historical.

## Next executable sequence

The complementary additions and exact invocations are in `docs/TOOL_EXTENSIONS.md`.
They close specific gaps in reusable testbenches, mutation detection, IP manifests,
compiler profiling and thermal response. They add seven tools across four opt-in
groups and do not duplicate OpenROAD capabilities. Source pins for Yosys,
LibreLane, nix-eda and nixpkgs are unchanged. Validation is recorded in
`evidence/extensions-validation-20260908.json`; no STK/ANA/RF/MS design milestone
is accepted from these additions.

1. Resolve the Nix closure and build the existing digital reference/stock/candidate profiles.
2. Extend/close the analog profile until the audit shows Xschem, ngspice, Xyce, OpenVAF, CACE, Magic, KLayout, Netgen and GDSFactory are all present.
3. Provision SKY130A and run one digital RTL-to-GDS smoke plus one complete analog schematic-to-post-layout/CACE smoke.
4. Close RF packaging for openEMS, Palace and scikit-rf; provision IHP SG13G2; run the first passive EM fixture with convergence evidence.
5. Publish one qualified analog macro and one qualified RF/passive macro, then integrate them into a small LibreLane top-level design using exact release views.
6. Only after those stack gates are stable should broad Yosys optimization work use the mixed-signal flow as an acceptance environment.

## Session evidence discipline

Record branch/HEAD, lane, command, tool versions, PDK/model identities, inputs, outcomes, artifact references, accepted tasks, failed/skipped work and next blocker. Never replace NOT RUN with PASS because a package name, configuration file or directory exists. No unattended scheduler or periodic jobs are configured by these source files.
