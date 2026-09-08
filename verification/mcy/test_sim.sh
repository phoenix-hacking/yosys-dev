#!/usr/bin/env bash
set -euo pipefail
: "${ASIC_FLOW_ROOT:?Set ASIC_FLOW_ROOT to the repository root before mcy init/run}"
bash "$SCRIPTS/create_mutated.sh"
test ! -e results.xml # never classify stale results from a previous task
status=0
timeout 60 make -C "$ASIC_FLOW_ROOT/verification/cocotb" SIM=icarus \
    VERILOG_SOURCES="$PWD/mutated.v" SIM_BUILD="$PWD/sim_build" \
    COCOTB_RESULTS_FILE="$PWD/results.xml" > simulation.log 2>&1 || status=$?
python3 "$ASIC_FLOW_ROOT/scripts/simulation_result.py" results.xml --make-exit "$status" --mcy-output output.txt
