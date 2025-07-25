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

## Getting Statarted with SHADOWFI on a local machine
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
Welcome to the SHADOWFI Tool shell. Type help or ? to list commands.
Shadowfi>
```

#### Option 2: Custom instalation
1. Clone the SHADOWFI repository

```bash
git clone https://github.com/divadnauj-GB/shadowfi.git
cd shadowfi
```
2. Download and install OSS CAD Suite, for a customize intalation you can also the guidelines introduced in https://github.com/YosysHQ/oss-cad-suite-build

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
Welcome to the SHADOWFI Tool shell. Type help or ? to list commands.
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

