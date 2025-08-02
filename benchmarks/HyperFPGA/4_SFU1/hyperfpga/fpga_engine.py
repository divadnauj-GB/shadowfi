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
        data_set_dir = os.path.abspath(data_set_work_dir)
        
        sfu_data_0 = f"{data_set_dir}/dataset/input_cordic.csv"
        sfu_data_1 = f"{data_set_dir}/dataset/input_cordic.csv"
        sfu_data_2 = f"{data_set_dir}/dataset/input_rsqrt.csv"
        sfu_data_3 = f"{data_set_dir}/dataset/input_log2.csv"
        sfu_data_4 = f"{data_set_dir}/dataset/input_ex2.csv"

        data_arranged = {}
        with open(sfu_data_0,"r") as file:
            test_data0 = file.readlines()
            data_arranged[0]=[int(line.strip(),16) for line in test_data0]
            
        with open(sfu_data_1,"r") as file:
            test_data1 = file.readlines()
            data_arranged[1]=[int(line.strip(),16) for line in test_data1]
                
        with open(sfu_data_2,"r") as file:
            test_data2 = file.readlines()
            data_arranged[2]=[int(line.strip(),16) for line in test_data2]
                
        with open(sfu_data_3,"r") as file:
            test_data3 = file.readlines()
            data_arranged[3]=[int(line.strip(),16) for line in test_data3]
                
        with open(sfu_data_4,"r") as file:
            test_data4 = file.readlines()
            data_arranged[4]=[int(line.strip(),16) for line in test_data4]
            
        self.load_result_struct['data']=data_arranged
        return(self.load_result_struct)

    def write_result(self,write_args={},write_data={}):
        mode = write_args.get('mode','golden')
        work_dir = write_args.get('work_dir',"~/work")
        resp = write_data.get('resp',{})

        dest_root_work_dir = os.path.abspath(work_dir)

        with open(f"{dest_root_work_dir}/output_sfu_{mode}.csv","w") as fileo:
            for keys in resp.keys():
                for val in resp[keys]:
                    line_str = f"{keys},{val:0x} \n"                
                    fileo.write(line_str)


    def run(self,input_args={}):
        self.input_run_struct = input_args
        data_input = self.input_run_struct.get('data',{})
        cb0 = Comblock(0)
        def reset_SVC(cb):
            cb.write_reg(0,0)  # Reset the accelerator and clear the Comblock FIFO
            cb.write_reg(0,0xffffffff)  # Release reset 

        def sfu_op_sel(cb,sel):
            cb.write_reg(1,sel)  # Reset the accelerator and clear the Comblock FIFO
        
        def reset_fifo_in_out(cb):
            cb.fifo_in_clear()
            cb.fifo_out_clear()
    
        def read_check_fifo_output(cb,list_inout):
            rd_fl= cb.fifo_in_elements()
            if rd_fl!=0:
                if rd_fl==1:
                    list_inout.append(cb.read_fifo(rd_fl))
                else:
                    list_inout.extend(cb.read_fifo(rd_fl))
            (datax, elements, bit_over_flow, bit_almost_full, bit_full)=cb.fifo_out_status()
            return(elements, bit_almost_full)
        
        data_out = {}        
        try:
            reset_SVC(cb0)
            reset_fifo_in_out(cb0)
            sfu_op_sel(cb0,0)
            for key in data_input.keys():
                data = data_input[key]
                sfu_op_sel(cb0,int(key))
                Read_fifo=[]
                base=0
                end=0
                tot=len(data)
                
                for idx in range(0,len(data)):                    
                    (elements, bit_almost_full)=read_check_fifo_output(cb0,Read_fifo)
                    while(bit_almost_full):
                        (elements, bit_almost_full)=read_check_fifo_output(cb0,Read_fifo)
                    base=end
                    end=base+((1024-elements))                    
                    if end<tot and base<tot:
                        cb0.write_fifo(data[base:end])
                    elif base<tot and end>=tot:
                        cb0.write_fifo(data[base:tot])
                    else:
                        (elements, bit_almost_full)=read_check_fifo_output(cb0,Read_fifo)
                        break                

                cnt=0
                while(len(Read_fifo)<len(data)):
                #while(cnt<1024*5):
                    (elements, bit_almost_full)=read_check_fifo_output(cb0,Read_fifo)
                    cnt=cnt+1
                data_out[key]=Read_fifo
                       
        finally:
            print("got here")
        self.run_out_struct['resp']=data_out
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