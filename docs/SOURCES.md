# Inspected primary sources

Source inventory date: 2026-09-07. Source inspection is not successful execution.
These immutable links support the packaging and adapter decisions in this change.

- [LibreLane 3.0.14 release](https://github.com/librelane/librelane/releases/tag/3.0.14)
- [LibreLane source at f24e0ea](https://github.com/librelane/librelane/tree/f24e0ea5db2260719e9a0c7d51d07db74a87fa23)
- [Packaged tool closure and Python environments](https://github.com/librelane/librelane/blob/f24e0ea5db2260719e9a0c7d51d07db74a87fa23/default.nix)
- [Inherited dependency lock](https://github.com/librelane/librelane/blob/f24e0ea5db2260719e9a0c7d51d07db74a87fa23/flake.lock)
- [Pyosys synthesis steps and command shape](https://github.com/librelane/librelane/blob/f24e0ea5db2260719e9a0c7d51d07db74a87fa23/librelane/steps/pyosys.py)
- [Classic flow](https://github.com/librelane/librelane/blob/f24e0ea5db2260719e9a0c7d51d07db74a87fa23/librelane/flows/classic.py)
- [Flow registration](https://github.com/librelane/librelane/blob/f24e0ea5db2260719e9a0c7d51d07db74a87fa23/librelane/flows/flow.py)
- [CLI and config handoff](https://github.com/librelane/librelane/blob/f24e0ea5db2260719e9a0c7d51d07db74a87fa23/librelane/__main__.py)
- [nix-eda reference Yosys package](https://github.com/fossi-foundation/nix-eda/blob/8f990fb77529c09e540e453cd836af9930ec58db/nix/yosys.nix)
- [Fork CMake options](https://github.com/phoenix-hacking/yosys-dev/blob/43bbfbf71cba0435ebf806e9be8a888027c2903d/CMakeLists.txt)
- [Fork Python generator environment](https://github.com/phoenix-hacking/yosys-dev/blob/43bbfbf71cba0435ebf806e9be8a888027c2903d/cmake/FindPyosysEnv.cmake)

## Decisions

1. Use LibreLane's environment instead of collecting every tool from scratch.
2. Preserve Yosys history; maintain stack code separately and export a superproject.
3. Use a Python plugin, replacing only Synthesis in Classic initially.
4. Execute the identity audit in the same Yosys process, then delegate to the
   original pinned LibreLane synthesis script without cloning its implementation.
5. Override the pinned Make-based Yosys recipe for the CMake-based fork and enable
   native/Python installation. Build/API success must still be tested.
6. ORFS configuration is not LibreLane configuration. Existing ORFS checkpoint and
   wrapped-arithmetic features are references, not assumed compatible APIs.
7. Keep source pins, resolved build closure, runtime identity, PDK inventory and
   formal/physical evidence separate; no one record proves all five.

## Preparation review, 2026-09-08

- [Pinned nix-eda overlay](https://github.com/fossi-foundation/nix-eda/blob/8f990fb77529c09e540e453cd836af9930ec58db/flake.nix): GDSFactory is a Python package under `python3.pkgs`; EQY/SBY use `yosys-eqy`/`yosys-sby`. This overlay does not explicitly define OpenVAF Reloaded.
- [Pinned scikit-rf derivation](https://github.com/NixOS/nixpkgs/blob/b3aad468604d3e488d627c0b43984eb60e75e782/pkgs/development/python-modules/scikit-rf/default.nix): version 1.8.0, imported as `skrf`; project build/qualification remains pending.
- [IHP technology collateral](https://ihp-open-pdk-docs.readthedocs.io/en/latest/contents/technology_libraries/index.html): documents the analog, digital and openEMS/Palace directories. This is a reference for platform selection, not a pinned provisioned PDK.
- [Repository rename](https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository) and [GitHub CLI syntax](https://cli.github.com/manual/gh_repo_rename): rename preserves redirects; old URLs must not be reused for a different repository.
