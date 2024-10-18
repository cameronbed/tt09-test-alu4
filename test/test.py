# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    dut._log.info("Test project behavior")

    # Set the input values you want to test
    # a and b are inputs to our testbench
    dut.a.value = 13
    dut.b.value = 10

    # Wait for one clock cycle to see the output values
    # This will be different for each design.
    await ClockCycles(dut.clk, 10)

    # The following assersion is just an example of how to check the output values.
    # Change it to match the actual expected output of your module:
    dut._log.info(f"value of outputs are: {dut.sum.value} and {dut.carry_out.value}.")
    # Checking of the constraints after the assert are expired.
    # Checking for an error. This is what is expected.
    assert dut.sum.value == 7 and dut.carry_out.value == 1

    for x in range(15):
        for y in range(15):
            sum = x + y
            dut.a.value = x
            dut.b.value = y
            await ClockCycles(dut.clk, 10)
            dut._log.info(f"value of outputs are: {dut.sum.value} and {dut.carry_out.value}.")
            if sum > 10:
                assert dut.sum.value == sum and dut.carry_out.value == 1
            else:
                assert dut.sum.value == sum and dut.carry_out.value == 0
    return

    # Keep testing the module by changing the input values, waiting for
    # one or more clock cycles, and asserting the expected output values.
    
