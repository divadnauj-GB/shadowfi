
rm -rf logs_hdl_elab
mkdir -p logs_hdl_elab


CTO=TCU
time mprof run -o logs_hdl_elab/mprofile_${CTO}.dat -C --python python FI/sabotuer_scripts/yosys_vhdl2verilog.py \
    -p=Benchmarks/Cores/TCU/TCU_2/src \
    -t=sub_tensor_core \
    -o=logs_hdl_elab/${CTO} \
    -ghdl="-fsynopsys" \
    -fno=sub_tensor_core.v > logs_hdl_elab/log_${CTO}.log

CTO=SFUv1
time mprof run -o logs_hdl_elab/mprofile_${CTO}.dat -C --python python FI/sabotuer_scripts/yosys_vhdl2verilog.py \
    -p=Benchmarks/Cores/SFU/SFU_0/src \
    -t=sfu \
    -o=logs_hdl_elab/${CTO} \
    -fno=sfu.v > logs_hdl_elab/log_${CTO}.log

CTO=SFUv2
time mprof run -o logs_hdl_elab/mprofile_${CTO}.dat -C --python python FI/sabotuer_scripts/yosys_vhdl2verilog.py \
    -p=Benchmarks/Cores/SFU/SFU_0/src \
    -t=sfu \
    -o=logs_hdl_elab/${CTO} \
    -fno=sfu.v > logs_hdl_elab/log_${CTO}.log

CTO=SVC
time mprof run -o logs_hdl_elab/mprofile_${CTO}.dat -C --python python FI/sabotuer_scripts/yosys_vhdl2verilog.py \
    -p=Benchmarks/Cores/stereo_vision_core/Stereo_Match_VHDL \
    -t=stereo_match \
    -par D=64 Wc=7 Wh=13 M=450 N=8 \
    -o=logs_hdl_elab/${CTO} \
    -fno=stereo_match.v > logs_hdl_elab/log_${CTO}.log
