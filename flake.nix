# GENERATED from toolchain.lock.json by scripts/stack.py render-flake.
# Run `nix flake lock` before build acceptance; this is not a fabricated lockfile.
{
  description = "Phoenix ASIC workspace: LibreLane plus an independently maintained Yosys fork";
  inputs = {
    librelane.url = "github:librelane/librelane/f24e0ea5db2260719e9a0c7d51d07db74a87fa23";
    yosys-candidate = {
      url = "git+https://github.com/phoenix-hacking/yosys-dev.git?rev=43bbfbf71cba0435ebf806e9be8a888027c2903d&submodules=1";
      flake = false;
    };
    yosys-stock = {
      url = "git+https://github.com/YosysHQ/yosys.git?rev=435977e97008578a4532da60e70f75b5e88d076d&submodules=1";
      flake = false;
    };
  };
  outputs = { self, librelane, yosys-candidate, yosys-stock }:
    let
      system = "x86_64-linux";
      base = librelane.legacyPackages.${system};
      lock = builtins.fromJSON (builtins.readFile ./toolchain.lock.json);
      mk = profile: src: revision:
        import ./nix/profile.nix {
          inherit profile src revision librelane self lock base;
        };
      reference = mk "reference" null null;
      stock = mk "stock" yosys-stock lock.sources.yosys_stock.revision;
      candidate = mk "candidate" yosys-candidate lock.sources.yosys_candidate.revision;
    in {
      packages.${system} = {
        reference = reference.runner;
        stock = stock.runner;
        candidate = candidate.runner;
        default = reference.runner;
      };
      devShells.${system} = {
        reference = reference.shell;
        stock = stock.shell;
        candidate = candidate.shell;
        default = reference.shell;
      };
      checks.${system}.offline = base.runCommand "phoenix-offline-tests" {
        nativeBuildInputs = [ base.python3 base.git ];
      } ''
        cp -R ${self}/. work
        chmod -R u+w work
        cd work
        python3 -m unittest discover -s tests -v
        touch $out
      '';
    };
}
