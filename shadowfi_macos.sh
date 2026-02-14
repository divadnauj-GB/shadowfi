#!/bin/bash

# How to use this script:
# 1. Make sure you have Lima installed on your MacOS. You can install it using Homebrew: `brew install lima`.
# 2. Place this script in the same directory as your Singularity image (e.g., `singularity_v1.sif`) and the Lima configuration file (e.g., `singularity_ce.yml`).
# 3. Run the script with the desired arguments for your Singularity container. 
#    For example: `./shadowfi_macos.sh -s my_script.s`

check_limvm=$( limactl list | grep singularity_ce >/dev/null ; echo $?)
if [[ $check_limvm -ne 0 ]]; then
    limactl start singularity_ce.yml
    if [[ ! -f singularity_v1.sif ]]; then
        limactl shell singularity_ce singularity pull  --arch arm64 library://divadnauj-gb/shadowfi/shadowfi:v1; chmod +x shadowfi_v1.sif
        limactl stop singularity_ce
    fi
fi

limactl start singularity_ce
limactl shell singularity_ce singularity run shadowfi_v1.sif $@
limactl stop singularity_ce