# Components

`components/yosys` is a real Git submodule pinned to the compiler-tree commit
`43bbfbf71cba0435ebf806e9be8a888027c2903d`. Its compiler history is preserved
inside this repository's history; it is not a separately renamed GitHub repository.

The submodule URL `./` resolves to the superproject's origin, so renaming the
repository to `asic-flow` also works for new component checkouts. Git checks out
the exact compiler commit, whose own submodules are ABC and compiler libraries;
it never selects this flow branch as its component source.

`python3 scripts/stack.py bootstrap` initializes an empty submodule checkout and
its dependencies. It verifies the index gitlink against `toolchain.lock.json`
and refuses to reset divergent or dirty component work. Repeat invocation is safe.
An independent export uses an absolute compiler URL, since that new repository
does not contain the original compiler history.

Normal Nix builds use the manifest's committed source input, not arbitrary files
in a dirty checkout. Update the component gitlink and manifest together in a
reviewed standalone integration PR. Keep reference and candidate build output
separate. Fork LibreLane/OpenROAD only for a demonstrated missing extension API.
