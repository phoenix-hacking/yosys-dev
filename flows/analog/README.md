# Analog / Custom IC Flow

The analog lane targets transistor-level custom IC blocks such as ADCs, DACs, references, bias networks, LNAs, mixers, PLL analog cores, data-converter front ends, sensor interfaces and power-management circuits.

Baseline sequence:

```text
Xschem schematic
  -> SPICE/Verilog-A netlist
  -> ngspice and/or Xyce pre-layout simulation
  -> Magic/KLayout custom layout
  -> DRC
  -> LVS with Netgen or PDK-supported KLayout rules
  -> parasitic extraction
  -> ngspice/Xyce post-layout simulation
  -> CACE characterization/regression
  -> qualified macro views
```

Required tooling is tracked in `TOOLCHAIN_MATRIX.md`.

## Analog IP release bundle

A block promoted for mixed-signal integration should publish the applicable views under one immutable release identity:

```text
<ip>/
  schematic/
  spice/
  layout/
  extracted/
  models/
  cace/
  views/
    <block>.gds
    <block>.lef
    <block>.v
    <block>.lib        # only when meaningful
    <block>.cdl
    <block>.va         # optional behavioral model
    interface.yaml
```

The exact filenames may differ by PDK/project, but mixed-signal integration must never combine views from different macro revisions silently.

## Qualification

A passing schematic simulation is not qualification. Required evidence includes applicable corners, DRC, LVS, extracted post-layout simulation and specification checks. Monte Carlo/mismatch is required where the PDK models and block specification make it meaningful.
