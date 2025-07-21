# Simulations using CocoTB

Simulations in this directory are made using [cocotb](https://github.com/cocotb/cocotb), a COroutine based COsimulation library for writing TestBenches in Python to test VHDL or Verilog designs (`# pip install cocotb` in Linux systems).
For VHDL simulation we are using [GHDL](https://github.com/ghdl/ghdl) with [GtkWave](http://gtkwave.sourceforge.net/) as waveform viewer.

## Description

* The components used in `comblock.vhdl` are part of [FPGA Lib](https://github.com/INTI-CMNB-FPGA/fpga_lib) and have their owns testbenches there.
* Under the `comblock` directory we test the integration made in this core, with loopbacks between REGs and FIFOs.
* The files `axif.vhdl` and `axil.vhdl` were obtained with the Vivado IP packager, and are used to provides an AXI wrapper, called `axi_comblock`, which is exercised performing write and read AXI operations.

* Run a simulation with `make`
* Clean the generated files with `make clean`
* Open the waveform viewer with `make view`
