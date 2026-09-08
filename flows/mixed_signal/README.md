# Mixed-Signal SoC Integration

The mixed-signal lane composes independently qualified digital, analog and RF/EM blocks into one chip. It does not flatten transistor-level analog circuitry into Yosys.

## Hierarchical view contract

Each analog/RF macro may provide, as applicable:

- GDS/OASIS physical view
- LEF abstract for digital floorplanning/routing
- SPICE/CDL source and extracted netlists
- Verilog black-box/functional model
- Liberty timing/power interface model where meaningful
- SDC/interface constraints
- Verilog-A or real-number behavioral model
- pin, supply and voltage-domain metadata
- placement/routing keepouts
- substrate/noise sensitivity metadata
- load, jitter or bandwidth characterization relevant to the digital boundary

Every view is tied to one immutable macro release identity.

## Initial verification strategy

The baseline open flow is hierarchical:

1. analog/RF blocks pass their own schematic, layout, DRC/LVS, extraction and characterization gates;
2. digital logic uses behavioral/abstract macro views for system verification and physical implementation;
3. top-level assembly uses the exact qualified macro GDS/LEF/netlist revision;
4. top-level physical verification checks assembly consistency;
5. cross-domain constraints are recorded explicitly.

The baseline does not claim proprietary-style full-chip AMS co-simulation. Future research may integrate open co-simulation mechanisms when they can be validated.

## Cross-domain metadata roadmap

The project should eventually encode explicit interfaces for:

- clock/jitter budgets
- ADC aperture/clock uncertainty
- analog supply-noise budgets
- digital switching/noise-sensitive macro separation
- voltage domains and level-shifter/isolation requirements
- thermal/power-region constraints
- substrate-sensitive regions
- RF keepouts and sensitive routing classes
- digital pin loads and analog drive capability

This metadata belongs at the top-level flow boundary, not hidden in tool-specific scripts.
