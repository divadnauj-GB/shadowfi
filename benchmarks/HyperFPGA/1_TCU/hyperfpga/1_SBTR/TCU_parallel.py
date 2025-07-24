
from fpga_init import *
import ipyparallel as ipp
import numpy as np
from PIL import Image
import math
import time
from fault_inj_helper import *


FPGA_cluster = init_fpga(configname='TCU_1_SBTR',nodes_selected=[1])
nodes = FPGA_cluster.rc[:]

with nodes.sync_imports():
    import os
    from struct import unpack
    from comblock import Comblock

@nodes.remote(block=True)
def finj_task(input_data,f_list=[],fi_config={}):
    def parse_fault(fi_config={},fault=[]):
        fault_list_name= fi_config.get("FAULT_LIST_NAME", "fault_list.txt")
        fault_model = fi_config.get("FAULT_MODEL","S@")
        F_sim_report = fi_config.get("F_SIM_REPORT", "simulation_report.csv")
        max_num_inj = fi_config.get("MAX_NUM_INJ", -1)
        num_target_components = fi_config.get("NUM_TARGET_COMPONENTS", 1)
        total_bit_shift = fi_config.get("TOTAL_BIT_SHIFT", 0)
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
    
        if len(fault)!=0:
            fi_structure["component"] = int(fault[0])
            fi_structure["start_bit_pos"] = int(fault[3])
            fi_structure["end_bit_pos"] = int(fault[4])
            fi_structure["bit_pos"] = int(fault[5])
            fi_structure["f_model"] = int(fault[6])
            fi_structure["seu_time"] = int(fault[7])
        return(fi_structure)
        
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

    def tcu_compute(data_input):
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
        b=0;
        e=0
        t=len(data_input)
        
        try:
            reset_SVC(cb0)
            reset_fifo_in_out(cb0)
            """
            for idx in range(0,len(data_input)):  
                (elements, bit_almost_full)=read_check_fifo_output(cb0,Read_fifo)
                while(bit_almost_full):
                    (elements, bit_almost_full)=read_check_fifo_output(cb0,Read_fifo)
                b=e
                e=b+(1024-elements)
                if e<t and b<t:
                    cb0.write_fifo(data_input[b:e])
                elif b<t and e>=t:
                    cb0.write_fifo(data_input[b:t])
                else:
                    (elements, bit_almost_full)=read_check_fifo_output(cb0,Read_fifo)
                    break
            """
            for idx in range(0,len(data_input),1024):    
                (elements, bit_almost_full)=read_check_fifo_output(cb0,Read_fifo)
                while(bit_almost_full):
                    (elements, bit_almost_full)=read_check_fifo_output(cb0,Read_fifo)               
                cb0.write_fifo(data_input[idx:idx+1024])
            (elements, bit_almost_full)=read_check_fifo_output(cb0,Read_fifo)          
        finally:
            print("got here")
        return Read_fifo
    
    Result={}
    if len(f_list)!=0:
        for idx,fault_info in enumerate(f_list):
            fi_structure=parse_fault(fi_config=fi_config,fault=fault_info)
            f_descriptor=create_fault_descriptor(fi_structure)
            fi_sbtr_config(f_descriptor)
            resp_faulty = tcu_compute(input_data)
            Result[idx]=resp_faulty
    else:
        fi_structure=parse_fault(fi_config=fi_config,fault=[])
        f_descriptor=create_fault_descriptor(fi_structure)
        fi_sbtr_config(f_descriptor)
        resp_faulty = tcu_compute(input_data)
        #resp_faulty = tcu_compute(input_data) # just the first time in the golden sim
        Result[0]=resp_faulty
    return(Result)

    
    
def load_data():
    tcu_data_filename = f"./dataset/values_dot_product.csv"
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

        #new_row = [A0,A1,A2,A3,A0,A1,A2,A3,A0,A1,A2,A3,A0,A1,A2,A3,B0,B0,B0,B0,B1,B1,B1,B1,B2,B2,B2,B2,B3,B3,B3,B3,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,D0,D0,D0,D0,D0,D0,D0,D0,D0,D0,D0,D0,D0,D0,D0,D0]
        new_row = [A0,A1,A2,A3,A0,A1,A2,A3,A0,A1,A2,A3,A0,A1,A2,A3,B0,B0,B0,B0,B1,B1,B1,B1,B2,B2,B2,B2,B3,B3,B3,B3,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0]
        data_ready.extend(new_row)
    return(data_ready)


def write_result(resp,mode="golden"):
    with open(f"./logs/output_dot_product_{mode}.csv","w") as fileo:
        for idx in range(0,len(resp),16):
            TCU_out=resp[idx:idx+16]
            line_str = [f"{val:0x}" for val in TCU_out]
            line=",".join(line_str)
            fileo.write(f"{line}\n")

def main():    
    FAULT_MODEL="S@"
    F_LIST_NAME="fault_list.csv"
    F_INJ_REPORT="finj_report.csv"
    MAX_NUM_INJ=10
    NUM_JOBS=1
    CHUNK_SIZE=10

    os.system("mkdir -p logs")
    
    fi_infrastructure=load_fi_infrastructure("sub_tensor_core_fi_infrastructure.json")
    num_target_components=len(fi_infrastructure)
    fault_list=read_fault_list(f"{FAULT_MODEL}_{F_LIST_NAME}")
    total_bit_shift = int(fault_list[-1][4])

    
    fi_config = {
        "FAULT_LIST_NAME": f"{FAULT_MODEL}_{F_LIST_NAME}",
        "FAULT_MODEL": f"{FAULT_MODEL}",
        "F_SIM_REPORT": f"{F_INJ_REPORT}",
        "MAX_NUM_INJ": MAX_NUM_INJ,
        "NUM_TARGET_COMPONENTS": num_target_components,
        "TOTAL_BIT_SHIFT": total_bit_shift,
        "JOBS": NUM_JOBS
    }
    
    TCU_data=load_data()
    s_time=time.time()
    resp_golden=finj_task(TCU_data,f_list=[],fi_config=fi_config)
    write_result(resp_golden[0][0],mode="golden")
    e_time=time.time()
    print(f"fi_time={e_time-s_time}---------------------")
    
    
    f_index=len(read_finj_report(f"{FAULT_MODEL}_{F_INJ_REPORT}"))
    
    
    for idx in range(f_index,len(fault_list),CHUNK_SIZE):
        s_time=time.time()
        fault_info=fault_list[idx:idx+CHUNK_SIZE]
        resp_faulty=finj_task(TCU_data,f_list=fault_info,fi_config=fi_config)
        for keys in resp_faulty[0].keys():
            key=int(keys)
            result_sim="Masked"
            if resp_golden[0][0]!=resp_faulty[0][keys]:
                result_sim="SDC"
                write_result(resp_faulty[0][keys],mode=f"f{idx+int(key)}")
            result = f"{fault_info[key][0]},{fault_info[key][1]},{fault_info[key][2]},{fault_info[key][3]},{fault_info[key][4]},{fault_info[key][5]},{fault_info[key][6]},{fault_info[key][7]},{result_sim}\n"
            write_finj_report(f"{FAULT_MODEL}_{F_INJ_REPORT}",result)
        e_time=time.time()
        print(f"fi_time={e_time-s_time}---------------------")
        if idx>=MAX_NUM_INJ and MAX_NUM_INJ>=0:
            break
    
    FPGA_cluster.reboot_cluster()

if __name__=='__main__':
    main()