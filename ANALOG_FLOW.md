# Analog / Mixed-Signal Flow

This document describes the custom-circuit side of `asic-flow`. RF/EM is a separate first-class lane; see `flows/rf/README.md`. Top-level composition is described in `flows/mixed_signal/README.md`.

## Scope

The analog lane covers transistor-level custom IC blocks such as amplifiers/OTAs, comparators, bias/reference circuits, ADC/DAC sub-blocks, PLL/VCO analog circuitry, sensor interfaces, power-management blocks, LNAs and mixers when their verification is predominantly circuit-level.

Distributed RF structures such as inductors, transformers/baluns and transmission lines additionally require the RF/EM lane.

## Baseline toolchain

```text
Xschem
  -> schematic + SPICE/Verilog-A netlist
ngspice / Xyce
  -> operating point, DC, AC, transient, noise and applicable nonlinear analyses
OpenVAF Reloaded / OSDI or PDK-supported Verilog-A model path
  -> compact device models
Magic / KLayout
  -> custom layout + DRC/extraction
Netgen and/or PDK-supported KLayout LVS
  -> layout-vs-schematic
post-layout ngspice / Xyce
  -> extracted verification
CACE
  -> specification/corner/regression automation
GDSFactory
  -> parameterized geometry and PCells where supported
```

Tool availability and release status are tracked in `TOOLCHAIN_MATRIX.md`.

## Standard analog implementation sequence

1. Define electrical specification and operating conditions.
2. Capture schematic and model dependencies.
3. Verify operating point and basic functionality.
4. Sweep relevant PVT and block-specific metrics.
5. Create custom layout with matching/symmetry/guarding techniques as applicable.
6. Run DRC.
7. Run LVS.
8. Extract parasitics.
9. Re-run post-layout simulation and compare with pre-layout behavior.
10. Run CACE characterization/spec regression.
11. Run mismatch/Monte-Carlo where models and specification require it.
12. Publish an immutable macro release bundle for mixed-signal integration.

## Block-specific evidence examples

ADC:
- sample rate and input bandwidth
- offset/gain
- DNL/INL as applicable
- SNDR/SINAD/ENOB/SFDR as applicable
- clock/aperture sensitivity
- reference/bias behavior
- PVT and mismatch
- extracted/post-layout results

LNA/mixer:
- gain
- noise figure/noise
- input/output matching where applicable
- linearity/compression/intermodulation metrics where applicable
- stability
- supply/current
- PVT and extracted behavior
- RF passives characterized through the RF/EM lane rather than ideal-only models

PLL/VCO-related blocks:
- tuning range
- startup/locking assumptions at block/system level
- phase-noise/jitter-relevant metrics where the simulator/model supports them
- supply sensitivity
- PVT and extracted behavior

## Macro release contract

An analog macro promoted into a large digital SoC must publish the applicable views under one immutable release identity:

- GDS/OASIS
- LEF abstract
- schematic/source SPICE/CDL
- extracted SPICE
- Verilog black box/behavioral model
- Liberty model where meaningful
- SDC/interface assumptions
- Verilog-A/real-number behavioral model where useful
- supply/voltage-domain metadata
- pin/load/jitter/noise characterization
- placement/routing/substrate keepouts or sensitive-region metadata

The mixed-signal top level must reject inconsistent view revisions.

## PDK targets

SKY130A is the first analog compatibility platform because of its existing open analog ecosystem. IHP SG13G2 is the first RF-capable mixed-signal reference because its open PDK publishes circuit, layout, Verilog-A, digital and EM tool collateral in one process kit.

## Qualification principle

Schematic simulation alone is never sufficient. An analog block is qualified only after the required physical verification, extraction, post-layout simulation and specification checks have passed for the declared process/model envelope.
