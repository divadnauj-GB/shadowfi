/*
* AXI ComBlock hardware test
*
* Author(s):
* * Rodrigo A. Melo
*
* Copyright (c) 2018-2019 Authors, INTI (MNT) and ICTP (MLAB)
* Distributed under the BSD 3-Clause License
*
* Description: the firmware for a hardware test of the AXI ComBlock
*/

#include <stdio.h>
#include "comblock.h"

#define TOOL vivado // vivado

#if TOOL == vivado
    #include "xparameters.h"
    #define AXIL_BASE    XPAR_COMBLOCK_0_AXIL_BASEADDR
    #define AXIF_BASE    XPAR_COMBLOCK_0_AXIF_BASEADDR
    #define IREGS_DEPTH  XPAR_COMBLOCK_0_REGS_IN_DEPTH
    #define OREGS_DEPTH  XPAR_COMBLOCK_0_REGS_OUT_DEPTH
    #define REGS_DEPTH   ((IREGS_DEPTH < OREGS_DEPTH) ? IREGS_DEPTH : OREGS_DEPTH)
    #define DRAM_DEPTH   (1<<XPAR_COMBLOCK_0_DRAM_IO_AWIDTH)
    #define IFIFO_DEPTH  XPAR_COMBLOCK_0_FIFO_IN_DEPTH
    #define OFIFO_DEPTH  XPAR_COMBLOCK_0_FIFO_OUT_DEPTH
    #define FIFO_DEPTH   ((IFIFO_DEPTH < OFIFO_DEPTH) ? IFIFO_DEPTH : OFIFO_DEPTH)
#endif

int tx_buf[DRAM_DEPTH], rx_buf[DRAM_DEPTH];

int main() {
    int i, val;

    printf("### Testing the ComBlock\r\n");

    printf("* Testing %d Registers...\r\n", REGS_DEPTH);
    printf("Writing from Output REG0 to REG%d\r\n", REGS_DEPTH-1);
    for (i=0; i < REGS_DEPTH; i++) {
        cbWrite(AXIL_BASE, CB_OREG0 + i, i);
    }
    printf("Reading from Input REG0 to REG%d (loopback)\r\n", REGS_DEPTH-1);
    for (i=0; i < REGS_DEPTH; i++) {
        val = cbRead(AXIL_BASE, i);
        if ( val != REGS_DEPTH-1-i )
           printf("ERROR: Reg %d = %d\r\n",i,val);
    }
    printf("Reading from Output REG0 to REG%d\r\n", REGS_DEPTH-1);
    for (i=0; i < REGS_DEPTH; i++) {
        val = cbRead(AXIL_BASE, CB_OREG0+ i);
        if ( val != i )
           printf("ERROR: Reg %d = %d\r\n",i,val);
    }

    printf("* Testing RAM with %d values...\r\n", DRAM_DEPTH);
    for (i=0; i < DRAM_DEPTH; i++) tx_buf[i] = i;
    cbWriteBulk(AXIF_BASE, tx_buf, DRAM_DEPTH);
    cbReadBulk(rx_buf, AXIF_BASE, DRAM_DEPTH);
    for (i=0; i < DRAM_DEPTH; i++)
        if (tx_buf[i] != rx_buf[i])
           printf("ERROR: Mem[%d] = %d\r\n", i, rx_buf[i]);

    printf("* Testing FIFOs with %d values...\r\n", FIFO_DEPTH);
    for (i=0; i < FIFO_DEPTH; i++) {
        cbWrite(AXIL_BASE,CB_OFIFO_VALUE,i);
    }
    for (i=0; i < FIFO_DEPTH; i++) {
        val = cbRead(AXIL_BASE, CB_IFIFO_VALUE);
        if ( val != i )
           printf("ERROR: FIFO %d = %d\r\n",i,val);
    }

    printf("### Finished\r\n");

    return 0;
}
