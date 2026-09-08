# Analog and Mixed-Signal ASIC Flow

This document defines the analog/mixed-signal lane of `asic-flow`. It is deliberately parallel to, rather than embedded inside, the LibreLane/Yosys digital path.

## Objectives

The analog lane must support a reproducible open-source path from schematic through post-layout characterization for analog IP and provide stable abstract views for mixed-signal SoC integration.

The first production-quality target is not automated analog synthesis. It is a trustworthy, scriptable, reviewable analog implementation and verification environment with explicit tool/model/PDK identity.

## Initial toolchain

| Function | Primary tool | Secondary / optional |
|---|---|---|
| Schematic capture | Xschem | Qucs-S later |
| Pre-layout SPICE | ngspice | Xyce |
| Verilog-A compact models | OpenVAF / OSDI | simulator-native model support where applicable |
| Device sizing / gm-ID analysis | Python + pygmid where supported | project-specific notebooks/scripts |
| Custom layout | KLayout and/or Magic | GDSFactory for generated geometry |
| DRC | PDK-supported KLayout/Magic decks | both where available for cross-checking |
| LVS | Netgen | PDK-specific alternatives if required |
| Extraction | PDK-supported extraction path | field/EM extraction later where justified |
| Post-layout simulation | ngspice / Xyce | — |
| Specification regression | CACE | custom Python harnesses |
| RF / EM | openEMS / Palace where supported | later research lane |
| Generated analog layout | GDSFactory / BAG/ALIGN-style research | optional; never required for hand-layout support |

## Canonical analog flow

```text
schematic + model set
        ↓
netlist generation
        ↓
pre-layout simulation
        ↓
corner / temperature / parameter sweeps
        ↓
custom layout
        ↓
DRC
        ↓
LVS
        ↓
parasitic extraction
        ↓
post-layout simulation
        ↓
specification characterization
        ↓
qualified IP release
```

A qualified analog release must retain the exact schematic/netlist revision, layout revision, extracted view, PDK/model revision, simulator identity, verification decks, and characterization configuration.

## Recommended repository layout

```text
integrations/analog/
├── xschem/
├── spice/
├── cace/
├── extraction/
└── mixed_signal/

benchmarks/analog/
├── primitives/
├── opamps/
├── references/
├── data_converters/
└── mixed_signal_wrappers/

platforms/
├── sky130-analog.json
└── ihp-sg13g2.json
```

Do not commit foundry-restricted collateral. Platform manifests should point to provisioned PDK content by revision/digest.

## First qualification designs

The initial regression suite should contain small designs with unambiguous acceptance metrics rather than immediately attempting a complex RF or data-converter block.

1. MOS operating-point / model smoke test.
2. Current mirror.
3. Differential pair.
4. Common-source amplifier.
5. Two-stage op-amp or OTA.
6. Bandgap/reference example where the PDK provides appropriate devices/models.
7. Simple ring oscillator or comparator for mixed-signal timing interaction.
8. One analog macro integrated as a black-box physical macro into a tiny LibreLane digital top level.

Each design should have pre-layout and post-layout expected-metric envelopes, DRC/LVS requirements, and explicit corner/model coverage.

## Mixed-signal digital integration

The digital flow must never depend on transistor-level analog internals for normal place-and-route. Each qualified analog macro should publish the views needed by its consumers:

```text
analog source views:
  xschem schematic
  SPICE/CDL
  extracted SPICE

physical views:
  GDS/OASIS
  LEF abstract

system/digital views:
  Verilog black box or behavioral model
  Liberty timing/power model when meaningful
  SDC/interface constraints
  pin/power/voltage-domain metadata
```

A mixed-signal release manifest must assert that all of these views correspond to the same analog IP revision.

## Simulation policy

ngspice is the baseline simulator because of its broad open-PDK usage. Xyce should be maintained as a second lane where its device/model support is adequate, especially for larger sweeps or parallel simulation.

A simulator result is accepted only if the manifest records:

- simulator build/revision
- compact-model set and digest
- PDK corner
- temperature
- supply conditions
- analysis type and tolerances
- generated netlist digest
- convergence status
- measured outputs/specification evaluation

Simulation convergence is not equivalent to circuit correctness.

## DRC/LVS policy

A layout is not qualified until:

- required DRC decks report clean or explicitly waived results,
- LVS matches the intended schematic/netlist under the documented device mapping,
- extracted parasitics are generated from the same physical revision,
- post-layout simulations use that extracted view.

DRC and LVS reports are first-class evidence artifacts.

## Characterization policy

CACE should provide machine-readable specification tests where practical. Tests should cover operating corners, temperature, supply variation, and parameter sweeps supported by the PDK/model set.

For analog research, Monte Carlo/mismatch/yield testing may be added only when the PDK provides models suitable for that purpose. Do not fabricate statistical confidence from incomplete model support.

## IHP SG13G2 lane

IHP SG13G2 is a particularly useful analog/mixed/RF validation platform because its open PDK documents Xschem, ngspice, Xyce, KLayout, Magic, Netgen, Verilog-A/model tooling, parasitics, and digital LibreLane/OpenROAD collateral. This gives `asic-flow` a process where analog and digital views can be exercised under one openly documented PDK family.

## SKY130 lane

SKY130 remains useful for broad ecosystem compatibility and existing open-source analog examples/templates. Its role in this project is infrastructure and integration validation rather than a claim about advanced-node analog capability.

## Future research lanes

After the manual/scripted flow is stable, investigate:

- parameterized analog generators,
- BAG/ALIGN-style schematic/layout generation,
- optimization-driven sizing,
- surrogate-model assisted design-space exploration,
- incremental extraction and characterization caches,
- automated analog macro abstraction generation,
- mixed-signal behavioral model generation,
- RF/EM co-simulation,
- analog-aware floorplanning constraints for OpenROAD.

Any learned or optimization-driven method must be checked against actual SPICE/physical verification and must retain deterministic fallback/reference runs.

## Initial analog acceptance gates

- **ANA-01** Pin analog tool versions and add them to the resolved-toolchain manifest.
- **ANA-02** Provision and inventory one analog-capable PDK/model set.
- **ANA-03** Run an Xschem → ngspice schematic smoke test.
- **ANA-04** Run the same supported circuit in Xyce where models permit and compare key measurements.
- **ANA-05** Qualify OpenVAF/OSDI model compilation for a PDK that requires it.
- **ANA-06** Complete custom layout of a small analog block.
- **ANA-07** Obtain clean DRC and LVS.
- **ANA-08** Extract parasitics and pass post-layout simulation/spec checks.
- **ANA-09** Add CACE characterization with machine-readable pass/fail metrics.
- **ANA-10** Publish a digital integration view and place the analog macro in a tiny LibreLane top level.
- **ANA-11** Verify top-level GDS/LVS/view consistency for that mixed-signal fixture.
- **ANA-12** Repeat the qualification on a second analog-capable PDK before claiming generality.

No ANA task is accepted based solely on configuration presence; each requires retained execution evidence.
