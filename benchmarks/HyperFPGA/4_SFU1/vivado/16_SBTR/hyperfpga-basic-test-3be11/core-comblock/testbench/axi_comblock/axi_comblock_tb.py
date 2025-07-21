import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, ClockCycles
from cocotb.result import TestFailure, ReturnValue

REGS_IN_BASE     = 0
REGS_OUT_BASE    = 64

#
# Test of AXIL
#

@cocotb.test()
def test01_axil(dut):
    """
    Testing the AXI Lite Interface
    """
    cocotb.fork(Clock(dut.aclk, 2).start())
    yield reset(dut)
    for i in range(16):
        yield axil_write(dut, REGS_OUT_BASE + i*4, i)
    for i in range(16):
        data = yield axil_read(dut, REGS_IN_BASE + i*4)
        do_assert(data == i, "IREG%d=%d is not the awaited value (%d)" % (i, data, i))

#
# Test of AXIF
#

@cocotb.test()
def test02_axif(dut):
    """
    Testing the AXI Full Interface
    """
    cocotb.fork(Clock(dut.aclk, 2).start())
    yield reset(dut)
    samples = 256
    for i in range(samples):
        yield axif_write(dut, i*4, i)
    for i in range(samples):
        data = yield axif_read(dut, i*4)
        do_assert(data == i, "MEM[%d]=%d is not the awaited value (%d)" % (i, data, i))

#
# Basic Operations
#

@cocotb.coroutine
def axil_write(dut, addr, value):
    dut.axil_awaddr  <= addr
    dut.axil_wdata   <= value
    dut.axil_awvalid <= 1
    dut.axil_wvalid  <= 1
    yield RisingEdge(dut.aclk)
    while (dut.axil_awready.value == 0):
        yield RisingEdge(dut.aclk)
    while (dut.axil_wready.value == 0):
        yield RisingEdge(dut.aclk)
    dut.axil_awvalid <= 0
    dut.axil_wvalid  <= 0
    yield RisingEdge(dut.aclk)

@cocotb.coroutine
def axil_read(dut, addr):
    dut.axil_araddr  <= addr
    dut.axil_arvalid <= 1
    dut.axil_rready  <= 1
    yield RisingEdge(dut.aclk)
    while (dut.axil_arready.value == 0):
        yield RisingEdge(dut.aclk)
    while (dut.axil_rvalid.value == 0):
        yield RisingEdge(dut.aclk)
    dut.axil_arvalid <= 0
    dut.axil_rready  <= 0
    data = dut.axil_rdata.value.integer
    yield RisingEdge(dut.aclk)
    raise ReturnValue(data)

@cocotb.coroutine
def axif_write(dut, addr, value):
    dut.axif_awaddr  <= addr
    dut.axif_wdata   <= value
    dut.axif_awvalid <= 1
    dut.axif_wvalid  <= 1
    while (dut.axif_awready.value == 0):
        yield RisingEdge(dut.aclk)
    while (dut.axif_wready.value == 0):
        yield RisingEdge(dut.aclk)
    dut.axif_awvalid <= 0
    dut.axif_wvalid  <= 0
    yield RisingEdge(dut.aclk)

@cocotb.coroutine
def axif_read(dut, addr):
    dut.axif_araddr  <= addr
    dut.axif_arvalid <= 1
    dut.axif_rready  <= 1
    while (dut.axif_arready.value == 0):
        yield RisingEdge(dut.aclk)
    while (dut.axif_rvalid.value == 0):
        yield RisingEdge(dut.aclk)
    dut.axif_arvalid <= 0
    dut.axif_rready  <= 0
    data = dut.axif_rdata.value.integer
    yield RisingEdge(dut.aclk)
    raise ReturnValue(data)

#
# Auxiliary functions and coroutines
#

@cocotb.coroutine
def reset(dut):
    dut.aresetn       <= 0
    dut.axil_awaddr   <= 0
    dut.axil_awvalid  <= 0
    dut.axil_wdata    <= 0
    dut.axil_wvalid   <= 0
    dut.axil_araddr   <= 0
    dut.axil_arvalid  <= 0
    dut.axil_rready   <= 0
    dut.axif_awaddr   <= 0
    dut.axif_awvalid  <= 0
    dut.axif_wdata    <= 0
    dut.axif_wvalid   <= 0
    dut.axif_araddr   <= 0
    dut.axif_arvalid  <= 0
    dut.axif_rready   <= 0
    yield ClockCycles(dut.aclk, 3)
    dut.aresetn       <= 1
    yield RisingEdge(dut.aclk)
    dut._log.info("Reset complete")

def do_assert(cond, msg):
    if not cond:
       print(msg)
