#include "comblock.h"

bool in(unsigned long long *bitset, int number) {
    return *bitset & (1 << number);
}

void add(unsigned long long *bitset, int number) {
    *bitset |= (1 << number);
}

int comblock_init() {
    CB_sets [5] = {0};
    DIR *dir;
    struct dirent *entry;
    const char *path = "/dev/";
    const char *patterns[5] = {"ComBlock_([0-9]+)_regs_i",
                            "ComBlock_([0-9]+)_regs_o",
                            "ComBlock_([0-9]+)_fifo_i",
                            "ComBlock_([0-9]+)_fifo_o",
                            "ComBlock_([0-9]+)_ram_io"};

    regex_t regex;
    regmatch_t match[2];
    char number[2];
    // Open the directory
    dir = opendir(path);
    if (dir == NULL) {
        return -ENOENT;
    }

    for(int i = 0; i < 5; i++) {
        // Compile the regular expression
        if (regcomp(&regex, patterns[i], REG_EXTENDED) != 0) {
            closedir(dir);
            return -1;
        return;
        }

        // Read the directory entries
        while ((entry = readdir(dir)) != NULL) {
            // Match the file name against the regex pattern
            if (regexec(&regex, entry->d_name, 2, match, 0) == 0) {
                // Copy the matched string to the number char
                snprintf(number, match[1].rm_eo - match[1].rm_so + 1, "%.*s", 
                     (int)(match[1].rm_eo - match[1].rm_so), entry->d_name + match[1].rm_so);
                // Add the valid number into the corresponding CB_set
                add(&CB_sets[i], (int) atoi(number));
            }
        }
        regfree(&regex);
    }
    // Close the directory
    closedir(dir);
    return 0;
}

int read_FIFO(u32 comblock, u32 *send_buf, u32 length) {
    char fname[25];
    volatile u32 i = 0;
    send_buf[0] = 0;

    if(!in(&CB_sets[FIFO_I], comblock)) {
        return -ENOENT;
    }

    snprintf(fname, sizeof(fname), "/dev/ComBlock_%d_regs_i", comblock);

    int dev_i = open(fname, O_RDONLY);
    if(dev_i == -1) {
        return -1;
    }

    while(!(lseek(dev_i, 0, SEEK_CUR)) && (i < length)) {
        if (read(dev_i, &send_buf[i + 1], 4) < 0) {
            close(dev_i);
            return -1;
        }
        i++;
        send_buf[0] = i;
    }

    close(dev_i);
    return 0;
}

int write_FIFO(u32 comblock, u32 *recv_buf, u32 length, u32 *send_buf) {
    char fname[25];
    volatile u32 i = 0;
    send_buf[0] = 0;

    if(!in(&CB_sets[FIFO_O], comblock)) {
        return -ENOENT;
    }

    snprintf(fname, sizeof(fname), "/dev/ComBlock_%d_fifo_o", comblock);

    int dev_o = open(fname, O_WRONLY);
    if(dev_o == -1) {
        return -1;
    }

   while(!(lseek(dev_o, 0, SEEK_CUR)) && (i < length)) {
         if (write(dev_i, &recv_buf[i + 1], 4) < 0) {
            close(dev_o);
            return -1;
        }
        i++;
    }

    close(dev_o);
    return 0;
}

int read_RAM(u32 comblock, u32 offset, u32 *send_buf, u32 length, u32 inc) {
    char fname[25];
    volatile u32 i = 0;
    send_buf[0] = 0;

    if(!in(&CB_sets[RAM_IO], comblock)) {
        return -ENOENT;
    }

    snprintf(fname, sizeof(fname), "/dev/ComBlock_%d_ram_io", comblock);

    int dev_i = open(fname, O_RDONLY);
    if(dev_i == -1) {
        return -1;
    }

    if (lseek(dev_i, offset * 4, SEEK_SET) < 0) {
        return -1;
    }

    for (i = 0; i < length; i ++) {
        if (read(dev_i, &send_buf[i + 1], 4) < 0) {
            return -1;
        }
        if (inc > 1) {
            if (lseek(dev_i, 4 * (i - 1), SEEK_CUR) < 0) {
                return -1;
            }
        }
        i++;
        send_buf[0] = i;
    }

    close(dev_i);
    return 0;
}

int write_RAM(u32 comblock, u32 offset, u32 *recv_buf, u32 length, u32 inc, u32 *send_buf) {
    char fname[25];
    volatile u32 i = 0;
    send_buf[0] = 0;

    if(!in(&CB_sets[RAM_IO], comblock)) {
        return -ENOENT;
    }

    snprintf(fname, sizeof(fname), "/dev/ComBlock_%d_ram_io", comblock);

    int dev_o = open(fname, O_WRONLY);
    if(dev_o == -1) {
        return -1;
    }

    if (lseek(dev_i, offset * 4, SEEK_SET) < 0) {
        return -1;
    }

    for (i = 0; i < length; i ++) {
        if (write(dev_o, &recv_buf[i], 4) < 0) {
            return -1;
        }
        if (inc > 1) {
            if (write(dev_o, 4 * (i - 1), SEEK_CUR) < 0) {
                return - 1;
            }
        }
        i++;
        send_buf[0] = i;
    }
    
    close(dev_o);
    return 0;
}

int read_reg(u32 comblock, u32 reg, u32 *send_buf) {
    char fname[25];
    volatile u32 i = 0;
    send_buf[0] = 0;

    if(!in(&CB_sets[REGS_I], comblock)) {
        return -ENOENT;
    }

    snprintf(fname, sizeof(fname), "/dev/ComBlock_%d_regs_i", comblock);

    int dev_i = open(fname, O_RDONLY);
    if(dev_i == -1) {
        return -1;
    }

    if (lseek(dev_i, reg * 4, SEEK_SET) < 0) {
        close(dev_i);
        return -1;
    }

    if (write(dev_i, &send_buf[1], 4) < 0) {
        close(dev_i);
        return -1;
    }

    close(dev_i);
    return 0;
}

int write_reg(u32 comblock, u32 reg, u32 *recv_buf) {
    char fname[25];
    volatile u32 i = 0;
    send_buf[0] = 0;

    if(!in(&CB_sets[REGS_O], comblock)) {
        return -ENOENT;
    }

    snprintf(fname, sizeof(fname), "/dev/ComBlock_%d_regs_o", comblock);

    int dev_o = open(fname, O_WRONLY);
    if(dev_o == -1) {
        return -1;
    }

    if (lseek(dev_o, reg * 4, SEEK_SET) < 0) {
        close(dev_o);
        return -1;
    }

    if (write(dev_o, &recv_buf, 4) < 0) {
        close(dev_o);
        return -1;
    }

    close(dev_o);
    return 0;
}

int clean_FIFO_o(u32 comblock) {
    char fname[25];

    if(!in(&CB_sets[FIFO_O], comblock)) {
        return -ENOENT;
    }

    snprintf(fname, sizeof(fname), "/dev/ComBlock_%d_fifo_o", comblock);
    int dev_o = open(fname, O_WRONLY);
    if(dev_o == -1) {
        return -1;
    }

    if (lseek(dev_o, 0, SEEK_SET) < 0) {
        close(dev_o);
        return -1;
    }
}

int clean_FIFO_i(u32 comblock) {
    char fname[25];

    if(!in(&CB_sets[FIFO_I], comblock)) {
        return -ENOENT;
    }

    snprintf(fname, sizeof(fname), "/dev/ComBlock_%d_fifo_i", comblock);

    int dev_i = open(fname, O_RDONLY);
    if(dev_i == -1) {
        return -1;
    }

    if (lseek(dev_i, 0, SEEK_SET) < 0) {
        close(dev_i);
        return -1;
    }
}