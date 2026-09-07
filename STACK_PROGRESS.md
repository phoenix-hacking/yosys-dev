# Stack progress

Updated 2026-09-07. This is integration/bootstrap progress, not compiler completion.

| Layer | Status |
|---|---|
| Standalone workspace source | Prepared; staged in a dedicated Yosys branch |
| Independent GitHub repository | NOT CREATED; repository-administration capability unavailable |
| Source revisions | Pinned: LibreLane 3.0.14, stock and candidate Yosys |
| Transitive Nix build lock | NOT RESOLVED in this environment |
| CMake/Pyosys package override | Implemented, NOT BUILT |
| LibreLane pass-through plugin | Implemented; pure helpers tested; real API tests pending |
| Offline configuration / export / identity / PDK-inventory tests | See evidence/bootstrap-validation.json |
| Yosys compiler build and upstream tests | NOT RUN |
| PDK download / provisioning / qualification | NOT RUN |
| Actual LibreLane synthesis / route / formal / PPA | NOT RUN |
| Native incremental compiler / physical ECO | NOT IMPLEMENTED by this change |
| Original compiler task acceptance | Unchanged; no credit inferred from stack scaffolding |

**7 / 24 narrowly scoped STK bring-up tasks have offline implementation evidence.**
This is not a weighted project-completion percentage. STK-04 explicitly covers
helpers only; the real runtime/API gate remains STK-12.

Next executable task: STK-09, resolve the Nix closure on a suitable Linux host;
then STK-10–12, build the profiles and run the real plugin/identity smoke. Resolve
actual failures before expanding architecture. Repository creation can be done
independently with the supplied export path.

## Session evidence discipline

Record branch/HEAD, command, tool versions, inputs, outcomes, artifact references,
accepted tasks, failed/skipped work and next blocker. Never replace NOT RUN with
PASS because a configuration file exists. Keep publishing status separate from
runtime validation. No agents, scheduler, self-hosted runner or periodic jobs have
been provisioned by these source files.
