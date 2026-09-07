# Yosys ASIC progress dashboard

Last updated: 2026-09-07 · Plan version: 1.0 · Repository: `phoenix-hacking/yosys-dev`.

[Execution plan and all checkboxes](ASIC_EXECUTION_PLAN.md) · [Synthesis research](docs/asic-roadmap/RESEARCH_REPORT.md) · [OpenLane integration report](docs/asic-roadmap/OPENLANE_INTEGRATION_REPORT.md).

## Current state

**Planning published. Engineering implementation and validation have not been credited by this documentation change.**

| Measure | Current evidence-backed status |
|---|---|
| Core acceptance tasks | **0 / 240 accepted** |
| Core workstreams | **0 / 20 accepted** |
| Core milestones | **0 / 9 accepted** |
| Research acceptance tasks | **0 / 48 accepted** |
| Research experiments | **0 / 8 concluded** |
| Initial planned PR queue | **0 / 24 implementation PRs accepted**; queue IDs are not GitHub PR numbers |
| Baseline source anchor | Repository head verified at `435977e97008578a4532da60e70f75b5e88d076d` before documentation additions |
| Baseline build / upstream tests | **NOT RUN in this documentation session** |
| Formal edit-replay tests | **NOT RUN** |
| OpenLane stock/fork comparison | **NOT RUN** |
| Mapping cache / incremental compiler | **Not implemented by this change** |
| Speedup / memory / PPA results | **Not measured** |
| Commercial parity | **Not established** |

These are acceptance-task counts, not an estimate of weighted engineering completion or time remaining. Task sizes differ. Documentation volume, commit count and lines of code are not completion metrics.

## Next executable tranche

**PR-001: baseline inventory, complete lock schema and supported-envelope definition.**

Scope: BAS-01 through BAS-04 and OLN-01. The exact source SHA is known, but that does not complete these tasks: the full toolchain, dependencies, OpenLane generation, PDK/models, recipe and supported semantics still need to be selected, recorded and validated.

Required deliverables are a source/dependency inventory, versioned toolchain-lock schema with missing values rejected, a source-linked audit of the first implementation boundary, and a documented first ASIC/OpenLane configuration. Evidence should identify which inputs remain unresolved rather than silently using latest versions.

Then execute PR-002 through PR-006 for isolated builds, metrics, real A→B fixtures and an oracle that rejects intentionally wrong netlists. Bring up PR-007/008 for the real OpenLane stock/fork baseline. Only then promote the mapping-cache implementation through PR-009–016.

The first meaningful compiler win is a real local RTL edit that rebuilds the correct mapping jobs, skips unchanged expensive work, proves the intended updated circuit and shows measured end-to-end benefit.

## Milestone board

| Milestone | Scope | Accepted / total | State | Exit evidence |
|---|---|---:|---|---|
| M0 | Baseline, verification oracle, OpenLane handoff | 0 / 36 | READY TO START | Pinned builds, detected wrong netlists, matched physical smoke |
| M1 | Artifact store and native mapping cache | 0 / 24 | WAITING ON M0 | Exact input invalidation, failure-safe reuse, measured cold/warm cost |
| M2 | Stage/module reuse and maintained analyses | 0 / 36 | NOT STARTED | Correct dependency histories and fresh-analysis comparisons |
| M3 | Capacity and ASIC memory safety | 0 / 24 | NOT STARTED | Scaling/resource evidence and no unexplained large-memory fallback |
| M4 | Timing and physical-context contracts | 0 / 24 | NOT STARTED | Matched fresh/incremental timing and stale-context rejection |
| M5 | Word-level alternatives and ASIC QoR | 0 / 24 | NOT STARTED | Proof plus held-out mapped/routed Pareto comparisons |
| M6 | Hierarchy, frontend and regional reuse | 0 / 36 | NOT STARTED | Correct local edits with explicit boundary tradeoffs |
| M7 | Validated physical ECO | 0 / 12 | NOT STARTED | Narrow ECO with final-netlist proof, timing, physical checks and rollback |
| M8 | Held-out evaluation and release hardening | 0 / 24 | NOT STARTED | Independent reproduction, support envelope, negative-outlier report |
| Total | Core program | **0 / 240** | PLANNED | No engineering completion inferred from this plan |

Some work can overlap according to the execution plan's dependency graph. A milestone row is not a promise of calendar delivery or an instruction to serialize all work.

## Workstream ledger

Owners and implementation PRs are unassigned. Set them when work actually begins.

| ID | Workstream | Accepted | State | Owner / PR / evidence |
|---|---|---:|---|---|
| BAS | Pinned baseline and measurement | 0 / 12 | READY | Unassigned; none |
| VAL | Edit replay and formal oracle | 0 / 12 | TODO | Unassigned; none |
| OLN | OpenLane baseline and handoff | 0 / 12 | READY FOR SELECTION/AUDIT | Unassigned; none |
| CAS | Content-addressed artifacts | 0 / 12 | TODO | Unassigned; none |
| MAP | Native mapping-result reuse | 0 / 12 | TODO | Unassigned; none |
| DAG | Stage/module dependency graph | 0 / 12 | TODO | Unassigned; none |
| REV | Revisions and analyses | 0 / 12 | TODO | Unassigned; none |
| OPT | Pass preservation and dirty optimization | 0 / 12 | TODO | Unassigned; none |
| CAP | Capacity, memory and scheduling | 0 / 12 | TODO | Unassigned; none |
| MEM | Memories/macros and strict fallback | 0 / 12 | TODO | Unassigned; none |
| TIM | Timing and constraint lifetime | 0 / 12 | TODO | Unassigned; none |
| PHY | Physical context and correspondence | 0 / 12 | TODO | Unassigned; none |
| WIR | Typed regions and transactions | 0 / 12 | TODO | Unassigned; none |
| QOR | Arithmetic/mux candidates and selection | 0 / 12 | TODO | Unassigned; none |
| HIE | Hierarchy and boundary budgets | 0 / 12 | TODO | Unassigned; none |
| FEN | Incremental elaboration | 0 / 12 | TODO | Unassigned; none |
| REG | Within-module incrementality | 0 / 12 | TODO | Unassigned; none |
| ECO | Physical incremental implementation | 0 / 12 | TODO | Unassigned; none |
| PPA | Held-out quality/parity evidence | 0 / 12 | TODO | Unassigned; none |
| REL | Hardening and release | 0 / 12 | TODO | Unassigned; none |

## Research ledger

A completed experiment may have a negative result. Track evidence completion separately from successful promotion into the compiler.

| ID | Experiment | Accepted tasks | Outcome | Production promotion |
|---|---|---:|---|---|
| R01 | Persistent characterized candidate portfolios | 0 / 6 | NOT RUN | No |
| R02 | Bounded typed equality saturation | 0 / 6 | NOT RUN | No |
| R03 | Learned physical candidate ranking | 0 / 6 | NOT RUN | No |
| R04 | Certified sequential retiming/resynthesis | 0 / 6 | NOT RUN | No |
| R05 | Solver-guided local/multi-output synthesis | 0 / 6 | NOT RUN | No |
| R06 | Adaptive optimization action scheduling | 0 / 6 | NOT RUN | No |
| R07 | Distributed content-addressed compilation | 0 / 6 | NOT RUN | No |
| R08 | Stability-aware ECO and proof composition | 0 / 6 | NOT RUN | No |
| Total | Research program | **0 / 48** | No experiments concluded | No research promotion claimed |

## Decisions and unresolved prerequisites

| Decision / prerequisite | Status | Responsible tasks | Why it matters |
|---|---|---|---|
| Stock Yosys source revision | Source SHA confirmed; build pending | BAS-01/05/06 | Prevent moving or accidental same-binary controls |
| Full frontend/plugin/ABC/build lock | Incomplete | BAS-01/02/05/06 | Source alone does not determine the executable |
| OpenLane generation and commit | Not selected/pinned | OLN-01/02 | OpenLane and ORFS APIs/options are not interchangeable |
| OpenROAD/embedded OpenSTA versions | Not pinned | OLN-01, TIM-01 | Timing/interface support depends on actual build |
| First PDK/library/corners/models | Not selected/validated | BAS-04/08, OLN-01, MEM | Correct mapping, proof and physical comparison |
| First mapper backend | Audit/measurement pending | MAP-01/02 | Do not force experimental `abc_new` solely because it has a convenient hook |
| Supported exact-reuse contract | To implement and validate | DAG-01–04, MAP | Byte identity, structural identity and equivalence are different guarantees |
| Initial physical ECO scope | Proposed narrow pre-CTS scope only | ECO-01 | Arbitrary RTL-to-routed ECO is not assumed available |
| Complete research bibliography/reproductions | Inherited leads; audit pending | BAS-03, PPA-11, R01–R08 | Conversational citations are not portable verified evidence |
| Benchmark compute and licensed inputs | Not provisioned by this change | BAS, OLN, PPA | Resource and redistribution constraints must be explicit |

These are engineering prerequisites, not a request to stop planning. Resolve what the repository/toolchain can establish before asking the owner for genuinely necessary choices.

## Benchmark scorecard

Do not fill this table with target values or illustrative performance numbers. Use measured values with immutable run references.

| Metric | Stock clean | Fork clean | Fork incremental | Fork incremental + physical ECO |
|---|---|---|---|---|
| Synthesis wall time | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| Total validated turnaround | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| Concurrent job memory | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| Mapping jobs executed/reused | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| Cache cold/hit overhead | N/A | NOT RUN | NOT RUN | NOT RUN |
| Weighted synthesis work reuse | N/A | N/A | NOT RUN | NOT RUN |
| Mapped standard-cell area | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| Post-route setup/hold and coverage | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| Physical checks / final-netlist proof | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| Implementation churn | N/A | NOT RUN | NOT RUN | NOT RUN |
| Required formal equivalence | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

Separate synthesis reuse from physical reuse using the execution plan's S0–S4 lanes. A full-flow restart that happens to reuse an earlier result is not evidence that a native Yosys stage was correctly skipped. A faster synthesis run is not evidence that a routed ECO was validated.

## How to update progress

1. Start from the current branch/commit and check for other contributors' changes. Read the relevant workstream and prerequisites.
2. Assign a task/PR tranche and record `IN_PROGRESS`; do not check its box merely because development began.
3. Record implemented code, exact commands and results in the task evidence file. Use `IMPLEMENTED_UNVERIFIED` when required checks have not run.
4. Run required correctness, invalidation, recovery and benchmark gates. Preserve failures and inconclusive results.
5. Record acceptance with limitations and review. Only then check the task in `ASIC_EXECUTION_PLAN.md` and update this ledger in the same documentation update.
6. Recompute accepted task/workstream/milestone counts; do not double-count a task appearing in both a PR row and its workstream.
7. Record the next concrete task and actual blocker. Keep research outcome and production promotion separate.

The planned automated consistency checker is REL-09; it is not installed by these Markdown files. Until it exists, validate counts and evidence manually or with a one-off local audit and do not represent that audit as synthesis verification.

### Session handoff template

```markdown
Date / branch / HEAD:
Selected task IDs and PR tranche:
Actual implementation commits:
Changed source/configuration:
Tests run and exact outcomes:
Proof results and assumptions:
Metrics/artifact references:
Accepted tasks (with evidence):
Implemented but unverified tasks:
Blockers and unsupported cases:
Next smallest dependency-ready tranche:
```

## Publication and execution log

| Date | Change | Evidence | Engineering credit |
|---|---|---|---|
| 2026-09-07 | OpenLane integration report published | Commit `5c57d131a56ee2564b9663a1b340570b1db5226f` | None; planning |
| 2026-09-07 | Structured synthesis research report published | Commit `530bfa152b737c47cbae126155f5f2819fb5b1f1` | None; planning |
| 2026-09-07 | Granular execution plan published | Commit `387f622e9501fa09f1b9e929e767bc09aa901421` | None; 240 core + 48 research tasks defined |
| 2026-09-07 | Progress dashboard initialized | This file's Git history | None; actual engineering/proof/flow results remain uncredited |

Publication preserved upstream source code and created planning Markdown. The reports are structured repository editions of supplied research, not byte-for-byte transcripts; they explicitly distinguish original research leads from publication-time verification and from future implementation.

No background task, automatic weekly execution, benchmark farm, GitHub issue batch, or synthesis implementation was created by this documentation action.
