# Components

`yosys-dev` remains an independent compiler repository. In the staged workspace,
`python3 scripts/stack.py bootstrap` creates an ignored writable checkout pinned
by `toolchain.lock.json`. It refuses to reset existing divergent/dirty work.

The independent export creates a real Git submodule at `components/yosys`.
Run `git submodule update --init --recursive` after the initial commit. The
bootstrap publication deliberately does not change the Yosys fork's root
`.gitmodules`, or recursively add the staging branch as a component of itself.

Normal Nix builds use the manifest's committed source input, not arbitrary files
in a dirty checkout. Update the component gitlink and manifest together in a
reviewed standalone integration PR. Keep reference and candidate build output
separate. Fork LibreLane/OpenROAD only for a demonstrated missing extension API.
