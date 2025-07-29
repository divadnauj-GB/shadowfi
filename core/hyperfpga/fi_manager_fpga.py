import sys
import os
import shutil
import importlib.util
from warnings import warn
import asyncio
import time
import logging

from core.hyperfpga.comblock.comblock import *

def create_fault_descriptor(fi_structure):
    modules = fi_structure["modules"]
    sr_leght = fi_structure["sr_lenght"]
    component = fi_structure["component"]
    start_bit_pos = fi_structure["start_bit_pos"]
    end_bit_pos = fi_structure["end_bit_pos"]
    bit_pos = fi_structure["bit_pos"]
    f_cntrl = fi_structure["f_model"]
    seu_time = fi_structure["seu_time"]
    f_descriptor=[]
    f_descriptor.append(f_cntrl)
    f_descriptor.append(modules)
    f_descriptor.append(component)
    f_descriptor.append(sr_leght)
    f_descriptor.append(seu_time)
    f_descriptor.append(start_bit_pos)
    f_descriptor.append(end_bit_pos)
    for idx in range(fi_structure["sr_lenght"]):
        absolute_bit_pos = bit_pos + start_bit_pos
        if idx>= start_bit_pos and idx < end_bit_pos:
            if idx == absolute_bit_pos:
                f_descriptor.append(1)
            else:
                if idx == end_bit_pos-2:
                    f_descriptor.append(f_cntrl&1)
                    f_cntrl = f_cntrl >> 1
                elif idx == end_bit_pos -1:
                    f_descriptor.append(f_cntrl&1)
                    f_cntrl = f_cntrl >> 1
                else:
                    f_descriptor.append(0)                               
        else:
            f_descriptor.append(0)
    return(f_descriptor) 




def fi_sbtr_config(fault_descriptor):
    def fi_port_conf(cb,RSTN=0, TFEN=0, SREN=0):
        FI_PORT = ((RSTN<<2)|(TFEN<<1)|(SREN))
        cb.write_reg(0,FI_PORT)
    def clk_gen(cb,PORT):
        PORT=PORT^(1<<3)
        cb.write_reg(0,PORT)
        PORT=PORT^(1<<3)
        cb.write_reg(0,PORT)
    cb1 = Comblock(1)
    # 0 -> SREN
    # 1 -> TFEN
    # 2 -> RSTN
    # 3 -> CLK not from here
    RSTN=0
    TFEN=0
    SREN=0
    SI=0
    FI_PORT = ((SI<<4)|(RSTN<<2)|(TFEN<<1)|(SREN))
    cb1.write_reg(0,FI_PORT)
    clk_gen(cb1,FI_PORT)
    RSTN=1
    TFEN=0
    SREN=0
    SI=0
    FI_PORT = ((SI<<4)|(RSTN<<2)|(TFEN<<1)|(SREN))
    for _ in range(10):
        clk_gen(cb1,FI_PORT)
    for element in fault_descriptor[7:]:
        RSTN=1
        TFEN=0
        SREN=1
        SI=element
        FI_PORT = ((SI<<4)|(RSTN<<2)|(TFEN<<1)|(SREN))
        clk_gen(cb1,FI_PORT)
    RSTN=1
    TFEN=1
    SREN=0
    SI=0
    FI_PORT = ((SI<<4)|(RSTN<<2)|(TFEN<<1)|(SREN))
    for _ in range(2):
        clk_gen(cb1,FI_PORT)   


"""
def run_one_task_fault_free_emulation(input_data={},fi_config={}):
    emu_config = fi_config.get('project',{}).get('emu_config', {})
    max_num_inj = emu_config.get('max_num_faults', -1)
    num_target_components = int(emu_config.get('num_target_components', 0))
    total_bit_shift = int(emu_config.get('total_bit_shift', 0))
    
    fi_structure = {
        "modules": num_target_components,  # 
        "sr_lenght": total_bit_shift,  # 
        "f_model": 3,  # fault model: 0-> stuck-at-0, 1: stuck-at-1, 2: bit-flip
        "component": 0,
        "start_bit_pos": 0,
        "end_bit_pos": 0,
        "bit_pos": 0,
        "seu_time": 0,
    }
    
    try:
        f_descriptor=create_fault_descriptor(fi_structure)
        fi_sbtr_config(f_descriptor)
        result_data=apply_test_data(input_data)
    except Exception as error:
        raise(error)
    return result_data



def run_one_task_fault_emulation(fault_list, input_data={}, golden_results={},fi_config={}):
    emu_config = fi_config.get('project',{}).get('emu_config', {})
    max_num_inj = emu_config.get('max_num_faults', -1)
    num_target_components = int(emu_config.get('num_target_components', 0))
    total_bit_shift = int(emu_config.get('total_bit_shift', 0))
    
    sdc_count = 0
    masked = 0
    simulation_report = []
    fi_structure = {
        "modules": num_target_components,  # 
        "sr_lenght": total_bit_shift,  # 
        "f_model": 3,  # fault model: 0-> stuck-at-0, 1: stuck-at-1, 2: bit-flip
        "component": 0,
        "start_bit_pos": 0,
        "end_bit_pos": 0,
        "bit_pos": 0,
        "seu_time": 0,
    }
    for idx, fault_info in enumerate(fault_list):
        # generate one fault descriptor
        # List_injections.append([idx, inst, module, start_bit_pos, end_bit_pos, fault_index, ftype, seutime])
        fi_structure["component"] = int(fault_info[0])
        fi_structure["start_bit_pos"] = int(fault_info[3])
        fi_structure["end_bit_pos"] = int(fault_info[4])
        fi_structure["bit_pos"] = int(fault_info[5])
        fi_structure["f_model"] = int(fault_info[6])
        fi_structure["seu_time"] = int(fault_info[7])

        f_descriptor=create_fault_descriptor(fi_structure)
        fi_sbtr_config(f_descriptor)
        try:
            result_data=apply_test_data(input_data)
            fi_class=sdc_check(result_data,golden_results)
        except Exception as error:
            fi_class = "DUE"
            result_data={}

        result_fi = f"{fault_info[0]},{fault_info[1]},{fault_info[2]},{fault_info[3]},{fault_info[4]},{fault_info[5]},{fault_info[6]}"
        
        if fi_class == "Masked":
            masked += 1
            simulation_report.append([result_fi,fi_class,{}])
        else:
            sdc_count += 1
            simulation_report.append([result_fi,fi_class,result_data])
        if idx>=max_num_inj and max_num_inj>0:
            break
    return simulation_report
"""


