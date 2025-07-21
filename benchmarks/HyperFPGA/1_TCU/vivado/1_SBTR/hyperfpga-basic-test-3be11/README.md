# HyperFPGA Basic Test Example Project

## Cloning the basic_test_3be11 project

```bash
git clone https://gitlab.com/MBallina/hyperfpga-basic-test-3be11.git
```

```bash
cd <repository-directory>
```
The following command will initialize the submodules in this repository. (Core Comlock is a submodule of this repository)

```bash
git submodule update --init
```


## Block Designs

This is an example of a basic project using the HyperFPGA BSP. The design includes two block designs:

##  basic_test_3be11: This design contains 
- comblock_0, where the description is as follows:
    - Output registers:
        0. Loopback out
        1. Data A for addition
        2. Data B for addition
        3. Data A for multiplication
        4. Data B for multiplication
    - Input registers:
        0. Loopback input
        1. Addition result
        2. Multiplication result (LSB)
        3. Multiplication result (MSB)
    - FIFO out: 32-bit data width, 1024 depth, loopback with FIFO in.
    - Dual-port RAM: 32-bit data width, 16-bit address width, 65535 data depth. The data is written from the PL using a 16-bit counter, with each value written to each address, and it can only be read from the PS.

## basic_test_2_3be11: This design contains two components:
- comblock_0, where the description is as follows:
    - Output registers:
        0. Loopback out
        1. Data A for addition
        2. Data B for addition
        3. Data A for multiplication
        4. Data B for multiplication
    - Input registers:
        0. Loopback input
        1. Addition result
        2. Multiplication result (LSB)
        3. Multiplication result (MSB)
    - FIFO out: 32-bit data width, 1024 depth, loopback with FIFO in.
    - Dual-port RAM: 32-bit data width, 16-bit address width, 65535 data depth. The data is written from the PL using a 16-bit counter, with each value written to each address, and it can only be read from the PS.
- comblock_1, with the following description:
    - Output registers:
        0. Loopback out
    - Input registers:
        0. Loopback input
    - FIFO out: 32-bit data width, 1024 depth, loopback with FIFO in.
    - Dual-port RAM: 32-bit data width, 16-bit address width, 65535 data depth. There is no connection with any elements in the PL for writing or reading from the PS.

you can use just the block design tcl to recreate the it in vivado, remember to import the clomblock ip into vivado before run the tcl file.

## Recreate the project

There is also a tcl project script that can be used to recreate the basic_test_3be11 project, by running the following command in vivado Tcl console:

```bash
source ./basic_test-3be11_prj.tcl
```
this will create the basic_test-3be11_prj project in the current working folder, and import the clomblock ip into vivado. **All the design where created with Vivado 2022.2.** 