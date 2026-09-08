{ pkgs }:
let
  resolve = name:
    if builtins.hasAttr name pkgs then builtins.getAttr name pkgs else null;

  requiredNames = [
    "xschem"
    "ngspice"
    "xyce"
    "gdsfactory"
    "openvaf-reloaded"
  ];

  # These are required by the intended analog/RF release envelope, but may need
  # a project-local derivation or additional flake input if the inherited
  # nix-eda package set does not expose them directly.
  externallyPackagedRequired = [
    "cace"
    "openems"
    "palace"
    "scikit-rf"
  ];

  optionalNames = [
    "qucs-s"
    "gnucap"
    "gmsh"
    "paraview"
  ];

  resolvedRequired = builtins.filter (x: x != null)
    (map (name: resolve name) requiredNames);
  missingRequired = builtins.filter (name: resolve name == null) requiredNames;

  resolvedOptional = builtins.filter (x: x != null)
    (map (name: resolve name) optionalNames);
  missingOptional = builtins.filter (name: resolve name == null) optionalNames;
in {
  inherit requiredNames externallyPackagedRequired optionalNames;
  packages = resolvedRequired ++ resolvedOptional;
  inherit missingRequired missingOptional;
}
