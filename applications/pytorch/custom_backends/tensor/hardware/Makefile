TOP       := sub_tensor_core
RTL       := TCU_core.v
OBJDIR    := obj_dir
BIN       := sim_$(TOP)
ROOT      := $(CURDIR)

VERILATOR ?= verilator
CXXFLAGS  := -O2 -std=c++17 -I$(ROOT)/include

TB_SRCS := \
	tb_main.cpp \
	src/tcu_utils.cpp \
	src/tcu_reference.cpp \
	src/tcu_driver.cpp \
	src/tcu_tiled.cpp

all: build

build:
	$(VERILATOR) \
		--cc $(RTL) \
		--top-module $(TOP) \
		--exe $(TB_SRCS) \
		--build \
		-Wno-fatal \
		-Wno-WIDTHTRUNC \
		-Wno-CASEOVERLAP \
		-CFLAGS "$(CXXFLAGS)" \
		-o $(BIN)

run: build
	./$(OBJDIR)/$(BIN)

clean:
	rm -rf $(OBJDIR) *.vcd

.PHONY: all build run clean
