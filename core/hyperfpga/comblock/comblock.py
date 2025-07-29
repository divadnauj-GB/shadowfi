import os
from struct import unpack
from typing import Union


class Comblock:
    def __init__(self, comblock_num: int = 0):
        self.comblock_num = comblock_num
        self.cb_path = f"/dev/ComBlock_{self.comblock_num}"
        self.regs_fout = f"{self.cb_path}_regs_o"
        self.regs_fin = f"{self.cb_path}_regs_i"
        self.fifo_fout = f"{self.cb_path}_fifo_o"
        self.fifo_fin = f"{self.cb_path}_fifo_i"
        self.fram = f"{self.cb_path}_ram"

    def write_reg(self, register: int = 0, data: int = 0):
        try:
            with os.fdopen(os.open(self.regs_fout, os.O_WRONLY),
                           "bw", buffering = 0) as reg_out:
                reg_out.seek(register * 4)
                reg_out.write((data).to_bytes(4, 'little'))
        except FileNotFoundError:
            raise ValueError("File does not exist")

    def read_reg(self, register: int = 0):
        try:
            with os.fdopen(os.open(self.regs_fin, os.O_RDONLY),
                           "br", buffering = 0) as reg_in:
                reg_in.seek(register * 4)
                return int.from_bytes(reg_in.read(4), 'little')
        except:
            return None

    def write_fifo(self, data: Union[int, list] = 0):
        try:
            with os.fdopen(os.open(self.fifo_fout, os.O_WRONLY),
                           "bw", buffering = 0) as fifo_out:
                if isinstance(data, list):
                    for value in data:
                        fifo_out.write((value).to_bytes(4, 'little'))
                else: 
                    fifo_out.write((data).to_bytes(4, 'little'))
        except FileNotFoundError:
            raise ValueError("File does not exist")

    def read_fifo(self, length = 1):
        try:
            with os.fdopen(os.open(self.fifo_fin, os.O_RDONLY),
                           "br", buffering = 0) as fifo_in:
                if length == 1:
                    return int.from_bytes(fifo_in.read(4), 'little')
                return [int.from_bytes(fifo_in.read(4), 'little') for _ in range(length)]
        except:
            return None

    def fifo_in_elements(self):
        with os.fdopen(os.open(self.fifo_fin, os.O_RDONLY),
                       "br", buffering = 0) as fifo_in:
            return fifo_in.tell()//4

    def fifo_in_status(self):
        data = self.read_reg(34)
        bit_empty = (data >> 0) & 0x1
        bit_almost_empty = (data >> 1) & 0x7FFF 
        bit_under_flow = (data >> 2) & 0x1 
        elements = (data >> 16) & 0xFFFF
        return data, elements, bit_under_flow, bit_almost_empty, bit_empty

    def fifo_out_status(self):
        data = self.read_reg(38)
        bit_full = (data >> 0) & 0x1
        bit_almost_full = (data >> 1) & 0x7FFF 
        bit_over_flow = (data >> 2) & 0x1 
        elements = (data >> 16) & 0xFFFF
        return data, elements, bit_over_flow, bit_almost_full, bit_full

    def fifo_in_clear(self):
        self.write_reg(33, 1)
        self.write_reg(33, 0)
        while self.fifo_in_elements() != 0:
            _ = self.read_fifo()

    def fifo_out_clear(self):
        self.write_reg(37, 1)
        self.write_reg(37, 0)
        
    def read_ram(self, addr: int =0 , addr_max: int = 0, addr_length: int = 16):
        try:
            with os.fdopen(os.open(self.fram, os.O_RDWR), "br+", buffering = 0) as ram:
                if addr_max == 0:
                    if addr <= 2**addr_length:
                        ram.seek(addr*4, 0)
                        data = int.from_bytes(ram.read(4), 'little')
                    else:
                        raise TypeError("Address out of range.")
                else:
                    if addr_max <= 2**addr_length:
                        data = []
                        for value in  range(addr, addr_max+1):
                            ram.seek(value*4, 0)
                            data.append(int.from_bytes(ram.read(4), 'little'))
                    else:
                        raise TypeError("Address out of range.")
            return data
        except:
            return None

    def write_ram(self, addr: int = 0, data = Union[int, list], addr_length: int = 16):
        try:
            with os.fdopen(os.open(self.fram, os.O_RDWR), "br+", buffering = 0) as ram:
                if isinstance(data, list):
                    data_len = len(data)
                    addr_max = addr + data_len
                else:
                    addr_max = addr
                if addr_max <= 2**addr_length:
                    if isinstance(data, list):
                        for i, value in enumerate(data):
                            ram.seek((addr+i)*4)
                            ram.write((value).to_bytes(4, 'little'))
                    else:
                        ram.seek(addr*4)
                        ram.write((data).to_bytes(4, 'little'))
                else:
                    raise TypeError("Address out of range.")
        except FileNotFoundError:
            raise ValueError("File does not exist")
