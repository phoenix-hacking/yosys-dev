# ASIC Flow Toolchain Matrix

This matrix is the authoritative capability checklist for `asic-flow`. A tool being listed here means the flow intends to support it; it does **not** mean the tool or its PDK integration has already been built or qualified.

Status vocabulary:

- **required** — part of the supported flow envelope and must be present in a release profile.
- **reference** — preferred implementation for the capability.
- **optional** — useful alternate or research tool; absence does not block the baseline flow.
- **pending package** — source/tool selected, but the reproducible build integration has not passed.
- **pending PDK** — binary may exist, but the required process collateral has not been qualified.
- **qualified** — tool identity, invocation, PDK collateral and representative acceptance tests have passed.

## Digital ASIC lane

| Capability | Tool | Policy | Current integration state | Release acceptance |
|---|---|---|---|---|
| RTL/SystemVerilog elaboration | Yosys + Slang/sv-elab/Pyosys | required/reference | candidate fork pinned; build pending | selected RTL corpus elaborates; wrong binary/binding rejected |
| Logic synthesis | Yosys | required/reference | fork pinned | stock/candidate clean runs + formal equivalence |
| Boolean technology mapping | ABC / Yosys mapping | required | inherited with Yosys | mapped-netlist equivalence + reproducible QoR |
| Formal equivalence | EQY / SBY / Yosys SAT | required | inherited in digital environment | intentionally incorrect netlist must fail oracle |
| RTL simulation/lint support | Verilator, Icarus Verilog | required support tools | inherited in LibreLane environment | smoke simulation/lint fixtures pass |
| Static timing | OpenSTA | required/reference | inherited in LibreLane | clean timing coverage and scenario identity recorded |
| Floorplan/place/CTS/route | OpenROAD | required/reference | inherited in LibreLane | full digital RTL-to-GDS flow passes |
| Physical verification | KLayout, Magic, Netgen | required | inherited in LibreLane | DRC/LVS requirements for selected PDK pass |
| PDK management | Ciel | required | inherited | immutable platform content inventory recorded |
| Flow orchestration | LibreLane | required/reference | release 3.0.14 selected | complete stateful flow executes using intended Yosys/Pyosys |

## Analog / custom IC lane

| Capability | Tool | Policy | Current integration state | Release acceptance |
|---|---|---|---|---|
| Schematic capture | Xschem | required/reference | package/PDK qualification pending | schematic-to-netlist smoke for reference PDK |
| Alternate schematic/simulation UI | Qucs-S | optional | not yet packaged in project profile | only promoted if PDK integration is reproducible |
| Baseline circuit simulation | ngspice | required/reference | available in nix-eda ecosystem; project qualification pending | DC/AC/transient/noise reference fixtures reproduce |
| Large/parallel circuit simulation | Xyce | required on Linux | available in nix-eda ecosystem; project qualification pending | same selected device/model fixtures compare within defined tolerances |
| Verilog-A compact-model compilation | OpenVAF Reloaded / OSDI | required when PDK needs it | nix-eda provides OpenVAF Reloaded; project qualification pending | PDK Verilog-A model compiles and simulator loads it |
| Alternate model path | ADMS/Xyce plugin flow | conditional | PDK/tool dependent | required only where selected PDK documents it |
| Analog characterization/regression | CACE | required/reference | source selected; project packaging pending | corners/spec limits + Monte Carlo/mismatch where models permit |
| Custom layout | KLayout and Magic | required | already digital dependencies; analog tech qualification pending | layout edit/import/export + PDK DRC smoke |
| LVS | Netgen and/or PDK-supported KLayout LVS | required | binary present digitally; analog rules pending | schematic/layout netlists agree on fixtures |
| Parasitic extraction | PDK-supported Magic/KLayout/extraction scripts | required | PDK dependent | extracted RC netlist produced and post-layout simulation succeeds |
| Programmatic layout/PCells | GDSFactory | required support capability | nix-eda provides GDSFactory; project qualification pending | parameterized passive/device layout smoke |
| gm/ID/device characterization | pygmid or equivalent Python analysis | optional/reference research | not yet packaged | validated against selected PDK model sweeps |
| Alternate analog simulator | Gnucap | optional | not yet packaged | used only where model compatibility is demonstrated |

## RF / electromagnetic lane

| Capability | Tool | Policy | Current integration state | Release acceptance |
|---|---|---|---|---|
| Planar/full-wave EM | openEMS | required RF capability | packaging + PDK integration pending | passive fixture produces reproducible S-parameters |
| 3D FEM electromagnetics | Palace | required RF capability | packaging + PDK integration pending | reference inductor/transformer/balun fixture converges and exports S-parameters |
| S-parameter/network analysis | scikit-rf | required support capability | packaging pending | Touchstone ingest, de-embedding/network checks pass |
| Parametric RF geometry | GDSFactory | required support capability | package pending | geometry is deterministic and DRC-clean under reference PDK |
| Meshing/visualization helpers | Gmsh/ParaView or solver-supported equivalents | optional | pending | promoted only when required by accepted solver path |

IHP SG13G2 is the first RF-oriented reference PDK because its open collateral explicitly includes `openems/`, `palace/`, `gdsfactory/`, Verilog-A, analog simulation and LibreLane/OpenROAD support. SKY130 remains a simpler digital/analog compatibility platform.

## Mixed-signal integration lane

Mixed-signal integration does not imply that Yosys or LibreLane simulates transistor-level analog circuitry. `asic-flow` joins independently qualified views.

Required view types, where meaningful for a block:

- schematic/source SPICE/CDL
- extracted SPICE
- GDS/OASIS
- LEF abstract
- Verilog black-box or behavioral model
- Liberty timing/power model for digital-facing interfaces
- SDC/interface constraints
- Verilog-A or real-number behavioral model
- supplies, voltage domains, substrate/keepout information
- pin/load/jitter/noise/interface characterization metadata

Initial mixed-signal verification is **hierarchical**: analog/RF blocks are characterized independently, behavioral/interface views are used in system-level digital verification, and top-level physical assembly uses the exact qualified macro revision. Full proprietary-style continuous-time/event-driven AMS co-simulation is not claimed by the baseline open flow.

Future co-simulation research may evaluate XSPICE, Xyce/digital coupling, `spicebind`, cocotb-driven orchestration, or other open mechanisms, but those must earn their own correctness and convergence gates.

## Platforms

| Platform | Intended use | Required lanes | Status |
|---|---|---|---|
| SKY130A | first digital RTL-to-GDS and open analog compatibility | digital + analog | provisioning/qualification pending |
| IHP SG13G2 | analog/mixed/RF reference, BiCMOS/passives, plus digital integration | digital + analog + RF/EM | provisioning/qualification pending |
| GF180MCU | secondary open mixed-signal portability target | digital + analog | future |

## Capabilities deliberately not overclaimed

The open stack does not yet claim commercial signoff parity for advanced-node extraction, EM/IR, reliability, production DFT/ATPG, UPF-class low-power implementation, foundry-certified RF signoff, or proprietary AMS co-simulation. Where open tooling exists, it may be integrated as an experimental lane, but release claims require PDK-specific evidence.
