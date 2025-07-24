onerror {resume}
quietly WaveActivateNextPane {} 0

radix define iee754s_fp -float -fraction 23 -base decimal -precision 10

set SFUS 1

add wave -noupdate -label CLK /sfu_tb/s_clk_i
add wave -noupdate -label RST /sfu_tb/s_rst_n
add wave -noupdate -label START /sfu_tb/s_start_i
add wave -noupdate -label DATA_IN -radix iee754s_fp /sfu_tb/s_src1_i
add wave -noupdate -label OPER /sfu_tb/s_selop_i
add wave -noupdate -label RESULT -radix iee754s_fp /sfu_tb/s_Result_o
add wave -noupdate -label STALL /sfu_tb/s_stall_o

add wave -noupdate -group SFU_PROC /sfu_tb/DUT/*

add wave -noupdate -group cordic /sfu_tb/DUT/Cordic_inst/*
add wave -noupdate -group rsqrt /sfu_tb/DUT/rsqrt_ints/*
add wave -noupdate -group log2 /sfu_tb/DUT/log2_inst/*
add wave -noupdate -group exp2 /sfu_tb/DUT/exp2_inst/*

add wave -noupdate -group lg2_shift /sfu_tb/DUT/log2_inst/shifter/*
add wave -noupdate -group lg2_clz /sfu_tb/DUT/log2_inst/leading_zeros/*


TreeUpdate [SetDefaultTree]
WaveRestoreCursors {{Cursor 1} {80000 ps} 0}
quietly wave cursor active 1
configure wave -namecolwidth 76
configure wave -valuecolwidth 49
configure wave -justifyvalue left
configure wave -signalnamewidth 0
configure wave -snapdistance 10
configure wave -datasetprefix 0
configure wave -rowmargin 4
configure wave -childrowmargin 2
configure wave -gridoffset 0
configure wave -gridperiod 1
configure wave -griddelta 40
configure wave -timeline 0
configure wave -timelineunits ns
update
WaveRestoreZoom {0 ps} {180 ns}
