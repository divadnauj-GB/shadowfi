//#pragma once

#ifndef COMBLOCKDEV_H
#define COMBLOCKDEV_H

#define DEBUG

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/init.h>
#include <linux/cdev.h>
#include <linux/platform_device.h>
#include <linux/device.h>
#include <linux/slab.h>
#include <linux/fs.h>
#include <linux/ioctl.h>

#include <linux/io.h>
#include <linux/errno.h>

#include <linux/of_device.h>
#include <linux/of_platform.h>

#include <linux/regmap.h>

#include <asm/uaccess.h>

#define BUFF_LEN 128 // depends on CB FIFO and RAM max depth but also available Linux RAM

enum mem_types {
	RAM,
	FIFO_I,
	FIFO_O,
	REGS_I,
	REGS_O,
};

static const char *mem_class[] = {
	[RAM]		=	"ComBlock_ram_",
	[FIFO_I]	=	"ComBlock_fifo_i",
	[FIFO_O]	=	"ComBlock_fifo_o",
	[REGS_I]	=	"ComBlock_regs_i",
	[REGS_O]	=	"ComBlock_regs_o",
};

union Data {
	unsigned int i;
	char str[4];
};

#define	DEVICE_NAME						"ComBlock"
#define	DEVICE_NAME_RAM					"_ram"
#define	DEVICE_NAME_FIFO_IN				"_fifo_i"
#define	DEVICE_NAME_FIFO_OUT			"_fifo_o"
#define	DEVICE_NAME_REGS_IN				"_regs_i"
#define	DEVICE_NAME_REGS_OUT			"_regs_o"


#define	COMBLOCK_IOC_MAGIC				'a'

#define	COMBLOCK_IOC_RESET				_IO(COMBLOCK_IOC_MAGIC, 0)
#define	COMBLOCK_IOC_IFIFO_RESET		_IO(COMBLOCK_IOC_MAGIC, 1)
#define	COMBLOCK_IOC_OFIFO_RESET		_IO(COMBLOCK_IOC_MAGIC, 2)
#define	COMBLOCK_IOC_REG_READ			_IOR(COMBLOCK_IOC_MAGIC, 3, struct params *)
#define	COMBLOCK_IOC_REG_WRITE			_IOW(COMBLOCK_IOC_MAGIC, 4, struct params *)
#define	COMBLOCK_IOC_FIFO_READ			_IOR(COMBLOCK_IOC_MAGIC, 5, struct params *)
#define	COMBLOCK_IOC_IFIFO_STATUS_READ	_IOR(COMBLOCK_IOC_MAGIC, 6, struct params *)
#define	COMBLOCK_IOC_OFIFO_STATUS_READ	_IOR(COMBLOCK_IOC_MAGIC, 7, struct params *)
#define	COMBLOCK_IOC_FIFO_WRITE			_IOW(COMBLOCK_IOC_MAGIC, 8, struct params *)
#define	COMBLOCK_IOC_RAM_READ			_IOR(COMBLOCK_IOC_MAGIC, 9, struct params *)
#define	COMBLOCK_IOC_RAM_WRITE			_IOW(COMBLOCK_IOC_MAGIC, 10, struct params *)
#define	COMBLOCK_IOC_MAXNR				10

/* FIFO Registers offset */

#define	CB_IFIFO_VALUE					32
#define	CB_IFIFO_CONTROL				33
#define	CB_IFIFO_STATUS					34
#define	CB_REGO_OFFSET					64

// RFU: 35

#define	CB_OFIFO_VALUE					36
#define	CB_OFIFO_CONTROL				37
#define	CB_OFIFO_STATUS					38

#define	SUCCESS							0
#define	FAIL							(-1)

#define	STR_LEN							20
#define	CDEV_NUM						5
#define comblock_nr_devs				5

#define	readreg(offset)					__raw_readl(offset)
#define	writereg(val, offset)			__raw_writel(val, offset)

// Device properties
struct comblock_local {
	// for char device
	struct cdev cdev[CDEV_NUM];
	struct semaphore sem; // for interface mutex
	// device tree properties
	struct fasync_struct * async_queue;
	void __iomem *axi_l_base_addr;
	void __iomem *axi_f_base_addr;
	int major;
	int minor[CDEV_NUM];
	int active_minor;
	unsigned int reg_in_enable;
	unsigned int reg_in_width;
	unsigned int reg_in_depth;
	unsigned int reg_out_enable;
	unsigned int reg_out_width;
	unsigned int reg_out_depth;
	unsigned int fifo_in_enable;
	unsigned int fifo_in_depth;
	unsigned int fifo_in_width;
	unsigned int fifo_out_enable;
	unsigned int fifo_out_depth;
	unsigned int fifo_out_width ;
	unsigned int ram_enable;
	unsigned int ram_depth;
	unsigned int ram_width;
	long long unsigned int axi_f_start;
	long long unsigned int axi_f_end;
	long long unsigned int axi_l_start;
	long long unsigned int axi_l_end;
};

int device_open(struct inode *inode, struct file *file);
int device_fasync(int fd, struct file * file, int mode);
int device_release(struct inode *inode, struct file *file);

ssize_t fifo_read (struct file *file, char __user *buf, size_t count, loff_t *f_pos);
loff_t fifo_i_lseek(struct file *file, loff_t f_pos, int whence);

ssize_t fifo_write (struct file *file, const char __user *buf, size_t count, loff_t *f_pos);
loff_t fifo_o_lseek(struct file *file, loff_t f_pos, int whence);

ssize_t ram_read (struct file *file, char __user *buf, size_t count, loff_t *f_pos);
ssize_t ram_write (struct file *file, const char __user *buf, size_t count, loff_t *f_pos);
loff_t ram_lseek(struct file *file, loff_t f_pos, int whence);

ssize_t regs_read (struct file *file, char __user *buf, size_t count, loff_t *f_pos);
loff_t regs_i_lseek(struct file *file, loff_t f_pos, int whence);

ssize_t regs_write (struct file *file, const char __user *buf, size_t count, loff_t *f_pos);
loff_t regs_o_lseek(struct file *file, loff_t f_pos, int whence);

#endif
