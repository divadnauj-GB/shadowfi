PWD=$(shell pwd)

export COCOTB_REDUCED_LOG_FMT=1

COMBLOCK_SOURCES = graysync.vhdl tdpram.vhdl fifo.vhdl comblock.vhdl
VHDL_SOURCES     = $(addprefix $(PWD)/../../src/comblock/hdl/,$(COMBLOCK_SOURCES)) $(PWD)/../../src/helpers/fifo_loop.vhdl $(PWD)/comblock_top.vhdl

TOPLEVEL  = comblock_top
MODULE    = comblock_tb

SIM       = ghdl
SIM_FILE  = $(SIM_BUILD)/comblock.ghw
SIM_ARGS  = --wave=$(SIM_FILE) --ieee-asserts=disable-at-0
SIM_BUILD = build

include $(shell cocotb-config --makefiles)/Makefile.sim

view:
	gtkwave $(SIM_FILE)

clean::
	@rm -fr *.pyc
