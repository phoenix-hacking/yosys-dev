# Digital ASIC Flow

The digital lane targets very large standard-cell ASICs and heterogeneous SoCs.

Pipeline:

```text
RTL/SystemVerilog
  -> Yosys/Pyosys
  -> mapped standard-cell netlist + synthesis metadata
  -> LibreLane
  -> OpenSTA/OpenROAD
  -> KLayout/Magic/Netgen verification
  -> GDS/OASIS + timing/physical evidence
```

The modified compiler at `components/yosys` owns incremental compilation, synthesis artifacts, dependency/invalidation tracking, maintained analyses, hierarchy/specialization, memory/macro inference, technology mapping, timing/physical-aware synthesis decisions, proof obligations and synthesis QoR work.

LibreLane owns orchestration. OpenSTA owns timing semantics. OpenROAD owns floorplanning, placement, CTS, routing, parasitics and physical repair. The top-level stack owns reproducibility, PDK selection, benchmark comparison, evidence and mixed-signal macro assembly.

A major Yosys QoR change is not promoted until it survives a matched downstream implementation run.
