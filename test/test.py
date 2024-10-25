import cocotb
from cocotb.triggers import RisingEdge, Timer
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

    # Wait for global reset
    await Timer(50, units='ns')
    dut.rst_n.value = 1

    # Helper function to display results
    def display_result(op_name):
        print(f"{op_name}: result = {dut.uo_out.value}, uio_out = {dut.uio_out.value}")

    def alu_operation(a, b, opcode):
        if opcode == 0:  # ADD
            return (a + b) & 0xF  # 4-bit sum
        elif opcode == 1:  # SUB
            return (a - b) & 0xF  # 4-bit difference
        elif opcode == 2:  # MUL
            return (a * b) & 0xF  # 4-bit product
        elif opcode == 3:  # DIV
            return (a // b) if b != 0 else 0  # Division, avoid div by zero
        elif opcode == 4:  # AND
            return a & b
        elif opcode == 5:  # OR
            return a | b
        elif opcode == 6:  # XOR
            return a ^ b
        elif opcode == 7:  # NOT
            return (~a) & 0xF  # Invert `a`, 4-bit mask
        elif opcode == 8:  # ENC
            return (a ^ 0xAB) & 0xFF  # Encryption example
        return 0

    for a in range(15):
        for b in range(15):
            for opcode in range(9):
                dut.ui_in.value = (b << 4) | a
                dut.uio_in.value = opcode

                await Timer(50, units='ns')

                expected_result = alu_operation(a, b, opcode)

                display_result(opcode)

                assert dut.uo_out.value == expected_result, \
                    f"Opcode {opcode}: a={a}, b={b}, expected {expected_result}, got {dut.uo_out.value}"

    dut._log.info("All test cases passed.")

    # Test ADD operation
    dut.ui_in.value = 0b0011_0101  # a = 3, b = 5
    dut.uio_in.value = 0b0000      # opcode = ADD
    await Timer(50, units='ns')
    display_result("ADD")
    assert dut.uo_out.value == 0b0000_1000  # Expect 8 (0b00001000)

    # Test SUB operation
    dut.ui_in.value = 0b0010_0001  # a = 2, b = 1
    dut.uio_in.value = 0b0001      # opcode = SUB
    await Timer(50, units='ns')
    display_result("SUB")
    assert dut.uo_out.value == 0b0000_0001  # Expect 1 (0b00000001)

    # Test MUL operation
    dut.ui_in.value = 0b0010_0011  # a = 2, b = 3
    dut.uio_in.value = 0b0010      # opcode = MUL
    await Timer(50, units='ns')
    display_result("MUL")
    assert dut.uo_out.value == 0b0000_0110  # Expect 6 (0b00000110)

    # Test DIV operation
    dut.ui_in.value = 0b0100_0010  # a = 4, b = 2
    dut.uio_in.value = 0b0011      # opcode = DIV
    await Timer(50, units='ns')
    display_result("DIV")
    # Expect 4 and 2 (0b0000_0010 0b0000_0100)
    assert dut.uo_out.value == 0b00000010

    # Test AND operation
    dut.ui_in.value = 0b0010_0010  # a = 2, b = 2
    dut.uio_in.value = 0b0100      # opcode = AND
    await Timer(50, units='ns')
    display_result("AND")
    assert dut.uo_out.value == 0b0000_0010  # Expect 2 (0b00000010)

    # Test OR operation
    dut.ui_in.value = 0b1100_1010  # a = 12, b = 10
    dut.uio_in.value = 0b0101      # opcode = OR
    await Timer(50, units='ns')
    display_result("OR")
    assert dut.uo_out.value == 0b00001110  # Expect 14 (0b00001110)

    # Test XOR operation
    dut.ui_in.value = 0b1100_1010  # a = 12, b = 10
    dut.uio_in.value = 0b0110      # opcode = XOR
    await Timer(50, units='ns')
    display_result("XOR")
    assert dut.uo_out.value == 0b0000_0110  # Expect 6 (0b00000110)

    # Test NOT operation
    dut.ui_in.value = 0b1100_1010  # a = 12, b = ignored
    dut.uio_in.value = 0b0111      # opcode = NOT
    await Timer(50, units='ns')
    display_result("NOT")
    assert dut.uo_out.value == 0b00000011  # Expect 101 (0b00100101)

    # Test ENC operation
    dut.ui_in.value = 0b0010_1100  # a = 2, b = 12
    dut.uio_in.value = 0b1000      # opcode = ENC
    await Timer(50, units='ns')
    display_result("ENC")
    assert dut.uo_out.value == (0b0010_1100 ^ 0xAB)  # Expect encryption result with key 0xAB
