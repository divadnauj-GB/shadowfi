TOP       := sub_tensor_core
RTL       := TCU_core.v
TB        := tb_sub_tensor_core.cpp
OBJDIR    := obj_dir
BIN       := sim_$(TOP)

VERILATOR ?= verilator
CXXFLAGS  := -O2 -std=c++17

all: build

build:
	$(VERILATOR) \
		--cc $(RTL) \
		--top-module $(TOP) \
		--exe $(TB) \
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
