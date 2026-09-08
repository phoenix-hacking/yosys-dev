# UVA HotSpot thermal model; intentionally distinct from the KDE perf viewer.
{ lib, stdenv, python3, src, revision }:
stdenv.mkDerivation {
  pname = "hotspot-thermal";
  version = "7.0-${builtins.substring 0 12 revision}";
  inherit src;
  enableParallelBuilding = true;
  makeFlags = [ "CC=${stdenv.cc.targetPrefix}cc" "SUPERLU=0" ];
  buildTargets = [ "hotspot" ];
  doCheck = true;
  nativeCheckInputs = [ python3 ];
  checkPhase = ''
    runHook preCheck
    python3 ${../scripts/thermal_smoke.py} --hotspot "$PWD/hotspot" \
      --config "$PWD/template.config" --output "$TMPDIR/thermal-smoke"
    runHook postCheck
  '';
  installPhase = ''
    runHook preInstall
    install -Dm755 hotspot "$out/bin/hotspot"
    install -Dm644 template.config "$out/share/hotspot-thermal/template.config"
    install -Dm644 LICENSE "$out/share/licenses/hotspot-thermal/LICENSE"
    runHook postInstall
  '';
  meta = {
    description = "UVA HotSpot compact thermal model for architectural studies";
    homepage = "https://github.com/uvahotspot/HotSpot";
    license = {
      shortName = "HotSpot";
      fullName = "HotSpot license (permission to use, copy, modify and distribute)";
      url = "https://github.com/uvahotspot/HotSpot/blob/${revision}/LICENSE";
      free = true;
    };
    platforms = lib.platforms.linux;
    mainProgram = "hotspot";
  };
}
