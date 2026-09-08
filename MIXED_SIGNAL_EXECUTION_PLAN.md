# Analog / RF / Mixed-Signal Execution Plan

This plan extends the digital stack bring-up without changing the Yosys compiler completion numerator. Tasks require evidence, not file presence.

## A. Analog lane — ANA

- [ ] **ANA-01** Resolve/package Xschem, ngspice, Xyce, OpenVAF Reloaded, CACE, Magic, KLayout, Netgen and GDSFactory in a reproducible Linux profile. Record source/build identities.
- [ ] **ANA-02** Add analog tool doctor: executable paths, versions, Python module paths, simulator plugin/model paths and GUI/headless capability.
- [ ] **ANA-03** Provision a SKY130 analog reference workspace with verified simulator models, Xschem bindings, layout tech, DRC, LVS and extraction data.
- [ ] **ANA-04** Provision IHP SG13G2 analog collateral and compile required Verilog-A models for ngspice/OSDI and Xyce-supported model path.
- [ ] **ANA-05** Add a minimal resistor/current-source/op-amp smoke design proving Xschem -> ngspice netlist/simulation.
- [ ] **ANA-06** Run the same compatible reference circuit in Xyce and define acceptable cross-simulator tolerances where appropriate.
- [ ] **ANA-07** Add custom-layout smoke through Magic/KLayout and stream GDS/OASIS deterministically.
- [ ] **ANA-08** Run DRC and LVS on the reference analog cell; deliberately broken geometry/netlist must fail the oracle.
- [ ] **ANA-09** Produce extracted parasitics and run post-layout simulation; retain pre/post comparison.
- [ ] **ANA-10** Add CACE datasheet/spec regression with PVT sweeps and failure injection.
- [ ] **ANA-11** Add mismatch/Monte-Carlo regression where PDK models support it; classify unsupported model capabilities explicitly.
- [ ] **ANA-12** Define/publish an immutable analog macro release bundle with GDS/LEF/SPICE/CDL/Verilog/Liberty/behavioral views as applicable.
- [ ] **ANA-13** Add analog benchmark blocks: amplifier, comparator, reference/bias, ADC sub-block, DAC sub-block and PLL/VCO-relevant fixture.
- [ ] **ANA-14** Qualify one complete analog macro from schematic through extracted/spec acceptance on SKY130 or IHP.

## B. RF / EM lane — RF

- [ ] **RF-01** Package/audit openEMS, Palace, scikit-rf and any required mesh/helper tools in a reproducible RF profile.
- [ ] **RF-02** Provision IHP SG13G2 openEMS/Palace/GDSFactory technology collateral and record exact PDK revision.
- [ ] **RF-03** Add deterministic GDSFactory geometry smoke for an RF passive.
- [ ] **RF-04** Add Touchstone/S-parameter schema and scikit-rf post-processing regression.
- [ ] **RF-05** Run openEMS reference transmission-line/passive case and retain solver/mesh/frequency configuration.
- [ ] **RF-06** Run Palace reference passive/port case and retain solver/mesh/frequency configuration.
- [ ] **RF-07** Establish mesh/convergence checks; one solver run is not qualification.
- [ ] **RF-08** Extract a passive compact/network model from EM output and verify it in ngspice/Xyce.
- [ ] **RF-09** Add inductor benchmark with L/Q/SRF metrics and DRC-clean geometry.
- [ ] **RF-10** Add transformer/balun benchmark with coupling/loss/matching metrics and DRC-clean geometry.
- [ ] **RF-11** Add RF interconnect/transmission-line benchmark and circuit-model correlation.
- [ ] **RF-12** Define/publish immutable RF macro release bundle including physical geometry, S-parameters, model, ports and characterization metadata.

## C. Mixed-signal integration — MS

- [ ] **MS-01** Define `macro-release.schema.json` binding every analog/RF abstract view to one content/revision identity.
- [ ] **MS-02** Define `mixed-signal-interface.schema.json` for supplies, voltage domains, clocks, loads, jitter/noise budgets, keepouts and sensitive regions.
- [ ] **MS-03** Add top-level macro view consistency checker; intentionally mismatched GDS/LEF/Verilog/SPICE revisions must fail.
- [ ] **MS-04** Integrate a qualified analog macro as a LEF/GDS black box in a small LibreLane digital design.
- [ ] **MS-05** Run top-level digital implementation around the macro while honoring placement/routing keepouts and pins.
- [ ] **MS-06** Run top-level physical assembly DRC/LVS or PDK-supported consistency checks using the exact macro release.
- [ ] **MS-07** Add behavioral analog macro model to digital/system simulation and verify interface-level functionality.
- [ ] **MS-08** Add voltage-domain/level-shifter/isolation metadata checks for mixed-voltage designs where the selected platform supports them.
- [ ] **MS-09** Add clock/jitter/load interface metadata and propagate documented assumptions into digital timing constraints.
- [ ] **MS-10** Add cross-domain evidence bundle tying digital implementation revision, macro releases, PDK revision and verification results together.
- [ ] **MS-11** Build a demonstration mixed-signal SoC: synthesized digital subsystem + analog macro + RF/passive macro on one top-level layout.
- [ ] **MS-12** Evaluate open AMS co-simulation candidates (XSPICE/Xyce coupling/spicebind/cocotb orchestration) without promoting one until correctness and convergence are demonstrated.

## D. Benchmark families

The long-term corpus should contain both isolated blocks and integrated systems:

Digital:
- CPU/control, SIMD/GPU, DSP/MAC/FFT, accelerator, NoC/crossbar/FIFO, memory interfaces, large generated hierarchies.

Analog:
- amplifier/OTA, comparator, references/bias, ADC/DAC sub-blocks, oscillator/PLL elements, sensor/power interfaces.

RF:
- inductor, transformer/balun, transmission line, matching/interconnect structures.

Mixed:
- digital accelerator with ADC/DAC-facing interface;
- digital subsystem clocked by an abstracted PLL macro;
- high-speed/RF-facing digital control surrounding qualified analog/RF macros.

## E. Acceptance rule

A lane is not called supported until its required tooling is packaged, the selected PDK provides the needed collateral, deliberately broken fixtures fail, and at least one representative end-to-end design passes the lane's complete verification chain.
