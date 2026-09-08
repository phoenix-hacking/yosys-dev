# ASIC Flow

`asic-flow` is the top-level open-source ASIC development environment for this project. The long-term target is a unified flow for very large digital SoCs and custom analog/RF circuitry on the same chip.

It has four first-class domains:

1. **Digital ASIC** — LibreLane orchestration with the modified Yosys compiler under `components/yosys`, OpenSTA timing, OpenROAD physical implementation, and open physical-verification tools.
2. **Analog / custom IC** — Xschem, ngspice/Xyce, Verilog-A model support, custom layout, DRC/LVS, extraction and CACE characterization.
3. **RF / EM** — distributed passives and RF structures using openEMS and/or Palace, with GDSFactory and S-parameter/network analysis support.
4. **Mixed-signal integration** — immutable analog/RF macro views joined to large digital implementations through explicit physical, timing, voltage, load, jitter, noise and keepout metadata.

The repository is flow-first rather than Yosys-first:

```text
asic-flow/
├── README.md
├── SOFTWARE_REQUIREMENTS.md
├── TOOLCHAIN_MATRIX.md
├── STACK_EXECUTION_PLAN.md
├── STACK_PROGRESS.md
├── MIXED_SIGNAL_EXECUTION_PLAN.md
├── ANALOG_FLOW.md
├── toolchain.lock.json
├── flake.nix
├── nix/
├── components/
│   └── yosys/                  # pinned Yosys fork
├── flows/
│   ├── digital/
│   ├── analog/
│   ├── rf/
│   └── mixed_signal/
├── integrations/
│   ├── librelane/
│   └── analog/
├── verification/
├── benchmarks/
├── platforms/
├── schemas/
├── scripts/
├── tests/
└── evidence/
```

## Digital lane

```text
RTL / SystemVerilog / constraints / macros
        ↓
components/yosys
        ↓
mapped netlist + synthesis metadata
        ↓
LibreLane
        ↓
OpenSTA / OpenROAD
        ↓
KLayout / Magic / Netgen
        ↓
GDS + timing + physical-verification evidence
```

The digital compiler work remains centered on Yosys: incremental compilation, artifact reuse, dependency/invalidation tracking, maintained analyses, ASIC mapping, timing/physical-aware synthesis decisions, proof obligations, and QoR improvement for CPU/GPU/DSP/accelerator/NoC-class designs.

## Analog lane

```text
Xschem
  ↓
ngspice / Xyce
  ↓
OpenVAF/OSDI or PDK-specific Verilog-A model path
  ↓
Magic / KLayout custom layout
  ↓
DRC + Netgen/KLayout LVS + extraction
  ↓
post-layout simulation
  ↓
CACE characterization
  ↓
qualified analog macro views
```

This lane covers ADCs, DACs, PLL analog cores, bandgaps/references, LNAs, mixers, sensor interfaces, power-management blocks and other custom circuits. Analog blocks are not synthesized by Yosys.

## RF / EM lane

```text
parameterized/custom RF geometry
  ↓
GDSFactory / PDK layout
  ↓
openEMS and/or Palace
  ↓
S-parameters / impedance / field results
  ↓
scikit-rf and circuit-model extraction
  ↓
ngspice/Xyce verification
```

This lane is intended for structures such as inductors, transformers/baluns, transmission lines and package-/substrate-sensitive RF interconnect.

## Mixed-signal integration

A complex SoC can therefore combine multi-million-cell digital logic with custom analog/RF macros. The digital flow sees those macros through explicit abstract views such as LEF/GDS, Verilog black boxes/behavioral models, Liberty/SDC where meaningful, SPICE/CDL, voltage-domain metadata and physical keepouts.

The baseline verification model is hierarchical: qualify each analog/RF macro independently, then integrate the exact qualified revision into the digital/top-level assembly. Full proprietary-style continuous-time/event-driven AMS co-simulation is a future research lane, not a current claim.

See:

- [TOOLCHAIN_MATRIX.md](TOOLCHAIN_MATRIX.md) — complete capability/tool checklist and qualification state.
- [SOFTWARE_REQUIREMENTS.md](SOFTWARE_REQUIREMENTS.md) — stack ownership and release contract.
- [flows/digital/README.md](flows/digital/README.md)
- [flows/analog/README.md](flows/analog/README.md)
- [flows/rf/README.md](flows/rf/README.md)
- [flows/mixed_signal/README.md](flows/mixed_signal/README.md)
- [verification/README.md](verification/README.md)

## Reference platforms

- **SKY130A** — initial digital RTL-to-GDS and open analog compatibility bring-up.
- **IHP SG13G2** — first RF-capable mixed-signal reference target because its open PDK provides analog/mixed/RF, Verilog-A, GDSFactory, openEMS/Palace and LibreLane/OpenROAD collateral.
- **GF180MCU** — later portability target for open mixed-signal work.

## Pinned digital starting point

- LibreLane: `3.0.14`, commit `f24e0ea5db2260719e9a0c7d51d07db74a87fa23`
- Candidate Yosys component: `phoenix-hacking/yosys-dev` at `43bbfbf71cba0435ebf806e9be8a888027c2903d`
- Stock Yosys control: upstream commit `435977e97008578a4532da60e70f75b5e88d076d`

## Build and reproducibility

```sh
git clone --branch codex/librelane-stack-bootstrap-20260907 https://github.com/phoenix-hacking/yosys-dev.git asic-flow
cd asic-flow
python3 scripts/stack.py check
python3 scripts/stack.py bootstrap
python3 -m unittest discover -s tests -v
```

The stack keeps separate reference/stock/candidate digital profiles. Analog and RF tools require the same discipline: immutable tool identity, PDK/model identity, configuration digest and retained evidence.

Follow [docs/BRINGUP.md](docs/BRINGUP.md) for Nix resolution, tool audits, PDK
recording and the first qualification runs. `nix/tool-catalog.json` maps the
required tool names to actual package attributes, executables and Python modules.
`phoenix-analog-tool-audit --lane all` exits nonzero for missing or unusable tools;
an available package is still not a qualified design flow.

## Ownership boundary

- **Yosys:** synthesis/compiler work.
- **LibreLane:** digital flow orchestration and state handoff.
- **OpenSTA:** timing semantics.
- **OpenROAD:** digital physical implementation and physical context.
- **Xschem/ngspice/Xyce/OpenVAF:** analog schematic/model/simulation path.
- **Magic/KLayout/Netgen:** custom-layout physical verification and interchange.
- **CACE:** analog characterization/regression.
- **openEMS/Palace/scikit-rf:** RF/EM characterization path.
- **Top-level `asic-flow`:** toolchain locking, PDK integration, mixed-signal assembly, benchmarks, evidence and release qualification.

## Current status

This remains a bootstrap, not a qualified tapeout environment. Digital Nix/LibreLane/Pyosys builds, PDK qualification, synthesis/formal/place-route evidence, analog model/simulator qualification, analog DRC/LVS/extraction, RF/EM solver packaging and mixed-signal assembly tests remain explicit gates.

The prepared source is on draft PR #1, branch
`codex/librelane-stack-bootstrap-20260907`; `main` still contains the compiler
tree until that PR is merged. The GitHub remote is currently `yosys-dev`.
The connector excludes repository-administration access, so the owner must run
the rename in [docs/REPOSITORY_RENAME.md](docs/REPOSITORY_RENAME.md). Renaming
does not merge the PR. Existing immutable compiler source URLs are retained until
the remote rename is verified; GitHub redirects them after a rename.
