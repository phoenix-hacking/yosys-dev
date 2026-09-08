"""Revision A oracle: reset, carry/overflow, select, multiplication and counter wrap."""
import random

import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def check_mixed(dut):
    rng = random.Random(0xA51C)
    count = 0
    boundaries = [0, 1, 127, 128, 254, 255]
    vectors = [(a, b, select, 0) for a in boundaries for b in boundaries for select in (0, 1)]
    vectors += [(rng.randrange(256), rng.randrange(256), rng.randrange(2), int(i == 350))
                for i in range(700)]
    for a, b, select, reset in [(0, 0, 0, 1)] + vectors:
        dut.clk.value = 0
        dut.rst.value = reset
        dut.a.value, dut.b.value, dut.select.value = a, b, select
        await Timer(5, unit="ns")
        dut.clk.value = 1
        await Timer(5, unit="ns")
        count = 0 if reset else (count + 1) % 256
        expected = {"product": 0 if reset else a * b,
                    "result": 0 if reset else (a + b if select else a), "count": count}
        for name, value in expected.items():
            actual = getattr(dut, name).value
            assert actual.is_resolvable, f"{name} contains X/Z"
            assert int(actual) == value, f"{name}: got {actual}, expected {value}"
