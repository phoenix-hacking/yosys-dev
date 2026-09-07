# Yosys + OpenLane integration report

Publication date: 2026-09-07.

**Provenance:** Repository edition of the OpenLane integration report supplied by the project owner in the planning conversation. Markdown code fences and mathematical formatting have been normalized. This is a research/design document, not a claim that the described features have been implemented. The implementation authority is [ASIC_EXECUTION_PLAN.md](../../ASIC_EXECUTION_PLAN.md); current evidence and status belong in [ASIC_PROGRESS.md](../../ASIC_PROGRESS.md). The accompanying synthesis research is in [RESEARCH_REPORT.md](RESEARCH_REPORT.md).

**Important execution clarification:** OpenLane and OpenROAD-flow-scripts (ORFS) are different orchestrators. ORFS variables mentioned below are integration precedents, not configuration options that can be assumed to work in OpenLane. Likewise, OpenLane step restart, reusable Yosys synthesis artifacts, OpenROAD incremental routing, and a complete RTL-to-physical ECO workflow are distinct capabilities. The execution plan requires proving each separately. No arbitrary RTL-to-routed-ECO capability is assumed to exist.

## Architectural direction

Using Yosys inside OpenLane changes the integration priorities in a useful way, but it does not change the central goal: improve Yosys itself.

The main change is to design the Yosys enhancements to exploit OpenLane/OpenROAD as the downstream physical feedback and validation environment. OpenLane uses Yosys for synthesis and OpenROAD/OpenSTA for implementation and timing, giving the project a natural laboratory for testing whether a Yosys optimization survives placement and routing.

Some of the proposed architecture has partial analogues in the OpenROAD flow ecosystem. ORFS includes hierarchical synthesis controls, reusable Yosys checkpoints, partition blackboxing, and arithmetic implementation alternatives. The fork should integrate with the relevant concepts instead of creating incompatible representations, without confusing the ORFS and OpenLane configuration interfaces.

```text
RTL
 ↓
Modified Yosys
 ├─ incremental elaboration
 ├─ stage-level artifact reuse
 ├─ analysis manager / precise invalidation
 ├─ arithmetic + mux candidate synthesis
 ├─ technology mapping
 └─ stable object/correspondence metadata
 ↓
mapped Verilog + metadata
 ↓
OpenLane / OpenROAD
 ├─ OpenSTA timing
 ├─ floorplan / placement
 ├─ parasitic estimation
 ├─ congestion
 ├─ buffering / sizing
 └─ route
 ↓
physical feedback
 ↓
optional Yosys resynthesis of selected regions
```

The final feedback arrow is a major development objective, not merely another file handoff.

## 1. Incremental Yosys becomes even more valuable

OpenLane is a multi-stage flow. If Yosys cheaply regenerates only changed portions of a design and exposes reliable correspondence, downstream implementation state becomes a candidate for reuse. It is not automatically safe to preserve physical state just because synthesis artifacts were reused.

Define two incremental modes.

### `incremental_exact`

```text
RTL A
 → synthesize
 → artifacts

small edit

RTL B
 → detect changed synthesis units
 → rebuild changed units
 → reproduce the clean compilation contract for the same recipe
```

This is the first target. Exact reuse means matching all consumed compilation inputs. Byte-identical results require deterministic serialization and a deterministic recipe; functional equivalence alone is a weaker guarantee and must not be mislabeled.

### `incremental_eco`

```text
RTL A
 → Yosys
 → OpenLane implementation

small RTL edit → B

Yosys:
  reuse unaffected synthesized regions
  rebuild changed regions

OpenROAD adapter:
  identify physical state whose assumptions remain valid
  preserve that state
  repair affected implementation regions
  revalidate timing and physical correctness
```

The second mode may intentionally differ structurally from a clean optimization run while remaining correct for B. It requires its own implementation, proof, constraint, timing, and physical-quality gates.

The system-level metric becomes:

$$T_{\mathrm{RTL\ edit\rightarrow updated\ physical\ implementation}}.$$

Report synthesis turnaround separately so physical-flow changes cannot conceal whether Yosys itself improved.

## 2. Keep the artifact boundary compatible with OpenLane

Yosys can use internal stage artifacts for speed, but its external boundary should remain conventional:

```text
mapped Verilog
constraint input references and explicit correspondence
memory/macro information
hierarchy/correspondence metadata
optional incremental-change manifest
```

Do not require a proprietary or opaque Yosys checkpoint reader in every downstream consumer. Preserve ordinary netlist interoperability.

ORFS's `SYNTH_CHECKPOINT` is an RTLIL synthesis checkpoint precedent. The equivalent OpenLane integration must be implemented through the selected OpenLane generation's actual step/configuration interface.

```text
OpenLane
   ↓
Yosys project cache
   ↓
load valid coarse-synthesis artifact
   ↓
rebuild invalidated partitions
   ↓
mapping
```

The cache is a native Yosys service. OpenLane supplies explicit inputs and records returned artifacts; it does not become a second implementation of Yosys's semantic dependency analysis.

## 3. Add a useful incremental netlist manifest

A machine-readable change manifest is a required bridge between synthesis reuse and possible physical reuse.

The original conceptual example was:

```json
{
  "old_design": "sha256:...",
  "new_design": "sha256:...",
  "changed_modules": ["gpu_execute_3", "lsu_ctrl"],
  "removed_instances": ["top/u_gpu/u_lane3/u_old_mux"],
  "added_instances": ["top/u_gpu/u_lane3/u_new_mux"],
  "changed_nets": ["top/u_gpu/u_lane3/result_bus"],
  "unchanged_partitions": ["top/u_cpu", "top/u_noc", "top/u_dsp0"]
}
```

This is an illustrative shape, not an implemented schema. A production schema must additionally carry versioning, library and constraint identities, stable IDs with generation information, pin correspondence, exact changes to connectivity and cell semantics, source revision, and explicit reuse eligibility/failure reasons.

A surviving hierarchical name is not proof that the object is unchanged. An unchanged logic partition is not proof that its placement, clock, routing, or parasitics remain valid.

The long-term combination is:

```text
Yosys semantic incremental compiler
        +
OpenROAD physical incremental implementation
```

## 4. Physical feedback should use OpenROAD, not a new Yosys placer

Make OpenROAD the first provider for a versioned `PhysicalContext` interface.

The original API sketch was:

```cpp
PhysicalNetInfo physical_net(ObjectId net);

struct PhysicalNetInfo {
    double estimated_wire_length;
    double capacitance;
    double resistance;
    double congestion_score;
};

struct PhysicalPinInfo {
    double x;
    double y;
    double arrival;
    double required;
    double slew;
};
```

These are conceptual APIs. Implementation must specify units, rise/fall and early/late sense, scenario, coordinate system, topology/netlist digest, and freshness. A single unqualified floating-point arrival value is insufficient for ASIC timing.

Placement, routing, extraction, and timing data should come from OpenROAD/OpenSTA. Yosys owns candidate generation and synthesis decisions.

```text
Yosys candidate generation
        ↓
cheap logical timing estimate
        ↓
candidate shortlist
        ↓
OpenROAD placement/parasitic estimate
        ↓
candidate ranking
        ↓
Yosys accepts the best legal structural implementation
```

The architecture moves toward physically aware synthesis, without claiming numerical parity with commercial implementations.

## 5. Timing integration

Use the same pinned OpenSTA semantics downstream and for synthesis feedback where feasible.

```text
Yosys optimizer's timing assumptions
        ↔
OpenLane/OpenROAD timing assumptions
```

The integration must align Liberty corners, SDC, units, operating conditions, clock treatment, derates, parasitic model, and constraint coverage. Merely using the same timing engine executable is not enough.

For the identical updated netlist, constraints, and parasitics:

```text
incrementally maintained timing
        versus
fresh timing recomputation
```

must agree within an explicitly justified absolute-plus-relative tolerance. Validate endpoint/path coverage, not only WNS/TNS. Failed, unsupported, and missing results must remain distinguishable from passing results.

## 6. OpenLane as the primary physical QoR oracle

### Fast: Yosys and small formal checks

```text
runtime
aggregate memory
mapped area
cell count
formal equivalence
invalidation/work-reuse assertions
```

### Extended/nightly: Yosys + OpenSTA

```text
WNS / TNS
setup and hold coverage
slew/capacitance violations
unconstrained endpoints
constraint-binding consistency
```

### Milestone: full pinned OpenLane/OpenROAD

```text
post-place and post-route timing
fixed-floorplan cell area and utilization
separate area/floorplan sweeps
wirelength and inserted buffers
congestion/routing violations
DRC/LVS as supported by the pinned flow
activity-qualified power estimates or explicitly labeled proxies
wall time, CPU time, aggregate memory
```

Promotion rule:

> A major synthesis QoR improvement must survive physical implementation on the declared benchmark envelope. Generic gate-count improvement is not routed ASIC improvement.

These are intended test tiers. Publication of this document does not configure schedules or execute tests.

## 7. Benchmark methodology

For each QoR change:

```text
Stock Yosys → identical downstream OpenLane configuration → result
Fork Yosys  → identical downstream OpenLane configuration → result
```

Pin the OpenLane generation/commit, OpenROAD and embedded OpenSTA revisions, Yosys and ABC identities, PDK/library/macro contents, SDC, frontend, synthesis recipe, physical assumptions, seeds where exposed, host, and thread/memory limits.

Distinguish fixed die/core area from fixed utilization. Changing synthesized cell area while forcing constant utilization changes floorplan dimensions; this is a different experiment from using an identical floorplan.

Measure area, WNS, TNS, wirelength, runtime and total validated RTL-to-implementation turnaround. Timing-target sweeps should be reported as Pareto tradeoffs, not one handpicked point.

For incremental work, separate four B lanes:

```text
1. Stock B clean synthesis + full physical implementation.
2. Fork B clean synthesis + full physical implementation.
3. Fork A→B incremental synthesis + full physical implementation.
4. Fork A→B incremental synthesis + validated physical ECO/reuse.
```

Lane 3 isolates synthesis reuse; lane 4 measures additional physical reuse. Add a stock same-partition-policy control whenever boundaries change.

## 8. Hierarchical synthesis

Large SoCs should not be forced into a single flat optimization job.

```text
SoC
├── CPU cluster
│   ├── core
│   ├── L2
│   └── coherency
├── GPU
│   ├── scheduler
│   ├── SIMD tile
│   └── memory unit
├── DSP
├── NoC
└── peripherals
```

Each suitable compilation unit may have:

```text
elaboration artifact
coarse artifact
mapped artifact
boundary functional summary
boundary timing assumptions
physical characterization/context
explicit dependency identity
```

A DSP edit should not force CPU/GPU synthesis unless an actual consumed dependency changes. Conversely, shared package changes, global mapping changes, interface changes, or propagated child facts can legitimately invalidate distant work.

Hierarchical synthesis is distinct from full hierarchical physical implementation. Large physical blocks may need separate OpenLane runs, macro abstracts, timing models, and an integration methodology. Prove the supported composition rather than equating source hierarchy with implementation hierarchy.

## 9. Arithmetic candidates with physical context

ORFS's wrapped-operator approach is a useful precedent for retaining implementations. Extend candidate generation inside Yosys rather than assuming a particular ORFS feature is directly available through OpenLane.

```text
Adder:      area-oriented, prefix, hybrid
Multiplier: Booth, compressor-tree, context-specific decomposition
Reduction:  depth-balanced, arrival-aware
Mux:        sharing-oriented, duplicated, late-select optimized
```

```text
candidate synthesis
      ↓
fast OpenROAD characterization
      ↓
measured ranking
      ↓
implementation selection
```

Preserve finite-width semantics, signedness, truncation, saturation/rounding, and pipeline behavior. Candidate ranking never substitutes for equivalence.

## 10. Revised ordering

The integration destination moves physical-context plumbing earlier than complex physical-aware optimizers:

```text
1. Benchmark and correctness harness
2. Native mapping cache
3. Dependency DAG
4. Analysis manager
5. Measured memory/capacity improvements
6. OpenSTA timing service
7. OpenROAD physical-context contract/provider
8. Arithmetic and mux candidates
9. Physical-aware selection
10. Fine-grained region incrementality
11. Validated physical ECO integration
```

A minimal OpenLane binary-selection/artifact handoff belongs in the initial baseline work, so all subsequent Yosys changes can be tested in their intended environment.

## 11. Persistent physically characterized candidates

A long-term differentiator is retaining previously proved, characterized implementations across builds.

```text
Candidate A: low area / moderate output load
Candidate B: larger / stronger output-driving implementation
Candidate C: suited to a late-arriving operand
```

These descriptions are illustrative, not measured results.

When a semantic region is unchanged but its context changes, first ask whether a previously proved implementation is a better fit. Re-evaluate in the new context; physical characterization is not universally portable across placement, library, corner, or floorplan changes.

This combines:

```text
artifact reuse
    +
proof reuse under explicit assumptions
    +
context-dependent implementation selection
```

The intended advantage is synthesis knowledge accumulated across revisions, not an unsupported claim that commercial tools lack any analogous facility.

## 12. Strict project boundary

Yosys owns incremental semantic compilation, dependency and analysis reuse, hierarchy policy, arithmetic/logic optimization, mapping, timing/physical-aware synthesis decisions, proof obligations, and correspondence.

OpenSTA supplies timing analysis. OpenROAD supplies physical implementation and context. OpenLane supplies orchestration, configuration, artifacts, and flow-level validation.

Do not put global placement, CTS, routing, extraction, or a new STA engine into Yosys.

The long-term target is:

> Yosys is the incremental semantic and optimization engine; OpenROAD maintains valid physical implementation state; OpenLane orchestrates both without discarding reusable state unnecessarily.

## Publication-time reference clarification

These public references support the OpenLane-versus-ORFS distinction and the integration extension points. They are not evidence that the proposed incremental/ECO features are already implemented.

- [OpenLane custom steps](https://openlane2.readthedocs.io/en/latest/usage/writing_custom_steps.html): explicit inputs, outputs, configuration variables, and returned view/metric updates.
- [OpenLane custom flows](https://openlane2.readthedocs.io/en/stable/usage/writing_custom_flows.html): flow composition and `Yosys.Synthesis` invocation.
- [ORFS variables](https://openroad-flow-scripts.readthedocs.io/en/latest/user/FlowVariables.html): `SYNTH_CHECKPOINT`, hierarchy, partitioning, and wrapped-operator options are ORFS-specific.

The exact OpenLane/OpenROAD/PDK versions still need to be selected and pinned during the baseline milestone. No default `latest` version is a valid benchmark lock.
