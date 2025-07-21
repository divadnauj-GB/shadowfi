#ifndef UDMA_H
#define UDMA_H

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <errno.h>
#include <dirent.h>
#include <stdbool.h>
#include <limits.h>
#include <regex.h>
#include <types.h>

/*---------STATUS FLAGS------------*/
#define FAIL				0
#define SUCCESS				1
#define OVERFLOW			2
#define UNDERFLOW			3
#define LOG_ENABLE			4
#define LOG_DISABLE			5

/*-------------------------------*/
#define MAX_CB_NUM          100

bool in(unsigned long long *bitset, int number);
int add(unsigned long long *bitset, int number);

/*
Write process:
	check if resource is available in case of specific commands
	check if memory is reachable in case of udma or mem
	check if width of word is compatible
		return success or fail

read process
	check if resource is available in case of specific commands
	check if memory is reachable in case of udma or mem
		return success or fail

send_buf [0] error report:
	0 -> Failure
	1 -> Success
	2 -> overflow
	3 -> underflow
	4 -> logging enabled
	5 -> logging disabled
send_buf [1] length
*/

enum cb_mem {
    REGS_I,
    REGS_O,
    FIFO_I,
    FIFO_O,
    RAM_IO
};

extern unsigned long long CB_sets [5];

int comblock_init();

int read_FIFO(u32 comblock, u32 *send_buf, u32 length);
int write_FIFO(u32 comblock, u32 *recv_buf, u32 length, u32 *send_buf);
int clean_FIFO_i(u32 comblock);
int clean_FIFO_o(u32 comblock);

int read_RAM(u32 comblock, u32 offset, u32 *send_buf, u32 length, u32 inc);
int write_RAM(u32 comblock, u32 offset, u32 *recv_buf, u32 length, u32 inc, u32 *send_buf);

int read_reg(u32 comblock, u32 reg, u32 *send_buf);
int write_reg(u32 comblock, u32 reg, u32 *recv_buf);

#endif //UDMA_H
