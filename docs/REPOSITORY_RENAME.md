# Rename the GitHub repository to asic-flow

The target is `phoenix-hacking/asic-flow`, preserving repository ID `1359721599`,
all compiler history and draft PR #1. This is a rename of the existing repository.
The connected GitHub plugin excludes repository-administration access.

On a machine authenticated to GitHub with repository administration rights:

```sh
gh repo rename asic-flow --repo phoenix-hacking/yosys-dev --yes
gh repo view phoenix-hacking/asic-flow --json nameWithOwner,url
```

Alternatively, open the repository's Settings > General and change its name.
After verifying the new name, update this checkout:

```sh
git remote set-url origin https://github.com/phoenix-hacking/asic-flow.git
git submodule sync --recursive
python3 scripts/stack.py bootstrap
```

The Yosys gitlink stays at `43bbfbf71cba0435ebf806e9be8a888027c2903d`.
Its `./` submodule URL follows the superproject origin. The source lock and
generated Nix flake retain the old immutable compiler URL, which GitHub redirects.
Once the rename is verified, change only `sources.yosys_candidate.repository`
to `phoenix-hacking/asic-flow`, render the flake again and refresh the export
manifest. Do not change compiler, LibreLane or inherited dependency revisions
as part of the name migration. A real `flake.lock`, once resolved, must also be
regenerated and checked when an input URL changes.

The draft flow branch and the default branch are separate concerns. Renaming
the remote does not merge PR #1 or qualify any EDA tool, PDK or design.

Sources: [GitHub rename behavior](https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository)
and [GitHub CLI command](https://cli.github.com/manual/gh_repo_rename).
