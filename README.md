# Phoenix ASIC Stack

This repository branch is organized as the **top-level ASIC implementation stack**. LibreLane is the flow/orchestration layer, and the modified Yosys compiler lives underneath it at `components/yosys` as a pinned component.

The architecture is intentionally stack-first:

```text
asic-stack/
├── README.md
├── SOFTWARE_REQUIREMENTS.md
├── STACK_EXECUTION_PLAN.md
├── STACK_PROGRESS.md
├── toolchain.lock.json
├── flake.nix
├── nix/
├── integrations/
│   └── librelane/
├── benchmarks/
├── platforms/
├── schemas/
├── scripts/
├── tests/
├── evidence/
└── components/
    └── yosys/      # pinned Yosys fork
```

## Component boundary

`components/yosys` is where synthesis-engine development happens: incremental compilation, artifact reuse, dependency/invalidation tracking, maintained analyses, ASIC mapping, timing/physical-aware synthesis decisions, proof obligations, and synthesis QoR work.

The top level owns the complete implementation environment: LibreLane orchestration, toolchain locking, PDK/platform selection, OpenSTA/OpenROAD integration, benchmark/edit-replay execution, end-to-end resource and PPA measurement, and release evidence.

LibreLane/OpenROAD are not substitutes for the Yosys work. They are the downstream implementation and validation environment.

## Pinned starting point

- LibreLane: `3.0.14`, commit `f24e0ea5db2260719e9a0c7d51d07db74a87fa23`
- Candidate Yosys component: `phoenix-hacking/yosys-dev` at `43bbfbf71cba0435ebf806e9be8a888027c2903d`
- Stock Yosys control: upstream commit `435977e97008578a4532da60e70f75b5e88d076d`

See [SOFTWARE_REQUIREMENTS.md](SOFTWARE_REQUIREMENTS.md) for the full stack contract and [STACK_EXECUTION_PLAN.md](STACK_EXECUTION_PLAN.md) for bring-up and acceptance gates.

## Initial checkout

```sh
git clone <this repository>
cd <repository>
git submodule update --init --recursive
python3 scripts/stack.py check
```

The candidate component is pinned. Do not advance `components/yosys`, the source lock, or synthesis acceptance thresholds independently.

## Build profiles

The stack keeps three different controls:

- `reference`: LibreLane's packaged reference environment.
- `stock`: pinned upstream Yosys built through the comparison packaging path.
- `candidate`: this project's Yosys fork.

On the supported Linux host, resolve the real Nix closure before claiming reproducibility:

```sh
python3 scripts/stack.py resolve
nix develop .#reference
python3 scripts/stack.py doctor --profile reference
```

Repeat separately for `stock` and `candidate`.

## Flow ownership

```text
RTL / constraints / macros
        ↓
components/yosys
        ↓
mapped netlist + synthesis metadata
        ↓
LibreLane
        ↓
OpenSTA / OpenROAD / physical verification tools
        ↓
measured implementation evidence
```

The target long-term feedback loop is:

```text
Yosys candidate generation
        ↓
OpenSTA/OpenROAD context
        ↓
Yosys candidate selection / local resynthesis
        ↓
LibreLane implementation and validation
```

## Current status

This is still a bootstrap, not a validated RTL-to-GDS release. Offline checks passed in the bootstrap work, but Nix builds, live Pyosys/LibreLane integration, PDK qualification, formal equivalence, placement/routing, and PPA acceptance remain explicit gates in `STACK_PROGRESS.md`.

Native incremental synthesis and general RTL-to-routed ECO are not yet implemented.

## GitHub repository naming

The tree is now stack-first. The active GitHub connector cannot create or rename repositories, so the remote may still display the historical `yosys-dev` repository name until an owner/admin renames it or publishes this branch as `phoenix-hacking/asic-stack`. The repository contents and component hierarchy no longer depend on the old root-level Yosys layout.
