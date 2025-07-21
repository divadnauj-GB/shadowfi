# Tutorial: ComBlock in Vivado

![Tool](https://img.shields.io/badge/Tool-Vitis&nbsp;2020.2-blue.svg)
![Board](https://img.shields.io/badge/Board-ZedBoard-green.svg)
![Creative Commons Attribution 4.0 International Logo](https://i.creativecommons.org/l/by/4.0/80x15.png)

Previous to the version 2019.2, it was enough to download Vivado to have also the Software
Development Kit (SDK).
From version 2019.2, you must download Vitis, which also installs Vivado.

The tutorial is organized as follows:
* [Vivado](#vivado)
* [Vitis (Vivado 2019.2 and later)](#vitis-vivado-20192-and-later)
* [SDK (Vivado 2019.1 and earlier)](#sdk-vivado-20191-and-earlier)

# Vivado

## Step 1 - Create a new project

Open Vivado and select *Create Project* to launch the *New Project* wizard.

![Create a New Project](vivado/tuto/1-1.png)

Select *Project name* and *Project location*, then **Next**.

![Project Name](vivado/tuto/1-2.png)

Select *RTL Project* and check *Do not specify sources at this time*.
Press **Next**.

![Project Type](vivado/tuto/1-3.png)

In the *Default Part* screen, select the *Boards* tab, choose the *ZedBoard*
and press **Next**.

![Default Part](vivado/tuto/1-4.png)

Press **Finish** in the *New Project Summary* screen.

![Summary](vivado/tuto/1-5.png)

## Step 2 - Include the ComBlock

To add the *ComBlock* to the *IP Repository*, go to *Settings* -> *IP* -> *Repository*.
Click on `+` and browse to `core_comblock/src`.
Pree *Select*.

![IP repositories](vivado/tuto/2-1.png)

One IP (the *ComBlock*) and five interfaces must be found.
Press **Ok** to confirm.

![Add Repository](vivado/tuto/2-2.png)

Click on *Create Block Design* and accept the default *Design name* pressing **Ok**.

![Create Block Design](vivado/tuto/2-3.png)

Press `+` to search the *ComBlock* (you can use the *search* file to filter results).

![Adding the ComBlock](vivado/tuto/2-4.png)

Select the *ComBlock* and it will appear as a component in the *Diagram* tab.

![The ComBlock Component](vivado/tuto/2-5.png)

## Step 3 - Include the PS

Here we will add the *Processor System*.
Press `+` and search *zynq* to include *ZYNQ7 Processing System*.

![Adding the PS](vivado/tuto/3-1.png)

A green line (*Designer Assistance*) will appear. Select *Run Block Automation*.

![Default PS](vivado/tuto/3-2.png)

Be sure to check *Apply Board Preset*.

![Run Block Automation](vivado/tuto/3-3.png)

Press **Ok**. You will see that *Run Block Automation* disappeared.

![Default PS for the ZedBoard](vivado/tuto/3-4.png)

Double click in the Zynq Component to *Re-customize IP*.
Go to *Peripheral I/O Pins* and uncheck *TTC0*.

![Re-customize PS](vivado/tuto/3-5.png)

Then press **Ok**.

![Used PS for the ZedBoard](vivado/tuto/3-6.png)

Select *Run Connection Automation*, then press **Ok**.

![Connection Automation](vivado/tuto/3-7.png)

You will have a *block design* as follows:

![Partial Block Design 1](vivado/tuto/3-8.png)

## Step 4 - Final design

Go to *Add Sources* and select *Add or create design sources*.

![Add or create sources](vivado/tuto/4-1.png)

Press `+` or *Add Files*.

![Add sources](vivado/tuto/4-2.png)

Browse to `core_comblock/src/helpers` and select `fifo_loop.vhdl`.

![Select fifo_loop.vhdl](vivado/tuto/4-3.png)

Press **Finish**.

![Add Sources Summary](vivado/tuto/4-4.png)

Go to the *Sources* panel -> *Design Sources*, right-click over `fifo_loop.vhdl`
and select *Add Module to Block Design*.

![Add Module](vivado/tuto/4-5.png)

You will have a *block design* as follows:

![Partial Block Design 2](vivado/tuto/4-6.png)

## Step 5 - ComBlock connections

Double click over the *ComBlock* component.
Select 16 input and output registers.
Enable the FIFO output.

![Re-customize the ComBlock](vivado/tuto/5-1.png)

Connect *reg0_o* to *reg15_i*, *reg1_o* to *reg14_i* and so on.

![Interconnect the registers](vivado/tuto/5-2.png)

Interconnect the `fifo_loop` with the *ComBlock as follows:

![Connect the FIFO Loop](vivado/tuto/5-3.png)

You will have a *block design* as follows:

![Final Block Design](vivado/tuto/5-4.png)

Optionally, you can select the *Processing System*, the *PS Reset* and
the *AXI SmartConnect*, right-click and create a *Hierarchy*, to have
a simpler *block design*, as follows:

![Final Block Design with Hierarchy](vivado/tuto/5-5.png)

## Step 6 - Generate the Bitstream

Run *Validate Design*.

![Validate the Design](vivado/tuto/6-1.png)

Go to *Sources* panel, rigth-click over the *block design* name and select
*Create HDL Wrapper*.
Choose *Let Vivado manage wrapper and auto-update* and press **Ok**.

![Create HDL Wrapper](vivado/tuto/6-2.png)

Go to *Flow Navigator* -> *Program and Debug* and select *Generate Bitstream*,
then press **Ok**.

![Launch Runs](vivado/tuto/6-3.png)

When *Bitstream Generation Completed* appeared, press *Cancel*.

![Bitstream Generation Completed](vivado/tuto/6-4.png)

From here, you need to choose how to follows according to the suite version.

* [Vitis (Vivado 2019.2 and later)](#vitis-vivado-20192-and-later)
* [SDK (Vivado 2019.1 and earlier)](#sdk-vivado-20191-and-earlier)


# Vitis (Vivado 2019.2 and later)

Go to *File* -> *Export* -> *Export Hardware*, check *Include bitstream* and press **Ok**.

![Export Hardware](vivado/tuto/7-1.png)

*Export Hardware for Vitis (2019.2 and later)*

To launch Vitis from Vivado, go to *Tools* -> *Launch Vitis*.

## Step 7 - Launching Vitis

![Vitis IDE](vivado/tuto/20-1.png)

After the *Splash Screen*, you must select a workspace.

![Select workspace](vivado/tuto/20-2.png)

Select one and press *Launch* to reach the *Welcome Screen*.

![Welcome](vivado/tuto/20-3.png)

Select *Create Application Project*.

## Step 8 - Project Creation

Choose a *Project name* and press **Next**.

![New Application Project](vivado/tuto/21-1.png)

Go to the Tab *Create a new platform from hardware (xsa)* and press the `+` button.

![Platform](vivado/tuto/21-2.png)

Browse to your project directory and select the previously exported XSA.
Press the **OK** button and then **Next**.

![Select XSA](vivado/tuto/21-3.png)

Select *OS* and *Language* (the default options, *standalone* and *C*, for this example).
Press **Next**.

![Domain](vivado/tuto/21-4.png)

Select a *Template* (*Hello World* for this example) and press **Finish**.

![Templates](vivado/tuto/21-5.png)

You will reach the Vitis Project Screen.

![Vitis Project Screen](vivado/tuto/21-6.png)

## Step 9 - Working with Vitis

Go to *Xilinx* -> *Program FPGA* and transfer the selected bitstream.

![Program FPGA](vivado/tuto/22-1.png)

Select the System Project (*tutorial_example* in our case), right-click and select
*Build Project* to launch the compilation.

![Build Project](vivado/tuto/22-2.png)

Go to *Open Console* -> *Command Sheel Console* and configure the Serial Terminal
(or use your favourite terminal).

![Config the Serial Terminal 1](vivado/tuto/22-3.png)

![Config the Serial Terminal 2](vivado/tuto/22-4.png)
![Config the Serial Terminal 3](vivado/tuto/22-5.png)

Select the System Project, *right-click* and select *Run As* -> *1 Launch on Hardware*.

![Run As](vivado/tuto/22-6.png)

Go to *Display Selected Console* and select your previously configured terminal
(or check your terminal output).

![Execution Output](vivado/tuto/22-7.png)

From here, you can change `helloworld.c` (*tutorial_system* -> *tutorial* -> *src*) (for example
with code from [this](../examples/test/test.c) example), Build the Project and Run again.


# SDK (Vivado 2019.1 and earlier)

Go to *File* -> *Export* -> *Export Hardware*, check *Include bitstream* and press **Ok**.

![Export Hardware](vivado/tuto/6-6.png)

*Export Hardware for SDK (2019.1 and earlier)*

To launch SDK from Vivado, go to *File* -> *Launch SDK*.

## Step 7 - Launching SDK

![SDK IDE](vivado/tuto/10-1.png)

After the *Splash Screen*, you will reach the following screen.

![Main SDK](vivado/tuto/10-2.png)

Go to *File* -> *New* -> *Application Project*.

## Step 8 - Project Creation

Choose a *Project name*.
Select *OS* and *Language* (the default options, *standalone* and *C*, for this example).
Press **Next**.

![New Application Project](vivado/tuto/11-1.png)

Select a *Template* (*Hello World* for this example) and press **Finish**.

![Templates](vivado/tuto/11-2.png)

## Step 9 - Working with SDK

Go to *Xilinx* -> *Program FPGA* and transfer the selected bitstream.

![Program FPGA](vivado/tuto/12-1.png)

Go to *SDK Terminal* -> `+` and configure the Serial Terminal
(or use your favourite terminal).

![Config the Serial Terminal](vivado/tuto/12-2.png)

Select the Appliation Project (*tutorial* in our case), right-click and
select *Run As* -> *1 Launch on Hardware*.

![Run As](vivado/tuto/12-3.png)

Go to *SDK Terminal* (or check your terminal output) and see the result.

![Execution Output](vivado/tuto/12-4.png)

From here, you can change `helloworld.c` (*tutorial* -> *src*) (for example with code
from [this](../examples/test/test.c) example), and Run again.
