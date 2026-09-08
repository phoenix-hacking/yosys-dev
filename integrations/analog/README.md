# Analog integration adapters

This directory owns adapters between the pinned tool environment and the analog
flow described in [flows/analog](../../flows/analog/README.md). RF solver adapters
belong in [flows/rf](../../flows/rf/README.md); shared macro release/view checks
belong in [verification](../../verification/README.md).

Required tools are declared in `toolchain.lock.json`; their Nix attribute paths,
program names and Python modules are in `nix/tool-catalog.json`.
`phoenix-analog-tool-audit --lane analog` checks the selected package paths and
imports and exits nonzero for missing or unusable requirements. This does not
test simulator models, OSDI loading, schematic netlisting, DRC/LVS or CACE limits.

The first adapter increment must record exact schematic/netlist/configuration,
tool, PDK/model/corner and output identities; execute a headless Xschem/ngspice
smoke; and preserve command, exit status, convergence status and measured values.
Unsupported model paths and failed simulation convergence must block acceptance.
Xyce model compilation must follow its PDK-supported path; ngspice OSDI artifacts
are not assumed interchangeable with Xyce plugins.

Subsequent increments add extraction, CACE regression, deliberate failure cases
and immutable macro view publication under ANA-05 through ANA-14. These adapters
remain pending; the directory and tool audit do not represent a qualified block.
