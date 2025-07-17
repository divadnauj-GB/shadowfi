mkdir -p logs

#for CTO in TCU2 stereo_vision_core SFU0 SFU1; do
for CTO in stereo_vision_core; do
    SBTR_SZ=3k
    for SBTR_SZ in 3k ; do
        #rm  logs/mprofile_${SBTR_SZ}_${JOBS}_${CTO}.dat
        #mprof run -o logs/mprofile_${SBTR_SZ}_${JOBS}_${CTO}.dat -C --python python sim_emu_main.py -cfg=bench_config.yml -b=${CTO} -m=Config_files/target_modules_${SBTR_SZ}.yml -nf=1 -j=${JOBS} > logs/log_${SBTR_SZ}_${JOBS}_${CTO}.log
        #mv timestamps.json logs/timestamps_${SBTR_SZ}_${JOBS}_${CTO}.json
        #python performance_analysis.py --mprofile ./logs/mprofile_${SBTR_SZ}_${JOBS}_${CTO}.dat --timestampfile=./logs/timestamps_${SBTR_SZ}_${JOBS}_${CTO}.json --output=./logs/perf_${SBTR_SZ}_${JOBS}_${CTO}.csv  -j=${JOBS}
        #for JOBS in 1 2 4 8 10; do
        for JOBS in 8; do
            python shadowfi.py -cfg=bench_config.yml -b=${CTO} -m=Config_files/target_modules_${SBTR_SZ}.yml -nf=10 -j=${JOBS} > logs/log_${SBTR_SZ}_${JOBS}_${CTO}.log
        done
    done

done 


#python sim_emu_main.py -cfg=bench_config.yml -b=${CTO} -m=Config_files/target_modules_3k.yml -nf=1 -j=${JOBS} > logs/log_3k_${JOBS}_${CTO}.log
#python sim_emu_main.py -cfg=bench_config.yml -b=${CTO} -m=Config_files/target_modules_6k.yml -nf=1 -j=${JOBS} > logs/log_6k_${JOBS}_${CTO}.log
#python sim_emu_main.py -cfg=bench_config.yml -b=${CTO} -m=Config_files/target_modules_12k.yml -nf=1 -j=${JOBS} > logs/log_12k_${JOBS}_${CTO}.log
#python sim_emu_main.py -cfg=bench_config.yml -b=${CTO} -m=Config_files/target_modules_24k.yml -nf=1 -j=${JOBS} > logs/log_24k_${JOBS}_${CTO}.log
#python sim_emu_main.py -cfg=bench_config.yml -b=${CTO} -m=Config_files/target_modules_48k.yml -nf=1 -j=${JOBS} > logs/log_48k_${JOBS}_${CTO}.log









# time python sim_emu_main.py -p Benchmarks/Cores/core_uriscv/src_v -t riscv_core -m riscv_core -tbp Benchmarks/Cores/core_uriscv/tb/tb_core_icarus -tbt tb_top -fm SEU> log_riscv.log

# time python sim_emu_main.py -cfg bench_config.yml  -b Adder32 -m Adder32 -nf -1 > log_Adder32.log &
# time python sim_emu_main.py -cfg bench_config.yml -b boothmul -m boothmul -nf -1 > log_boothmul.log &
# time python sim_emu_main.py -cfg bench_config.yml -b posit_add -m posit_add -nf -1 > log_posit_add.log &
# time python sim_emu_main.py -cfg bench_config.yml -b posit_mult -m posit_mult -nf -1 > log_posit_mult.log &
# time python sim_emu_main.py -cfg bench_config.yml -b core_uriscv -m riscv_core -nf -1 -fm SEU > log_core_uriscv_SEU.log &
# time python sim_emu_main.py -cfg bench_config.yml -b FpInvSqrt -m FpInvSqrt -nf -1 -fm SEU > log_FpInvSqrt_SEU.log 


# time python sim_emu_main.py -cfg bench_config.yml -b FpInvSqrt -m FpInvSqrt -nf -1 > log_FpInvSqrt.log & 
#time python sim_emu_main.py -cfg bench_config.yml -b core_uriscv -m riscv_core -nf -1 > log_core_uriscv.log

#time python sim_emu_main.py -p Benchmarks/Cores/boothmul/src -t boothmul -m boothmul -tbp Benchmarks/Cores/boothmul/tb -tbt tb_boothmul > log_boothmul.log
#time python sim_emu_main.py -p Benchmarks/Cores/FpInvSqrt/src -t FpInvSqrt -m FpInvSqrt -tbp Benchmarks/Cores/FpInvSqrt/tb -tbt tb_FpInvSqrt > log_FpInvSqrt.log
#time python sim_emu_main.py -p Benchmarks/Cores/posit_add/src -t posit_add -m posit_add -tbp Benchmarks/Cores/posit_add/tb -tbt tb_posit_add > log_posit_add.log
#time python sim_emu_main.py -p Benchmarks/Cores/posit_mult/src -t posit_mult -m posit_mult -tbp Benchmarks/Cores/posit_mult/tb -tbt tb_posit_mult > log_posit_mult.log
#
#time python sim_emu_main.py -p Benchmarks/Cores/FpInvSqrt/src -t FpInvSqrt -m FpInvSqrt -tbp Benchmarks/Cores/FpInvSqrt/tb -tbt tb_FpInvSqrt -fm SEU > log_FpInvSqrt.log





#    
#    exit 0
#    # elaborate flatten rtl design
#    bash FI/sabotuer_scripts/yosys_rtl_elaboration_verilog.sh -p Benchmarks/Cores/Adder32 -t Adder32 
#    # Extract the target module and insert saboteurs
#    bash FI/sabotuer_scripts/yosys_extract_module.sh -p Benchmarks/Cores/Adder32 -t Adder32 -m Adder32  -flt 1
#    # Launch simulation
#    bash FI/sabotuer_scripts/setup_verilator_sim.sh -p Benchmarks/Cores/Adder32 -t Adder32 
#
#    cd Benchmarks/Cores/Adder32
#    time Benchmarks/Cores/Adder32/obj_dir/Vtb_Adder32
#    cd -
#
#    # elaborate flatten rtl design
#    bash FI/sabotuer_scripts/yosys_rtl_elaboration_verilog.sh -p Benchmarks/Cores/boothmul -t boothmul 
#    # Extract the target module and insert saboteurs
#    bash FI/sabotuer_scripts/yosys_extract_module.sh -p Benchmarks/Cores/boothmul -t boothmul -m boothmul -flt 1
#    # Launch simulation
#    bash FI/sabotuer_scripts/setup_verilator_sim.sh -p Benchmarks/Cores/boothmul -t boothmul 
#
#    cd Benchmarks/Cores/boothmul
#    time Benchmarks/Cores/boothmul/obj_dir/Vtb_boothmul
#    cd -
#
#    exit 0
#    # elaborate flatten rtl design
#    bash FI/sabotuer_scripts/yosys_rtl_elaboration_verilog.sh -p Benchmarks/Cores/Num_ones -t num_ones 
#    # Extract the target module and insert saboteurs
#    bash FI/sabotuer_scripts/yosys_extract_module.sh -p Benchmarks/Cores/Num_ones -t num_ones -m num_ones  -flt 1
#    # Launch simulation
#    #bash FI/sabotuer_scripts/setup_verilator_sim.sh -p Benchmarks/Cores/Num_ones -t num_ones 
#    """