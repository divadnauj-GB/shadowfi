#include "comblock.h"

extern struct comblock_local *comblock_devs;

int device_fasync(int fd, struct file * file, int mode) {
	struct comblock_local * lp = (struct comblock_local*) file -> private_data;
	return fasync_helper(fd, file, mode, &lp -> async_queue);
}

/* 	This is called whenever a process attempts to open the device file
	We try to get the module if it is already running and we load the
	device parameters into the local struct.
	*/

int fifo_empty(void __iomem *base_addr) {
	pr_debug("ComBlock: FIFO empty.");
	return readreg(base_addr + CB_IFIFO_STATUS * 4) & 0x01;
}

int fifo_full(void __iomem *base_addr) {
	pr_debug("ComBlock: FIFO full.");
	return readreg(base_addr + CB_OFIFO_STATUS * 4) & 0x01;
}

int fifo_count(void __iomem *base_addr, int dir) {
    // return the current value of the fifo counter in bytes
    // param: dir, inidicate the fifo direction
	//  1 output
	//  0 input, respect to linux
	int count;

	if (dir) {
		count = 4 * readreg(base_addr + CB_OFIFO_STATUS * 4) >> 0x10;
		pr_debug("ComBlock: FIFO out count %d bytes.", count); 
	} else {
		count = 4 * readreg(base_addr + CB_IFIFO_STATUS * 4) >> 0x10;
		pr_debug("ComBlock: FIFO in count %d bytes.", count); 
	}
	return count;
}

/*enforce 32 bits*/
ssize_t regs_read (struct file *file, char __user *buf, size_t count, loff_t *f_pos) {
	struct comblock_local *lp = (struct comblock_local*) file -> private_data;
	int *lbuf;
	ssize_t ret = 0;

	pr_debug("ComBlock: REG read.");

	if(count != 4) {
		pr_debug("Only 32 bit operations allowed.");
		return -EPERM;
	}

	if(down_interruptible(&lp -> sem)) {
		pr_debug("ComBlock: BUSY.");
		return -EBUSY;
	}

	lbuf = kzalloc(sizeof(int), GFP_KERNEL);
	if(!lbuf) {
		pr_debug("ComBlock: kzalloc failed.");
		ret = -ENOMEM;
		goto up_interruptible;
	}
		
	*lbuf = readreg(lp -> axi_l_base_addr + *f_pos);
	ret = copy_to_user(buf, lbuf, sizeof(int));
	if(ret != 0) {
		pr_debug("ComBlock: copy to user failed");
		ret = -EIO;
		goto end;
	}
	
	ret = count;

	pr_debug("ComBlock: value %X", *lbuf);
	pr_debug("Vmem ADDR: %p", lp -> axi_l_base_addr + *f_pos);
	pr_debug("Mem ADDR: %llX", lp -> axi_l_start + *f_pos);

	end:
		kfree(lbuf);
	up_interruptible:
		up(&lp -> sem);
		return ret;
}

/*enforce 32 bits*/
ssize_t regs_write (struct file *file, const char __user *buf, size_t count, loff_t *f_pos) {
	struct comblock_local * lp =  (struct comblock_local*) file -> private_data;
	int *lbuf;
	ssize_t ret = 0;

	pr_debug("ComBlock: REG write.");

	if(count != 4) {
		pr_debug("Only 32 bit operations allowed.");
		return -EPERM;
	}

	if(down_interruptible(&lp -> sem)) {
		pr_debug("ComBlock: BUSY.");
		return -EBUSY;
	}

	lbuf = kzalloc(sizeof(int), GFP_KERNEL);
	if(!lbuf) {
		pr_debug("ComBlock: kzalloc failed.");
		ret = -ENOMEM;
		goto up_interruptible;
	}
	
	if(copy_from_user(lbuf, buf, sizeof(int)) != 0) {
		pr_debug("ComBlock: copy to user failed");
		ret = -EIO;
		goto end;
	}

	ret = count;

	writereg(*lbuf, lp -> axi_l_base_addr + *f_pos + CB_REGO_OFFSET); // 64 is the input registers offset
	pr_debug("Comblock: value %X", *lbuf);
	pr_debug("Vmem ADDR: %p", lp -> axi_l_base_addr + *f_pos + CB_REGO_OFFSET);
	pr_debug("Mem ADDR: %llX", lp -> axi_l_start + *f_pos + CB_REGO_OFFSET);

	end:
		kfree(lbuf);
	up_interruptible:
		up(&lp->sem);
		return ret;
}

loff_t regs_i_lseek(struct file *file, loff_t offset, int whence) {
	struct comblock_local *lp = (struct comblock_local *) file -> private_data;
	unsigned int max_size = (lp -> reg_in_depth - 1) * 4;
	loff_t ret = 0;

	pr_debug("ComBlock: REG in seek.");
	
	if(offset % 4 != 0) {
		pr_debug("Only 32 bit operations allowed.");
		return -EPERM;
	}

	if(down_interruptible(&lp->sem)) {
		pr_debug("ComBlock: BUSY.");
		return -EBUSY;
	}

	if (offset > max_size) {
		file -> f_pos = max_size;
	} else {
		file -> f_pos = offset;
	}

	switch(whence) {
		case SEEK_CUR:
			offset += file -> f_pos;
			if (offset > max_size && offset < 0) {
				ret = -EOVERFLOW;
			} else {
				file -> f_pos = offset;
				ret = file -> f_pos;
			}
		break;
		case SEEK_END:
			if (offset > 0) {
				ret = -EINVAL;
			} else {
				offset += max_size;
				if (offset < 0) {
					ret = -EOVERFLOW;
				} else {
					file -> f_pos = offset;
					ret = file -> f_pos;
				}
			}
		break;
		case SEEK_SET:
			if (offset > max_size) {
				ret = -EOVERFLOW;
			} else if (offset < 0) {
				ret = -EINVAL;
			} else {
				file -> f_pos = offset;
				ret = file -> f_pos;
			}
		break;
		default:
			ret = -EINVAL;
		break;
	}

	pr_debug("Regs i file position = %lld, offset= %lld, maxsize=%d \n", file -> f_pos, offset, max_size);
	pr_debug("Mem ADDR: %llX", lp -> axi_l_start + file -> f_pos);
	up(&lp -> sem);
	return ret;
}

loff_t regs_o_lseek(struct file *file, loff_t offset, int whence) {
	struct comblock_local *lp = (struct comblock_local *) file -> private_data;
	unsigned int max_size = (lp -> reg_out_depth - 1) * 4;
	loff_t ret = 0;
	pr_debug("ComBlock: REG out seek.");
	
	if(offset % 4 != 0) {
		pr_debug("Only 32 bit operations allowed.");
		return -EPERM;
	}

	if(down_interruptible(&lp -> sem)) {
		pr_debug("ComBlock: BUSY.");
		return -EBUSY;
	}

	switch(whence) {
		case SEEK_CUR:
			offset += file -> f_pos;
			if (offset > max_size && offset < 0) {
				ret = -EOVERFLOW;
			} else {
				file -> f_pos = offset;
				ret = file -> f_pos;
			}
		break;
		case SEEK_END:
			if (offset > 0) {
				ret = -EINVAL;
			} else {
				offset += max_size;
				if (offset < 0) {
					ret = -EOVERFLOW;
				} else {
					file -> f_pos = offset;
					ret = file -> f_pos;
				}
			}
		break;
		case SEEK_SET:
			if (offset > max_size) {
				ret = -EOVERFLOW;
			} else {
				file -> f_pos = offset;
				ret = file -> f_pos;
			}
		default:
			ret = -EINVAL;
		break;
	}

	pr_debug("Regs out file position = %lld, offset= %lld, maxsize=%d \n", file -> f_pos, offset, max_size);
	pr_debug("Mem ADDR: %llX", lp -> axi_l_start + file -> f_pos + 64);
	up(&lp -> sem);
	return ret;
}

/* ram_read function: takes the iomem from the lp device and the user params enforce 32 bits
	Takes from params the len to read.
	Writes on params the requested data and its len.
	returns total read
*/
ssize_t ram_read (struct file *file, char __user *buf, size_t count, loff_t *f_pos) {
	struct comblock_local * lp =  (struct comblock_local*) file -> private_data;
	unsigned int i = 0;
	ssize_t ret = 0;
	char *lbuf;

	pr_debug("ComBlock: RAM read.");

	if((count % 4 != 0) && (count < 1)) {
		pr_debug("Only 32 bit operations allowed.");
		return -EPERM;
	}

	if((count + *f_pos) > (lp -> ram_depth) * 4) {
		pr_debug("Operation overflow.");
		return -E2BIG;
	}

	if(down_interruptible(&lp -> sem)) {
		pr_debug("ComBlock: BUSY.");
		return -EBUSY;
	}

	pr_debug("[USER] Count: %ld", count);

	lbuf = kzalloc(count, GFP_KERNEL);
	if(!lbuf) {
		ret = -ENOMEM;
		goto end;
	}

	memcpy(lbuf, lp -> axi_f_base_addr + *f_pos, count);
	
	if(copy_to_user(buf, lbuf, count) != 0) {
		pr_debug("ComBlock: copy to user failed");
		ret = -EIO;
		goto end;
	}

	ret = count;
	
#ifdef DEBUG
	for (i = 0; i < count; i++) {
		pr_debug("[LKM] Read from ram: %X c %d.\n", lbuf[i], i);
		pr_debug("[User] Read from ram: %X c %d.\n", buf[i], i);
	}
#endif	

	pr_debug("Vmem ADDR: %p", lp -> axi_f_base_addr + *f_pos);
	pr_debug("Mem ADDR: %llX", lp -> axi_f_start + *f_pos);
	end:
		kfree(lbuf);
		up(&lp -> sem);
		return ret;
}

/* ram_write function: takes the iomem from the lp device and the user params
	Takes from params the len to write
	Writes on param the len wrote.
	returns total wrote
*/
ssize_t ram_write (struct file *file, const char __user *buf, size_t count, loff_t *f_pos) {
	struct comblock_local * lp =  (struct comblock_local*) file -> private_data;
	char *lbuf; 
	unsigned int i;
	ssize_t ret = 0;

	pr_debug("ComBlock: RAM write.");

	if((count % 4 != 0) && (count < 1)) {
		pr_debug("Only 32 bit operations allowed.");
		return -EPERM;
	}

	if((count + *f_pos) > (lp -> ram_depth) * 4) {
		pr_debug("Operation overflow.");
		return -E2BIG;
	}	

	if(down_interruptible(&lp -> sem)){
		return -EBUSY;
	}

	lbuf = kzalloc(count, GFP_KERNEL);
	if(!lbuf) {
		pr_debug("ComBlock: kzalloc failed.");
		ret = -ENOMEM;
		goto up_interruptible;
	}

	if(copy_from_user(lbuf, buf, count) != 0) {
		pr_debug("ComBlock: copy to user failed");
		ret = -EIO;
		goto end;
	}

#ifdef DEBUG
	for (i = 0; i < count; i++) {
		pr_debug("[USER] Write to ram: %X c %d.\n", buf[i], i);
		pr_debug("[LKM] Write to ram: %X c %d.\n", lbuf[i], i);
	}
#endif
	ret = count;
	memcpy(lp -> axi_f_base_addr + *f_pos, lbuf, count);
	pr_debug("Comblock: Write Ram %d", lbuf[0]);
	pr_debug("ADDR: %p", lp -> axi_f_base_addr + *f_pos);
	pr_debug("Mem ADDR: %llX", lp -> axi_f_start + *f_pos);

	end:
		kfree(lbuf);
	up_interruptible:
		up(&lp -> sem);
		return ret;
}

loff_t ram_lseek(struct file *file, loff_t offset, int whence) {
	struct comblock_local *lp = (struct comblock_local *) file -> private_data;
	unsigned int max_size = (lp -> ram_depth - 1) * 4;
	loff_t ret = 0;

	pr_debug("ComBlock: RAM seek.");

	if(offset % 4 != 0) {
		pr_debug("Only 32 bit operations allowed.");
		return -EPERM;
	}

	if(down_interruptible(&lp -> sem)) {
		return -EBUSY;
	}

	switch(whence) {
		case SEEK_CUR:
			offset += file -> f_pos;
			if (offset > max_size) {
				ret = -EOVERFLOW;
			} else {
				file -> f_pos = offset;
				ret = file -> f_pos;
			}
		break;
		case SEEK_END:
			if (offset > 0) {
				ret = -EINVAL;
			} else {
				offset += max_size;
				if (offset > max_size) {
					ret = -EOVERFLOW;
				} else {
					file -> f_pos = offset;
					ret = file -> f_pos;
				}
			}
		break;
		case SEEK_SET:
			if (offset > max_size) {
				ret = -EOVERFLOW;
			} else {
				file -> f_pos = offset;
				ret = file -> f_pos;
			}
		break;
		default:
			ret = -EINVAL;
		break;
	}

	pr_debug("RAM file position = %lld, offset= %lld, maxsize=%d \n", file -> f_pos, offset, max_size);
	up(&lp -> sem);
	return ret;
}

ssize_t fifo_write (struct file *file, const char __user *buf, size_t count, loff_t *f_pos) {
	struct comblock_local * lp =  (struct comblock_local*) file -> private_data;
	int *lbuf;
	unsigned int i = 0;
	ssize_t ret = 0;

	pr_debug("ComBlock: FIFO write %ld bytes.", count);
    
	if((count % 4 != 0) && (count < 1)) {
		pr_debug("Only 32 bit operations allowed.");
		return -EPERM;
	}

	if(fifo_count(lp -> axi_l_base_addr, 1) + count > lp -> fifo_out_depth * 4) {
		pr_debug("ComBlock: FIFO overflow.");
		ret = -E2BIG;
		goto up_interruptible;
	}

	if(down_interruptible(&lp -> sem) || fifo_full(lp -> axi_l_base_addr)) {
		return -EBUSY;
	}

	lbuf = kzalloc(count, GFP_KERNEL);
	if(!lbuf) {
		pr_debug("ComBlock: kzalloc failed.");
		ret = -ENOMEM;
		goto up_interruptible;
	}

	if(copy_from_user(lbuf, buf, count) != 0) {
		pr_debug("ComBlock: copy to user failed");
		ret = -EIO;
		goto end;
	}

#ifdef DEBUG
	for (i = 0; i < count; i++) {
		pr_debug("[USER] Write to fifo: %X c %d.\n", buf[i], i);
	}
#endif

	pr_debug("Mem ADDR: %llX", lp -> axi_l_start + CB_OFIFO_VALUE * 4);
	for(i = 0; i < count / 4; i++) { // check fifo full
		pr_debug("[LKM] Write to fifo: %X c %d\n", lbuf[i], i);
		writereg(lbuf[i], lp -> axi_l_base_addr + CB_OFIFO_VALUE * 4);
	}

	pr_debug("Written: %ld bytes", count);
	ret = count;
	end:
		kfree(lbuf);
	up_interruptible:
		up(&lp -> sem);
		return ret;
}

ssize_t fifo_read (struct file *file, char __user *buf, size_t count, loff_t *f_pos) {
	struct comblock_local * lp =  (struct comblock_local*) file -> private_data;
	int *lbuf;
	ssize_t ret = 0;
	unsigned int i = 0;

	pr_debug("ComBlock: FIFO read %ld bytes.", count);

	if((count % 4 !=0) && (count < 1)) {
		pr_debug("Only 32 bit operations allowed.");
		return -EPERM;
	}

	if(fifo_count(lp -> axi_l_base_addr, 0) < count) {
		pr_debug("ComBlock: FIFO overflow.");
		ret = -E2BIG;
		goto up_interruptible;
	}

	if(down_interruptible(&lp -> sem) || fifo_empty(lp -> axi_l_base_addr)) {
		pr_debug("ComBlock: BUSY.");
		return -EBUSY;
	}

	lbuf = kzalloc(count, GFP_KERNEL);
	if(!lbuf) {
		pr_debug("ComBlock: kzalloc failed.");
		ret = -ENOMEM;
		goto up_interruptible;
	}

	pr_debug("Mem ADDR: %llX", lp -> axi_l_start + CB_IFIFO_VALUE * 4);
	for(i = 0; i < count / 4; i ++) {
		lbuf[i] = readreg(lp -> axi_l_base_addr + CB_IFIFO_VALUE * 4);
		pr_debug("Read %X: %d\n", i, lbuf[i]);
	}

	if(copy_to_user(buf, lbuf, count) != 0) {
		pr_debug("ComBlock: copy to user failed");
		ret = -EIO;
		goto end;
	}

#ifdef DEBUG
	for (i = 0; i < count; i++) {
		pr_debug("[USER] Read from fifo: %X c %d.\n", buf[i], i);
	}
#endif

	ret = count;
	end:
		kfree(lbuf);
	up_interruptible:
		up(&lp -> sem);
		return ret;
}

loff_t fifo_o_lseek (struct file *file, loff_t offset, int whence) {
	struct comblock_local * lp =  (struct comblock_local*) file -> private_data;
	unsigned int max_size = (lp -> fifo_out_depth - 1) * 4;
	unsigned int count, ret = 0;

	pr_debug("ComBlock: FIFO out seek.");

	if(down_interruptible(&lp -> sem)) {
		pr_debug("ComBlock: BUSY.");
		return -EBUSY;
	}

	count = fifo_count(lp -> axi_l_base_addr, 1); // return fifo count

	switch(whence) {
		case SEEK_CUR:
			ret = count;
		break;
		case SEEK_END:
			ret = max_size;
		break;
		default:
			writereg(1, lp -> axi_l_base_addr + CB_OFIFO_CONTROL * 4);
			writereg(0, lp -> axi_l_base_addr + CB_OFIFO_CONTROL * 4);
			ret = count;
		break;
	}

	up(&lp -> sem);
	return ret;
}

loff_t fifo_i_lseek (struct file *file, loff_t offset, int whence) {
	struct comblock_local * lp =  (struct comblock_local*) file -> private_data;
	unsigned int max_size = (lp -> fifo_in_depth - 1) * 4;
	unsigned int count = 0;
	loff_t ret = 0;

	pr_debug("ComBlock: FIFO in seek.");

	if(down_interruptible(&lp -> sem)) {
		pr_debug("ComBlock: BUSY.");
		return -EBUSY;
	}
	
	count = fifo_count(lp -> axi_l_base_addr, 0); // return fifo count

	switch(whence) {
		case SEEK_CUR:
			ret = count;
		break;
		case SEEK_END:
			ret = max_size;
		break;
		default:
			writereg(1, lp -> axi_l_base_addr + CB_IFIFO_CONTROL * 4);
			writereg(0, lp -> axi_l_base_addr + CB_IFIFO_CONTROL * 4);
			ret = count;
		break;
	}

	up(&lp -> sem);
	return ret;
}

int device_open(struct inode *inode, struct file *file) {
	struct comblock_local *lp;
	unsigned int minor, minor_offset, dev_n;
	
	minor = MINOR(inode -> i_rdev);
	pr_debug("ComBlock: open (%d)\n", minor);
	
	minor_offset = minor % CDEV_NUM;
	dev_n = minor - minor_offset / CDEV_NUM;
	
	lp = container_of(inode -> i_cdev, struct comblock_local, cdev[minor_offset]);
	
	pr_debug("minor = %u, minor_offset = %u, dev_n= %u \n", minor, minor_offset, dev_n);
	pr_debug("Lp major %d, minor %d \n", lp -> major, lp -> minor[minor_offset]);
	
	file -> private_data = lp;

	return SUCCESS;
}

int device_release(struct inode *inode, struct file *file) {
	struct comblock_local * lp;
	unsigned int minor, minor_offset, dev_n;

	minor = MINOR(inode -> i_rdev);
	pr_debug("ComBlock: release (%d)\n", minor);
	
	minor_offset = minor % CDEV_NUM;
	dev_n = minor - minor_offset / CDEV_NUM;

	lp = container_of(inode -> i_cdev, struct comblock_local, cdev[minor_offset]);

	pr_debug("minor = %u, minor_offset = %u, dev_n= %u \n", minor, minor_offset, dev_n);
	pr_debug("Lp major %d, minor %d \n", lp -> major, lp -> minor[minor_offset]);

	pr_debug("ComBlock: release(%p,%p)\n", inode, file);

	return SUCCESS;
}

MODULE_LICENSE("GPL");
