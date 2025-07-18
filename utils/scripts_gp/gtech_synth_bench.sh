python FI/sabotuer_scripts/yosys_extract_module.py \
    -p=Benchmarks/Cores/stereo_vision_core \
    -lf=Benchmarks/Cores/stereo_vision_core/stereo_match.v  \
    -m=stereo_match \
    -o=yosys_synt_report \
    -fno=stereo_match_gate 

#python FI/sabotuer_scripts/yosys_extract_module.py \
#    -p=Benchmarks/Cores/boothmul/src \
#    -lf=Benchmarks/Cores/boothmul/src/boothmul.v  \
#    -m=boothmul \
#    -o=yosys_synt_report \
#    -fno=boothmul_gate
#
#python FI/sabotuer_scripts/yosys_extract_module.py \
#    -p=Benchmarks/Cores/FpInvSqrt/src \
#    -lf=Benchmarks/Cores/FpInvSqrt/src/FpInvSqrt.v  \
#    -m=FpInvSqrt \
#    -o=yosys_synt_report \
#    -fno=FpInvSqrt_gate
#
#python FI/sabotuer_scripts/yosys_extract_module.py \
#    -p=Benchmarks/Cores/posit_add/src \
#    -lf=Benchmarks/Cores/posit_add/src/posit_add.v  \
#    -m=posit_add \
#    -o=yosys_synt_report \
#    -fno=posit_add_gate
#
#python FI/sabotuer_scripts/yosys_extract_module.py \
#    -p=Benchmarks/Cores/posit_mult/src \
#    -lf=Benchmarks/Cores/posit_mult/src/posit_mult.v  \
#    -m=posit_mult \
#    -o=yosys_synt_report \
#    -fno=posit_mult_gate
#
#python FI/sabotuer_scripts/yosys_extract_module.py \
#    -p=Benchmarks/Cores/TCU/TCU_0/src \
#    -lf=Benchmarks/Cores/TCU/TCU_0/src/TCU_core.v  \
#    -m=sub_tensor_core \
#    -o=yosys_synt_report \
#    -fno=TCU_core_gate_0


python FI/sabotuer_scripts/yosys_extract_module.py \
    -p=Benchmarks/Cores/TCU/TCU_2/src \
    -lf=Benchmarks/Cores/TCU/TCU_2/src/TCU_core.v  \
    -m=sub_tensor_core \
    -o=yosys_synt_report \
    -fno=TCU_core_gate_2

#python FI/sabotuer_scripts/yosys_extract_module.py \
#    -p=Benchmarks/Cores/TCU/TCU_1/src \
#    -lf=Benchmarks/Cores/TCU/TCU_1/src/TCU_core.v  \
#    -m=sub_tensor_core \
#    -o=yosys_synt_report \
#    -fno=TCU_core_gate_1



python FI/sabotuer_scripts/yosys_extract_module.py \
    -p=Benchmarks/Cores/SFU/SFU_0/src \
    -lf=Benchmarks/Cores/SFU/SFU_0/src/sfu.v  \
    -m=sfu \
    -o=yosys_synt_report \
    -fno=sfu_0

python FI/sabotuer_scripts/yosys_extract_module.py \
    -p=Benchmarks/Cores/SFU/SFU_1/src \
    -lf=Benchmarks/Cores/SFU/SFU_1/src/sfu.v  \
    -m=sfu \
    -o=yosys_synt_report \
    -fno=sfu_1