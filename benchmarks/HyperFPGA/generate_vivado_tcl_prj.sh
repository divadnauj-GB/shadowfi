
DIR=`pwd`

for Bench in 1_TCU 2_SVC 3_SFU0 4_SFU1; do
#for Bench in 2_SVC 3_SFU0 4_SFU1; do
#for Bench in 1_TCU; do
    for SBTR in 0 1 2 4 8 16; do
        python recreate_script_generation.py --proj-dir $DIR/${Bench}/vivado/${SBTR}_SBTR/hyperfpga-basic-test-3be11 
        #rm -rf $DIR/${Bench}/vivado/${SBTR}_SBTR/hyperfpga-basic-test-3be11/basic_test-3be11_prj
    done 

done 









