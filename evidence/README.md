# Evidence scope

`bootstrap-validation.json` and `offline-unittest.log` are retained historical
bootstrap evidence from 2026-09-07. They do not certify later changes: preparation
review at `ad39cce779264d26e9620baca776b3f92972b3db` reproduced eight test errors
and two live-test skips, including source-schema drift and stale export hashes.

`preparation-validation-20260908.json` records the subsequent preparation fixes
and their validation. It does not qualify Nix packages, PDKs, synthesis, physical
implementation, analog/RF designs or mixed-signal assembly. Compiler progress
and STK/ANA/RF/MS flow acceptance remain separate.

Source manifests cover reviewed files only. Runtime tools, PDKs and design
artifacts belong outside Git and require their own identity/evidence inventories.
