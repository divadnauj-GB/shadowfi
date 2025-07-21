import os
import sys
import json
from comblock import Comblock


def read_finj_report(file_name):
    if(os.path.exists(os.path.abspath(file_name))):
        with open(file_name,"r") as file:
            return(file.readlines())
    else:
        with open(file_name,"w") as file:
            return([])

def write_finj_report(file_name,result):
    with open(file_name,"a+") as file:
        file.write(result)

def read_fault_list(f_name):
    fault_list_name=f_name
    with open(fault_list_name, "r") as f:
        fault_list = f.readlines()
    if len(fault_list) > 0:
        fault_list = [fault.strip().split(",") for fault in fault_list]
    else:
        print("No fault list found")
        return
    return(fault_list)

def save_file(file_name, mode, data):
    try:
        with open(file_name, mode) as fp:
            for line in data:
                fp.write(line)
    except OSError as err:
        print(f"The file was not saved due to {err}")

def load_fi_infrastructure(filename="file.json"):
    with open(filename,"r") as fin:
        fi_infrastructure = json.load(fin)
        return(fi_infrastructure)

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
    
    with open("fault_descriptor.txt", "w") as file:
        file.write(f"{f_cntrl}\n")
        file.write(f"{modules}\n")
        file.write(f"{component}\n")
        file.write(f"{sr_leght}\n")
        file.write(f"{seu_time}\n")
        file.write(f"{start_bit_pos}\n")
        file.write(f"{end_bit_pos}\n")
        for idx in range(fi_structure["sr_lenght"]):
            absolute_bit_pos = bit_pos + start_bit_pos
            if idx>= start_bit_pos and idx < end_bit_pos:
                if idx == absolute_bit_pos:
                    file.write(f"{1}\n")
                else:
                    if idx == end_bit_pos-2:
                        file.write(f"{f_cntrl&1}\n")
                        f_cntrl = f_cntrl >> 1
                    elif idx == end_bit_pos -1:
                        file.write(f"{f_cntrl&1}\n")
                        f_cntrl = f_cntrl >> 1
                    else:
                        file.write(f"{0}\n")                                
            else:
                file.write(f"{0}\n")


def read_fault_descriptor():
    with open("fault_descriptor.txt", "r") as file:
        f_descriptor = file.readlines()
    result = [int(val) for val in f_descriptor]
    return(result)





        