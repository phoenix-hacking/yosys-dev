# Resolve required tools from the *pinned* inherited EDA package set.
# Discovery is not a build, simulator/PDK qualification, or signoff result.
{ pkgs, lock, overrides ? {} }:
let
  catalog = builtins.fromJSON (builtins.readFile ./tool-catalog.json);
  unique = builtins.foldl' (xs: x: if builtins.elem x xs then xs else xs ++ [x]) [];
  requiredNames = unique (lock.tooling_contract.digital_required
    ++ lock.tooling_contract.analog_required ++ lock.tooling_contract.rf_required);
  atPath = path: builtins.foldl'
    (set: key: if builtins.isAttrs set && builtins.hasAttr key set
      then builtins.getAttr key set else null) pkgs path;
  resolve = name:
    let
      candidates = map (path: { inherit path; package = atPath path; })
        catalog.${name}.package_candidates;
      found = builtins.filter (x: x.package != null) candidates;
    in if builtins.hasAttr name overrides
      then { path = [ "profile-override" name ]; package = overrides.${name}; }
      else if found == [] then { path = null; package = null; }
      else builtins.head found;
  selected = builtins.listToAttrs (map (name: { inherit name; value = resolve name; }) requiredNames);
  present = builtins.filter (name: selected.${name}.package != null) requiredNames;
  packagesOfKind = kind: map (name: selected.${name}.package)
    (builtins.filter (name: catalog.${name}.kind == kind) present);
  missingRequired = builtins.filter (name: selected.${name}.package == null) requiredNames;
  manifest = builtins.listToAttrs (map (name:
    let
      item = selected.${name};
      pkg = item.package;
    in { inherit name; value = {
      available = pkg != null;
      attribute = item.path;
      kind = catalog.${name}.kind;
      version = if pkg == null then null else (pkg.version or "unknown");
      store_path = if pkg == null then null else toString pkg;
      qualified = false;
    }; }) requiredNames);
in {
  inherit requiredNames missingRequired manifest;
  packages = unique (packagesOfKind "native");
  pythonPackages = packagesOfKind "python";
  missingByLane = builtins.listToAttrs (map (lane: {
    name = lane;
    value = builtins.filter (name: builtins.elem name missingRequired)
      lock.tooling_contract."${lane}_required";
  }) [ "digital" "analog" "rf" ]);
}
