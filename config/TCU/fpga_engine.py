import os
import sys
import json

from core.hyperfpga.comblock.comblock import *


class fpga_engine():
    FILENAME="values_dot_product.csv"
    DEFAULWORKPATH="~/work"
    def __init__(self):
        self.load_result_struct = {'data':[]}
        self.input_run_struct = {'data':[]}
        self.run_out_struct = {'resp':[]}

    def load_test_data(self, input_args={}):
        data_set_work_dir=input_args.get('work_dir',self.DEFAULWORKPATH)
        tcu_data_filename = f"{os.path.abspath(data_set_work_dir)}/{self.FILENAME}"
        with open(tcu_data_filename,"r") as file:
            test_data = file.readlines()

        csv_filtered = [line.strip().split(',') for line in test_data]

        data_ready = []

        for items in csv_filtered:
            A0=int(items[0],16)
            A1=int(items[1],16)
            A2=int(items[2],16)
            A3=int(items[3],16)
            B0=int(items[4],16)
            B1=int(items[5],16)
            B2=int(items[6],16)
            B3=int(items[7],16)
            C0=int(items[8],16)
            D0=int(items[9],16)

            new_row = [A0,A1,A2,A3,A0,A1,A2,A3,A0,A1,A2,A3,A0,A1,A2,A3,B0,B0,B0,B0,B1,B1,B1,B1,B2,B2,B2,B2,B3,B3,B3,B3,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0]
            data_ready.extend(new_row)
            self.load_result_struct['data']=data_ready
        return(self.load_result_struct)

    def write_result(self,write_args={},write_data={}):
        mode = write_args.get('mode','golden')
        work_dir = write_args.get('work_dir',"~/work")
        resp = write_data.get('resp',[])
        with open(f"{os.path.abspath(work_dir)}/output_dot_product_{mode}.csv","w") as fileo:
            for idx in range(0,len(resp),16):
                TCU_out=resp[idx:idx+16]
                line_str = [f"{val:0x}" for val in TCU_out]
                line=",".join(line_str)
                fileo.write(f"{line}\n")


    def run(self,input_args={}):
        self.input_run_struct = input_args
        data_input = self.input_run_struct.get('data',[])
        cb0 = Comblock(0)
        def reset_SVC(cb):
            cb.write_reg(0,0)  # Reset the accelerator and clear the Comblock FIFO
            cb.write_reg(0,0xffffffff)  # Release reset 
        
        def reset_fifo_in_out(cb):
            cb.fifo_in_clear()
            cb.fifo_out_clear()

        def read_check_fifo_output(cb,list_inout):
            rd_fl= cb.fifo_in_elements()
            if rd_fl!=0:
                list_inout.extend(cb.read_fifo(rd_fl))
            (data, elements, bit_over_flow, bit_almost_full, bit_full)=cb.fifo_out_status()
            return(elements, bit_almost_full)
        
        Read_fifo=[]
        cnt=0
        b=0
        e=0
        t=len(data_input)
        
        try:
            reset_SVC(cb0)
            reset_fifo_in_out(cb0)
            for idx in range(0,len(data_input),1024):    
                (elements, bit_almost_full)=read_check_fifo_output(cb0,Read_fifo)
                while(bit_almost_full):
                    (elements, bit_almost_full)=read_check_fifo_output(cb0,Read_fifo)               
                cb0.write_fifo(data_input[idx:idx+1024])
            (elements, bit_almost_full)=read_check_fifo_output(cb0,Read_fifo)          
        finally:
            print("got here")
        self.run_out_struct['resp']=Read_fifo
        return (self.run_out_struct)


    def sdc_check(self,results, golden):
        """sdc_check
        Args:
            results (dict): Dictionary with the results 
            golden (dict): Dictionary with the golden results

        Returns:
            str: return an string indicating whether the inputs match
        """
        if results != golden:
            result = "SDC"
        else:
            result = "Masked"
        return result