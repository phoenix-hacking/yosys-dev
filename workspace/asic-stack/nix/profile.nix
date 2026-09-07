# Keep reference, matched stock and candidate environments explicit.
{ profile, src, revision, librelane, self, lock, base }:
let
  pkgs = if profile == "reference" then base
    else base.extend (import ./yosys-cmake.nix { inherit src revision; });
  ll = if profile == "reference" then pkgs.python3.pkgs.librelane
    else pkgs.python3.pkgs.librelane.override {
      yosys = pkgs.yosys;
      # Initial Verilog envelope. No incompatible external binary plugins.
      yosys-plugin-set = [];
    };
  plugin = pkgs.python3.pkgs.buildPythonPackage {
    pname = "librelane-plugin-phoenix";
    version = "0.1.0";
    pyproject = true;
    src = ../integrations/librelane;
    build-system = [ pkgs.python3.pkgs.setuptools ];
    dependencies = [ ll ];
    doCheck = false;
  };
  py = pkgs.python3.withPackages (ps: [ ll plugin ps.psutil ]);
  ys = (pkgs.yosys.withPythonPackages.override { target = pkgs.yosys; })
    (ps: with ps; [ click rich pyyaml ]);
  identity = pkgs.writeText "phoenix-toolchain-${profile}.json" (builtins.toJSON {
    schema_version = 1;
    inherit profile;
    librelane_revision = lock.sources.librelane.revision;
    yosys_revision = revision;
    yosys_package_version = pkgs.yosys.version;
    yosys_native = "${pkgs.yosys}/bin/yosys";
    pyosys_roots = [ "${pkgs.yosys}" "${pkgs.yosys.python}" ];
    openroad = "${pkgs.openroad}/bin/openroad";
    opensta = "${pkgs.opensta}/bin/sta";
    external_binary_plugins = [];
  });
  runner = pkgs.symlinkJoin {
    name = "phoenix-asic-${profile}";
    paths = [
      (pkgs.writeShellScriptBin "phoenix-librelane" ''
        export _LLN_OVERRIDE_YOSYS=${ys}/bin/yosys
        exec ${py}/bin/librelane "$@"
      '')
      (pkgs.writeShellScriptBin "phoenix-toolchain" ''
        if [ "''${1:-}" = "--path" ]; then
          printf '%s\n' '${identity}'
        else
          cat '${identity}'
        fi
      '')
    ];
  };
in {
  inherit runner identity;
  shell = pkgs.mkShell {
    packages = [ runner py pkgs.git pkgs.nix pkgs.ciel ] ++ ll.includedTools;
    shellHook = ''
      export PHOENIX_PROFILE=${profile}
      echo 'Phoenix ${profile}: use scripts/stack.py doctor before a flow run.'
    '';
  };
}
