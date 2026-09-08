# RF / Electromagnetic Flow

The RF/EM lane covers structures whose behavior is not captured adequately by lumped schematic models alone: inductors, transformers/baluns, transmission lines, RF interconnect, package-sensitive structures and other distributed passives.

Baseline architecture:

```text
parameterized geometry / custom layout
  -> GDS/OASIS + layer/material mapping
  -> openEMS and/or Palace field solve
  -> S-parameters / impedance / field results
  -> scikit-rf network analysis and post-processing
  -> compact/passive model
  -> ngspice/Xyce circuit-level verification
  -> DRC/LVS/assembly with the analog and digital top level
```

IHP SG13G2 is the first intended RF reference platform because the open PDK publishes technology support for openEMS, Palace, GDSFactory, analog simulators and the digital toolchain.

## Required evidence

For an RF passive or macro, record:

- geometry and PDK/material revision
- solver/version and meshing settings
- ports and reference impedance
- frequency sweep
- convergence/mesh study where needed
- S-parameter output
- derived Q, loss, resonance or matching metrics as applicable
- compact model identity used in circuit simulation
- DRC-clean physical geometry

No RF block is considered qualified solely from schematic simulation using an ideal inductor/transformer model.
