/*
	ComBlock Module

Rodrigo Melo, Werner Florian, Bruno Valinoti.
*/

#include "comblock.h"

static int comblock_major;

static int dev_count = 0;
struct comblock_local *comblock_devs;
static struct class *comblock_class [CDEV_NUM];

static void get_dev_name(char * buff, unsigned int dev_num, char* type) {
	sprintf(buff, "%s_%d%s", DEVICE_NAME, dev_num, type);
}

static int byte_width(int width) {
	if(width <= 0)
		return 0;
	else if (width < 9)
		return 1;
	else if (width < 17)
		return 2;
	else if (width < 33)
		return 4;
	else 
		return width;
}

/* This structure will hold the functions to be called when a process does 
 * something to the device we created. Since a pointer to this structure 
 * is kept in the devices table, it can't be local to init_module. NULL is 
 * for unimplemented functions. 
 */

static struct file_operations cdev_fops[] = {
	{// RAM
		.owner = THIS_MODULE,
		.open = device_open,
		.read = ram_read,
		.write = ram_write,
		.llseek = ram_lseek,
		.release = device_release,
		.fasync = device_fasync
	},
	{// FIFO_IN
		.owner = THIS_MODULE,
		.open = device_open,
		.read = fifo_read,
		.llseek = fifo_i_lseek,
		.release = device_release,
		.fasync = device_fasync
	},
	{// FIFO_OUT
		.owner = THIS_MODULE,
		.open = device_open,
		.write = fifo_write,
		.llseek = fifo_o_lseek,
		.release = device_release,
		.fasync = device_fasync
	},
	{// REGS_IN
		.owner = THIS_MODULE,
		.open = device_open,
		.read = regs_read,
		.llseek = regs_i_lseek,
		.release = device_release,
		.fasync = device_fasync
	},
	{// REGS_OUT
		.owner = THIS_MODULE,
		.open = device_open,
		.write = regs_write,
		.llseek = regs_o_lseek,
		.release = device_release,
		.fasync = device_fasync
	}
};

void destroy_classes(void) {
	int i;
	for(i = 0; i < CDEV_NUM; i++) {
		if(comblock_class[i])
			class_destroy(comblock_class[i]);
	}
}

void delete_devices(int dev_count) {
	int i, j;
	for(i=0; i < dev_count; i++) {
		for(j = 0; j < CDEV_NUM; j++) {
			if(comblock_devs[i].cdev[j].dev) {
				cdev_del(&comblock_devs[i].cdev[j]);
				comblock_devs[i].cdev[j].dev = 0;
			}
		}
	}
}

void destroy_devices(int dev_count) {
	int i, j;
	for(i=0; i < dev_count; i++) {
		for(j = 0; j < CDEV_NUM; j++) {
			if(comblock_devs[i].cdev[j].dev) {
				device_destroy(comblock_class[j], MKDEV(comblock_major, i * CDEV_NUM + j));
			}
		}
	}
}

void iounmap_mem_regions(void) {
	int i;
	for(i=0; i < dev_count; i++) {
		if(comblock_devs[i].axi_l_base_addr)
			iounmap(comblock_devs[i].axi_l_base_addr);
		if(comblock_devs[i].axi_f_base_addr)
			iounmap(comblock_devs[i].axi_f_base_addr);
	}
}

void release_mem_regions(void) {
	int i;
	for(i=0; i < dev_count; i++) {
		if(comblock_devs[i].axi_l_start) 
			release_mem_region(comblock_devs[i].axi_l_start, comblock_devs[i].axi_l_end - comblock_devs[i].axi_l_start + 1);
		if(comblock_devs[i].axi_f_start) 
			release_mem_region(comblock_devs[i].axi_f_start, comblock_devs[i].axi_f_end - comblock_devs[i].axi_f_start + 1);
	}
}

static int device_comblock_init(struct device * dev, struct comblock_local * lp, char * dev_name, int dev_count, int minor_offset) {
	dev_t devno;
	int ret = 0;
	struct device *device = NULL;

	dev_info(dev, "Registering cdev");

	lp  ->  major = comblock_major;

	devno = MKDEV(comblock_major, minor_offset + dev_count * CDEV_NUM);
	lp  ->  minor[minor_offset] = MINOR(devno);
	cdev_init(&lp  ->  cdev[minor_offset], &cdev_fops[minor_offset]);
	
	dev_info(dev, "%s allocate \t <%d,%d>", dev_name, lp  ->  major, lp  ->  minor[minor_offset]);
	ret = cdev_add(&lp  ->  cdev[minor_offset], devno, 1);
	if(ret < 0) {
		dev_notice(dev, "Error %d adding %s", ret, dev_name);
		return ret;
	}

	if(!comblock_class[minor_offset]) {
		comblock_class[minor_offset] = class_create(THIS_MODULE, mem_class[minor_offset]);
		if (IS_ERR(comblock_class[minor_offset])) {
			pr_err("Class %s creation failed \n", mem_class[minor_offset]);
			ret = PTR_ERR(comblock_class);
			goto cleanup;
		}
	}

	device = device_create(comblock_class[minor_offset], dev, devno, NULL, dev_name);

	if (IS_ERR(device)) {
		ret = PTR_ERR(device);
		dev_warn(dev, "Error %d when creating device %s %d", ret, dev_name, lp  ->  minor[minor_offset]);
		goto out_cadd;
	}

	return 0;
	
	cleanup:
		destroy_classes();
	out_cadd:
		delete_devices(dev_count);
		return ret;
}

/* Probe device tree to retrieve parameters */
static int device_probe(struct platform_device *pdev) {
	struct comblock_local *lp = &comblock_devs[dev_count];
	struct device *dev = &pdev  ->  dev;

	unsigned int reg_in_enable	= 0;
	unsigned int reg_in_width	= 0;
	unsigned int reg_in_depth	= 0;
	unsigned int reg_out_enable	= 0;
	unsigned int reg_out_width	= 0;
	unsigned int reg_out_depth	= 0;
	unsigned int fifo_in_enable	= 0;
	unsigned int fifo_in_depth	= 0;
	unsigned int fifo_in_width	= 0;
	unsigned int fifo_out_enable	= 0;
	unsigned int fifo_out_depth	= 0;
	unsigned int fifo_out_width	= 0;
	unsigned int ram_enable	= 0;
	unsigned int ram_depth		= 0;
	unsigned int ram_width		= 0;
	long long unsigned int axi_f_start	= 0;
	long long unsigned int axi_f_end	= 0;
	long long unsigned int axi_l_start	= 0;
	long long unsigned int axi_l_end	= 0;
	
	int ret = 0;

	char dev_name[STR_LEN];

	dev_info(dev, "Device Tree Probing");

	// load parameters into the structure
	{
		ret = device_property_count_u32(dev, "REGS_IN_ENA");
		if (ret <= 0) {
			dev_err(dev, "REGS_IN_ENA property missing or empty");
			reg_in_enable = 0;
		} else {
			ret = device_property_read_u32(dev, "REGS_IN_ENA", &reg_in_enable);
			if (ret)
				return ret;
		}
		if(reg_in_enable){
			ret = device_property_count_u32(dev, "REGS_IN_DEPTH");
			if (ret <= 0) {
				dev_err(dev, "REGS_IN_DEPTH property missing or empty");
				return ret ? ret : -ENODATA;
			}
			ret = device_property_read_u32(dev, "REGS_IN_DEPTH", &reg_in_depth);
			if (ret)
				return ret;

			ret = device_property_count_u32(dev, "REGS_IN_DWIDTH");
			if (ret <= 0) {
				dev_err(dev, "REGS_IN_DWIDTH property missing or empty");
				return ret ? ret : -ENODATA;
			}
			ret = device_property_read_u32(dev, "REGS_IN_DWIDTH", &reg_in_width);
			if (ret)
				return ret;
		}
		

		ret = device_property_count_u32(dev, "REGS_OUT_ENA");
		if (ret <= 0) {
			dev_err(dev, "REGS_OUT_ENA property missing or empty");
			reg_out_enable = 0;
		} else {
			ret = device_property_read_u32(dev, "REGS_OUT_ENA", &reg_out_enable);
			if (ret)
				return ret;
		}
		if (reg_out_enable) {
			ret = device_property_count_u32(dev, "REGS_OUT_DEPTH");
			if (ret <= 0) {
				dev_err(dev, "REGS_OUT_DEPTH property missing or empty");
				return ret ? ret : -ENODATA;
			}
			ret = device_property_read_u32(dev, "REGS_OUT_DEPTH", &reg_out_depth);
			if (ret)
				return ret;

			ret = device_property_count_u32(dev, "REGS_OUT_DWIDTH");
			if (ret <= 0) {
				dev_err(dev, "REGS_OUT_DWIDTH property missing or empty");
				return ret ? ret : -ENODATA;
			}
			ret = device_property_read_u32(dev, "REGS_OUT_DWIDTH", &reg_out_width);
			if (ret)
				return ret;
		}

		ret = device_property_count_u32(dev, "FIFO_IN_ENA");
		if (ret <= 0) {
			dev_err(dev, "FIFO_IN_ENA property missing or empty");
			fifo_in_enable = 0;
		} else {
			ret = device_property_read_u32(dev, "FIFO_IN_ENA", &fifo_in_enable);
			if (ret)
				return ret;
		}
		if (fifo_in_enable) {
			ret = device_property_count_u32(dev, "FIFO_IN_DEPTH");
			if (ret <= 0) {
				dev_err(dev, "FIFO_IN_DEPTH property missing or empty");
				return ret ? ret : -ENODATA;
			}
			ret = device_property_read_u32(dev, "FIFO_IN_DEPTH", &fifo_in_depth);
			if (ret)
				return ret;

			ret = device_property_count_u32(dev, "FIFO_IN_DWIDTH");
			if (ret <= 0) {
				dev_err(dev, "FIFO_IN_DWIDTH property missing or empty");
				return ret ? ret : -ENODATA;
			}
			ret = device_property_read_u32(dev, "FIFO_IN_DWIDTH", &fifo_in_width);
			if (ret)
				return ret;
		}

		ret = device_property_count_u32(dev, "FIFO_OUT_ENA");
		if (ret <= 0) {
			dev_err(dev, "FIFO_OUT_ENA property missing or empty");
			fifo_out_enable = 0;
		} else {
			ret = device_property_read_u32(dev, "FIFO_OUT_ENA", &fifo_out_enable);
			if (ret)
				return ret;
		}
		if (fifo_out_enable) {
			ret = device_property_count_u32(dev, "FIFO_OUT_DEPTH");
			if (ret <= 0) {
				dev_err(dev, "FIFO_OUT_DEPTH property missing or empty");
				return ret ? ret : -ENODATA;
			}
			ret = device_property_read_u32(dev, "FIFO_OUT_DEPTH", &fifo_out_depth);
			if (ret)
				return ret;

			ret = device_property_count_u32(dev, "FIFO_OUT_DWIDTH");
			if (ret <= 0) {
				dev_err(dev, "FIFO_OUT_DWIDTH property missing or empty");
				return ret ? ret : -ENODATA;
			}
			ret = device_property_read_u32(dev, "FIFO_OUT_DWIDTH", &fifo_out_width);
			if (ret)
				return ret;
		}

		ret = device_property_count_u32(dev, "DRAM_IO_ENA");
		if (ret <= 0) {
			dev_err(dev, "DRAM_IO_ENA property missing or empty");
			ram_enable = 0;
		} else {
			ret = device_property_read_u32(dev, "DRAM_IO_ENA", &ram_enable);
			if (ret)
				return ret;
		}
		if (ram_enable) {
			ret = device_property_count_u32(dev, "DRAM_IO_DEPTH");
			if (ret <= 0) {
				dev_err(dev, "DRAM_IO_DEPTH property missing or empty");
				return ret ? ret : -ENODATA;
			}
			ret = device_property_read_u32(dev, "DRAM_IO_DEPTH", &ram_depth);
			if(ret)
				return ret;

			ret = device_property_count_u32(dev, "DRAM_IO_DWIDTH");
			if (ret <= 0) {
				dev_err(dev, "DRAM_IO_DWIDTH property missing or empty");
				return ret ? ret : -ENODATA;
			}
			ret = device_property_read_u32(dev, "DRAM_IO_DWIDTH", &ram_width);
			if (ret)
				return ret;
		}

		lp  ->  reg_in_enable = reg_in_enable;
		lp  ->  reg_in_depth = reg_in_depth;
		lp  ->  reg_in_width = byte_width(reg_in_width);
		lp  ->  reg_out_enable = reg_out_enable;
		lp  ->  reg_out_depth = reg_out_depth;
		lp  ->  reg_out_width = byte_width(reg_out_width);
		lp  ->  fifo_in_enable = fifo_in_enable;
		lp  ->  fifo_in_depth = fifo_in_depth;
		lp  ->  fifo_in_width = byte_width(fifo_in_width);
		lp  ->  fifo_out_enable = fifo_out_enable;
		lp  ->  fifo_out_depth = fifo_out_depth;
		lp  ->  fifo_out_width = byte_width(fifo_out_width);
		lp  ->  ram_enable = ram_enable;
		lp  ->  ram_depth = ram_depth;
		lp  ->  ram_width = byte_width(ram_width);
	}

	// Memory allocation
	
	if(lp  ->  reg_in_enable || lp  ->  reg_out_enable || lp  ->  fifo_in_enable || lp  ->  fifo_out_enable) {
		ret = device_property_count_u64(dev, "C_AXIL_BASEADDR");
		if (ret <= 0) {
			dev_err(dev, "C_AXIL_BASEADDR property missing or empty");
			return ret ? ret : -ENODATA;
		}
		ret = device_property_read_u64(dev, "C_AXIL_BASEADDR", &axi_l_start);
		if(ret)
			return ret;

		ret = device_property_count_u64(dev, "C_AXIL_HIGHADDR");
		if (ret <= 0) {
			dev_err(dev, "C_AXIL_HIGHADDR property missing or empty");
			return ret ? ret : -ENODATA;
		}
		ret = device_property_read_u64(dev, "C_AXIL_HIGHADDR", &axi_l_end);
		if(ret)
			return ret;
		
		if(!request_mem_region(axi_l_start, axi_l_end - axi_l_start + 1, DEVICE_NAME)) {
			dev_err(dev, "Couldn't lock memory region at %llu\n", axi_l_start);
			ret = -EBUSY;
			goto out_free_local;
		}
		lp  ->  axi_l_start = axi_l_start;
		lp  ->  axi_l_end = axi_l_end;
		lp  ->  axi_l_base_addr = ioremap(axi_l_start, axi_l_end - axi_l_start + 1);
	}
	
	if(lp  ->  ram_enable) {
		ret = device_property_count_u64(dev, "C_AXIF_BASEADDR");
		if (ret <= 0) {
			dev_err(dev, "C_AXIF_BASEADDR property missing or empty");
			return ret ? ret : -ENODATA;
		}
		ret = device_property_read_u64(dev, "C_AXIF_BASEADDR", &axi_f_start);
		if(ret)
			return ret;

		ret = device_property_count_u64(dev, "C_AXIF_HIGHADDR");
		if (ret <= 0) {
			dev_err(dev, "C_AXIF_HIGHADDR property missing or empty");
			return ret ? ret : -ENODATA;
		}
		ret = device_property_read_u64(dev, "C_AXIF_HIGHADDR", &axi_f_end);
		if(ret)
			return ret;
		
		if(!request_mem_region(axi_f_start, axi_f_end - axi_f_start + 1, DEVICE_NAME)) {
			dev_err(dev, "Couldn't lock memory region at %llu\n", axi_f_start);
			ret = -EBUSY;
			goto out_free_local;
		}
		lp  ->  axi_f_start = axi_f_start;
		lp  ->  axi_f_end = axi_f_end;
		lp  ->  axi_f_base_addr = ioremap(axi_f_start, axi_f_end - axi_f_start + 1);
	}

	if(!lp  ->  axi_l_base_addr && !lp  ->  axi_f_base_addr) {
		dev_err(dev, "Could not allocate iomem\n");
		ret = -EIO;
		goto out_free_mem_region;
	}

// Char devices init
	if(lp  ->  ram_enable) {
		get_dev_name(dev_name, dev_count, DEVICE_NAME_RAM);
		ret = device_comblock_init(dev, lp, dev_name, dev_count, RAM);
		if(ret < 0) {
			dev_err(dev, "Could not create RAM dev \n");
			goto out_free_iomap;
		}
	}

	if(lp  ->  fifo_in_enable) {
		get_dev_name(dev_name, dev_count, DEVICE_NAME_FIFO_IN);
		ret = device_comblock_init(dev, lp, dev_name, dev_count, FIFO_I);
		if(ret < 0) {
			dev_err(dev, "Could not create FIFO dev \n");
			goto out_free_iomap;
		}
	}

	if(lp  ->  fifo_out_enable) {
		get_dev_name(dev_name, dev_count, DEVICE_NAME_FIFO_OUT);
		ret = device_comblock_init(dev, lp, dev_name, dev_count, FIFO_O);
		if(ret < 0) {
			dev_err(dev, "Could not create FIFO dev \n");
			goto out_free_iomap;
		}
	}

	if(lp  ->  reg_in_enable) {
		get_dev_name(dev_name, dev_count, DEVICE_NAME_REGS_IN);
		ret = device_comblock_init(dev, lp, dev_name, dev_count, REGS_I);
		if(ret < 0) {
			dev_err(dev, "Could not create Registers dev \n");
			goto out_free_iomap;
		}
	}

	if(lp  ->  reg_out_enable) {
		get_dev_name(dev_name, dev_count, DEVICE_NAME_REGS_OUT);
		ret = device_comblock_init(dev, lp, dev_name, dev_count, REGS_O);
		if(ret < 0) {
			dev_err(dev, "Could not create Registers dev \n");
			goto out_free_iomap;
		}
	}

	dev_count ++;

	sema_init(&lp  ->  sem, 1);
	dev_info(dev, "Comblock detected with the following parameters: \n");
	dev_info(dev, "Enables: \tIReg %d,\tOReg %d, \tIFIFO %d, \tOFIFO %d, \tRAM %d \n", lp  ->  reg_in_enable, lp  ->  reg_out_enable, lp  ->  fifo_in_enable, lp  ->  fifo_out_enable, lp  ->  ram_enable);
	dev_info(dev, "Depth: \tIReg %d,\tOReg %d, \tIFIFO %d, \tOFIFO %d, \tRAM %d \n", lp -> reg_in_depth, lp -> reg_out_depth, lp -> fifo_in_depth, lp -> fifo_out_depth, lp -> ram_depth);
	dev_info(dev, "Width: \tIReg %d,\tOReg %d, \tIFIFO %d, \tOFIFO %d, \tRAM %d \n", lp -> reg_in_width, lp -> reg_out_width, lp -> fifo_in_width, lp -> fifo_out_width, lp -> ram_width);
	
	dev_set_drvdata(dev, lp); //save device data to platform device

	return 0;

	out_free_iomap:
		iounmap_mem_regions();
	out_free_mem_region:
		release_mem_regions();
	out_free_local:
		dev_set_drvdata(dev, NULL);
		return ret;
}

static int device_remove(struct platform_device *pdev) {
	struct device *dev = &pdev  ->  dev;
	struct comblock_local *lp = dev_get_drvdata(dev);
	int i;

	for(i = 0; i < CDEV_NUM; i++) {
		if(lp -> cdev[i].dev) {
			dev_info(dev, "Removing <%d,%d>", comblock_major, MINOR(lp -> cdev[i].dev));
			device_destroy(comblock_class[i], MKDEV(comblock_major, lp -> minor[i]));
			cdev_del(&lp -> cdev[i]);
			lp -> cdev[i].dev = 0;
		}
	}
	return 0;
}

#ifdef CONFIG_OF
static struct of_device_id comblock_of_match[] = {
	{ .compatible = "xlnx,comblock-2.0" },
	{ /* sentinel */ },
};
MODULE_DEVICE_TABLE(of, comblock_of_match);
#else
#define comblock_of_match
#endif

static struct platform_driver comblock_driver = {
	.driver = {
		.name = DEVICE_NAME,
		.owner = THIS_MODULE,
		.of_match_table = comblock_of_match,
	},
	.probe = device_probe,
	.remove = device_remove,
};

/* Initialize the module - Register the character device */
static int comblock_init(void) {
	int ret = 0;
	dev_t devno = 0;
	pr_info("Start ComBlock. ver.0.01 \n");

	ret = alloc_chrdev_region(&devno, 0, comblock_nr_devs * CDEV_NUM, DEVICE_NAME);
	if(ret < 0) {
		pr_warn("Warning can't get major %d", comblock_major);
		return ret;
	}
	comblock_major = MAJOR(devno);

	// local stuct that keeps devices info inside this lkm
	comblock_devs = kzalloc(sizeof(struct comblock_local) * comblock_nr_devs, GFP_KERNEL); 
	if (!comblock_devs) {
		pr_err("Cound not allocate %d ComBlock devices \n ", comblock_nr_devs);
		ret = -ENOMEM;
		goto cleanup;
	}

	return platform_driver_register(&comblock_driver);

	cleanup:
		unregister_chrdev_region(MKDEV(comblock_major, 0), comblock_nr_devs * CDEV_NUM);
		return ret;
}

/* Cleanup - unregister the appropriate file from /proc */ 
static void comblock_exit(void) {
	platform_driver_unregister(&comblock_driver);
	pr_info("Deleting classes \n");
	destroy_classes();
	release_mem_regions();
	kfree(comblock_devs);
	unregister_chrdev_region(MKDEV(comblock_major, 0), comblock_nr_devs * CDEV_NUM);
	pr_info("Exit ComBlock \n");
}


module_init(comblock_init);
module_exit(comblock_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Werner Florian");
MODULE_DESCRIPTION("ComBlock - FPGA interface block");

