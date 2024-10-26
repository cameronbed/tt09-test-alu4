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
        print(f"{op_name}: result = {dut.uo_out.value}, uio_out = {dut.uio_out.value}")

    def alu_operation(a, b, opcode):
        if opcode == 0:  # ADD
            return (a + b) & 0x1F  # 5-bit sum to include carry-out
        elif opcode == 1:  # SUB
            return (a - b) & 0x1F  # 5-bit difference to include borrow
        elif opcode == 2:  # MUL
            return (a * b) & 0xFF  # 8-bit product
        elif opcode == 3:  # DIV
            if b != 0:
                quotient = a // b
                remainder = a % b
            else:
                quotient = 0
                remainder = 0
            return (quotient << 4) | remainder  # Quotient in upper 4 bits, remainder in lower 4 bits
        elif opcode == 4:  # AND
            return a & b
        elif opcode == 5:  # OR
            return a | b
        elif opcode == 6:  # XOR
            return a ^ b
        elif opcode == 7:  # NOT
            return (~a) & 0xF  # Invert `a`, 4-bit mask
        elif opcode == 8:  # ENC
            combined_input = (a << 4) | b
            return (combined_input ^ 0xAB) & 0xFF  # Encryption example
        return 0

    for a in range(16):
        for b in range(16):
            for opcode in range(9):
                dut.ui_in.value = (a << 4) | b  # Corrected input assignment
                dut.uio_in.value = opcode

                await RisingEdge(dut.clk)  # Wait for clock edge to synchronize
                await Timer(1, units='ns')  # Small delay to allow signals to propagate

                expected_result = alu_operation(a, b, opcode)

                display_result(opcode)

                assert dut.uo_out.value == expected_result, \
                    f"Opcode {opcode_names[opcode]}: a={a}, b={b}, expected {expected_result}, got {int(dut.uo_out.value)}"

    dut._log.info("All test cases passed.")

    # Individual Test Cases

    # Test ADD operation
    a = 3
    b = 5
    dut.ui_in.value = (a << 4) | b
    dut.uio_in.value = 0b0000  # opcode = ADD
    await RisingEdge(dut.clk)
    expected_result = alu_operation(a, b, 0)
    display_result(0)
    assert dut.uo_out.value == expected_result, f"ADD failed: expected {expected_result}, got {int(dut.uo_out.value)}"

    # Test SUB operation
    a = 2
    b = 1
    dut.ui_in.value = (a << 4) | b
    dut.uio_in.value = 0b0001  # opcode = SUB
    await RisingEdge(dut.clk)
    expected_result = alu_operation(a, b, 1)
    display_result(1)
    assert dut.uo_out.value == expected_result, f"SUB failed: expected {expected_result}, got {int(dut.uo_out.value)}"

    # Test MUL operation
    a = 2
    b = 3
    dut.ui_in.value = (a << 4) | b
    dut.uio_in.value = 0b0010  # opcode = MUL
    await RisingEdge(dut.clk)
    expected_result = alu_operation(a, b, 2)
    display_result(2)
    assert dut.uo_out.value == expected_result, f"MUL failed: expected {expected_result}, got {int(dut.uo_out.value)}"

    # Test DIV operation
    a = 4
    b = 2
    dut.ui_in.value = (a << 4) | b
    dut.uio_in.value = 0b0011  # opcode = DIV
    await RisingEdge(dut.clk)
    expected_result = alu_operation(a, b, 3)
    display_result(3)
    assert dut.uo_out.value == expected_result, f"DIV failed: expected {expected_result}, got {int(dut.uo_out.value)}"

    # Test AND operation
    a = 2
    b = 2
    dut.ui_in.value = (a << 4) | b
    dut.uio_in.value = 0b0100  # opcode = AND
    await RisingEdge(dut.clk)
    expected_result = alu_operation(a, b, 4)
    display_result(4)
    assert dut.uo_out.value == expected_result, f"AND failed: expected {expected_result}, got {int(dut.uo_out.value)}"

    # Test OR operation
    a = 12
    b = 10
    dut.ui_in.value = (a << 4) | b
    dut.uio_in.value = 0b0101  # opcode = OR
    await RisingEdge(dut.clk)
    expected_result = alu_operation(a, b, 5)
    display_result(5)
    assert dut.uo_out.value == expected_result, f"OR failed: expected {expected_result}, got {int(dut.uo_out.value)}"

    # Test XOR operation
    a = 12
    b = 10
    dut.ui_in.value = (a << 4) | b
    dut.uio_in.value = 0b0110  # opcode = XOR
    await RisingEdge(dut.clk)
    expected_result = alu_operation(a, b, 6)
    display_result(6)
    assert dut.uo_out.value == expected_result, f"XOR failed: expected {expected_result}, got {int(dut.uo_out.value)}"

    # Test NOT operation
    a = 12
    dut.ui_in.value = (a << 4)  # b is ignored
    dut.uio_in.value = 0b0111  # opcode = NOT
    await RisingEdge(dut.clk)
    expected_result = alu_operation(a, 0, 7)
    display_result(7)
    assert dut.uo_out.value == expected_result, f"NOT failed: expected {expected_result}, got {int(dut.uo_out.value)}"

    # Test ENC operation
    a = 2
    b = 12
    dut.ui_in.value = (a << 4) | b
    dut.uio_in.value = 0b1000  # opcode = ENC
    await RisingEdge(dut.clk)
    expected_result = alu_operation(a, b, 8)
    display_result(8)
    assert dut.uo_out.value == expected_result, f"ENC failed: expected {expected_result}, got {int(dut.uo_out.value)}"
