SIM ?= icarus
TOPLEVEL_LANG := verilog
TOPLEVEL := mixed_top
COCOTB_TEST_MODULES := test_mixed
VERILOG_SOURCES ?= $(abspath ../../benchmarks/designs/mixed/A/top.v)
SIM_BUILD ?= $(abspath ../../.runs/cocotb/$(SIM))
COCOTB_RESULTS_FILE ?= $(SIM_BUILD)/results.xml
include $(shell cocotb-config --makefiles)/Makefile.sim
