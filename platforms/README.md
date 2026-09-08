# Platform / PDK Policy

`asic-flow` supports multiple process platforms, but each lane is qualified independently against real PDK collateral.

## SKY130A

Primary purpose:
- first digital RTL-to-GDS bring-up;
- first open analog compatibility and macro-integration smoke;
- infrastructure validation, not advanced-node PPA claims.

Required digital collateral includes standard-cell Liberty/LEF/GDS, RC/corner data, tech LEF, IO/macro views and physical-verification decks.

Required analog collateral includes transistor/passive models, simulator initialization, schematic symbols/model bindings, layout tech, DRC/LVS, extraction and device generators where available.

## IHP SG13G2

Primary purpose:
- first analog/mixed/RF reference platform;
- BiCMOS/passive/RF device work;
- openEMS/Palace/GDSFactory integration;
- mixed-signal top-level assembly with a digital standard-cell subsystem.

The PDK revision used by a run must identify all tool-specific collateral consumed by Xschem, ngspice/Xyce, Verilog-A compilation, KLayout/Magic/Netgen, GDSFactory, LibreLane/OpenROAD and RF/EM solvers.

## GF180MCU

Future portability target for digital + analog mixed-signal flows. It is not part of the initial qualification gate.

## Evidence rule

A platform directory name or downloaded PDK tree is not a qualification. Accepted evidence records content revision/digest, model corners, technology files, extraction settings, standard-cell/macro revisions and every tool-specific configuration consumed by the run.
