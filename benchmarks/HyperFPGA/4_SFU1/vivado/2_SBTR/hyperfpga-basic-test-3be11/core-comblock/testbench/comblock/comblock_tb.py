import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb.result import TestFailure, ReturnValue

IREGS_BASE       = 0
OREGS_BASE       = 16

IFIFO_VALUE      = 32
IFIFO_CONTROL    = 33
IFIFO_STATUS     = 34
OFIFO_VALUE      = 36
OFIFO_CONTROL    = 37
OFIFO_STATUS     = 38

MASK_FLAGS       = 0x7
MASK_COUNTER     = 0xFFFF0000

#
# Test of the REGs
#

@cocotb.test()
def test01_regs(dut):
    """
    Testing REGs
    """
    cocotb.fork(Clock(dut.clk_i, 2).start())
    yield reset(dut)
    yield write_reg_bulk(dut,OREGS_BASE,0)
    yield  read_reg_bulk(dut,IREGS_BASE, 0)
    yield write_reg_bulk(dut,OREGS_BASE,9)
    yield  read_reg_bulk(dut,IREGS_BASE, 9)
    yield  read_reg_bulk(dut,OREGS_BASE,9)

@cocotb.coroutine
def write_reg_bulk(dut, from_reg, start_value):
    dut._log.info("Writing from REG %d to %d" % (from_reg, from_reg+15))
    for i in range(from_reg,from_reg+16):
        yield write_reg(dut, i, start_value)
        start_value += 1

@cocotb.coroutine
def read_reg_bulk(dut, from_reg, start_value):
    dut._log.info("Reading from REG %d to %d" % (from_reg, from_reg+15))
    for i in range(from_reg,from_reg+16):
        data = yield read_reg(dut, i)
        do_assert(data == start_value, "REG(%d)=%d is not the awaited (%d)" % (i, data, start_value))
        start_value += 1

#
# Test of the DRAM
#

@cocotb.test()
def test02_dram(dut):
    """
    Testing DRAM
    """
    cocotb.fork(Clock(dut.clk_i, 2).start())
    yield reset(dut)
    samples = 256
    dut._log.info("Writing")
    for i in range(0,samples):
        yield write_ram(dut, i, i)
    dut._log.info("Reading")
    dut.mem_addr_i <= 0
    yield RisingEdge(dut.clk_i)
    for i in range(1,samples):
        data = yield read_ram(dut, i)
        do_assert(data == i-1, "DRAM=%d is not the awaited (%d)" % (data, i-1))
    yield RisingEdge(dut.clk_i)
    do_assert(dut.mem_data_o == i, "DRAM=%d is not the awaited (%d)" % (dut.mem_data_o, i))

#
# Test of the FIFOs
#

@cocotb.test()
def test03_fifo_data(dut):
    """
    Testing FIFOs data transfer
    """
    cocotb.fork(Clock(dut.clk_i, 2).start())
    yield reset(dut)
    samples = 256 # TODO: 300
    dut._log.info("* Writing to FIFO OUT")
    for i in range(samples):
        yield write_reg(dut, OFIFO_VALUE, i)
    dut._log.info("* Reading from FIFO IN")
    for i in range(samples):
        data = yield read_reg(dut, IFIFO_VALUE)
        do_assert(data == i, "FIFO value %d is not the awaited (%d)" % (i, data))

@cocotb.test()
def test04_fifo_signaling(dut):
    """
    Testing FIFOs signaling
    """
    cocotb.fork(Clock(dut.clk_i, 2).start())
    yield reset(dut)
    #
    dut._log.info("* Checking initial states")
    status = yield read_reg(dut, OFIFO_STATUS, MASK_FLAGS)
    do_assert(status == 0, "OFIFO_STATUS = %s" % status)
    status  = yield read_reg(dut, IFIFO_STATUS, MASK_FLAGS)
    do_assert(status == 3, "IFIFO_STATUS = %s" % status)
    #
    dut._log.info("* Writing")
    status = yield read_reg(dut, OFIFO_STATUS, MASK_FLAGS)
    while (status == 0):
        yield write_reg(dut, OFIFO_VALUE, 0xCAFE)
        status = yield read_reg(dut, OFIFO_STATUS, MASK_FLAGS)
    dut._log.info("  * Checking Almost Full")
    do_assert(status == 2, "OFIFO_STATUS = %s" % (status))
    dut._log.info("  * Checking Full")
    yield write_reg(dut, OFIFO_VALUE, 0xAAAA)
    status = yield read_reg(dut, OFIFO_STATUS, MASK_FLAGS)
    do_assert(status == 3, "OFIFO_STATUS = %s" % (status))
    dut._log.info("  * Checking Overflow")
    yield write_reg(dut, OFIFO_VALUE, 0x5555)
    status = yield read_reg(dut, OFIFO_STATUS, MASK_FLAGS)
    do_assert(status == 7, "OFIFO_STATUS = %s" % (status))
    #
    dut._log.info("* Reading")
    status = yield read_reg(dut, IFIFO_STATUS, MASK_FLAGS)
    while (status == 0):
        data = yield read_reg(dut, IFIFO_VALUE)
        status = yield read_reg(dut, IFIFO_STATUS, MASK_FLAGS)
    dut._log.info("  * Checking Almost Empty")
    do_assert(status == 2, "IFIFO_STATUS = %s" % (status))
    dut._log.info("  * Checking Empty")
    data = yield read_reg(dut, IFIFO_VALUE)
    status = yield read_reg(dut, IFIFO_STATUS, MASK_FLAGS)
    do_assert(status == 3, "IFIFO_STATUS = %s" % (status))
    dut._log.info("  * Checking Underflow")
    data = yield read_reg(dut, IFIFO_VALUE)
    status = yield read_reg(dut, IFIFO_STATUS, MASK_FLAGS)
    do_assert(status == 7, "IFIFO_STATUS = %s" % (status))

@cocotb.test()
def test05_fifo_others(dut):
    """
    Testing FIFOs counters and clean
    """
    cocotb.fork(Clock(dut.clk_i, 2).start())
    yield reset(dut)
    samples = 256
    dut._log.info("* Checking status at the begining")
    status = yield read_reg(dut, OFIFO_STATUS)
    do_assert(status == 0, "OFIFO_STATUS = %s" % status)
    status = yield read_reg(dut, IFIFO_STATUS)
    do_assert(status == 3, "IFIFO_STATUS = %s" % status)
    dut._log.info("* Filling the FIFOs")
    status = yield read_reg(dut, OFIFO_STATUS, MASK_FLAGS)
    while (status < 7):
        yield write_reg(dut, OFIFO_VALUE, 0xAAAA)
        status = yield read_reg(dut, OFIFO_STATUS, MASK_FLAGS)
    yield ClockCycles(dut.clk_i, 10)
    dut._log.info("* Checking counters before clean")
    status = yield read_reg(dut, OFIFO_STATUS, MASK_COUNTER)
    status = status >> 16
    do_assert(status == samples, "OFIFO_STATUS = %s" % status)
    status = yield read_reg(dut, IFIFO_STATUS, MASK_COUNTER)
    status = status >> 16
    do_assert(status == samples, "IFIFO_STATUS = %s" % status)
    yield write_reg(dut, OFIFO_CONTROL,1)
    yield write_reg(dut, IFIFO_CONTROL,1)
    yield RisingEdge(dut.clk_i) # TODO: remove
    dut._log.info("* Checking counters after clean")
    status = yield read_reg(dut, OFIFO_STATUS)
    do_assert(status == 0, "OFIFO_STATUS = %s" % status)
    status = yield read_reg(dut, IFIFO_STATUS)
    do_assert(status == 3, "IFIFO_STATUS = %s" % status)

#
# Basic Operations
#

@cocotb.coroutine
def write_reg(dut, addr, value):
    dut.reg_wr_ena_i  <= 1
    dut.reg_wr_addr_i <= addr
    dut.reg_wr_data_i <= value
    yield RisingEdge(dut.clk_i)
    dut.reg_wr_ena_i <= 0

@cocotb.coroutine
def read_reg(dut, addr, mask=0xFFFFFFFF):
    dut.reg_rd_addr_i <= addr
    yield RisingEdge(dut.clk_i)
    dut.reg_rd_ena_i  <= 1
    yield RisingEdge(dut.clk_i)
    dut.reg_rd_ena_i  <= 0
    raise ReturnValue(dut.reg_rd_data_o.value.integer & mask)

@cocotb.coroutine
def write_ram(dut, addr, value):
    dut.mem_we_i   <= 1
    dut.mem_addr_i <= addr
    dut.mem_data_i <= value
    yield RisingEdge(dut.clk_i)
    dut.mem_we_i   <= 0

@cocotb.coroutine
def read_ram(dut, addr):
    dut.mem_addr_i <= addr
    yield RisingEdge(dut.clk_i)
    raise ReturnValue(dut.mem_data_o.value.integer)

#
# Auxiliary functions and coroutines
#

@cocotb.coroutine
def reset(dut):
    dut.reg_wr_ena_i  <= 0
    dut.reg_wr_data_i <= 0
    dut.reg_wr_addr_i <= 0
    dut.reg_rd_ena_i  <= 0
    dut.reg_rd_addr_i <= 0
    dut.mem_we_i      <= 0
    dut.mem_addr_i    <= 0
    dut.mem_data_i    <= 0
    dut.rst_i         <= 1
    yield ClockCycles(dut.clk_i, 3)
    dut.rst_i         <= 0
    yield RisingEdge(dut.clk_i)
    dut._log.info("Reset complete")

def do_assert(cond, msg):
    if not cond:
       raise TestFailure(msg)
