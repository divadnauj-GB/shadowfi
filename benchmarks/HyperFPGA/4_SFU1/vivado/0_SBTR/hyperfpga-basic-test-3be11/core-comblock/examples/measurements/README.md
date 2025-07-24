# Measurements example

It is a design to measure the [resources utilization](utilization.md) of the ComBlock, using
several configurations in a same block design (see [../../doc/user_guide.md](#resources) for
details of each configuration).

## Instructions using Vivado

It uses the PyFPGA project. Follows [this](https://gitlab.com/rodrigomelo9/pyfpga#installation)
instructions to install it.

> As target device, the ZedBoard was used.

* Prepare the terminal to run Vivado: `<VIVADO>/settings64.sh`
* Run `make`

> It could take a while because it runs synthesis and implementation of a whole system with
> several blocks.

* The report will be in [utilization.md](utilization.md).
* Run `make clean` to delete the generated files.

> **Tip:** you can open the generated *build/vivado.xpr* file with Vivado, to see the block design
> and play with it.
