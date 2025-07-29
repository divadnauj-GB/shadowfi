import os
import sys
import json

from core.hyperfpga.comblock.comblock import *


class fpga_engine():
    """Define any constant to be used inside the FPGA engine class"""
    FILENAME="values_dot_product.csv"
    DEFAULWORKPATH="~/work"
    def __init__(self):
        """initialize some variables when required"""
        self.load_result_struct = {'data':[]}
        self.input_run_struct = {'data':[]}
        self.run_out_struct = {'resp':[]}
        ...

    def load_test_data(self, input_args={}):
        """Define the function to read the test data, input_args may contain configuration in adictionary fashion"""
        ...
        return(self.load_result_struct)

    def write_result(self,write_args={},write_data={}):
        """Define the function for writing the results of the fpga_engine"""
        ...


    def run(self,input_args={}):
        self.input_run_struct = input_args
        data_input = self.input_run_struct.get('data',[])
        cb0 = Comblock(0)

        """Define the funtion that runs the workload on the FPGA accelerator you can define functions for controlling the comblock"""
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
        
        ...
        
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