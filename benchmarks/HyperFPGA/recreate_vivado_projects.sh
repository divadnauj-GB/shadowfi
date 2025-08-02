
DIR=`pwd`

PROJ_NAME="basic_test-3be11_prj"

for Bench in 1_TCU 2_SVC 3_SFU0 4_SFU1; do
#for Bench in 2_SVC 3_SFU0 4_SFU1; do
#for Bench in 1_TCU; do
    for SBTR in 0 1 ; do
        cd ./${Bench}/vivado/${SBTR}_SBTR/hyperfpga-basic-test-3be11
        # Generate the Vivado project
        # This script is used to generate the Vivado project for the HyperFPGA benchmark
        vivado -mode tcl -source recreate_project.tcl -tclargs --project_name ${PROJ_NAME}
        cd ${DIR}
        
    done

done









