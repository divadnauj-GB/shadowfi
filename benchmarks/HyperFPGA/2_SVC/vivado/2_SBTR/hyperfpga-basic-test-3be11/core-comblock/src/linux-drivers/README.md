# ComBlock Linux Driver

This is intended to be used with any ComBlock that is appropriately instantiated in the device tree overlay.
The corresponding entry is as follows:

``` C
&comblock_0 {
    REGS_IN_ENA = <1>;
    REGS_IN_DWIDTH = <32>;
    REGS_IN_DEPTH = <4>;
    REGS_OUT_ENA = <1>;
    REGS_OUT_DWIDTH = <32>;
    REGS_OUT_DEPTH = <4>;
    DRAM_IO_ENA = <0>;
    DRAM_IO_DWIDTH = <16>;
    DRAM_IO_DEPTH = <0>;
    FIFO_IN_ENA = <0>;
    FIFO_IN_DWIDTH = <16>;
    FIFO_IN_DEPTH = <1024>;
    FIFO_OUT_ENA = <0>;
    FIFO_OUT_DWIDTH = <16>;
    FIFO_OUT_DEPTH = <1024>;
};
```

With all these fields, the driver will be able to correctly instantiate the ComBlock devices.
Alternatively, one can use the [XSA2Bit](https://gitlab.com/ictp-mlab/xsa2bit) tool to automatically generate and compile the bitstream and device tree overlay.

One device entry is created per memory, resulting in the following naming convention under the ```/dev/``` folder:

| ComBlock resource | ComBlock device name |
|-|-|
| Input registers   | ComBlock_N_regs_i      |
| Output registers  | ComBlock_N_regs_o      |
| Input FIFO        | ComBlock_N_fifo_i      |
| Output FIFO       | ComBlock_N_fifo_o      |
| DRAM              | ComBlock_N_ram      |

Where the  ```N``` stands for the ComBlock index starting from 0 up to ```N-1``` ComBlocks.

## Compilation

To compile the driver you should create a new Petalinux project using your ```XSA```:

```bash
petalinux-create -t project -n my_cool_project --template <zynqmp/zynq>
cd my_cool_project/
petalinux-config --get-hw-description <...my_cool_platform.xsa>
```

At this point a configuration window will open where you can select the parameters tu customize your Linux.
When you are done, close it and proceed to create a module.

```bash
petalinux-create -t modules -n comblock --enable
```

This will create a folder inside your project at ```my_cool_project/project-spec/meta-user/recipes-modules/comblock/```.
Here you have to copy the source files under the ```files/``` subfolder.

Now you need to add your files into the ```bitbake``` compilation path you have to edit the ```my_cool_project/project-spec/meta-user/recipes-modules/comblock/comblock.bb``` file with editing the ```SRC_URI``` entry as follows:

```c
SRC_URI =  "file://Makefile \
            file://comblock.h \
            file://comblock_driver.c \
            file://comblock_calls.c \
            file://COPYING \
          "
```

Now compile your Petalinux project.

```bash
petalinux-build 
```

You will find the ```comblock.ko``` file in side your project, in the following directory: ```build/tmp/work/<platform name>-xilinx-linux/comblock/1.0-r0```

> With a compiled project you can compile only the module by running:

```bash
petalinux-build -c comblock -x compile
```

## Usage

The character devices created by the ComBlock driver are readable or writable, depending on the direction, as any other file.
In ```C``` one would open a ComBlock device as follows:

```C
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int main() {
    int dev_o = open("/dev/ComBlock_0_regs_o", O_WRONLY);
    int dev_i = open("/dev/ComBlock_0_regs_i", O_RDONLY);
    // At this point dev_o and dev_i are accessible for lseek, read, or write
}
```

Similarly, when working with Python:

``` Python
import os

dev_o = os.fdopen(os.open('/dev/ComBlock_0_regs_o', os.O_WRONLY), "bw", buffering = 0)
dev_i = os.fdopen(os.open('/dev/ComBlock_0_regs_i', os.O_RDONLY), "br", buffering = 0) 
```

In the case of Python it is recommended to use [context managers](https://docs.python.org/3/library/contextlib.html) to avoid unsafe releases.

Each of the resources supports different kind of operations, here is the detailed list:

* DRAM
  * read
  * write
  * llseek

* Input FIFO
  * read
  * llseek

* Output FIFO
  * write
  * llseek

* Input registers
  * read
  * llseek

* Output registers
  * write
  * llseek

In the next sections I will show the peculiarities of each operation.

### Reading and writing registers

Output registers are separated in different devices.

For ```C```:

``` C
// open the device
int dev_o = open("/dev/ComBlock_0_regs_o", O_WRONLY);
int dev_i = open("/dev/ComBlock_0_regs_i", O_RDONLY);
char buf_o[4]="abc";
char buf_i[4];

// set cursor at register 1 for dev_o
lseek(dev_o, 4, 0);

//write to the device
write(dev_o, &buf_o, 4);

// set cursor at register 2 for dev_i
lseek(dev_i, 16, 0);

// read from the device
read(dev_i, &buf_i, 4)
```

For ```Python```:

```Python
test = bytes(b'\xDE\xAD\xBE\xEF')

with os.fdopen(os.open('/dev/ComBlock_0_regs_i', os.O_RDONLY), "br", buffering = 0) as reg_in, os.fdopen(os.open('/dev/ComBlock_0_regs_o', os.O_WRONLY), "bw", buffering = 0) as reg_out:
    # set cursor at register 0
    reg_out.seek(0,0)
    reg_out.write(test)
    # set cursor at register 0
    reg_in.seek(0,0)
    print(reg_in.read(4))
    # set cursor at register 1
    reg_out.seek(4,0)
    reg_out.write(test1)
    # set cursor at register 1
    reg_in.seek(4,0)
    print(reg_in.read(4))
```

### FIFOs

For ```C```:

```C
// open the device
int dev_o = open("/dev/ComBlock_0_fifo_o", O_WRONLY);
int dev_i = open("/dev/ComBlock_0_fifo_i", O_RDONLY);
char buf_o[4]="abc";
char buf_i[4];

// clear the output fifo using lseek and pointing to -1
lseek(dev_o, -1, 0);

//write to the device
write(dev_o, &buf_o, 4);

// clear the input fifo using lseek and pointing to -1
lseek(dev_i, -1, 0);

//write to the device
read(dev_i, &buf_i, 4)
```

For ```Python```:

```Python
with os.fdopen(os.open('/dev/ComBlock_0_fifo_i', os.O_RDONLY), "br", buffering = 0) as fifo_in, os.fdopen(os.open('/dev/ComBlock_0_fifo_o', os.O_WRONLY), "bw", buffering = 0) as fifo_out:
    # clear FIFO
    fifo_out.lseek(-1)
    for i in range(1024):
        # write to FIFO
        fifo_out.write((i).to_bytes(4, 'little'))
    # get FIFO count
    print(fifo_out.tell())
    print(fifo_in.tell())
    err = 0
    for i in range(1024):
        # read from FIFO
        if(abs(i - int.from_bytes(fifo_in.read(4), 'little'))):
            err+=1

```

### DRAM

For ```C```:

```C
// open the device
int dev = open("/dev/ComBlock_0_ram", O_RDWR);

char buf_o[4]="abc";
char buf_i[4];

// set ram address
lseek(dev, 0, 0);

//write to the device
write(dev, &buf_o, 4);

// set ram address
lseek(dev, 0, 0);

//read 
read(dev, &buf_i, 4)
```

For ```Python```:

```Python

with os.fdopen(os.open('/dev/ComBlock_0_ram', os.O_RDWR), "br+", buffering = 0) as ram:
    err = 0
    for i in range(100):
        # set RAM address
        ram.seek(i*4, 0)
        # write to RAM
        val = int.from_bytes(ram.read(4), 'little')
        if(abs(i - val)):
            print(f'value {val} pos  {i}')
            err+=1
    print(f"{err} errors during reading 100 consecutive values from the RAM.")

    ram.seek(0,0)
    # read from RAM
    print([i for i in struct.unpack("IIII", ram.read(16))])
```
