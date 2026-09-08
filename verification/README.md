# Verification Architecture

Verification is domain-specific and evidence-driven.

## Digital

- Yosys regression tests
- EQY/SBY/Yosys SAT equivalence
- OpenSTA timing coverage
- LibreLane/OpenROAD implementation checks
- DRC/LVS/antenna as required by the PDK
- stock-vs-candidate matched QoR runs

## Analog

- schematic simulation
- PVT/corner sweeps
- noise/linearity/bandwidth/stability metrics as applicable
- mismatch/Monte Carlo where supported
- DRC
- LVS
- parasitic extraction
- post-layout simulation
- CACE specification regression

## RF/EM

- solver convergence/mesh checks
- frequency sweeps and S-parameters
- compact-model correlation
- DRC-clean geometry
- circuit-level verification of extracted/derived model

## Mixed-signal top level

- exact macro view/revision consistency
- supply and voltage-domain checks
- interface timing/load/jitter/noise constraints
- physical keepouts and macro placement legality
- top-level DRC/LVS/assembly consistency
- behavioral/system simulation for digital-visible macro behavior

A cache hit, successful tool invocation, or clean schematic simulation is never sufficient evidence by itself.
