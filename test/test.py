import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb.clock import Clock

@cocotb.test()
async def test_tt_um_Richard28277(dut):
    # Clock generation
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Initialize Inputs
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.ena.value = 1
    dut.rst_n.value = 0

    # Wait for global reset and stabilization
    await Timer(50, units='ns')
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)  # Allow time for the reset to settle

    # Opcode names for display
    opcode_names = {
        0: "ADD",
        1: "SUB",
        2: "MUL",
        3: "DIV",
        4: "AND",
        5: "OR",
        6: "XOR",
        7: "NOT",
        8: "ENC"
    }

    # Helper function to display results
    def display_result(opcode):
        op_name = opcode_names.get(opcode, "UNKNOWN")
        print(f"{op_name}: result = {int(dut.uo_out.value)}, uio_out = {int(dut.uio_out.value)}")

    def alu_operation(a, b, opcode):
        if opcode == 0:  # ADD
            sum_result = (a + b) & 0x1F  # 5-bit result
            carry_out = (a + b) >> 4     # Carry-out (5th bit)
            return sum_result, carry_out
        elif opcode == 1:  # SUB
            result = a - b
            if result < 0:
                result = (result + 32) & 0x1F  # Adjust for 5-bit signed result
            return result, (result >> 4) & 1  # Return 5-bit result and borrow

        elif opcode == 2:  # MUL
            return (a * b) & 0xFF, 0
        elif opcode == 3:  # DIV
            if b != 0:
                quotient = a // b
                remainder = a % b
            else:
                quotient = 0
                remainder = 0
            return (quotient << 4) | remainder, 0
        elif opcode == 4:  # AND
            return a & b, 0
        elif opcode == 5:  # OR
            return a | b, 0
        elif opcode == 6:  # XOR
            return a ^ b, 0
        elif opcode == 7:  # NOT
            return (~a) & 0xF, 0
        elif opcode == 8:  # ENC
            combined_input = (a << 4) | b
            return (combined_input ^ 0xAB) & 0xFF, 0
        return 0, 0

    for a in range(16):
        for b in range(16):
            for opcode in range(9):
                dut.ui_in.value = (a << 4) | b
                dut.uio_in.value = opcode

                await ClockCycles(dut.clk, 2)  # Wait for 2 cycles for signals to propagate

                expected_result, expected_carry_out = alu_operation(a, b, opcode)

                display_result(opcode)

                # Check the output
                assert dut.uo_out.value == expected_result, \
                    f"Opcode {opcode_names[opcode]}: a={a}, b={b}, expected {expected_result}, got {int(dut.uo_out.value)}"

                # Check the carry-out if applicable
                if opcode in [0, 1]:  # ADD or SUB
                    assert dut.uio_out.value[6] == expected_carry_out, \
                        f"Opcode {opcode_names[opcode]}: a={a}, b={b}, expected carry_out {expected_carry_out}, got {dut.uio_out.value[6]}"

    dut._log.info("All test cases passed.")
