#!/bin/bash



./obj_dir/Vtb_tcu > stdout.txt 2> stderr.txt 

if [[ -n "$GOLDEN" ]]; then
    echo "generating golden files"
    mv output_dot_product.csv golden_output_dot_product.csv
    mv stdout.txt golden_stdout.txt
    mv stderr.txt golden_stderr.txt
fi