#!/bin/bash



./obj_dir/Vtb_sfu> stdout.txt 2> stderr.txt 

if [[ -n "$GOLDEN" ]]; then
    echo "generating golden files"
    mv output_sin.csv golden_output_sin.csv
    mv output_cos.csv golden_output_cos.csv
    mv output_rsqrt.csv golden_output_rsqrt.csv
    mv output_log2.csv golden_output_log2.csv
    mv output_ex2.csv golden_output_ex2.csv
    mv output_rcp.csv golden_output_rcp.csv
    mv output_sqrt.csv golden_output_sqrt.csv

    mv stdout.txt golden_stdout.txt
    mv stderr.txt golden_stderr.txt
fi

