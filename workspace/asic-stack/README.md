# Phoenix ASIC stack — LibreLane development workspace

This workspace integrates an independently maintained Yosys ASIC synthesis fork
with **LibreLane 3.0.14**, the OpenLane successor, and its packaged physical tools.
It is a development bootstrap, **not a validated RTL-to-GDS distribution yet**.

## Publication and repository boundary

The intended standalone repository is `phoenix-hacking/asic-stack`. Repository
creation was unavailable through the active GitHub connector, so this tree is
staged at `workspace/asic-stack/` in a dedicated `yosys-dev` branch. It can run
there or be exported independently. The Yosys compiler source layout is unchanged.

`yosys-dev` owns compiler implementation and compiler tests. This workspace owns
LibreLane integration, environment selection, benchmarks, physical feedback and
system-level evidence. The existing compiler plan remains authoritative:

- [Compiler execution plan](https://github.com/phoenix-hacking/yosys-dev/blob/main/ASIC_EXECUTION_PLAN.md)
- [Compiler progress](https://github.com/phoenix-hacking/yosys-dev/blob/main/ASIC_PROGRESS.md)
- [Research report](https://github.com/phoenix-hacking/yosys-dev/blob/main/docs/asic-roadmap/RESEARCH_REPORT.md)
- [Earlier OpenLane integration report](https://github.com/phoenix-hacking/yosys-dev/blob/main/docs/asic-roadmap/OPENLANE_INTEGRATION_REPORT.md)

Start with [STACK_PROGRESS.md](STACK_PROGRESS.md), [AGENTS.md](AGENTS.md), and
[the integration plan](STACK_EXECUTION_PLAN.md).

## What this change provides

- Immutable source selections for LibreLane, stock Yosys and the candidate fork.
- Nix reference/stock/candidate profiles with a CMake/Python-enabled compiler override.
- A registered `Phoenix.Classic` flow replacing only the synthesis step.
- A same-process native-binary/Pyosys audit before the original synthesis script.
- Real A/B RTL fixtures, explicit clean-flow runner, platform content inventory.
- Offline safety tests and an export utility that creates a pinned Yosys gitlink.
- A clear separation between implemented bootstrap code and unperformed EDA validation.

**Not implemented:** native incremental synthesis, general physical ECO, automatic
formal acceptance, automatic PPA promotion, or an agent scheduling service. A
successful smoke command records `FLOW_COMPLETED_UNVERIFIED`, never accepted PPA.

## Offline checks

Python 3.10+ and Git are sufficient:

```sh
python3 scripts/stack.py check
python3 -m unittest discover -s tests -v
```

Two real-LibreLane API tests are deliberately skipped when LibreLane is absent.
That is not a successful synthesis run. See `evidence/bootstrap-validation.json`.

## Resolve and build on a Linux EDA host

Initial support: x86_64 Linux, Nix >=2.27 with flakes enabled. The source commits
are pinned now. The root **transitive `flake.lock` is not fabricated**; generating,
reviewing and committing it is the next build-environment acceptance gate.
LibreLane's own pinned lock supplies its existing dependency selections.

```sh
python3 scripts/stack.py resolve
nix develop .#reference
python3 scripts/stack.py doctor --profile reference
python3 -m unittest discover -s tests -v
```

Run other profiles in separate shells:

```sh
nix develop .#stock
python3 scripts/stack.py doctor --profile stock

nix develop .#candidate
python3 scripts/stack.py doctor --profile candidate
```

The stock and candidate profiles use the same CMake recipe and no external binary
Yosys plugins in the initial Verilog envelope. The reference profile preserves
LibreLane's packaged reference dependencies, while the audited runner explicitly
selects its base compiler. These are different controls. A stock-control compiler
build is not assumed to be identical to LibreLane's original reference compiler.

The current fork uses CMake; the pinned nix-eda reference Yosys uses Make. Simply
changing `src` or shell `PATH` is insufficient. The override explicitly enables
Python and installs Pyosys. Its full build still needs to run on the EDA host.

For writable source, initialize the exported submodule or use `bootstrap` in the
staged workspace:

```sh
# Standalone repository:
git submodule update --init --recursive

# Staged workspace alternative:
python3 scripts/stack.py bootstrap
```

The normal Nix candidate is selected by the manifest/flake, not silently by a
dirty component checkout. To test an agent commit, update the source selection,
render the flake, resolve the changed input, and retain the exact revision.

## Platform and first smoke

SKY130A / `sky130_fd_sc_hd` is selected as the first **bring-up platform**, not a
flagship-node quality proxy. No PDK was downloaded or qualified in this session.
Use the pinned environment's Ciel to provision the chosen revision. Inspect
`ciel --help` for its installed command interface. Then inventory actual data:

```sh
python3 scripts/stack.py seal-platform \
  --pdk-root /absolute/path/to/pdks --revision <40-hex-selected-PDK-revision>
python3 scripts/stack.py run --profile candidate --revision A \
  --pdk-root /absolute/path/to/pdks
python3 scripts/stack.py run --profile candidate --revision B \
  --pdk-root /absolute/path/to/pdks
```

Repeat A/B in the stock shell. For full downstream implementation, explicitly add
`--stage full`; default runs stop at synthesis. Every run has an isolated directory
under `.runs/`, a console log, selected identities, and explicit unverified status.
The PDK content inventory is rechecked; hashing time occurs before measured flow
wall time and must be added when evaluating total validated turnaround.

Do not call the current A/B runs incremental: both compile cleanly. The fixture
is intentionally small and single-module; it cannot demonstrate module reuse.
Formal equivalence, richer fixtures, PPA extraction and native-reuse lanes are
tracked follow-on tasks. Any failed/missing audit fails the smoke command.

## Create the independent repository

Export to a NEW directory outside any existing Git repository:

```sh
python3 scripts/export_workspace.py /absolute/path/to/asic-stack
cd /absolute/path/to/asic-stack
git diff --cached --stat
git commit -m "Initialize LibreLane ASIC development workspace"
gh repo create phoenix-hacking/asic-stack --public --source=. --remote=origin --push
git submodule update --init --recursive
```

The export command does not create a remote or push. The final GitHub command
requires your authenticated repository-creation permission. Use `--private`
instead when appropriate for your deployment; do not upload restricted RTL/PDKs.
The export is checksummed and excludes all unlisted runtime data. It does not copy
Yosys history into the stack, and it refuses existing destinations.

## Updating and accepting changes

`toolchain.lock.json` selects source revisions; `flake.nix` is generated from it.
After an intentional source update:

```sh
python3 scripts/stack.py render-flake --write
python3 scripts/stack.py resolve
```

Review source/lock changes together, regenerate the export manifest from the
reviewed file list, and rerun tests. In the final standalone repository, advance
the Yosys gitlink to the same revision in the same PR. CI must not automatically
change pins or acceptance thresholds to make a failing compiler patch pass.

Keep heavy outputs, local `.state` records, credentials and PDK contents outside
Git. Commit concise evidence summaries with retrievable artifact digests.
