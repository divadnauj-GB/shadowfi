
DIR=`pwd`

for Bench in 1_TCU 2_SVC 3_SFU0 4_SFU1; do
#for Bench in 2_SVC 3_SFU0 4_SFU1; do
#for Bench in 1_TCU; do
    for SBTR in 0 1 2 4 8 16; do
        cd ./${Bench}/vivado/${SBTR}_SBTR/hyperfpga-basic-test-3be11
        # Generate the Vivado project
        # This script is used to generate the Vivado project for the HyperFPGA benchmark
        vivado -mode tcl -source ../../../../generate_project_tcl.tcl
        
        F="/basic_test-3be11_prj/basic_test-3be11_prj.srcs/utils_1/imports/"
        R="/"
        sed -i "s!${F}!${R}!g" ./recreate_project.tcl

        F="/home/juancho/Documents/GitHub/EmuFaultSim/BenchpyRTLFIv1/Benchmarks/HyperFPGA/${Bench}/vivado/${SBTR}_SBTR/hyperfpga-basic-test-3be11/"
        R="./"
        sed -i "s!${F}!${R}!g" ./recreate_project.tcl
        
        rm -rf basic_test-3be11_prj
        rm -rf .Xil
        rm -rf .Xiltemp
        rm -rf .git
        rm *.log
        rm *.jou
        rm *.txt
        rm *.pdf
        rm *.str
        rm -f ./core-comblock/.git
        cd ${DIR}
        
        
    done 

done 









