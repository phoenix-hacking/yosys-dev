# Pure evaluation regression: no network, builds, or fabricated package closure.
# nix-instantiate --eval --strict nix/tests/tool-discovery.nix
let
  fixture = name: { outPath = "/nix/store/unit-test-${name}"; version = "fixture"; };
  lock = builtins.fromJSON (builtins.readFile ../../toolchain.lock.json);
  found = import ../analog-tools.nix {
    inherit lock;
    pkgs = {
      xschem = fixture "xschem";
      python3.pkgs.gdsfactory = fixture "gdsfactory";
    };
    overrides.librelane = fixture "selected-librelane";
  };
  extension = import ../analog-tools.nix {
    inherit lock;
    extensions = [ "verification" "thermal" ];
    pkgs = {
      python3.pkgs.cocotb = fixture "cocotb";
      hotspot = throw "The KDE perf viewer must never satisfy thermal analysis";
    };
    overrides.hotspot-thermal = fixture "hotspot-thermal";
  };
in
assert found.manifest.gdsfactory.available;
assert found.manifest.gdsfactory.attribute == [ "python3" "pkgs" "gdsfactory" ];
assert !found.manifest.cace.available;
assert builtins.elem "cace" found.missingByLane.analog;
assert builtins.elem "palace" found.missingByLane.rf;
assert !builtins.elem "librelane" found.missingByLane.digital;
assert found.manifest.librelane.store_path == "/nix/store/unit-test-selected-librelane";
assert builtins.length found.packages == 1;
assert builtins.length found.pythonPackages == 2;
assert !builtins.hasAttr "cocotb" found.manifest;
assert extension.manifest.cocotb.available;
assert builtins.elem "mcy" extension.missingByExtension.verification;
assert extension.missingByExtension.thermal == [];
assert extension.manifest.hotspot-thermal.store_path == "/nix/store/unit-test-hotspot-thermal";
assert !builtins.hasAttr "heaptrack" extension.manifest;
{ status = "PASS"; scope = "package discovery only"; }
