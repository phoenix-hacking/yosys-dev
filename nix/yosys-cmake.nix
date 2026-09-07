# Adapt the pinned nix-eda package interface to the fork's CMake build.
# Source-reviewed; full Nix build is an explicit pending acceptance gate.
{ src, revision }:
final: prev: {
  yosys = (prev.yosys.override { yosys = final.yosys; }).overrideAttrs (old: {
    inherit src;
    version = "dev-${builtins.substring 0 12 revision}";
    nativeBuildInputs = (old.nativeBuildInputs or []) ++ [ final.cmake final.ninja ];
    buildInputs = (old.buildInputs or []) ++ [ final.gtest final.readline final.libtommath ];
    unpackPhase = ''
      runHook preUnpack
      cp -R ${src}/. .
      chmod -R u+w .
      runHook postUnpack
    '';
    configurePhase = ''
      runHook preConfigure
      cmake -S . -B build -G Ninja \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX="$out" \
        -DYOSYS_USE_BUNDLED_LIBS=ON \
        -DYOSYS_SKIP_ABC_SUBMODULE_CHECK=ON \
        -DYOSYS_CHECKOUT_INFO=${revision} \
        -DYOSYS_WITH_PYTHON=ON \
        -DYOSYS_INSTALL_LIBRARY=ON \
        -DYOSYS_INSTALL_PYTHON=ON \
        -DYOSYS_INSTALL_PYTHON_SITEDIR="$python/${final.python3.sitePackages}" \
        -DPython3_EXECUTABLE=${old.passthru.python3-env}/bin/python3
      runHook postConfigure
    '';
    buildPhase = ''
      runHook preBuild
      cmake --build build --parallel "$NIX_BUILD_CORES"
      runHook postBuild
    '';
    installPhase = ''
      runHook preInstall
      cmake --install build
      runHook postInstall
    '';
    # Replace the old Make recipe's setup.py invocation; this source uses CMake.
    postInstall = ''
      mkdir -p "$python/${final.python3.sitePackages}/pyosys-0.0.0.dist-info"
      printf 'Metadata-Version: 2.1\nName: pyosys\nVersion: 0.0.0\n' \
        > "$python/${final.python3.sitePackages}/pyosys-0.0.0.dist-info/METADATA"
      cat > "$TMPDIR/phoenix-binding-probe.py" <<'PY'
from pyosys import libyosys as ys
assert ys.Design is not None
ys.run_pass("help synth")
PY
      "$out/bin/yosys" -Q -y "$TMPDIR/phoenix-binding-probe.py"
    '';
    # Full upstream tests are a distinct required CI gate, not implied by install.
    doCheck = false;
  });
}
