# LibreLane ASIC workspace

The integrated workspace is staged at [workspace/asic-stack](workspace/asic-stack/README.md).
Yosys source and its upstream layout are unchanged. The intended independent
`phoenix-hacking/asic-stack` repository could not be created by this connector;
the tested export script creates a clean standalone workspace with a pinned
Yosys submodule entry for owner-authorized publication.

Read the [stack progress](workspace/asic-stack/STACK_PROGRESS.md),
[bring-up plan](workspace/asic-stack/STACK_EXECUTION_PLAN.md), and
[offline validation evidence](workspace/asic-stack/evidence/bootstrap-validation.json).

Implemented bootstrap code is not an accepted compiler optimization or validated
RTL-to-GDS release. Nix resolution/build, real LibreLane synthesis, PDK provisioning,
formal equivalence and physical validation remain explicit follow-on gates.
The original ASIC_EXECUTION_PLAN.md and ASIC_PROGRESS.md remain authoritative for
native compiler work and are not credited by workspace scaffolding.
