# stop any simulation that is currently running
quit -sim

vlib work

vcom -93 ./log2_pkg.vhd
vcom -93 ./cordic_vhdl/parts/cordic_ieee.vhd
vcom -93 ./cordic_vhdl/parts/fp_leading_zeros_and_shift.vhd
vcom -93 ./cordic_vhdl/parts/multFP.vhd
vcom -93 ./cordic_vhdl/parts/mux2_1.vhd
vcom -93 ./cordic_vhdl/parts/prueba.vhd
vcom -93 ./cordic_vhdl/parts/punto1.vhd
vcom -93 ./cordic_vhdl/parts/right_shifter.vhd
vcom -93 ./cordic_vhdl/parts/suma_resta.vhd
vcom -93 ./cordic_vhdl/cordic.vhd


vcom -93 ./log2_vhdl/parts/log2_ieee.vhd
vcom -93 ./log2_vhdl/parts/mux.vhd
vcom -93 ./log2_vhdl/parts/CLZ.vhd
vcom -93 ./log2_vhdl/parts/comparator.vhd
vcom -93 ./log2_vhdl/parts/FA.vhd
vcom -93 ./log2_vhdl/parts/left_shifter.vhd
vcom -93 ./log2_vhdl/parts/log2_luts_64x23b.vhd
vcom -93 ./log2_vhdl/parts/mult.vhd
vcom -93 ./log2_vhdl/parts/ones_complement.vhd
vcom -93 ./log2_vhdl/parts/sum_ripple_carry_adder.vhd
vcom -93 ./log2_vhdl/log2_fp.vhd

vcom -93 ./exp2_vhdl/parts/exp2_ieee.vhd
vcom -93 ./exp2_vhdl/parts/exp2_luts_64x23b.vhd
vcom -93 ./exp2_vhdl/exp2_fp.vhd

vcom -93 ./rsqrt_vhdl/rsqrt_ieee.vhd
vcom -93 ./rsqrt_vhdl/rsqrt.vhd

vcom -93 ./sfu.vhd
vcom -93 ./sfu_tb.vhd

# start the Simulator, including some libraries that may be needed
vsim work.sfu_tb
# show waveforms specified in wave.do
do wave.do
# advance the simulation the desired amount of time
run 110 ms