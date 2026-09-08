# ASIC Flow

`asic-flow` is the top-level open-source ASIC development environment for this project. It supports two first-class implementation lanes:

1. **Digital ASIC** — LibreLane orchestration with the modified Yosys compiler under `components/yosys`, OpenSTA timing analysis, OpenROAD physical implementation, and open physical-verification tools.
2. **Analog / mixed-signal ASIC** — schematic capture, SPICE/Verilog-A simulation, custom layout, DRC/LVS, parasitic extraction, characterization, and post-layout simulation using open-source tools.

The repository is intentionally flow-first rather than Yosys-first:

```text
asic-flow/
├── README.md
├── SOFTWARE_REQUIREMENTS.md
├── STACK_EXECUTION_PLAN.md
├── STACK_PROGRESS.md
├── ANALOG_FLOW.md
├── toolchain.lock.json
├── flake.nix
├── nix/
├── integrations/
│   ├── librelane/          # digital flow integration
│   └── analog/             # analog/mixed-signal orchestration adapters
├── benchmarks/
│   ├── digital/
│   └── analog/
├── platforms/
├── schemas/
├── scripts/
├── tests/
├── evidence/
└── components/
    └── yosys/              # pinned Yosys fork
```

## Digital lane

```text
RTL / constraints / macros
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

The digital compiler work remains centered on Yosys: incremental compilation, artifact reuse, dependency/invalidation tracking, maintained analyses, ASIC mapping, timing/physical-aware synthesis decisions, proof obligations, and QoR improvement.

## Analog / mixed-signal lane

The initial open-source tool contract is:

```text
Xschem
  ↓ schematic/netlist
ngspice / Xyce
  ↓ pre-layout simulation
OpenVAF / OSDI where required for Verilog-A compact models
  ↓
Magic and/or KLayout
  ↓ custom layout
DRC / extraction
  ↓
Netgen LVS
  ↓
post-layout ngspice / Xyce simulation
  ↓
CACE characterization/regression
  ↓
qualified analog IP views + GDS
```

Optional later integrations include Qucs-S, GDSFactory, BAG/ALIGN-style generators, and RF/EM tools such as openEMS or Palace where a supported PDK provides the required models.

Analog blocks are **not** synthesized by Yosys or forced through LibreLane. At mixed-signal top level, analog IP is represented to the digital flow through the appropriate abstract views (LEF/GDS, timing/power models where applicable, Verilog/black-box views, SPICE/CDL, and integration constraints).

See [ANALOG_FLOW.md](ANALOG_FLOW.md) for the detailed analog architecture.

## Pinned digital starting point

- LibreLane: `3.0.14`, commit `f24e0ea5db2260719e9a0c7d51d07db74a87fa23`
- Candidate Yosys component: `phoenix-hacking/yosys-dev` at `43bbfbf71cba0435ebf806e9be8a888027c2903d`
- Stock Yosys control: upstream commit `435977e97008578a4532da60e70f75b5e88d076d`

The first analog qualification should use a PDK with maintained open analog collateral. SKY130 can provide an initial compatibility lane; IHP SG13G2 is also valuable because its open PDK explicitly documents analog/mixed/RF flows and tool configuration.

## Build and reproducibility

The stack keeps independent `reference`, `stock`, and `candidate` digital profiles. Analog tools and PDK models must likewise have immutable version/build identities in accepted evidence.

```sh
git clone <this repository>
cd <repository>
git submodule update --init --recursive
python3 scripts/stack.py check
```

## Project boundary

- **Yosys:** synthesis/compiler work.
- **LibreLane:** digital flow orchestration and state handoff.
- **OpenSTA:** timing semantics.
- **OpenROAD:** digital physical implementation and physical context.
- **Xschem/ngspice/Xyce/OpenVAF:** analog schematic/model/simulation path.
- **Magic/KLayout/Netgen:** custom-layout physical verification and interchange.
- **CACE:** analog characterization and regression.
- **Top level `asic-flow`:** version locking, PDK integration, mixed-signal assembly, benchmarking, evidence, and release qualification.

## Current status

This is still a bootstrap, not a qualified digital or analog tapeout environment. Offline stack checks passed, but Nix builds, live LibreLane/Pyosys execution, PDK qualification, formal equivalence, digital placement/routing, analog simulation/model qualification, analog DRC/LVS, and PPA/spec acceptance remain explicit gates.

The repository tree is now branded and architected as `asic-flow`. The connected GitHub interface does not expose repository-rename administration, so the remote slug may continue to display `yosys-dev` until it is renamed through GitHub repository settings or another administrative interface.
