# SHADOWFI 
<div style="text-align: center;">
    <img src="./doc/SHADOWFI-logo.png" width="100" >
</div>

SHADOWFI is an emulation-based fault injection framework for fault chareacterization and reliability assesemnt of hardware designs.  SHADOWFI leverages the acceleration capabilities of hiperscale infrastructures providing support for executing long fault injection tasks in both High Performance Computing (HPC) and FPGA hiperscaler systems.

SHADOWFI implments fault instrumentation by inserting saboteur circuits directly on syntesizable HDL designs. This instrumentation is applied automatically based on user configurations, providing flexibility regarding the target components or hardware structures subject of evaluation.

SHADOWFI provides both a CLI and GUI interfaces to automate the configuration and setup of the fault injection campaigns. SHADOWFI incorporates two main workflows. The simulation workflow is mainly dedicated for executing fault injection workloads on HPC systems, whereas the emulation workflow accelerates the fault injection taks by using FPGA hiperscale systems.  

## Host System Requirements

- linux X64
- gcc >= 10
- g++ >= 10
- Clang
- llvm
- ninja-build
- Singularity >= 3.10.5
- OSS CAD Suite >= 20241117 or superior
- Anaconda / Miniconda
- Python >=3.11
- Vivado v2022.2 (For HyperFPGA binaries generation)

## Getting Started with SHADOWFI on a local machine

This guide shows the basic steps for install and use SHADOWFI. You can follow any of the following procedures.

### Instalation procedure

#### Option 1: Use a prebuild singularity container

1. Install singularity on your machine or ensure that singularity is already installed in your system. Follow the indications presented in this link [https://docs.sylabs.io/guides/3.5/user-guide/quick_start.html. ]

2. Clone the SHADOWFI repository

    ```bash
    git clone https://github.com/divadnauj-GB/shadowfi.git
    cd shadowfi
    ```

3. Download the prebuild singuarity image with all dependencies

    ```bash
    singularity pull  --arch amd64 library://divadnauj-gb/shadowfi/shadowfi:v1
    ```

4. Run SHADOWFI in CLI mode

    ```bash
    singularity run shadowfi_v1.sif
    # the following prompt will appear 
    ```

    ```bash
    "Welcome to the SHADOWFI Tool shell. Type help or ? to list commands."
    Shadowfi>
    ```

#### Option 2: Custom instalation

1. Clone the SHADOWFI repository

    ```bash
    git clone https://github.com/divadnauj-GB/shadowfi.git
    cd shadowfi
    ```

2. Download and install OSS CAD Suite, for a customize intalation you can also the guidelines introduced in <https://github.com/YosysHQ/oss-cad-suite-build>

    ```bash
    cd sif
    wget https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2024-11-17/oss-cad-suite-linux-x64-20241117.tgz
    # uncompress into the current directory
    tar -xvzf oss-cad-suite-linux-x64-20241117.tgz
    # Add environmental variables to .bashrc
    PWD = `pwd`
    echo "${PWD}/oss-cad-suite/bin" >> ~/.bashrc
    cd -
    ```

3. Create a conda environmet with all the necesary packages

    ```bash
    conda create -n SHADOWFI python=3.11
    conda activate SHADOWFI
    pip install -r requirements 
    ```

4. Run SHADOWFI in CLI mode

    ```bash
    conda activate SHADOWFI
    python shadowfi_shell.py 
    # the following prompt will appear
    "Welcome to the SHADOWFI Tool shell. Type help or ? to list commands."
    Shadowfi> 
    ```

#### Option3: Build your own singularity container

1. Clone the SHADOWFI repository

    ```bash
    git clone https://github.com/divadnauj-GB/shadowfi.git
    cd shadowfi
    ```

2. Build the singularity image:
For a different OSS CAD Suite version please modify the oss-cad-link and version on the [shadowfi.def](./sif/shadowfi.def) file

    ```bash
    # This automatically download and integrate OSS CAD on the image
    sudo singularity build shadowfi.sif ./sif/shadowfi.def
    ```

3. Run SHADOWFI in CLI mode

    ```bash
    singularty run shadowfi.sif
    # the following prompt will appear
    ```

    ```bash
    "Welcome to the SHADOWFI Tool shell. Type help or ? to list commands."
    Shadowfi> 
    ```

### Executing the first Fault Injection Campaign

The following sequence of steps illustate the interactive use of SHADOFI across a sequence of steps.

1. Run the CLI interface by typing the following command:

    ```bash
    # when using singularity run this command
    singularity run shadowfi_v1.sif

    # When not using singularity run the following commands
    conda activate SHADOWFI
    python shadowfi_shell.py
    ```

2. Create a new project:

    ```bash
    Shadowfi> create --name TCU --design-config ./config/TCU/design_config.yml
    [2025-07-25 03:51:38] INFO - Config copied to /home/test_env/shadowfi/projects/TCU/config.yaml
    Configuration saved to /home/test_env/shadowfi/projects/TCU/config.yaml
    [2025-07-25 03:51:38] INFO - Project TCU created at /home/test_env/shadowfi/projects/TCU
    Shadowfi>
    ```

3. Elaborate the project:

    ```bash
    Shadowfi> elaborate
    ...
    Warnings: 1 unique messages, 1 total
    End of script. Logfile hash: 9633524f2a, CPU: user 0.08s system 0.02s, MEM: 17.46 MB peak
    Yosys 0.47+61 (git sha1 81011ad92, clang++ 18.1.8 -fPIC -O3)
    Time spent: 48% 2x read_verilog (0 sec), 16% 2x write_json (0 sec), ...
    Hierarchy saved to hierarchy.json
    [2025-07-25 03:53:06] INFO - Elaboration completed.
    Shadowfi>
    ```

4. Configure the fault instrumentation and run saboteur placing and routing:

    ```bash
    Shadowfi> pnr --cmp-sel hierarchy --user-cmp-sel ./config/TCU/target_modules_3k.yml
    ...
    Hierarchy saved to hierarchy.json
    [2025-07-25 03:54:35] INFO - Number of target components: 1, Total bit shift: 1534
    Configuration saved to /home/test_env/shadowfi/projects/TCU/config.yaml
    [2025-07-25 03:54:35] INFO - Place and Route completed.
    Shadowfi>
    ```

5. Configure and compile the testbench simulation:

    ```bash
    Shadowfi> tb_setup --tb-config ./config/TCU/tb_config.yml
    ...
    make[1]: Leaving directory '/home/test_env/shadowfi/benchmarks/Cores/TCU/TCU_2/tb/obj_dir'
    - V e r i l a t i o n   R e p o r t: Verilator 5.031 devel rev v5.030-78-g5470cf9fa
    - Verilator: Built from 1.654 MB sources in 25 modules, into 17.552 MB in 25 C++ files needing 0.018 MB
    - Verilator: Walltime 38.198 s (elab=0.288, cvt=4.225, bld=33.160); cpu 5.488 s on 8 threads; alloced 196.203 MB
    -- DONE -------------------------------------
    [2025-07-25 03:56:47] INFO - Simulation setup for project TCU completed successfully.
    Shadowfi> 
    ```

6. Configure the fault simulation:

    ```bash
    Shadowfi> fsim_setup --fsim-config ./config/TCU/sim_config.yml --run-script ./config/TCU/run.sh --sdc-check-script ./config/TCU/sdc_check.sh
    ...
    [2025-07-25 03:58:07] INFO - Setting up fault injection for project: TCU
    Configuration saved to /home/test_env/shadowfi/projects/TCU/config.yaml
    [2025-07-25 03:58:08] INFO - Fault injection setup for project TCU completed successfully.
    Shadowfi> 
    ```

7. Run the fault injection campaign:

    ```bash
    Shadowfi> fsim_exec
    ...
    [2025-07-25 03:32:40] INFO - Running command:  bash /home/test_env/shadowfi/projects/TCU/.parsims/.job0/run.sh 
    [2025-07-25 03:32:42] INFO - Running command:  bash /home/test_env/shadowfi/projects/TCU/.parsims/.job0/sdc_check.sh 
    0,d_unit0@adder0,fpadd_3_pipe,0,1534,5,0,0,Masked

    SDC: 0, Masked: 11
    Fault simulation finished
    [2025-07-25 03:32:42] INFO - Simulation execution complete.
    Shadowfi> 
    ```

NOTE: SHADOWFI supports a basic scripting support, therefore the previous steps can be executed automatically by executing the following command:

```bash
# when using singularity run this command
singularity run shadowfi_v1.sif -s TCU.s

# When not using singularity run the following commands
conda activate SHADOWFI
python shadowfi_shell.py -s TCU.s
```

## Getting Started with HPC simulations

