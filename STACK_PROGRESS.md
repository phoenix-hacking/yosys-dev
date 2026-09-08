# Stack progress

Updated 2026-09-07. This is integration/bootstrap progress, not compiler completion or tapeout qualification.

| Layer | Status |
|---|---|
| Top-level `asic-flow` architecture | PREPARED on branch: digital, analog, RF/EM and mixed-signal lanes documented |
| Independent GitHub repository / rename | NOT DONE; repository-admin rename/create action unavailable through current connector |
| Digital source revisions | Pinned: LibreLane 3.0.14, stock Yosys and candidate Yosys |
| Transitive Nix build lock | NOT RESOLVED in this environment |
| CMake/Pyosys package override | Implemented, NOT BUILT |
| LibreLane pass-through plugin | Implemented; pure helpers tested previously; real API tests pending |
| Analog/RF Nix discovery | Added for inherited xschem/ngspice/xyce/gdsfactory/OpenVAF-class packages; NOT BUILT |
| CACE packaging | REQUIRED, NOT YET CLOSED in project profile |
| openEMS packaging | REQUIRED RF CAPABILITY, NOT YET CLOSED |
| Palace packaging | REQUIRED RF CAPABILITY, NOT YET CLOSED |
| scikit-rf packaging | REQUIRED RF SUPPORT, NOT YET CLOSED |
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

## Next executable sequence

1. Resolve the Nix closure and build the existing digital reference/stock/candidate profiles.
2. Extend/close the analog profile until the audit shows Xschem, ngspice, Xyce, OpenVAF, CACE, Magic, KLayout, Netgen and GDSFactory are all present.
3. Provision SKY130A and run one digital RTL-to-GDS smoke plus one complete analog schematic-to-post-layout/CACE smoke.
4. Close RF packaging for openEMS, Palace and scikit-rf; provision IHP SG13G2; run the first passive EM fixture with convergence evidence.
5. Publish one qualified analog macro and one qualified RF/passive macro, then integrate them into a small LibreLane top-level design using exact release views.
6. Only after those stack gates are stable should broad Yosys optimization work use the mixed-signal flow as an acceptance environment.

## Session evidence discipline

Record branch/HEAD, lane, command, tool versions, PDK/model identities, inputs, outcomes, artifact references, accepted tasks, failed/skipped work and next blocker. Never replace NOT RUN with PASS because a package name, configuration file or directory exists. No unattended scheduler or periodic jobs are configured by these source files.
